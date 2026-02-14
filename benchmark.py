#!/usr/bin/env python3
"""
Benchmark script for document ingestion pipeline.

Processes a sample PDF and reports detailed timing and statistics.
"""

import sys
import argparse
from pathlib import Path
import tempfile

from src.layoutir.utils.logging_config import setup_logging
from src.layoutir.pipeline import Pipeline
from src.layoutir.adapters import DoclingAdapter
from src.layoutir.chunking import SemanticSectionChunker


def format_time(seconds: float) -> str:
    """Format time duration"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"


def format_size(bytes_count: int) -> str:
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f}{unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f}TB"


def run_benchmark(input_pdf: Path, use_gpu: bool = False):
    """
    Run benchmark on a PDF file.

    Args:
        input_pdf: Path to PDF file
        use_gpu: Enable GPU acceleration
    """
    print("="*80)
    print("Document Ingestion Pipeline - Benchmark")
    print("="*80)
    print()

    # Setup logging (suppress most output)
    setup_logging(log_level='WARNING', structured=False)

    # File info
    file_size = input_pdf.stat().st_size
    print(f"Input File: {input_pdf.name}")
    print(f"File Size:  {format_size(file_size)}")
    print(f"GPU:        {'Enabled' if use_gpu else 'Disabled'}")
    print()

    # Create pipeline
    adapter = DoclingAdapter(use_gpu=use_gpu)
    chunk_strategy = SemanticSectionChunker(max_heading_level=2)

    pipeline = Pipeline(
        adapter=adapter,
        chunk_strategy=chunk_strategy,
        config={'benchmark': True, 'use_gpu': use_gpu}
    )

    # Process with temporary output
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        print("Processing...")
        print("-"*80)

        document = pipeline.process(input_pdf, output_dir)
        stats = pipeline.get_stats()

        print()
        print("="*80)
        print("Benchmark Results")
        print("="*80)
        print()

        # Extraction statistics
        print("Extraction Statistics:")
        print(f"  Pages:      {document.stats.get('page_count', 0):>6}")
        print(f"  Blocks:     {document.stats.get('block_count', 0):>6}")
        print(f"  Tables:     {document.stats.get('table_count', 0):>6}")
        print(f"  Images:     {document.stats.get('image_count', 0):>6}")
        print()

        # Chunk statistics
        doc_dir = output_dir / document.document_id
        chunks_file = doc_dir / "chunks.json"
        if chunks_file.exists():
            import json
            with open(chunks_file) as f:
                chunks = json.load(f)
                print(f"  Chunks:     {len(chunks):>6}")
                if chunks:
                    avg_size = sum(len(c['content']) for c in chunks) / len(chunks)
                    print(f"  Avg chunk:  {int(avg_size):>6} chars")
        print()

        # Performance metrics
        total_time = stats['total_time']
        pages_per_sec = document.stats.get('page_count', 0) / total_time if total_time > 0 else 0
        mb_per_sec = (file_size / (1024*1024)) / total_time if total_time > 0 else 0

        print("Performance Metrics:")
        print(f"  Total time:     {format_time(total_time)}")
        print(f"  Pages/sec:      {pages_per_sec:.2f}")
        print(f"  MB/sec:         {mb_per_sec:.2f}")
        print()

        # Stage timing
        print("Stage Timing:")
        timing_data = []
        for stage, duration in stats['timing'].items():
            pct = (duration / total_time * 100) if total_time > 0 else 0
            timing_data.append((stage, duration, pct))

        # Sort by duration descending
        timing_data.sort(key=lambda x: x[1], reverse=True)

        for stage, duration, pct in timing_data:
            bar_width = int(pct / 2)  # Scale to 50 chars max
            bar = "█" * bar_width
            print(f"  {stage:15} {format_time(duration):>8} ({pct:5.1f}%) {bar}")

        print()

        # Output size
        output_size = sum(
            f.stat().st_size
            for f in doc_dir.rglob('*')
            if f.is_file()
        )

        print(f"Output Size: {format_size(output_size)}")
        print(f"Compression: {(output_size / file_size * 100):.1f}% of input")

        print()
        print("="*80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Benchmark document ingestion pipeline"
    )

    parser.add_argument(
        '--input',
        type=Path,
        help='Input PDF file (default: first PDF in docs/pdfs/)'
    )

    parser.add_argument(
        '--use-gpu',
        action='store_true',
        help='Enable GPU acceleration'
    )

    args = parser.parse_args()

    # Find input PDF
    if args.input:
        input_pdf = args.input
    else:
        # Search for test PDF
        test_pdf_dirs = [
            Path("docs/pdfs"),
            Path("tests/pdfs"),
        ]

        input_pdf = None
        for pdf_dir in test_pdf_dirs:
            if pdf_dir.exists():
                pdfs = list(pdf_dir.glob("*.pdf"))
                if pdfs:
                    input_pdf = pdfs[0]
                    break

        if not input_pdf:
            print("Error: No test PDF found. Specify --input or add PDF to docs/pdfs/",
                  file=sys.stderr)
            return 1

    if not input_pdf.exists():
        print(f"Error: File not found: {input_pdf}", file=sys.stderr)
        return 1

    try:
        run_benchmark(input_pdf, use_gpu=args.use_gpu)
        return 0

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
