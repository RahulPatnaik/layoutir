# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-02-19

### Added
- `_stability_constants.py`: single source of truth for all hash-affecting values (block ID algorithm, hex length, truncation limits, spatial rounding precision, canonical JSON kwargs, semantic hash algorithm). Any future change to these values requires a version bump and golden fixture regeneration.
- `OrderingValidator`: deterministic 5-tier spatial sort (page → y → x → block type priority → Docling order) with `ROUND_PRECISION=4`. Annotates each block with `OrderingMetadata` for discrepancy visibility. Docling order remains canonical.
- `SemanticEqualityChecker` and `compute_semantic_hash()`: canonical JSON comparison for round-trip equality testing. No external dependencies.
- `assert_semantic_equality()`: raises `AssertionError` with diff context on semantic mismatch.
- `FormattingData`, `TextStyle`, `FontProperties`, `OrderingMetadata`, `CellSpan` schema classes: all optional, all default to `None` for full backward compatibility.
- `TestStabilityProtection`: 5 static analysis tests that fail if stability-critical literals (`[:16]`, `sha256`, `utf-8`, inline `json.dumps` kwargs) are reintroduced outside the constants module.
- `TestGoldenIRFixtures`: hash regression tests against stored golden IR fixtures. Fails if determinism regresses.
- `TestBackwardCompatibility`: verifies IR JSON produced before 1.0.4 loads without error.
- `DoclingExtractor` now accepts optional `config` dict; set `capture_formatting=True` to extract font and style metadata (default: `False` to preserve baseline performance).

### Changed
- All hardcoded literals in `hashing.py`, `ordering_validator.py`, and `equality.py` replaced with imports from `_stability_constants.py`.
- `normalizer.py` now runs `OrderingValidator.validate_and_annotate()` after block sort and converts raw formatting dicts to typed `FormattingData` instances.

### Fixed
- `generate_document_id` was using a bare `[:16]` literal inconsistent with the rest of the ID generation functions. Now uses `BLOCK_ID_HEX_LENGTH`.
- `generate_image_id` was calling `hashlib.sha256()` directly instead of going through the algorithm constant.

### Stability Contract
- Zero behavioral drift from 1.0.3: all block IDs, document IDs, and `compute_semantic_hash()` outputs are byte-identical.
- `compute_semantic_hash()` is now a public contract. Its output will not change without a minor version bump.
- OCR non-determinism warning: scanned PDFs processed via OCR may produce non-identical text across runs due to OCR engine variance. This is a known limitation of the underlying OCR pipeline, not of LayoutIR.

## [1.0.3] - 2026-02-15

### Changed
- **License changed from MIT to Apache 2.0**
- Updated package metadata to reflect Apache-2.0 license

## [1.0.2] - 2026-02-15

### Changed
- **BREAKING**: Removed PyTorch from base dependencies to allow explicit CUDA version control
- PyTorch and torchvision now available as optional dependencies via `pip install layoutir[cuda]`
- Users must install PyTorch separately with CUDA 13.0 support before using LayoutIR

### Installation
For GPU acceleration with CUDA 13.0, install PyTorch first:
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
pip install layoutir
```

Or use the cuda extra (requires manual PyTorch installation first):
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
pip install layoutir[cuda]
```

## [1.0.1] - 2026-02-15

### Fixed
- Export `Pipeline` and `DoclingAdapter` from main package for easier imports
- Users can now use `from layoutir import Pipeline, DoclingAdapter` directly

## [1.0.0] - 2026-02-15

### Added
- Initial release of LayoutIR
- Production-grade document ingestion pipeline with compiler-like architecture
- PDF parsing via Docling with standard pipeline (Heron-101 vision model)
- Image extraction from born-digital PDFs with configurable resolution
- Canonical IR schema with deterministic hash-based IDs
- Multiple chunking strategies:
  - SemanticSectionChunker (heading-based sections)
  - TokenWindowChunker (fixed token windows with overlap)
  - LayoutAwareChunker (stub for future development)
- Multiple export formats:
  - Markdown with image references
  - Plain text
  - Parquet (for efficient structured storage)
  - Asset extraction (images as PNG, tables as CSV)
- CLI interface with `layoutir` command
- Python API for programmatic use
- GPU acceleration support
- Structured logging with timing metrics
- Comprehensive documentation and examples

### Fixed
- Critical bug in docling_extractor.py where `iterate_items()` tuples were incorrectly accessed
- Image extraction configuration for born-digital PDFs (added `generate_picture_images=True`)
- Proper handling of DocItem extraction from Docling's tuple-based iterator

### Technical Details
- Built on Docling 1.0+ with standard pipeline (not VLM)
- Requires Python >=3.12
- Uses Pydantic v2 for schema validation
- Implements deterministic hashing for reproducible outputs
- Supports GPU acceleration via CUDA

### Known Limitations
- Currently supports only PDF input format
- Semantic chunking limited to heading-based sections
- No incremental update support (processes entire document each time)

[1.0.0]: https://github.com/RahulPatnaik/layoutir/releases/tag/v1.0.0
