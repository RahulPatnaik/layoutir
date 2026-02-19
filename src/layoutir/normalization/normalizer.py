"""
Normalization layer converting raw elements to canonical IR.

This layer applies deterministic hashing and schema validation.
"""

from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

from ..schema import (
    Document,
    Block,
    BlockType,
    BoundingBox,
    TableData,
    ImageData,
    DocumentMetadata,
    Relationship,
    FormattingData,
    FontProperties,
    TextStyle,
)
from ..extraction.docling_extractor import RawDocument, RawBlock, RawTable, RawImage
from ..utils.hashing import (
    hash_file,
    generate_document_id,
    generate_block_id,
    generate_table_id,
    generate_image_id,
)

logger = logging.getLogger(__name__)


class Normalizer:
    """Converts raw extracted elements to canonical IR"""

    def __init__(self, source_path: Path, parser_version: str):
        """
        Initialize normalizer.

        Args:
            source_path: Path to source file
            parser_version: Version string of parser used
        """
        self.source_path = Path(source_path)
        self.parser_version = parser_version

        # Compute source hash once
        self.source_hash = hash_file(self.source_path)
        self.document_id = generate_document_id(self.source_hash)

        logger.info(f"Initialized normalizer for document {self.document_id}")

    def normalize(self, raw_doc: RawDocument, config: Dict[str, Any]) -> Document:
        """
        Normalize raw document to canonical IR.

        Args:
            raw_doc: Raw extracted document
            config: Configuration used for processing

        Returns:
            Canonical Document IR
        """
        logger.info("Normalizing raw document to canonical IR")

        # Normalize blocks
        blocks = self._normalize_blocks(raw_doc.blocks)

        # Normalize tables and create table blocks
        table_blocks, table_count = self._normalize_tables(raw_doc.tables)
        blocks.extend(table_blocks)

        # Normalize images and create image blocks
        image_blocks, image_count = self._normalize_images(raw_doc.images)
        blocks.extend(image_blocks)

        # Sort blocks by order
        blocks.sort(key=lambda b: b.order)

        # NEW: Validate and annotate ordering
        from .ordering_validator import OrderingValidator
        validator = OrderingValidator()
        blocks = validator.validate_and_annotate(blocks)

        # Build relationships
        relationships = self._build_relationships(blocks)

        # Create document metadata
        # Filter out keys we're setting explicitly to avoid duplicates
        extra_metadata = {
            k: v for k, v in raw_doc.metadata.items()
            if k not in {'page_count', 'source_format', 'source_path', 'source_hash'}
        }

        metadata = DocumentMetadata(
            page_count=raw_doc.page_count,
            source_format=self.source_path.suffix.lstrip('.'),
            source_path=str(self.source_path),
            source_hash=self.source_hash,
            **extra_metadata
        )

        # Compute stats
        stats = {
            'block_count': len(blocks),
            'table_count': table_count,
            'image_count': image_count,
            'page_count': raw_doc.page_count,
        }

        # Create canonical document
        document = Document(
            document_id=self.document_id,
            schema_version="1.0.0",
            parser_version=self.parser_version,
            metadata=metadata,
            blocks=blocks,
            relationships=relationships,
            stats=stats,
            processing_timestamp=datetime.utcnow(),
            config_used=config,
        )

        logger.info(
            f"Normalized document: {len(blocks)} blocks, "
            f"{table_count} tables, {image_count} images"
        )

        return document

    def _normalize_blocks(self, raw_blocks: List[RawBlock]) -> List[Block]:
        """Normalize text blocks to canonical format"""
        blocks = []

        for raw_block in raw_blocks:
            # Generate deterministic block ID
            block_id = generate_block_id(
                content=raw_block.text,
                page_number=raw_block.page_number,
                order=raw_block.order,
                block_type=raw_block.block_type
            )

            # Map to BlockType enum
            try:
                block_type = BlockType(raw_block.block_type)
            except ValueError:
                logger.warning(
                    f"Unknown block type '{raw_block.block_type}', defaulting to PARAGRAPH"
                )
                block_type = BlockType.PARAGRAPH

            # Normalize bounding box
            bbox = self._normalize_bbox(raw_block.bbox) if raw_block.bbox else None

            # Extract metadata
            metadata = raw_block.metadata.copy()

            # Create block
            block = Block(
                block_id=block_id,
                type=block_type,
                parent_id=None,  # Set in relationship building
                page_number=raw_block.page_number,
                bbox=bbox,
                content=raw_block.text,
                metadata=metadata,
                level=metadata.get('level'),
                order=raw_block.order,
            )

            # NEW: Convert formatting if present
            if raw_block.formatting:
                block.formatting_data = self._normalize_formatting(raw_block.formatting)

            blocks.append(block)

        return blocks

    def _normalize_tables(self, raw_tables: List[RawTable]) -> tuple[List[Block], int]:
        """Normalize tables to canonical format"""
        blocks = []

        for idx, raw_table in enumerate(raw_tables):
            # Generate deterministic table ID
            table_id = generate_table_id(
                document_id=self.document_id,
                page_number=raw_table.page_number,
                table_index=idx,
                raw_text=raw_table.raw_text
            )

            # Create TableData
            table_data = TableData(
                table_id=table_id,
                rows=len(raw_table.data),
                columns=len(raw_table.data[0]) if raw_table.data else 0,
                headers=raw_table.headers,
                data=raw_table.data,
                raw_text=raw_table.raw_text,
            )

            # Generate block ID for table
            block_id = generate_block_id(
                content=raw_table.raw_text,
                page_number=raw_table.page_number,
                order=raw_table.order,
                block_type="table"
            )

            # Normalize bounding box
            bbox = self._normalize_bbox(raw_table.bbox) if raw_table.bbox else None

            # Create table block
            block = Block(
                block_id=block_id,
                type=BlockType.TABLE,
                parent_id=None,
                page_number=raw_table.page_number,
                bbox=bbox,
                content=raw_table.raw_text,
                metadata={'table_id': table_id},
                table_data=table_data,
                order=raw_table.order,
            )

            blocks.append(block)

        return blocks, len(raw_tables)

    def _normalize_images(self, raw_images: List[RawImage]) -> tuple[List[Block], int]:
        """Normalize images to canonical format"""
        blocks = []

        for idx, raw_image in enumerate(raw_images):
            # Generate deterministic image ID
            image_id = generate_image_id(
                document_id=self.document_id,
                page_number=raw_image.page_number,
                image_index=idx,
                image_bytes=raw_image.image_bytes
            )

            # Create ImageData (path will be set during export)
            image_data = ImageData(
                image_id=image_id,
                page_number=raw_image.page_number,
                bbox=self._normalize_bbox(raw_image.bbox) if raw_image.bbox else None,
                extracted_path=None,  # Set during export
                caption=raw_image.caption,
                format=raw_image.format,
                width=raw_image.width,
                height=raw_image.height,
            )

            # Generate block ID for image
            content = raw_image.caption or f"[Image {image_id}]"
            block_id = generate_block_id(
                content=content,
                page_number=raw_image.page_number,
                order=raw_image.order,
                block_type="image"
            )

            # Normalize bounding box
            bbox = self._normalize_bbox(raw_image.bbox) if raw_image.bbox else None

            # Store image bytes in metadata for export
            metadata = {
                'image_id': image_id,
                'image_bytes': raw_image.image_bytes,  # Temporary for export
            }

            # Create image block
            block = Block(
                block_id=block_id,
                type=BlockType.IMAGE,
                parent_id=None,
                page_number=raw_image.page_number,
                bbox=bbox,
                content=content,
                metadata=metadata,
                image_data=image_data,
                order=raw_image.order,
            )

            blocks.append(block)

        return blocks, len(raw_images)

    def _normalize_bbox(self, bbox_dict: Dict[str, float]) -> BoundingBox:
        """Normalize bounding box to canonical format"""
        return BoundingBox(
            x0=bbox_dict.get('x0', 0.0),
            y0=bbox_dict.get('y0', 0.0),
            x1=bbox_dict.get('x1', 0.0),
            y1=bbox_dict.get('y1', 0.0),
            page_width=bbox_dict.get('page_width'),
            page_height=bbox_dict.get('page_height'),
        )

    def _normalize_formatting(self, raw_formatting: Dict[str, Any]) -> FormattingData:
        """Convert raw formatting dict to FormattingData schema"""
        font = None
        if 'font' in raw_formatting:
            font_dict = raw_formatting['font']
            font = FontProperties(
                name=font_dict.get('name'),
                size=font_dict.get('size'),
                weight=font_dict.get('weight'),
                color=font_dict.get('color'),
            )

        style = None
        if 'style' in raw_formatting:
            style_dict = raw_formatting['style']
            style = TextStyle(
                bold=style_dict.get('bold'),
                italic=style_dict.get('italic'),
                underline=style_dict.get('underline'),
            )

        links = raw_formatting.get('links', [])

        return FormattingData(font=font, style=style, links=links)

    def _build_relationships(self, blocks: List[Block]) -> List[Relationship]:
        """Build relationships between blocks"""
        relationships = []

        # Build parent-child relationships for headings
        heading_stack = []

        for block in blocks:
            if block.type == BlockType.HEADING and block.level:
                # Pop headings with equal or greater level
                while heading_stack and heading_stack[-1][1] >= block.level:
                    heading_stack.pop()

                # Set parent if there's a heading in stack
                if heading_stack:
                    parent_id = heading_stack[-1][0]
                    block.parent_id = parent_id

                    relationships.append(Relationship(
                        source_block_id=parent_id,
                        target_block_id=block.block_id,
                        relation_type="parent_child"
                    ))

                # Add current heading to stack
                heading_stack.append((block.block_id, block.level))

            elif heading_stack:
                # Associate regular blocks with nearest heading
                parent_id = heading_stack[-1][0]
                block.parent_id = parent_id

                relationships.append(Relationship(
                    source_block_id=parent_id,
                    target_block_id=block.block_id,
                    relation_type="parent_child"
                ))

        return relationships
