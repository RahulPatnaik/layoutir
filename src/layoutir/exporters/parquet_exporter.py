"""
Parquet exporter for canonical IR.

Exports structured data (tables, blocks) to Parquet format for efficient storage.
"""

from pathlib import Path
from typing import List
import logging
import json

from .base import Exporter
from ..schema import Document, Chunk

logger = logging.getLogger(__name__)


class ParquetExporter(Exporter):
    """Exports canonical IR to Parquet format"""

    def export(self, document: Document, output_dir: Path, chunks: List[Chunk] = None):
        """
        Export document to Parquet.

        Args:
            document: Canonical IR document
            output_dir: Output directory for this document
            chunks: Optional chunks to export
        """
        try:
            import pandas as pd
            import pyarrow as pa  # noqa: F401  # side-effect: enables engine='pyarrow' in pandas
            import pyarrow.parquet as pq
        except ImportError:
            logger.error("Parquet export requires pandas and pyarrow")
            raise RuntimeError("Install with: pip install pandas pyarrow")

        logger.info("Exporting document to Parquet")

        export_dir = output_dir / "exports" / "parquet"
        export_dir.mkdir(parents=True, exist_ok=True)

        # Export blocks
        self._export_blocks(document, export_dir, pd, pq)

        # Export tables
        self._export_tables(document, export_dir, pd, pq)

        # Export chunks if provided
        if chunks:
            self._export_chunks(chunks, export_dir, pd, pq)

        logger.info(f"Parquet export complete: {export_dir}")

    def _export_blocks(self, document: Document, export_dir: Path, pd, pq):
        """Export blocks to Parquet"""
        blocks_data = []

        for block in document.blocks:
            block_dict = {
                "block_id": block.block_id,
                "type": block.type.value,
                "page_number": block.page_number,
                "order": block.order,
                "content": block.content,
                "parent_id": block.parent_id,
                "level": block.level,
                "metadata": json.dumps(block.metadata),
            }

            # Add bbox if available
            if block.bbox:
                block_dict.update(
                    {
                        "bbox_x0": block.bbox.x0,
                        "bbox_y0": block.bbox.y0,
                        "bbox_x1": block.bbox.x1,
                        "bbox_y1": block.bbox.y1,
                    }
                )

            blocks_data.append(block_dict)

        # Create DataFrame and write
        df = pd.DataFrame(blocks_data)
        output_path = export_dir / "blocks.parquet"
        df.to_parquet(output_path, engine="pyarrow", compression="snappy")

        logger.info(f"Exported {len(blocks_data)} blocks to Parquet")

    def _export_tables(self, document: Document, export_dir: Path, pd, pq):
        """Export tables to Parquet"""
        tables_dir = export_dir / "tables"
        tables_dir.mkdir(exist_ok=True)

        table_count = 0

        for block in document.blocks:
            if block.table_data:
                table_data = block.table_data

                # Create DataFrame from table data
                if table_data.headers and table_data.data:
                    # Deduplicate column names
                    headers = self._deduplicate_columns(table_data.headers)
                    df = pd.DataFrame(table_data.data, columns=headers)
                elif table_data.data:
                    df = pd.DataFrame(table_data.data)
                else:
                    continue

                # Write to Parquet
                output_path = tables_dir / f"{table_data.table_id}.parquet"
                df.to_parquet(output_path, engine="pyarrow", compression="snappy")

                table_count += 1

        if table_count > 0:
            logger.info(f"Exported {table_count} tables to Parquet")

    def _deduplicate_columns(self, columns: List[str]) -> List[str]:
        """Deduplicate column names by appending numbers"""
        seen = {}
        result = []

        for col in columns:
            if col not in seen:
                seen[col] = 0
                result.append(col)
            else:
                seen[col] += 1
                result.append(f"{col}_{seen[col]}")

        return result

    def _export_chunks(self, chunks: List[Chunk], export_dir: Path, pd, pq):
        """Export chunks to Parquet"""
        chunks_data = []

        for chunk in chunks:
            chunk_dict = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "order": chunk.order,
                "content": chunk.content,
                "block_ids": json.dumps(chunk.block_ids),
                "metadata": json.dumps(chunk.metadata),
            }
            chunks_data.append(chunk_dict)

        # Create DataFrame and write
        df = pd.DataFrame(chunks_data)
        output_path = export_dir / "chunks.parquet"
        df.to_parquet(output_path, engine="pyarrow", compression="snappy")

        logger.info(f"Exported {len(chunks_data)} chunks to Parquet")
