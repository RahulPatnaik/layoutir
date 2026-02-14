"""
Markdown exporter for canonical IR.

Exports document and chunks to Markdown format.
"""

from pathlib import Path
from typing import List
import logging

from .base import Exporter
from ..schema import Document, Block, BlockType, Chunk

logger = logging.getLogger(__name__)


class MarkdownExporter(Exporter):
    """Exports canonical IR to Markdown format"""

    def export(self, document: Document, output_dir: Path, chunks: List[Chunk] = None):
        """
        Export document to Markdown.

        Args:
            document: Canonical IR document
            output_dir: Output directory for this document
            chunks: Optional chunks to export
        """
        logger.info("Exporting document to Markdown")

        export_dir = output_dir / "exports" / "markdown"
        export_dir.mkdir(parents=True, exist_ok=True)

        # Export full document
        full_doc_path = export_dir / "full_document.md"
        self._export_document(document, full_doc_path)

        # Export chunks if provided
        if chunks:
            chunks_dir = export_dir / "chunks"
            chunks_dir.mkdir(exist_ok=True)
            self._export_chunks(chunks, chunks_dir)

        logger.info(f"Markdown export complete: {export_dir}")

    def _export_document(self, document: Document, output_path: Path):
        """Export full document to Markdown"""
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write metadata header
            f.write(f"# Document: {document.document_id}\n\n")

            if document.metadata.title:
                f.write(f"**Title:** {document.metadata.title}\n\n")

            f.write(f"**Pages:** {document.metadata.page_count}\n")
            f.write(f"**Source:** {document.metadata.source_format}\n")
            f.write(f"**Processed:** {document.processing_timestamp.isoformat()}\n\n")

            f.write("---\n\n")

            # Write blocks
            for block in document.blocks:
                self._write_block(f, block)

    def _write_block(self, f, block: Block):
        """Write a single block to Markdown"""
        if block.type == BlockType.HEADING:
            # Render as markdown heading
            level = block.level or 1
            prefix = "#" * min(level, 6)
            f.write(f"{prefix} {block.content}\n\n")

        elif block.type == BlockType.PARAGRAPH:
            f.write(f"{block.content}\n\n")

        elif block.type == BlockType.LIST:
            # Render as list item
            indent = "  " * (block.list_level - 1) if block.list_level else ""
            f.write(f"{indent}- {block.content}\n")

        elif block.type == BlockType.TABLE:
            # Render table if we have data
            if block.table_data and block.table_data.data:
                self._write_table(f, block)
            else:
                f.write(f"```\n{block.content}\n```\n\n")

        elif block.type == BlockType.IMAGE:
            # Render image reference
            if block.image_data and block.image_data.extracted_path:
                alt_text = block.image_data.caption or "Image"
                f.write(f"![{alt_text}]({block.image_data.extracted_path})\n\n")
                if block.image_data.caption:
                    f.write(f"*{block.image_data.caption}*\n\n")
            else:
                f.write(f"*[Image: {block.content}]*\n\n")

        elif block.type == BlockType.CODE:
            f.write(f"```\n{block.content}\n```\n\n")

        elif block.type == BlockType.EQUATION:
            f.write(f"$$\n{block.content}\n$$\n\n")

        elif block.type == BlockType.CAPTION:
            f.write(f"*{block.content}*\n\n")

        elif block.type == BlockType.FOOTER or block.type == BlockType.HEADER:
            f.write(f"_{block.content}_\n\n")

        else:
            # Default: plain text
            f.write(f"{block.content}\n\n")

    def _write_table(self, f, block: Block):
        """Write table in Markdown format"""
        table_data = block.table_data

        # Write headers
        if table_data.headers:
            f.write("| " + " | ".join(table_data.headers) + " |\n")
            f.write("| " + " | ".join(["---"] * len(table_data.headers)) + " |\n")

        # Write data rows
        for row in table_data.data:
            # Pad row if needed
            padded_row = row + [""] * (table_data.columns - len(row))
            f.write("| " + " | ".join(padded_row[:table_data.columns]) + " |\n")

        f.write("\n")

    def _export_chunks(self, chunks: List[Chunk], chunks_dir: Path):
        """Export chunks to separate Markdown files"""
        for chunk in chunks:
            chunk_path = chunks_dir / f"chunk_{chunk.order:04d}.md"

            with open(chunk_path, 'w', encoding='utf-8') as f:
                # Write chunk metadata
                f.write(f"# Chunk {chunk.order}\n\n")
                f.write(f"**Chunk ID:** {chunk.chunk_id}\n")
                f.write(f"**Pages:** {chunk.metadata.get('page_range', 'unknown')}\n")
                f.write(f"**Blocks:** {chunk.metadata.get('block_count', 0)}\n\n")
                f.write("---\n\n")

                # Write content
                f.write(chunk.content)
                f.write("\n")

        logger.info(f"Exported {len(chunks)} chunks to {chunks_dir}")
