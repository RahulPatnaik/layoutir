"""Round-trip stability tests"""

import pytest
import re
from pathlib import Path
import json
import tempfile
from layoutir import Pipeline, Document
from layoutir.adapters import DoclingAdapter
from layoutir.utils.equality import assert_semantic_equality, compute_semantic_hash


class TestRoundTripStability:
    """Core round-trip stability tests"""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline with GPU disabled for consistent testing"""
        adapter = DoclingAdapter(use_gpu=False)
        return Pipeline(adapter=adapter)

    @pytest.fixture
    def sample_pdf(self):
        """Use existing test PDF"""
        docs_dir = Path(__file__).parent.parent / "docs" / "pdfs"
        pdf_path = docs_dir / "table.pdf"  # Adjust to actual test PDF
        if not pdf_path.exists():
            pytest.skip("Test PDF not available")
        return pdf_path

    def test_parse_twice_identical_ir(self, pipeline, tmp_path, sample_pdf):
        """Core test: parse(pdf) twice produces identical IR"""
        output_dir1 = tmp_path / "run1"
        output_dir1.mkdir()
        doc1 = pipeline.process(sample_pdf, output_dir1)

        output_dir2 = tmp_path / "run2"
        output_dir2.mkdir()
        doc2 = pipeline.process(sample_pdf, output_dir2)

        # Assert semantic equality
        assert_semantic_equality(doc1, doc2)

    def test_serialize_deserialize_stability(self, pipeline, tmp_path, sample_pdf):
        """Test: IR → JSON → IR preserves content"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        doc1 = pipeline.process(sample_pdf, output_dir)

        # Serialize
        json_path = tmp_path / "ir.json"
        with open(json_path, 'w') as f:
            f.write(doc1.model_dump_json(indent=2))

        # Deserialize
        with open(json_path, 'r') as f:
            doc2 = Document(**json.load(f))

        assert_semantic_equality(doc1, doc2)

    def test_block_order_deterministic(self, pipeline, tmp_path, sample_pdf):
        """Test: Block order is deterministic across runs"""
        docs = []
        for i in range(3):
            output_dir = tmp_path / f"run{i}"
            output_dir.mkdir()
            doc = pipeline.process(sample_pdf, output_dir)
            docs.append(doc)

        block_orders = [
            [(b.block_id, b.order) for b in doc.blocks]
            for doc in docs
        ]

        assert block_orders[0] == block_orders[1] == block_orders[2]

    def test_spatial_ordering_validation(self, pipeline, tmp_path, sample_pdf):
        """Test: Ordering validation runs and annotates blocks"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        doc = pipeline.process(sample_pdf, output_dir)

        blocks_with_ordering = [b for b in doc.blocks if b.ordering_metadata is not None]
        assert len(blocks_with_ordering) > 0

        for block in blocks_with_ordering:
            meta = block.ordering_metadata
            assert meta.docling_order == block.order

    def test_semantic_hash_stability(self, pipeline, tmp_path, sample_pdf):
        """
        Test: Semantic hash is deterministic across runs.
        This is the LONG-TERM STABILITY PROOF.
        """
        # Parse twice
        output_dir1 = tmp_path / "run1"
        output_dir1.mkdir()
        doc1 = pipeline.process(sample_pdf, output_dir1)
        hash1 = compute_semantic_hash(doc1)

        output_dir2 = tmp_path / "run2"
        output_dir2.mkdir()
        doc2 = pipeline.process(sample_pdf, output_dir2)
        hash2 = compute_semantic_hash(doc2)

        # Hashes MUST match for semantic stability
        assert hash1 == hash2, f"Semantic hashes differ: {hash1} != {hash2}"


class TestGoldenIRFixtures:
    """
    REGRESSION TEST REQUIREMENT: Golden IR fixtures for determinism.

    This test suite ensures that future changes don't break determinism.
    """

    @pytest.fixture
    def golden_fixtures_dir(self):
        """Directory containing golden IR JSON files"""
        return Path(__file__).parent / "fixtures" / "golden_ir"

    @pytest.fixture
    def pipeline(self):
        """Create pipeline with GPU disabled for consistent testing"""
        adapter = DoclingAdapter(use_gpu=False)
        return Pipeline(adapter=adapter)

    def test_golden_ir_hash_regression(self, pipeline, tmp_path, golden_fixtures_dir):
        """
        CRITICAL REGRESSION TEST: Parse known PDFs and verify hashes match golden values.

        This prevents:
        - Silent determinism regression
        - Ordering algorithm changes
        - Float precision drift
        - JSON serialization changes
        """
        if not golden_fixtures_dir.exists():
            pytest.skip("Golden fixtures not yet created")

        # Load golden hashes
        golden_hashes_path = golden_fixtures_dir / "golden_hashes.json"
        if not golden_hashes_path.exists():
            pytest.skip("Golden hashes file not found")

        with open(golden_hashes_path, 'r') as f:
            golden_hashes = json.load(f)

        # Test each golden PDF — PDFs live in docs/pdfs/, not in the fixture dir
        docs_dir = Path(__file__).parent.parent / "docs" / "pdfs"
        for pdf_name, expected_hash in golden_hashes.items():
            pdf_path = docs_dir / f"{pdf_name}.pdf"
            if not pdf_path.exists():
                continue

            # Parse and compute hash
            output_dir = tmp_path / pdf_name
            output_dir.mkdir()
            doc = pipeline.process(pdf_path, output_dir)
            actual_hash = compute_semantic_hash(doc)

            # CRITICAL: Hash must match golden value
            assert actual_hash == expected_hash, (
                f"Hash regression for {pdf_name}:\n"
                f"  Expected: {expected_hash}\n"
                f"  Actual:   {actual_hash}\n"
                f"  This indicates determinism has regressed!"
            )

    @pytest.mark.skip(reason="Manual test for creating golden fixtures")
    def test_create_golden_fixtures(self, pipeline, tmp_path, golden_fixtures_dir):
        """
        Helper test to create/update golden fixtures.
        Run manually when intentionally updating IR format.

        Usage: pytest tests/test_roundtrip.py::TestGoldenIRFixtures::test_create_golden_fixtures -v
        """
        golden_fixtures_dir.mkdir(parents=True, exist_ok=True)

        # Sample PDFs to use as golden fixtures
        docs_dir = Path(__file__).parent.parent / "docs" / "pdfs"
        sample_pdfs = {
            'table': docs_dir / 'table.pdf',
        }

        golden_hashes = {}
        for name, pdf_path in sample_pdfs.items():
            if not pdf_path.exists():
                print(f"Skipping {name}: PDF not found at {pdf_path}")
                continue

            output_dir = tmp_path / name
            output_dir.mkdir()
            doc = pipeline.process(pdf_path, output_dir)

            # Compute and store hash
            doc_hash = compute_semantic_hash(doc)
            golden_hashes[name] = doc_hash

            # Save IR JSON as golden fixture
            ir_path = golden_fixtures_dir / f"{name}_ir.json"
            with open(ir_path, 'w') as f:
                f.write(doc.model_dump_json(indent=2))

            print(f"Created golden fixture for {name}: {doc_hash}")

        # Save golden hashes
        with open(golden_fixtures_dir / 'golden_hashes.json', 'w') as f:
            json.dump(golden_hashes, f, indent=2)

        print(f"Golden fixtures created in {golden_fixtures_dir}")


class TestBackwardCompatibility:
    """Test backward compatibility with existing IR"""

    def test_load_ir_without_formatting(self, tmp_path):
        """Test: Can load old IR JSON without new fields"""
        ir_data = {
            "document_id": "doc_test",
            "schema_version": "1.0.0",
            "parser_version": "docling-1.0.0",
            "metadata": {
                "page_count": 1,
                "source_format": "pdf",
                "source_path": "/test.pdf",
                "source_hash": "abc123"
            },
            "blocks": [{
                "block_id": "blk_test",
                "type": "paragraph",
                "page_number": 1,
                "content": "Test",
                "order": 0,
                "metadata": {}
            }],
            "relationships": [],
            "stats": {"block_count": 1},
            "processing_timestamp": "2024-01-01T00:00:00",
            "config_used": {}
        }

        ir_path = tmp_path / "old_ir.json"
        with open(ir_path, 'w') as f:
            json.dump(ir_data, f)

        with open(ir_path, 'r') as f:
            doc = Document(**json.load(f))

        assert doc.document_id == "doc_test"
        assert doc.blocks[0].formatting_data is None  # New field defaults to None
        assert doc.blocks[0].ordering_metadata is None

    def test_load_ir_with_optional_fields(self, tmp_path):
        """Test: Can load new IR JSON with optional fields"""
        ir_data = {
            "document_id": "doc_test",
            "schema_version": "1.0.0",
            "parser_version": "docling-1.0.0",
            "metadata": {
                "page_count": 1,
                "source_format": "pdf",
                "source_path": "/test.pdf",
                "source_hash": "abc123"
            },
            "blocks": [{
                "block_id": "blk_test",
                "type": "paragraph",
                "page_number": 1,
                "content": "Test",
                "order": 0,
                "metadata": {},
                "formatting_data": {
                    "font": {"name": "Arial", "size": 12.0},
                    "style": {"bold": True},
                    "links": []
                },
                "ordering_metadata": {
                    "docling_order": 0,
                    "spatial_order": 0,
                    "order_discrepancy": False
                }
            }],
            "relationships": [],
            "stats": {"block_count": 1},
            "processing_timestamp": "2024-01-01T00:00:00",
            "config_used": {}
        }

        ir_path = tmp_path / "new_ir.json"
        with open(ir_path, 'w') as f:
            json.dump(ir_data, f)

        with open(ir_path, 'r') as f:
            doc = Document(**json.load(f))

        assert doc.document_id == "doc_test"
        assert doc.blocks[0].formatting_data is not None
        assert doc.blocks[0].formatting_data.font.name == "Arial"
        assert doc.blocks[0].ordering_metadata is not None
        assert doc.blocks[0].ordering_metadata.docling_order == 0


class TestStabilityProtection:
    """
    STABILITY INVARIANT ENFORCEMENT:

    These tests fail if any stability-critical literal is reintroduced outside
    _stability_constants.py. They act as a regression guard for future refactors.

    What is checked:
      - No [:N] slice literals (block/table/image ID length)
      - No hardcoded truncation limits (500, 200)
      - No inline json.dumps kwargs (sort_keys, ensure_ascii, separators)
      - No hardcoded hash algorithm strings (sha256)
      - No hardcoded encoding strings (utf-8) on hash-path files only
      - No ROUND_PRECISION = <literal> outside the constants file

    What is explicitly NOT checked (false positive exclusions):
      - _stability_constants.py itself (the allowed source of truth)
      - Docstring / comment lines (not live code)
      - File I/O encoding='utf-8' in exporters and pipeline (not hash-path)
      - round() calls using self.ROUND_PRECISION (correct usage)
      - Variable references that contain a constant name on the right-hand side
    """

    SRC_DIR = Path(__file__).parent.parent / "src" / "layoutir"
    CONSTANTS_FILE = SRC_DIR / "_stability_constants.py"

    # Files whose encoding='utf-8' is file I/O, not hash-path
    FILE_IO_ENCODING_EXCLUSIONS = {
        "exporters/markdown_exporter.py",
        "exporters/text_exporter.py",
        "exporters/asset_writer.py",
        "pipeline.py",
    }

    def _source_lines(self, skip_files=None):
        """Yield (relative_path, lineno, line) for all .py source lines."""
        skip_files = skip_files or set()
        for py_file in self.SRC_DIR.rglob("*.py"):
            rel = py_file.relative_to(self.SRC_DIR)
            if str(rel) in skip_files or py_file == self.CONSTANTS_FILE:
                continue
            for lineno, line in enumerate(py_file.read_text().splitlines(), 1):
                yield str(rel), lineno, line

    def _is_comment_or_docstring(self, line: str) -> bool:
        stripped = line.strip()
        return (
            stripped.startswith('#') or
            stripped.startswith('"""') or
            stripped.startswith("'''") or
            stripped.startswith('- ') or
            stripped.startswith('* ')
        )

    def _uses_constant(self, line: str) -> bool:
        """True if line references a _stability_constants name on the RHS."""
        constant_prefixes = (
            'BLOCK_ID_', 'TABLE_ID_', 'HASH_STRING_', 'HASH_DICT_',
            'SPATIAL_', 'CANONICAL_JSON_', 'SEMANTIC_HASH_',
        )
        return any(prefix in line for prefix in constant_prefixes)

    def test_no_bare_hex_length_slices(self):
        """No hardcoded stability-critical slice lengths outside _stability_constants.py.

        Checks specifically for the magic numbers that correspond to frozen constants:
          [:16]  → BLOCK_ID_HEX_LENGTH
          [:500] → BLOCK_ID_CONTENT_TRUNCATION
          [:200] → TABLE_ID_TEXT_TRUNCATION

        Display-only slices ([:30], [:3], etc.) are NOT stability-critical and are exempt.
        """
        # Only the specific lengths that are frozen in _stability_constants.py
        critical_lengths = {16, 500, 200}
        violations = []
        for rel, lineno, line in self._source_lines():
            if self._is_comment_or_docstring(line):
                continue
            for m in re.finditer(r'\[:(\d+)\]', line):
                n = int(m.group(1))
                if n in critical_lengths and not self._uses_constant(line):
                    violations.append(f"{rel}:{lineno}: {line.strip()}")
        assert not violations, (
            "Bare [:N] slice with stability-critical length found — use the corresponding constant:\n"
            "  [:16]  → BLOCK_ID_HEX_LENGTH\n"
            "  [:500] → BLOCK_ID_CONTENT_TRUNCATION\n"
            "  [:200] → TABLE_ID_TEXT_TRUNCATION\n"
            + "\n".join(violations)
        )

    def test_no_inline_json_dumps_kwargs(self):
        """No inline sort_keys=True/False or ensure_ascii= in live code outside constants"""
        violations = []
        for rel, lineno, line in self._source_lines():
            if self._is_comment_or_docstring(line):
                continue
            # Detect inline literal kwargs: sort_keys=True, ensure_ascii=False, etc.
            if re.search(r'sort_keys\s*=\s*(True|False)', line) and not self._uses_constant(line):
                violations.append(f"{rel}:{lineno}: {line.strip()}")
            if re.search(r'ensure_ascii\s*=\s*(True|False)', line) and not self._uses_constant(line):
                violations.append(f"{rel}:{lineno}: {line.strip()}")
            if re.search(r"separators\s*=\s*[\(\[]", line) and not self._uses_constant(line):
                violations.append(f"{rel}:{lineno}: {line.strip()}")
        assert not violations, (
            "Inline json.dumps kwargs found — use CANONICAL_JSON_* or HASH_DICT_* constants:\n"
            + "\n".join(violations)
        )

    def test_no_hardcoded_hash_algorithm(self):
        """No 'sha256' string literals in live code outside constants"""
        violations = []
        for rel, lineno, line in self._source_lines():
            if self._is_comment_or_docstring(line):
                continue
            # Allow docstring default descriptions like (default: sha256)
            if 'default:' in line or 'default =' in line:
                continue
            if re.search(r'["\']sha256["\']', line) and not self._uses_constant(line):
                violations.append(f"{rel}:{lineno}: {line.strip()}")
        assert not violations, (
            "Hardcoded 'sha256' found — use BLOCK_ID_HASH_ALGORITHM or SEMANTIC_HASH_ALGORITHM:\n"
            + "\n".join(violations)
        )

    def test_no_hardcoded_encoding_on_hash_path(self):
        """No hardcoded 'utf-8' on hash-path files (file I/O exclusions are exempt)"""
        violations = []
        for rel, lineno, line in self._source_lines(skip_files=self.FILE_IO_ENCODING_EXCLUSIONS):
            if self._is_comment_or_docstring(line):
                continue
            # open(..., encoding='utf-8') is file I/O — not hash-path
            if "open(" in line:
                continue
            if re.search(r'["\']utf-8["\']', line) and not self._uses_constant(line):
                violations.append(f"{rel}:{lineno}: {line.strip()}")
        assert not violations, (
            "Hardcoded 'utf-8' on hash path — use HASH_STRING_ENCODING or SEMANTIC_HASH_ENCODING:\n"
            + "\n".join(violations)
        )

    def test_stability_constants_exports_all_critical_names(self):
        """_stability_constants.py must export the full set of expected names"""
        from layoutir._stability_constants import (
            BLOCK_ID_HASH_ALGORITHM,
            BLOCK_ID_HEX_LENGTH,
            BLOCK_ID_CONTENT_TRUNCATION,
            TABLE_ID_TEXT_TRUNCATION,
            HASH_STRING_ENCODING,
            HASH_DICT_SORT_KEYS,
            HASH_DICT_ENSURE_ASCII,
            SPATIAL_ROUND_PRECISION,
            BLOCK_TYPE_SORT_PRIORITY,
            CANONICAL_JSON_SORT_KEYS,
            CANONICAL_JSON_SEPARATORS,
            CANONICAL_JSON_ENSURE_ASCII,
            CANONICAL_JSON_INDENT,
            SEMANTIC_HASH_ALGORITHM,
            SEMANTIC_HASH_ENCODING,
            SCHEMA_VERSION,
        )
        # If any of these imports fail, the test fails — all names must exist
        assert BLOCK_ID_HASH_ALGORITHM == "sha256"
        assert BLOCK_ID_HEX_LENGTH == 16
        assert SPATIAL_ROUND_PRECISION == 4
        assert CANONICAL_JSON_ENSURE_ASCII is False
        assert HASH_DICT_ENSURE_ASCII is True  # intentionally different
        assert CANONICAL_JSON_ENSURE_ASCII != HASH_DICT_ENSURE_ASCII
