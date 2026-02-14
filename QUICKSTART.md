# Quick Start Guide

Get started with Document IR in 5 minutes.

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Cache Docling models (~200-500MB)
# Required before first use
python tests/docling/doclingCacheModels.py
```

## Basic Usage

```bash
# Process a PDF
python ingest.py --input docs/pdfs/sample.pdf --output ./output
```

This will create:
```
output/
└── doc_a1b2c3d4e5f6.../
    ├── manifest.json          # Processing metadata
    ├── ir.json               # Canonical IR
    ├── chunks.json           # Chunk definitions
    ├── assets/
    │   ├── images/           # Extracted images
    │   └── tables/           # Tables as CSV
    └── exports/
        ├── markdown/         # Full doc + chunks
        ├── text/            # Plain text
        └── parquet/         # Structured data
```

## Common Workflows

### 1. Extract Text from PDF

```bash
python ingest.py --input paper.pdf --output ./out

# Find text output
cat output/doc_*/exports/text/full_document.txt
```

### 2. Chunk a Document

```bash
# Semantic chunking (by sections)
python ingest.py --input paper.pdf --output ./out --chunk-strategy semantic

# Token-based chunking
python ingest.py --input paper.pdf --output ./out \
  --chunk-strategy token \
  --chunk-size 512 \
  --chunk-overlap 50

# View chunks
ls output/doc_*/exports/markdown/chunks/
```

### 3. Extract Tables

```bash
python ingest.py --input report.pdf --output ./out

# Tables saved as CSV
ls output/doc_*/assets/tables/*.csv

# Tables also in Parquet for analysis
python -c "
import pandas as pd
df = pd.read_parquet('output/doc_*/exports/parquet/blocks.parquet')
tables = df[df['type'] == 'table']
print(tables)
"
```

### 4. Extract Images

```bash
python ingest.py --input slides.pdf --output ./out

# Images saved as PNG
ls output/doc_*/assets/images/*.png
```

### 5. Work with IR Directly

```python
import json
from src.layoutir.schema import Document

# Load canonical IR
with open('output/doc_abc123/ir.json') as f:
    data = json.load(f)
    document = Document(**data)

# Access structured data
for block in document.blocks:
    print(f"{block.type}: {block.content[:50]}")
```

## Performance Tuning

### Enable GPU Acceleration

```bash
# Install CUDA-enabled PyTorch first
# Then run with GPU
python ingest.py --input large.pdf --output ./out --use-gpu
```

### Debug Mode

```bash
python ingest.py --input file.pdf --output ./out \
  --log-level DEBUG \
  --structured-logs
```

## Testing

```bash
# Run integration test
python test_pipeline.py

# Run benchmark
python benchmark.py --input docs/pdfs/sample.pdf
```

Expected output:
```
================================================================================
Benchmark Results
================================================================================

Extraction Statistics:
  Pages:       42
  Blocks:     324
  Tables:       8
  Images:       5

Performance Metrics:
  Total time:     12.3s
  Pages/sec:      3.41
  MB/sec:         1.22

Stage Timing:
  parse           4.2s (34.1%) █████████████████
  extract         3.1s (25.2%) ████████████
  normalize       0.8s (6.5%)  ███
  ...
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design details
- Explore the `src/layoutir/` code
- Try different chunking strategies
- Customize exporters for your use case

## Troubleshooting

### "Docling not found"

```bash
pip install docling
```

### "Models not cached"

```bash
python tests/docling/doclingCacheModels.py
```

### "Out of memory"

Try disabling GPU or reducing batch sizes:
```bash
python ingest.py --input file.pdf --output ./out
# (GPU disabled by default)
```

### "No PDF found for testing"

Add a PDF to `docs/pdfs/` or specify `--input`:
```bash
python test_pipeline.py  # Will skip if no PDF found
python benchmark.py --input /path/to/your.pdf
```

## Support

For issues or questions, see the main project README.
