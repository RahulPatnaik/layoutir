# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
