"""
Extraction layer for Docling parsed documents.

Extracts raw structural elements without normalization.
"""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class RawBlock:
    """Raw extracted block before normalization"""
    text: str
    block_type: str
    page_number: int
    bbox: Optional[Dict[str, float]]
    order: int
    metadata: Dict[str, Any]
    formatting: Optional[Dict[str, Any]] = None  # NEW: Optional formatting data


@dataclass
class RawTable:
    """Raw extracted table before normalization"""
    page_number: int
    bbox: Optional[Dict[str, float]]
    data: List[List[str]]
    headers: Optional[List[str]]
    raw_text: str
    order: int


@dataclass
class RawImage:
    """Raw extracted image before normalization"""
    page_number: int
    bbox: Optional[Dict[str, float]]
    image_bytes: bytes
    format: str
    width: Optional[int]
    height: Optional[int]
    order: int
    caption: Optional[str] = None


@dataclass
class RawDocument:
    """Raw extracted document structure"""
    blocks: List[RawBlock]
    tables: List[RawTable]
    images: List[RawImage]
    page_count: int
    metadata: Dict[str, Any]


class DoclingExtractor:
    """Extracts raw structural elements from Docling ConversionResult"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize extractor.

        Args:
            config: Optional configuration dict
                - capture_formatting (bool): Extract font/style info (default: False for performance)
        """
        self.config = config or {}

    def extract(self, docling_result: Any) -> RawDocument:
        """
        Extract raw structural elements from Docling result.

        Args:
            docling_result: Docling ConversionResult object

        Returns:
            RawDocument with extracted elements
        """
        logger.info("Extracting structural elements from Docling result")

        # Get the converted document
        doc = docling_result.document

        blocks = []
        tables = []
        images = []

        # Counter for global ordering
        global_order = 0

        # Extract blocks
        # FIX: iterate_items() returns tuples of (DocItem, level)
        for item_tuple in doc.iterate_items():
            # Extract the actual DocItem from the tuple
            item = item_tuple[0] if isinstance(item_tuple, tuple) else item_tuple
            item_type = type(item).__name__

            # Extract text blocks
            if hasattr(item, 'text'):
                text = item.text.strip() if item.text else ""

                if not text:
                    continue

                # Determine block type
                block_type = self._map_docling_type(item_type, item)

                # Extract bounding box if available
                bbox = self._extract_bbox(item)

                # Get page number
                page_num = self._get_page_number(item)

                # Extract metadata
                metadata = self._extract_item_metadata(item)

                # NEW: Extract formatting (conditional - performance optimization)
                # Default False to preserve baseline performance
                formatting = None
                if self.config.get('capture_formatting', False):
                    formatting = self._extract_formatting(item)

                blocks.append(RawBlock(
                    text=text,
                    block_type=block_type,
                    page_number=page_num,
                    bbox=bbox,
                    order=global_order,
                    metadata=metadata,
                    formatting=formatting  # NEW (None if not enabled)
                ))

                global_order += 1

        # Extract tables
        table_order = 0
        for table in doc.tables:
            raw_table = self._extract_table(table, table_order)
            if raw_table:
                tables.append(raw_table)
                table_order += 1

        # Extract images
        image_order = 0
        for picture in doc.pictures:
            raw_image = self._extract_image(picture, image_order)
            if raw_image:
                images.append(raw_image)
                image_order += 1

        # Extract document metadata
        doc_metadata = self._extract_document_metadata(doc)

        logger.info(
            f"Extracted {len(blocks)} blocks, {len(tables)} tables, "
            f"{len(images)} images from {doc_metadata.get('page_count', 0)} pages"
        )

        return RawDocument(
            blocks=blocks,
            tables=tables,
            images=images,
            page_count=doc_metadata.get('page_count', 0),
            metadata=doc_metadata
        )

    def _map_docling_type(self, docling_type: str, item: Any) -> str:
        """Map Docling item type to canonical block type"""
        type_map = {
            'Title': 'heading',
            'Heading': 'heading',
            'Paragraph': 'paragraph',
            'List': 'list',
            'ListItem': 'list',
            'Table': 'table',
            'Picture': 'image',
            'Equation': 'equation',
            'Code': 'code',
            'Caption': 'caption',
            'Footer': 'footer',
            'Header': 'header',
        }

        # Check for specific attributes
        if hasattr(item, 'label'):
            label = str(item.label).lower()
            if 'title' in label or 'heading' in label:
                return 'heading'

        return type_map.get(docling_type, 'paragraph')

    def _extract_bbox(self, item: Any) -> Optional[Dict[str, float]]:
        """Extract bounding box from Docling item"""
        if hasattr(item, 'prov') and item.prov:
            for prov_item in item.prov:
                if hasattr(prov_item, 'bbox'):
                    bbox = prov_item.bbox
                    return {
                        'x0': bbox.l,
                        'y0': bbox.t,
                        'x1': bbox.r,
                        'y1': bbox.b,
                    }
        return None

    def _get_page_number(self, item: Any) -> int:
        """Extract page number from Docling item"""
        if hasattr(item, 'prov') and item.prov:
            for prov_item in item.prov:
                if hasattr(prov_item, 'page'):
                    return prov_item.page + 1  # Convert to 1-indexed

        return 1  # Default to page 1

    def _extract_item_metadata(self, item: Any) -> Dict[str, Any]:
        """Extract metadata from Docling item"""
        metadata = {}

        # Extract heading level
        if hasattr(item, 'label'):
            label = str(item.label)
            metadata['label'] = label

            # Try to extract heading level
            if 'heading' in label.lower():
                try:
                    level = int(label.split('_')[-1])
                    metadata['level'] = level
                except (ValueError, IndexError):
                    pass

        return metadata

    def _extract_formatting(self, item: Any) -> Optional[Dict[str, Any]]:
        """
        Extract formatting from Docling item (best-effort).
        Uses defensive hasattr checks - Docling may not provide all attributes.
        """
        formatting = {}

        # Extract font properties
        font_props = {}
        if hasattr(item, 'prov') and item.prov:
            for prov_item in item.prov:
                if hasattr(prov_item, 'font'):
                    font_obj = prov_item.font
                    if hasattr(font_obj, 'name'):
                        font_props['name'] = str(font_obj.name)
                    if hasattr(font_obj, 'size'):
                        font_props['size'] = float(font_obj.size)
                    if hasattr(font_obj, 'weight'):
                        font_props['weight'] = int(font_obj.weight)
                    if hasattr(font_obj, 'color'):
                        # Convert to hex
                        color = font_obj.color
                        if isinstance(color, tuple) and len(color) >= 3:
                            font_props['color'] = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

        if font_props:
            formatting['font'] = font_props

        # Extract text styling
        style_props = {}
        if hasattr(item, 'text_style') or hasattr(item, 'style'):
            style_obj = getattr(item, 'text_style', None) or getattr(item, 'style', None)
            if style_obj:
                if hasattr(style_obj, 'bold'):
                    style_props['bold'] = bool(style_obj.bold)
                if hasattr(style_obj, 'italic'):
                    style_props['italic'] = bool(style_obj.italic)
                if hasattr(style_obj, 'underline'):
                    style_props['underline'] = bool(style_obj.underline)

        if style_props:
            formatting['style'] = style_props

        # Extract links
        links = []
        if hasattr(item, 'links') and item.links:
            for link in item.links:
                uri = getattr(link, 'uri', None) or getattr(link, 'url', None)
                if uri:
                    links.append(str(uri))

        if links:
            formatting['links'] = links

        return formatting if formatting else None

    def _extract_table(self, table: Any, order: int) -> Optional[RawTable]:
        """Extract table data"""
        try:
            # Get table data as DataFrame
            if hasattr(table, 'data') and hasattr(table.data, 'grid'):
                grid = table.data.grid

                # Convert to list of lists
                data = []
                headers = None

                for row_idx, row in enumerate(grid):
                    row_data = []
                    for cell in row:
                        cell_text = cell.text if hasattr(cell, 'text') else str(cell)
                        row_data.append(cell_text)

                    if row_idx == 0:
                        headers = row_data
                    else:
                        data.append(row_data)

                # Get raw text
                raw_text = str(table.text) if hasattr(table, 'text') else ""

                # Get bbox and page
                bbox = self._extract_bbox(table)
                page_num = self._get_page_number(table)

                return RawTable(
                    page_number=page_num,
                    bbox=bbox,
                    data=data,
                    headers=headers,
                    raw_text=raw_text,
                    order=order
                )

        except Exception as e:
            logger.warning(f"Failed to extract table: {e}")

        return None

    def _extract_image(self, picture: Any, order: int) -> Optional[RawImage]:
        """Extract image data"""
        try:
            # Get image bytes
            if hasattr(picture, 'image') and hasattr(picture.image, 'pil_image'):
                pil_image = picture.image.pil_image

                # Convert to bytes
                buffer = BytesIO()
                pil_image.save(buffer, format='PNG')
                image_bytes = buffer.getvalue()

                # Get dimensions
                width, height = pil_image.size

                # Get bbox and page
                bbox = self._extract_bbox(picture)
                page_num = self._get_page_number(picture)

                # Try to get caption
                caption = None
                if hasattr(picture, 'text'):
                    caption = picture.text

                return RawImage(
                    page_number=page_num,
                    bbox=bbox,
                    image_bytes=image_bytes,
                    format='png',
                    width=width,
                    height=height,
                    order=order,
                    caption=caption
                )

        except Exception as e:
            logger.warning(f"Failed to extract image: {e}")

        return None

    def _extract_document_metadata(self, doc: Any) -> Dict[str, Any]:
        """Extract document-level metadata"""
        metadata = {}

        # Get page count
        if hasattr(doc, 'pages'):
            metadata['page_count'] = len(doc.pages)

        # Try to extract other metadata
        if hasattr(doc, 'metadata'):
            doc_meta = doc.metadata
            if hasattr(doc_meta, 'title'):
                metadata['title'] = doc_meta.title
            if hasattr(doc_meta, 'author'):
                metadata['author'] = doc_meta.author

        return metadata
