"""
STABILITY-CRITICAL: Frozen algorithmic constants for deterministic IR.

Semantic determinism is a PUBLIC CONTRACT of LayoutIR.
Any document processed with the same input must produce the same block IDs,
the same semantic hash, and the same canonical JSON — across runs, machines,
and library versions — for as long as these constants remain unchanged.

This module is the SINGLE SOURCE OF TRUTH for every value that affects:
  - compute_semantic_hash()       → SEMANTIC_HASH_* constants
  - generate_block_id()           → BLOCK_ID_* constants
  - generate_table_id()           → TABLE_ID_* + BLOCK_ID_HEX_LENGTH
  - generate_image_id()           → BLOCK_ID_* constants
  - hash_dict()                   → HASH_DICT_* constants
  - spatial ordering algorithm    → SPATIAL_* + BLOCK_TYPE_SORT_PRIORITY
  - canonical JSON serialization  → CANONICAL_JSON_* constants

CHANGE PROTOCOL — required for every modification:
  1. Bump SCHEMA_VERSION in this file and in schema.py
  2. Regenerate golden IR fixtures: tests/fixtures/golden_ir/golden_hashes.json
  3. Add a changelog entry documenting: what changed, old value, new value,
     and whether existing vector DB documents need reindexing
  4. If block IDs change: bump to minor version (x.Y.0)
  5. If semantic hash changes: bump to minor version (x.Y.0)
  6. If only non-output metadata changes: patch version acceptable (x.y.Z)

Failure to follow this protocol will silently invalidate:
  - Existing golden hashes in CI (tests will explode)
  - Vector DB IDs for all previously-indexed documents
  - Incremental update logic that relies on stable block IDs
  - LlamaIndex reader downstream consumers

Do not refactor, "clean up", or optimise constants here without reading
the full change protocol above.
"""

# ---------------------------------------------------------------------------
# BLOCK ID HASHING
# STABILITY-CRITICAL: changing any of these changes every block ID ever issued.
# ---------------------------------------------------------------------------

# Hash algorithm used for all ID generation.
# SHA-256 is collision-resistant and output-stable across Python versions.
# Changing to SHA-512 or MD5 changes every ID.
BLOCK_ID_HASH_ALGORITHM: str = "sha256"

# Number of hex characters taken from the full hash digest for block IDs.
# 16 hex chars = 64 bits of entropy. Sufficient for document-scale deduplication.
# Increasing this changes every emitted ID string; decreasing raises collision risk.
BLOCK_ID_HEX_LENGTH: int = 16

# Maximum characters of block content used when constructing the composite key.
# Content beyond this is ignored. Changing this changes IDs for long blocks.
BLOCK_ID_CONTENT_TRUNCATION: int = 500

# Maximum characters of table raw text used in table ID composite key.
TABLE_ID_TEXT_TRUNCATION: int = 200

# Composite key template for block IDs.
# Fields: block_type, page_number, order, content_sample
# The separator ":" must not appear in block_type values or IDs will collide.
BLOCK_ID_COMPOSITE_TEMPLATE: str = "{block_type}:{page_number}:{order}:{content_sample}"

# String encoding used when hashing text.
# UTF-8 is required; ASCII-only encoding would corrupt non-Latin content.
HASH_STRING_ENCODING: str = "utf-8"

# ---------------------------------------------------------------------------
# SPATIAL ORDERING
# STABILITY-CRITICAL: changing precision or key order changes spatial_order
# values in OrderingMetadata for every block, and will cause ordering
# discrepancy warnings to appear or disappear on existing documents.
# ---------------------------------------------------------------------------

# Decimal places for rounding PDF coordinates before spatial comparison.
# 4 decimals = 0.0001 unit precision at 72 DPI (sub-pixel, avoids float drift).
# 3 decimals caused real-world drift in multi-column layouts.
# 5+ decimals reintroduce floating-point noise that defeats determinism.
SPATIAL_ROUND_PRECISION: int = 4

# Priority assigned to each block type in the spatial sort tiebreaker (tier 4).
# Lower number = sorted earlier when page, y, and x all match.
# New block types added to the schema must be assigned a priority here.
# Do not renumber existing entries; only append new ones.
BLOCK_TYPE_SORT_PRIORITY: dict = {
    "heading":   1,
    "paragraph": 2,
    "list":      3,
    "table":     4,
    "image":     5,
    "equation":  6,
    "code":      7,
    "caption":   8,
    "header":    9,
    "footer":   10,
}

# ---------------------------------------------------------------------------
# CANONICAL JSON (semantic hash input)
# STABILITY-CRITICAL: changing any keyword argument to json.dumps changes
# compute_semantic_hash() output for every document ever hashed.
# ---------------------------------------------------------------------------

# All four arguments must be passed explicitly — never rely on defaults.
CANONICAL_JSON_SORT_KEYS: bool = True
CANONICAL_JSON_SEPARATORS: tuple = (',', ':')   # compact, no whitespace
CANONICAL_JSON_ENSURE_ASCII: bool = False        # preserve UTF-8; do not escape
CANONICAL_JSON_INDENT: None = None              # single-line output

# ---------------------------------------------------------------------------
# HASH_DICT serialization (general-purpose utility — NOT the semantic hash path)
# STABILITY-CRITICAL: hash_dict() output is used by call sites that may depend
# on stable dict hashes. ensure_ascii intentionally differs from canonical JSON.
# Do NOT unify with CANONICAL_JSON_ENSURE_ASCII. See comment below.
# ---------------------------------------------------------------------------

# sort_keys ensures deterministic output regardless of dict insertion order.
HASH_DICT_SORT_KEYS: bool = True

# ensure_ascii=True is intentionally different from CANONICAL_JSON_ENSURE_ASCII=False.
# hash_dict() is a general utility; its callers may rely on ASCII-safe output.
# Changing this to False would silently change hash output for any dict
# containing non-ASCII values. This must remain True unless all call sites
# are audited and a version bump is performed.
HASH_DICT_ENSURE_ASCII: bool = True

# NOTE: The two ensure_ascii values diverge by design.
# canonical JSON (equality.py): ensure_ascii=False  → preserves UTF-8
# hash_dict (hashing.py):       ensure_ascii=True   → ASCII-safe output
# This inconsistency is documented and must NOT be silently unified.

# ---------------------------------------------------------------------------
# SEMANTIC HASH (compute_semantic_hash output)
# STABILITY-CRITICAL: changing either value changes the output of
# compute_semantic_hash() for every document ever hashed.
# These are deliberately separate from BLOCK_ID_HASH_ALGORITHM: block IDs
# and semantic hashes are different contracts and may evolve independently.
# ---------------------------------------------------------------------------

# Hash algorithm applied to the canonical JSON bytes to produce the semantic hash.
SEMANTIC_HASH_ALGORITHM: str = "sha256"

# Encoding used when converting the canonical JSON string to bytes for hashing.
# Must match HASH_STRING_ENCODING; both are "utf-8" and must stay in sync.
SEMANTIC_HASH_ENCODING: str = "utf-8"

# ---------------------------------------------------------------------------
# SCHEMA VERSION (bump when any constant above changes)
# ---------------------------------------------------------------------------
SCHEMA_VERSION: str = "1.0.0"
