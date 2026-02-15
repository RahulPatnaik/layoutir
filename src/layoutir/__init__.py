"""
LayoutIR - Production-Grade Document Ingestion & Canonicalization Engine

An IR-first, extensible document compiler for AI systems.
"""

__version__ = "1.0.0"

from .schema import (
    Document,
    Block,
    BlockType,
    TableData,
    ImageData,
    BoundingBox,
    DocumentMetadata,
    Relationship,
    Chunk,
    Manifest,
)
from .pipeline import Pipeline
from .adapters import DoclingAdapter

__all__ = [
    "Document",
    "Block",
    "BlockType",
    "TableData",
    "ImageData",
    "BoundingBox",
    "DocumentMetadata",
    "Relationship",
    "Chunk",
    "Manifest",
    "Pipeline",
    "DoclingAdapter",
]
