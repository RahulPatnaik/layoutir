"""
Base exporter interface.

Exporters convert canonical IR to various output formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..schema import Document, Chunk


class Exporter(ABC):
    """Abstract base class for exporters"""

    @abstractmethod
    def export(self, document: Document, output_dir: Path, chunks: List[Chunk] = None):
        """
        Export document to target format.

        Args:
            document: Canonical IR document
            output_dir: Output directory for this document
            chunks: Optional chunks to export
        """
        pass
