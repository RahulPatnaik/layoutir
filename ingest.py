#!/usr/bin/env python3
"""
Document Ingestion CLI

Production-grade document ingestion & canonicalization engine.

Usage:
    python ingest.py --input file.pdf --output ./out --chunk-strategy semantic
"""

import argparse
import sys
from pathlib import Path

from src.layoutir.utils.logging_config import setup_logging
from src.layoutir.pipeline import Pipeline
from src.layoutir.adapters import DoclingAdapter
from src.layoutir.chunking import (
    SemanticSectionChunker,
    TokenWindowChunker,
    LayoutAwareChunker,
)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Document Ingestion & Canonicalization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest.py --input paper.pdf --output ./out
  python ingest.py --input paper.pdf --output ./out --chunk-strategy token --chunk-size 1024
  python ingest.py --input paper.pdf --output ./out --use-gpu --log-level DEBUG
        """
    )

    parser.add_argument(
        '--input',
        required=True,
        type=Path,
        help='Input file path (PDF)'
    )

    parser.add_argument(
        '--output',
        required=True,
        type=Path,
        help='Output directory for processed documents'
    )

    parser.add_argument(
        '--chunk-strategy',
        choices=['semantic', 'token', 'layout'],
        default='semantic',
        help='Chunking strategy (default: semantic)'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=512,
        help='Chunk size in tokens for token strategy (default: 512)'
    )

    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=50,
        help='Chunk overlap in tokens for token strategy (default: 50)'
    )

    parser.add_argument(
        '--max-heading-level',
        type=int,
        default=2,
        help='Max heading level for semantic chunking (default: 2)'
    )

    parser.add_argument(
        '--use-gpu',
        action='store_true',
        help='Enable GPU acceleration for PDF processing'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--structured-logs',
        action='store_true',
        help='Enable JSON structured logging'
    )

    return parser.parse_args()


def create_chunk_strategy(args):
    """Create chunking strategy from arguments"""
    if args.chunk_strategy == 'semantic':
        return SemanticSectionChunker(max_heading_level=args.max_heading_level)
    elif args.chunk_strategy == 'token':
        return TokenWindowChunker(
            chunk_size=args.chunk_size,
            overlap=args.chunk_overlap
        )
    elif args.chunk_strategy == 'layout':
        return LayoutAwareChunker()
    else:
        raise ValueError(f"Unknown chunk strategy: {args.chunk_strategy}")


def main():
    """Main entry point"""
    args = parse_args()

    # Setup logging
    setup_logging(
        log_level=args.log_level,
        structured=args.structured_logs
    )

    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Create adapter
    adapter = DoclingAdapter(use_gpu=args.use_gpu)

    # Create chunking strategy
    chunk_strategy = create_chunk_strategy(args)

    # Create pipeline
    pipeline = Pipeline(
        adapter=adapter,
        chunk_strategy=chunk_strategy,
        config={
            'chunk_strategy': args.chunk_strategy,
            'chunk_size': args.chunk_size,
            'chunk_overlap': args.chunk_overlap,
            'use_gpu': args.use_gpu,
        }
    )

    # Process document
    try:
        print(f"Processing: {args.input}")
        document = pipeline.process(args.input, args.output)

        # Print summary
        stats = pipeline.get_stats()
        print("\n" + "="*60)
        print("Processing Complete")
        print("="*60)
        print(f"Document ID: {document.document_id}")
        print(f"Pages: {document.stats.get('page_count', 0)}")
        print(f"Blocks: {document.stats.get('block_count', 0)}")
        print(f"Tables: {document.stats.get('table_count', 0)}")
        print(f"Images: {document.stats.get('image_count', 0)}")
        print(f"\nTotal time: {stats['total_time']:.2f}s")
        print("\nStage timing:")
        for stage, duration in stats['timing'].items():
            print(f"  {stage}: {duration:.2f}s")

        output_path = args.output / document.document_id
        print(f"\nOutput: {output_path}")
        print("="*60)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
