"""Utility modules for document IR processing"""

from .hashing import (
    hash_file,
    hash_string,
    hash_dict,
    generate_block_id,
    generate_document_id,
    generate_table_id,
    generate_image_id,
    generate_chunk_id,
)
from .logging_config import setup_logging, LogContext
from .equality import (
    assert_semantic_equality,
    compute_semantic_hash,
    SemanticEqualityChecker,
)

__all__ = [
    "hash_file",
    "hash_string",
    "hash_dict",
    "generate_block_id",
    "generate_document_id",
    "generate_table_id",
    "generate_image_id",
    "generate_chunk_id",
    "setup_logging",
    "LogContext",
    "assert_semantic_equality",
    "compute_semantic_hash",
    "SemanticEqualityChecker",
]
