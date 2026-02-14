"""
Docling PDF adapter for input processing.

Handles PDF parsing via Docling library with no business logic.
"""

from pathlib import Path
from typing import Any, Optional
import logging

from .base import InputAdapter

logger = logging.getLogger(__name__)


class DoclingAdapter(InputAdapter):
    """Adapter for PDF files using Docling library"""

    def __init__(
        self,
        use_gpu: bool = False,
        ocr_batch_size: int = 8,
        layout_batch_size: int = 8,
        table_batch_size: int = 4
    ):
        """
        Initialize Docling adapter.

        Args:
            use_gpu: Enable GPU acceleration
            ocr_batch_size: Batch size for OCR processing
            layout_batch_size: Batch size for layout analysis
            table_batch_size: Batch size for table extraction
        """
        self.use_gpu = use_gpu
        self.ocr_batch_size = ocr_batch_size
        self.layout_batch_size = layout_batch_size
        self.table_batch_size = table_batch_size

        # Lazy import to avoid dependency issues
        self._docling = None
        self._pipeline = None

    def _init_docling(self):
        """Lazy initialization of Docling components"""
        if self._docling is not None:
            return

        try:
            from docling.document_converter import DocumentConverter

            # Create converter with default options
            # Note: Current Docling API uses format_options parameter
            # GPU/CPU selection and batch sizes are handled automatically
            self._pipeline = DocumentConverter()

            self._docling = True
            logger.info("Docling pipeline initialized successfully")
            if self.use_gpu:
                logger.info("GPU acceleration will be used if available")

        except ImportError as e:
            logger.error(f"Failed to import Docling: {e}")
            raise RuntimeError("Docling library not available. Install with: pip install docling")

    def parse(self, file_path: Path, **kwargs) -> Any:
        """
        Parse PDF file using Docling.

        Args:
            file_path: Path to PDF file
            **kwargs: Additional Docling-specific options

        Returns:
            Docling ConversionResult object
        """
        self._init_docling()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        logger.info(f"Parsing PDF: {file_path}")

        try:
            result = self._pipeline.convert(str(file_path))
            logger.info(f"Successfully parsed {file_path}")
            return result

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise

    def supports_format(self, file_path: Path) -> bool:
        """
        Check if file is a PDF.

        Args:
            file_path: Path to input file

        Returns:
            True if file is PDF
        """
        return file_path.suffix.lower() == ".pdf"

    def get_parser_version(self) -> str:
        """
        Get Docling version.

        Returns:
            Docling version string
        """
        try:
            import docling
            return f"docling-{docling.__version__}"
        except (ImportError, AttributeError):
            return "docling-unknown"
