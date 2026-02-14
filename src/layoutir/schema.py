"""
Canonical Intermediate Representation (IR) Schema

This module defines the strict typed schema for the document IR.
All IDs are deterministic (hash-based) for idempotent processing.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class BlockType(str, Enum):
    """Enumeration of supported block types"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    EQUATION = "equation"
    CODE = "code"
    CAPTION = "caption"
    FOOTER = "footer"
    HEADER = "header"


class BoundingBox(BaseModel):
    """Bounding box coordinates (normalized to page dimensions)"""
    x0: float = Field(..., description="Left x coordinate")
    y0: float = Field(..., description="Top y coordinate")
    x1: float = Field(..., description="Right x coordinate")
    y1: float = Field(..., description="Bottom y coordinate")
    page_width: Optional[float] = Field(None, description="Page width for normalization")
    page_height: Optional[float] = Field(None, description="Page height for normalization")

    class Config:
        frozen = True  # Immutable for hashing


class TableData(BaseModel):
    """Structured table representation"""
    table_id: str = Field(..., description="Deterministic hash-based table ID")
    rows: int = Field(..., description="Number of rows")
    columns: int = Field(..., description="Number of columns")
    headers: Optional[List[str]] = Field(None, description="Column headers if detected")
    data: List[List[str]] = Field(..., description="Table data as list of rows")
    raw_text: str = Field(..., description="Fallback plain text representation")

    class Config:
        frozen = False  # Allow mutation during construction


class ImageData(BaseModel):
    """Image metadata and reference"""
    image_id: str = Field(..., description="Deterministic hash-based image ID")
    page_number: int = Field(..., description="Page number where image appears")
    bbox: Optional[BoundingBox] = Field(None, description="Bounding box on page")
    extracted_path: Optional[str] = Field(None, description="Relative path to extracted image file")
    caption: Optional[str] = Field(None, description="Associated caption if detected")
    format: Optional[str] = Field(None, description="Image format (png, jpg, etc.)")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")


class Block(BaseModel):
    """Canonical block representation"""
    block_id: str = Field(..., description="Deterministic hash-based block ID")
    type: BlockType = Field(..., description="Block type")
    parent_id: Optional[str] = Field(None, description="Parent block ID for hierarchical structure")
    page_number: int = Field(..., description="Page number (1-indexed)")
    bbox: Optional[BoundingBox] = Field(None, description="Bounding box coordinates")
    content: str = Field(..., description="Text content of the block")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional block metadata")

    # For specialized blocks
    table_data: Optional[TableData] = Field(None, description="Populated for TABLE blocks")
    image_data: Optional[ImageData] = Field(None, description="Populated for IMAGE blocks")

    # Hierarchical metadata
    level: Optional[int] = Field(None, description="Heading level (1-6) for HEADING blocks")
    list_level: Optional[int] = Field(None, description="Nesting level for LIST blocks")
    order: int = Field(..., description="Sequential order within document")


class DocumentMetadata(BaseModel):
    """Document-level metadata"""
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    page_count: int
    source_format: str = Field(..., description="Original format (pdf, docx, html)")
    source_path: str = Field(..., description="Path to source file")
    source_hash: str = Field(..., description="SHA256 hash of source file")


class Relationship(BaseModel):
    """Explicit relationship between blocks"""
    source_block_id: str
    target_block_id: str
    relation_type: Literal["parent_child", "caption_of", "continuation", "reference"]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Top-level canonical document representation"""
    document_id: str = Field(..., description="Deterministic hash of source file")
    schema_version: str = Field(default="1.0.0", description="IR schema version")
    parser_version: str = Field(..., description="Parser/library version used")

    metadata: DocumentMetadata = Field(..., description="Document metadata")
    blocks: List[Block] = Field(default_factory=list, description="Ordered list of blocks")
    relationships: List[Relationship] = Field(default_factory=list, description="Inter-block relationships")

    # Extraction stats
    stats: Dict[str, int] = Field(
        default_factory=dict,
        description="Extraction statistics (block_count, table_count, etc.)"
    )

    # Processing metadata
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow)
    config_used: Dict[str, Any] = Field(default_factory=dict, description="Configuration snapshot")


class Chunk(BaseModel):
    """Chunked segment of document for downstream processing"""
    chunk_id: str = Field(..., description="Deterministic hash-based chunk ID")
    document_id: str = Field(..., description="Parent document ID")
    block_ids: List[str] = Field(..., description="Blocks included in this chunk")
    content: str = Field(..., description="Concatenated text content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk metadata (page_range, token_count, etc.)"
    )
    order: int = Field(..., description="Sequential order in chunking strategy")


class Manifest(BaseModel):
    """Output manifest for a processed document"""
    document_id: str
    input_file_hash: str
    parser_version: str
    schema_version: str
    config_used: Dict[str, Any]
    created_at: datetime
    stats: Dict[str, int]
    output_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of output type to relative paths"
    )
