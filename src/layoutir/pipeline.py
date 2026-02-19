"""
Main pipeline orchestrator.

Coordinates all layers: Adapter → Extraction → Normalization → Export
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging
import time
from datetime import datetime

from .schema import Document, Manifest, Chunk
from .adapters import InputAdapter, DoclingAdapter
from .extraction import DoclingExtractor
from .normalization import Normalizer
from .chunking import ChunkStrategy, SemanticSectionChunker
from .exporters import (
    MarkdownExporter,
    TextExporter,
    ParquetExporter,
    AssetWriter,
)

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Main document ingestion pipeline.

    Orchestrates: Input → Extraction → Normalization → Chunking → Export
    """

    def __init__(
        self,
        adapter: Optional[InputAdapter] = None,
        chunk_strategy: Optional[ChunkStrategy] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize pipeline.

        Args:
            adapter: Input adapter (defaults to DoclingAdapter)
            chunk_strategy: Chunking strategy (defaults to SemanticSectionChunker)
            config: Pipeline configuration
        """
        self.adapter = adapter or DoclingAdapter()
        self.chunk_strategy = chunk_strategy or SemanticSectionChunker()
        self.config = config or {}

        # Initialize exporters
        self.markdown_exporter = MarkdownExporter()
        self.text_exporter = TextExporter()
        self.parquet_exporter = ParquetExporter()
        self.asset_writer = AssetWriter()

        # Timing stats
        self.timing = {}

        logger.info("Pipeline initialized")

    def process(self, input_path: Path, output_dir: Path) -> Document:
        """
        Process document through full pipeline.

        Args:
            input_path: Path to input file
            output_dir: Base output directory

        Returns:
            Canonical IR Document
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)

        logger.info(f"Processing document: {input_path}")

        # Stage 1: Parse input
        stage_start = time.time()
        parsed_doc = self._stage_parse(input_path)
        self.timing["parse"] = time.time() - stage_start

        # Stage 2: Extract raw elements
        stage_start = time.time()
        raw_doc = self._stage_extract(parsed_doc)
        self.timing["extract"] = time.time() - stage_start

        # Stage 3: Normalize to canonical IR
        stage_start = time.time()
        document = self._stage_normalize(input_path, raw_doc)
        self.timing["normalize"] = time.time() - stage_start

        # Stage 4: Chunk document
        stage_start = time.time()
        chunks = self._stage_chunk(document)
        self.timing["chunk"] = time.time() - stage_start

        # Stage 5: Create output directory structure
        doc_output_dir = self._create_output_structure(output_dir, document)

        # Stage 6: Write assets
        stage_start = time.time()
        self._stage_write_assets(document, doc_output_dir)
        self.timing["write_assets"] = time.time() - stage_start

        # Stage 7: Export to formats
        stage_start = time.time()
        self._stage_export(document, chunks, doc_output_dir)
        self.timing["export"] = time.time() - stage_start

        # Stage 8: Write IR and manifest
        stage_start = time.time()
        self._stage_write_ir_and_manifest(document, chunks, doc_output_dir)
        self.timing["write_metadata"] = time.time() - stage_start

        # Log summary
        total_time = sum(self.timing.values())
        logger.info(f"Pipeline complete in {total_time:.2f}s")
        logger.info(f"Output: {doc_output_dir}")

        return document

    def _stage_parse(self, input_path: Path) -> Any:
        """Stage 1: Parse input file"""
        logger.info("Stage 1/8: Parsing input")

        if not self.adapter.supports_format(input_path):
            raise ValueError(f"Unsupported format: {input_path.suffix}")

        parsed = self.adapter.parse(input_path)
        logger.info(f"Parsed {input_path.name}")

        return parsed

    def _stage_extract(self, parsed_doc: Any):
        """Stage 2: Extract raw structural elements"""
        logger.info("Stage 2/8: Extracting structural elements")

        extractor = DoclingExtractor()
        raw_doc = extractor.extract(parsed_doc)

        logger.info(
            f"Extracted: {len(raw_doc.blocks)} blocks, "
            f"{len(raw_doc.tables)} tables, {len(raw_doc.images)} images"
        )

        return raw_doc

    def _stage_normalize(self, input_path: Path, raw_doc) -> Document:
        """Stage 3: Normalize to canonical IR"""
        logger.info("Stage 3/8: Normalizing to canonical IR")

        parser_version = self.adapter.get_parser_version()
        normalizer = Normalizer(input_path, parser_version)
        document = normalizer.normalize(raw_doc, self.config)

        logger.info(f"Normalized document: {document.document_id}")

        return document

    def _stage_chunk(self, document: Document) -> List[Chunk]:
        """Stage 4: Chunk document"""
        logger.info("Stage 4/8: Chunking document")

        chunks = self.chunk_strategy.chunk(document)
        logger.info(f"Created {len(chunks)} chunks")

        return chunks

    def _create_output_structure(self, output_dir: Path, document: Document) -> Path:
        """Create output directory structure"""
        doc_output_dir = output_dir / document.document_id

        # Create directories
        (doc_output_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
        (doc_output_dir / "assets" / "tables").mkdir(parents=True, exist_ok=True)
        (doc_output_dir / "exports" / "markdown").mkdir(parents=True, exist_ok=True)
        (doc_output_dir / "exports" / "text").mkdir(parents=True, exist_ok=True)
        (doc_output_dir / "exports" / "parquet").mkdir(parents=True, exist_ok=True)
        (doc_output_dir / "logs").mkdir(parents=True, exist_ok=True)

        return doc_output_dir

    def _stage_write_assets(self, document: Document, output_dir: Path):
        """Stage 6: Write assets"""
        logger.info("Stage 6/8: Writing assets")

        self.asset_writer.write_assets(document, output_dir)

    def _stage_export(self, document: Document, chunks: List[Chunk], output_dir: Path):
        """Stage 7: Export to formats"""
        logger.info("Stage 7/8: Exporting to formats")

        # Export to Markdown
        self.markdown_exporter.export(document, output_dir, chunks)

        # Export to plain text
        self.text_exporter.export(document, output_dir, chunks)

        # Export to Parquet
        self.parquet_exporter.export(document, output_dir, chunks)

    def _stage_write_ir_and_manifest(
        self, document: Document, chunks: List[Chunk], output_dir: Path
    ):
        """Stage 8: Write IR and manifest"""
        logger.info("Stage 8/8: Writing IR and manifest")

        # Write canonical IR
        ir_path = output_dir / "ir.json"
        with open(ir_path, "w", encoding="utf-8") as f:
            f.write(document.model_dump_json(indent=2))

        # Write chunks
        if chunks:
            chunks_path = output_dir / "chunks.json"
            with open(chunks_path, "w", encoding="utf-8") as f:
                chunks_data = [chunk.model_dump() for chunk in chunks]
                json.dump(chunks_data, f, indent=2)

        # Create manifest
        manifest = Manifest(
            document_id=document.document_id,
            input_file_hash=document.metadata.source_hash,
            parser_version=document.parser_version,
            schema_version=document.schema_version,
            config_used=self.config,
            created_at=datetime.utcnow(),
            stats=document.stats,
            output_files={
                "ir": "ir.json",
                "chunks": "chunks.json",
                "markdown": "exports/markdown/full_document.md",
                "text": "exports/text/full_document.txt",
                "parquet_blocks": "exports/parquet/blocks.parquet",
                "parquet_chunks": "exports/parquet/chunks.parquet",
            },
        )

        # Write manifest
        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        logger.info("IR and manifest written")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline execution statistics.

        Returns:
            Dictionary of timing and stats
        """
        return {
            "timing": self.timing,
            "total_time": sum(self.timing.values()),
        }
