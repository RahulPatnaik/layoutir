"""
Plain text exporter for canonical IR.

Exports document to simple text format.
"""

from pathlib import Path
from typing import List
import logging

from .base import Exporter
from ..schema import Document, Chunk

logger = logging.getLogger(__name__)


class TextExporter(Exporter):
    """Exports canonical IR to plain text format"""

    def export(self, document: Document, output_dir: Path, chunks: List[Chunk] = None):
        """
        Export document to plain text.

        Args:
            document: Canonical IR document
            output_dir: Output directory for this document
            chunks: Optional chunks to export
        """
        logger.info("Exporting document to plain text")

        export_dir = output_dir / "exports" / "text"
        export_dir.mkdir(parents=True, exist_ok=True)

        # Export full document
        full_doc_path = export_dir / "full_document.txt"
        self._export_document(document, full_doc_path)

        # Export chunks if provided
        if chunks:
            chunks_dir = export_dir / "chunks"
            chunks_dir.mkdir(exist_ok=True)
            self._export_chunks(chunks, chunks_dir)

        logger.info(f"Text export complete: {export_dir}")

    def _export_document(self, document: Document, output_path: Path):
        """Export full document to plain text"""
        with open(output_path, "w", encoding="utf-8") as f:
            # Write blocks
            for block in document.blocks:
                f.write(block.content)
                f.write("\n\n")

    def _export_chunks(self, chunks: List[Chunk], chunks_dir: Path):
        """Export chunks to separate text files"""
        for chunk in chunks:
            chunk_path = chunks_dir / f"chunk_{chunk.order:04d}.txt"

            with open(chunk_path, "w", encoding="utf-8") as f:
                f.write(chunk.content)
                f.write("\n")

        logger.info(f"Exported {len(chunks)} chunks to {chunks_dir}")
