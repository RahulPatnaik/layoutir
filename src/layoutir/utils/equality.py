"""Semantic equality testing for IR documents via canonical JSON comparison

STABILITY-CRITICAL: The json.dumps keyword arguments used in _to_canonical_json()
are frozen in _stability_constants.py. Changing any of them changes
compute_semantic_hash() output for every document ever hashed.
"""

from typing import Any, Dict
import json
import hashlib
from ..schema import Document
from .._stability_constants import (
    CANONICAL_JSON_SORT_KEYS,
    CANONICAL_JSON_SEPARATORS,
    CANONICAL_JSON_ENSURE_ASCII,
    CANONICAL_JSON_INDENT,
    SEMANTIC_HASH_ALGORITHM,
    SEMANTIC_HASH_ENCODING,
)


class SemanticEqualityChecker:
    """
    Checks semantic equality via canonical JSON comparison.
    NO external dependencies (no DeepDiff) - uses built-in json module.
    """

    DOCUMENT_EXCLUDE_FIELDS = {'processing_timestamp', 'config_used'}
    BLOCK_EXCLUDE_FIELDS = {'formatting_data', 'ordering_metadata'}
    METADATA_EXCLUDE_KEYS = {'processing_time', 'image_bytes'}

    def assert_equal(self, doc1: Document, doc2: Document) -> None:
        """
        Assert semantic equality via canonical JSON comparison.
        Raises AssertionError if different.
        """
        dict1 = self._to_canonical_dict(doc1)
        dict2 = self._to_canonical_dict(doc2)

        json1 = self._to_canonical_json(dict1)
        json2 = self._to_canonical_json(dict2)

        if json1 != json2:
            # Find first difference for debugging
            lines1 = json1.split('\n')
            lines2 = json2.split('\n')
            diff_line = None
            for i, (line1, line2) in enumerate(zip(lines1, lines2)):
                if line1 != line2:
                    diff_line = i + 1
                    break

            raise AssertionError(
                f"Documents not semantically equal.\n"
                f"First difference at line {diff_line}:\n"
                f"  Doc1: {lines1[i] if diff_line else '(length mismatch)'}\n"
                f"  Doc2: {lines2[i] if diff_line else '(length mismatch)'}"
            )

    def compute_semantic_hash(self, doc: Document) -> str:
        """
        Compute deterministic hash of semantic content.
        This is the LONG-TERM STABILITY PROOF.
        """
        canonical_dict = self._to_canonical_dict(doc)
        canonical_json = self._to_canonical_json(canonical_dict)
        # Algorithm and encoding frozen in _stability_constants.SEMANTIC_HASH_*
        return hashlib.new(SEMANTIC_HASH_ALGORITHM, canonical_json.encode(SEMANTIC_HASH_ENCODING)).hexdigest()

    def _to_canonical_json(self, obj: Dict[str, Any]) -> str:
        """
        Convert dict to canonical JSON string.

        CANONICAL JSON SERIALIZATION RULES (EXPLICIT SPECIFICATION):
        - sort_keys=True: Deterministic key ordering (alphabetical)
        - separators=(',', ':'): No whitespace (compact, deterministic)
        - ensure_ascii=False: Preserve Unicode (avoid \\uXXXX escaping)
        - No indentation (indent=None): Compact single-line output

        These rules guarantee:
        - Byte-identical output for identical semantic content
        - Stable across Python versions (3.7+)
        - UTF-8 encoding determinism
        - No whitespace/formatting drift
        """
        # All kwargs sourced from _stability_constants — do not inline override
        return json.dumps(
            obj,
            sort_keys=CANONICAL_JSON_SORT_KEYS,
            separators=CANONICAL_JSON_SEPARATORS,
            ensure_ascii=CANONICAL_JSON_ENSURE_ASCII,
            indent=CANONICAL_JSON_INDENT,
        )

    def _to_canonical_dict(self, doc: Document) -> Dict[str, Any]:
        """Convert to canonical dict, removing non-semantic fields"""
        doc_dict = doc.model_dump()

        # Remove non-semantic document fields
        for field in self.DOCUMENT_EXCLUDE_FIELDS:
            doc_dict.pop(field, None)

        # Clean blocks (MUST be sorted by order for strict ordering)
        if 'blocks' in doc_dict:
            doc_dict['blocks'] = [self._clean_block(b) for b in doc_dict['blocks']]
            doc_dict['blocks'].sort(key=lambda b: b['order'])

        # Clean metadata
        if 'metadata' in doc_dict:
            for key in self.METADATA_EXCLUDE_KEYS:
                doc_dict['metadata'].pop(key, None)

        # Sort relationships for canonical order
        if 'relationships' in doc_dict:
            doc_dict['relationships'].sort(
                key=lambda r: (r['source_block_id'], r['target_block_id'])
            )

        return doc_dict

    def _clean_block(self, block_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove non-semantic fields from block"""
        block = block_dict.copy()
        for field in self.BLOCK_EXCLUDE_FIELDS:
            block.pop(field, None)
        if 'metadata' in block:
            for key in self.METADATA_EXCLUDE_KEYS:
                block['metadata'].pop(key, None)
        return block


def assert_semantic_equality(doc1: Document, doc2: Document) -> None:
    """
    Assert semantic equality via canonical JSON comparison.
    Raises AssertionError if different.
    """
    checker = SemanticEqualityChecker()
    checker.assert_equal(doc1, doc2)


def compute_semantic_hash(doc: Document) -> str:
    """
    Compute deterministic hash of document's semantic content.
    This is the long-term stability proof - same content = same hash.
    """
    checker = SemanticEqualityChecker()
    return checker.compute_semantic_hash(doc)
