"""
Base adapter interface for input formats.

Adapters handle format-specific parsing with NO business logic.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class InputAdapter(ABC):
    """Abstract base class for input format adapters"""

    @abstractmethod
    def parse(self, file_path: Path, **kwargs) -> Any:
        """
        Parse input file and return raw parsed document.

        Args:
            file_path: Path to input file
            **kwargs: Format-specific parsing options

        Returns:
            Raw parsed document object (format-specific)
        """
        pass

    @abstractmethod
    def supports_format(self, file_path: Path) -> bool:
        """
        Check if this adapter supports the given file format.

        Args:
            file_path: Path to input file

        Returns:
            True if format is supported
        """
        pass

    @abstractmethod
    def get_parser_version(self) -> str:
        """
        Get version string of underlying parser/library.

        Returns:
            Version string
        """
        pass
