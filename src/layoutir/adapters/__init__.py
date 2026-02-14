"""Input adapters for various document formats"""

from .base import InputAdapter
from .docling_adapter import DoclingAdapter

__all__ = [
    "InputAdapter",
    "DoclingAdapter",
]
