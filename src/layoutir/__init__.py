"""
LayoutIR - Production-Grade Document Ingestion & Canonicalization Engine

An IR-first, extensible document compiler for AI systems.
"""

__version__ = "1.0.3"

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
    # NEW: Round-trip stability classes
    FormattingData,
    TextStyle,
    FontProperties,
    OrderingMetadata,
    CellSpan,
)
from .pipeline import Pipeline
from .adapters import DoclingAdapter
from .utils.equality import assert_semantic_equality, compute_semantic_hash

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
    "FormattingData",
    "TextStyle",
    "FontProperties",
    "OrderingMetadata",
    "CellSpan",
    "Pipeline",
    "DoclingAdapter",
    "assert_semantic_equality",
    "compute_semantic_hash",
]
