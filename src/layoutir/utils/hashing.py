"""
Deterministic hashing utilities for stable ID generation.

All IDs must be reproducible across runs for the same input.

STABILITY-CRITICAL: The composite key format, hash algorithm, truncation
lengths, and ID prefix strings are frozen in _stability_constants.py.
Do not change those values inline here; change them there with a schema bump.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from .._stability_constants import (
    BLOCK_ID_HASH_ALGORITHM,
    BLOCK_ID_HEX_LENGTH,
    BLOCK_ID_CONTENT_TRUNCATION,
    TABLE_ID_TEXT_TRUNCATION,
    HASH_STRING_ENCODING,
    HASH_DICT_SORT_KEYS,
    HASH_DICT_ENSURE_ASCII,
)


def hash_file(file_path: Union[str, Path], algorithm: str = BLOCK_ID_HASH_ALGORITHM) -> str:
    """
    Compute deterministic hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hexadecimal hash digest
    """
    file_path = Path(file_path)
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def hash_string(text: str, algorithm: str = BLOCK_ID_HASH_ALGORITHM) -> str:
    """
    Compute deterministic hash of a string.

    Args:
        text: Input string
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hexadecimal hash digest
    """
    hasher = hashlib.new(algorithm)
    hasher.update(text.encode(HASH_STRING_ENCODING))
    return hasher.hexdigest()


def hash_dict(data: Dict[str, Any], algorithm: str = BLOCK_ID_HASH_ALGORITHM) -> str:
    """
    Compute deterministic hash of a dictionary.

    Sorts keys to ensure deterministic output.

    Args:
        data: Input dictionary
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hexadecimal hash digest
    """
    # kwargs frozen in _stability_constants.HASH_DICT_*
    # ensure_ascii intentionally differs from canonical JSON — do not unify
    normalized = json.dumps(
        data, sort_keys=HASH_DICT_SORT_KEYS, ensure_ascii=HASH_DICT_ENSURE_ASCII
    )
    return hash_string(normalized, algorithm)


def generate_block_id(content: str, page_number: int, order: int, block_type: str) -> str:
    """
    Generate deterministic block ID.

    Combines content, position, and type to create stable ID.

    Args:
        content: Block text content
        page_number: Page number
        order: Sequential order in document
        block_type: Block type string

    Returns:
        Block ID (first 16 chars of hash for readability)
    """
    # Truncate content — length frozen in _stability_constants.BLOCK_ID_CONTENT_TRUNCATION
    content_sample = content[:BLOCK_ID_CONTENT_TRUNCATION]

    composite = f"{block_type}:{page_number}:{order}:{content_sample}"
    full_hash = hash_string(composite)

    # ID length frozen in _stability_constants.BLOCK_ID_HEX_LENGTH
    return f"blk_{full_hash[:BLOCK_ID_HEX_LENGTH]}"


def generate_document_id(file_hash: str) -> str:
    """
    Generate deterministic document ID from file hash.

    Args:
        file_hash: Hash of source file

    Returns:
        Document ID
    """
    # ID length frozen in _stability_constants.BLOCK_ID_HEX_LENGTH
    return f"doc_{file_hash[:BLOCK_ID_HEX_LENGTH]}"


def generate_table_id(document_id: str, page_number: int, table_index: int, raw_text: str) -> str:
    """
    Generate deterministic table ID.

    Args:
        document_id: Parent document ID
        page_number: Page number
        table_index: Index of table on page
        raw_text: Raw table text for uniqueness

    Returns:
        Table ID
    """
    # Text truncation length frozen in _stability_constants.TABLE_ID_TEXT_TRUNCATION
    composite = (
        f"{document_id}:table:{page_number}:{table_index}:{raw_text[:TABLE_ID_TEXT_TRUNCATION]}"
    )
    full_hash = hash_string(composite)
    return f"tbl_{full_hash[:BLOCK_ID_HEX_LENGTH]}"


def generate_image_id(
    document_id: str, page_number: int, image_index: int, image_bytes: bytes
) -> str:
    """
    Generate deterministic image ID.

    Args:
        document_id: Parent document ID
        page_number: Page number
        image_index: Index of image on page
        image_bytes: Image binary data

    Returns:
        Image ID
    """
    # Hash the image content — algorithm frozen in _stability_constants.BLOCK_ID_HASH_ALGORITHM
    hasher = hashlib.new(BLOCK_ID_HASH_ALGORITHM)
    hasher.update(image_bytes)
    image_hash = hasher.hexdigest()[:BLOCK_ID_HEX_LENGTH]

    # Combine with position
    composite = f"{document_id}:img:{page_number}:{image_index}:{image_hash}"
    full_hash = hash_string(composite)

    return f"img_{full_hash[:BLOCK_ID_HEX_LENGTH]}"


def generate_chunk_id(document_id: str, block_ids: List[str], chunk_order: int) -> str:
    """
    Generate deterministic chunk ID.

    Args:
        document_id: Parent document ID
        block_ids: List of block IDs in chunk
        chunk_order: Sequential order of chunk

    Returns:
        Chunk ID
    """
    # Sort block IDs for determinism
    sorted_blocks = sorted(block_ids)
    blocks_str = ",".join(sorted_blocks)

    composite = f"{document_id}:chunk:{chunk_order}:{blocks_str}"
    full_hash = hash_string(composite)

    return f"chk_{full_hash[:BLOCK_ID_HEX_LENGTH]}"
