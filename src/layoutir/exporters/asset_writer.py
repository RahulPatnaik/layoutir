"""
Asset writer for extracting images and tables.

Writes binary assets to disk and updates IR references.
"""

from pathlib import Path
import logging

from ..schema import Document

logger = logging.getLogger(__name__)


class AssetWriter:
    """Writes extracted assets to disk"""

    def write_assets(self, document: Document, output_dir: Path):
        """
        Write all assets from document to disk.

        Updates image_data.extracted_path in blocks.

        Args:
            document: Canonical IR document
            output_dir: Output directory for this document
        """
        logger.info("Writing assets to disk")

        assets_dir = output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Write images
        images_dir = assets_dir / "images"
        images_dir.mkdir(exist_ok=True)
        image_count = self._write_images(document, images_dir)

        # Write tables (CSV format)
        tables_dir = assets_dir / "tables"
        tables_dir.mkdir(exist_ok=True)
        table_count = self._write_tables(document, tables_dir)

        logger.info(
            f"Wrote {image_count} images and {table_count} tables to {assets_dir}"
        )

    def _write_images(self, document: Document, images_dir: Path) -> int:
        """Write image assets"""
        image_count = 0

        for block in document.blocks:
            if block.image_data:
                image_data = block.image_data

                # Get image bytes from metadata (temporary storage)
                image_bytes = block.metadata.get('image_bytes')

                if image_bytes:
                    # Write image file
                    image_filename = f"{image_data.image_id}.{image_data.format}"
                    image_path = images_dir / image_filename

                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)

                    # Update extracted_path (relative to output_dir)
                    image_data.extracted_path = f"assets/images/{image_filename}"

                    # Remove temporary bytes from metadata
                    if 'image_bytes' in block.metadata:
                        del block.metadata['image_bytes']

                    image_count += 1

        return image_count

    def _write_tables(self, document: Document, tables_dir: Path) -> int:
        """Write table assets as CSV"""
        table_count = 0

        for block in document.blocks:
            if block.table_data:
                table_data = block.table_data

                # Write as CSV
                csv_filename = f"{table_data.table_id}.csv"
                csv_path = tables_dir / csv_filename

                with open(csv_path, 'w', encoding='utf-8') as f:
                    # Write headers
                    if table_data.headers:
                        f.write(",".join(self._escape_csv(h) for h in table_data.headers))
                        f.write("\n")

                    # Write data
                    for row in table_data.data:
                        f.write(",".join(self._escape_csv(cell) for cell in row))
                        f.write("\n")

                table_count += 1

        return table_count

    def _escape_csv(self, value: str) -> str:
        """Escape value for CSV"""
        if ',' in value or '"' in value or '\n' in value:
            return f'"{value.replace(chr(34), chr(34)+chr(34))}"'
        return value
