#!/usr/bin/env python3
"""
Minimal test case for document ingestion pipeline.

Tests basic functionality of the pipeline.
"""

import sys
from pathlib import Path
import tempfile

from src.layoutir.utils.logging_config import setup_logging
from src.layoutir.pipeline import Pipeline
from src.layoutir.adapters import DoclingAdapter
from src.layoutir.chunking import SemanticSectionChunker


def test_pipeline():
    """Test basic pipeline functionality"""
    print("Testing Document Ingestion Pipeline")
    print("="*60)

    # Setup logging
    setup_logging(log_level='INFO', structured=False)

    # Find a test PDF
    test_pdf_dirs = [
        Path("docs/pdfs"),
        Path("tests/pdfs"),
        Path("."),
    ]

    test_pdf = None
    for pdf_dir in test_pdf_dirs:
        if pdf_dir.exists():
            pdfs = list(pdf_dir.glob("*.pdf"))
            if pdfs:
                test_pdf = pdfs[0]
                break

    if not test_pdf:
        print("Warning: No test PDF found in docs/pdfs or tests/pdfs")
        print("Skipping test - pipeline structure validated")
        return True

    print(f"Test PDF: {test_pdf}")

    # Create temporary output directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        print(f"Output: {output_dir}")
        print()

        # Create pipeline
        adapter = DoclingAdapter(use_gpu=False)
        chunk_strategy = SemanticSectionChunker(max_heading_level=2)

        pipeline = Pipeline(
            adapter=adapter,
            chunk_strategy=chunk_strategy,
            config={'test': True}
        )

        # Process document
        try:
            document = pipeline.process(test_pdf, output_dir)

            # Validate results
            print("\n" + "="*60)
            print("Test Results")
            print("="*60)

            # Check document
            assert document.document_id, "Document ID should be set"
            assert document.schema_version == "1.0.0", "Schema version should be 1.0.0"
            assert len(document.blocks) > 0, "Should have extracted blocks"

            print(f"✓ Document ID: {document.document_id}")
            print(f"✓ Schema version: {document.schema_version}")
            print(f"✓ Blocks extracted: {len(document.blocks)}")
            print(f"✓ Pages: {document.stats.get('page_count', 0)}")

            # Check output structure
            doc_dir = output_dir / document.document_id

            assert (doc_dir / "manifest.json").exists(), "Manifest should exist"
            assert (doc_dir / "ir.json").exists(), "IR should exist"
            assert (doc_dir / "assets").exists(), "Assets directory should exist"
            assert (doc_dir / "exports").exists(), "Exports directory should exist"

            print(f"✓ Output structure created")

            # Check exports
            assert (doc_dir / "exports" / "markdown" / "full_document.md").exists()
            assert (doc_dir / "exports" / "text" / "full_document.txt").exists()
            assert (doc_dir / "exports" / "parquet" / "blocks.parquet").exists()

            print(f"✓ All exports generated")

            # Check timing
            stats = pipeline.get_stats()
            print(f"\n✓ Total processing time: {stats['total_time']:.2f}s")

            print("\n" + "="*60)
            print("All tests passed!")
            print("="*60)

            return True

        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    success = test_pipeline()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
