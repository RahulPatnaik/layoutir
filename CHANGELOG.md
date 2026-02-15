# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
