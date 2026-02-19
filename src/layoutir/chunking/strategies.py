"""
Pluggable chunking strategies operating on canonical IR.

All chunking operates on the IR, not raw text.
"""

from abc import ABC, abstractmethod
from typing import List
import logging

from ..schema import Document, Block, Chunk, BlockType
from ..utils.hashing import generate_chunk_id

logger = logging.getLogger(__name__)


class ChunkStrategy(ABC):
    """Abstract base class for chunking strategies"""

    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk document into segments.

        Args:
            document: Canonical IR document

        Returns:
            List of chunks
        """
        pass

    def _create_chunk(
        self, document: Document, blocks: List[Block], order: int, **metadata
    ) -> Chunk:
        """
        Helper to create a chunk from blocks.

        Args:
            document: Parent document
            blocks: Blocks to include in chunk
            order: Sequential order
            **metadata: Additional chunk metadata

        Returns:
            Chunk object
        """
        block_ids = [b.block_id for b in blocks]
        content = "\n\n".join(b.content for b in blocks)

        chunk_id = generate_chunk_id(
            document_id=document.document_id, block_ids=block_ids, chunk_order=order
        )

        # Compute page range
        page_numbers = [b.page_number for b in blocks]
        page_range = f"{min(page_numbers)}-{max(page_numbers)}" if page_numbers else "0"

        chunk_metadata = {
            "page_range": page_range,
            "block_count": len(blocks),
            "char_count": len(content),
            **metadata,
        }

        return Chunk(
            chunk_id=chunk_id,
            document_id=document.document_id,
            block_ids=block_ids,
            content=content,
            metadata=chunk_metadata,
            order=order,
        )


class SemanticSectionChunker(ChunkStrategy):
    """
    Chunks document by semantic sections.

    Groups blocks under each top-level heading into a chunk.
    """

    def __init__(self, max_heading_level: int = 2):
        """
        Initialize semantic section chunker.

        Args:
            max_heading_level: Maximum heading level to treat as section boundary
        """
        self.max_heading_level = max_heading_level

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk by semantic sections (headings).

        Args:
            document: Canonical IR document

        Returns:
            List of chunks, one per section
        """
        logger.info(f"Chunking document by semantic sections (max level {self.max_heading_level})")

        chunks = []
        current_section = []
        chunk_order = 0

        for block in document.blocks:
            # Check if this is a section boundary
            is_boundary = (
                block.type == BlockType.HEADING
                and block.level is not None
                and block.level <= self.max_heading_level
            )

            if is_boundary and current_section:
                # Create chunk from accumulated section
                chunk = self._create_chunk(
                    document=document,
                    blocks=current_section,
                    order=chunk_order,
                    strategy="semantic_section",
                )
                chunks.append(chunk)
                chunk_order += 1

                # Start new section
                current_section = [block]
            else:
                # Add to current section
                current_section.append(block)

        # Create chunk from final section
        if current_section:
            chunk = self._create_chunk(
                document=document,
                blocks=current_section,
                order=chunk_order,
                strategy="semantic_section",
            )
            chunks.append(chunk)

        logger.info(f"Created {len(chunks)} semantic chunks")
        return chunks


class TokenWindowChunker(ChunkStrategy):
    """
    Chunks document by fixed token windows with overlap.

    Uses character-based approximation (1 token ≈ 4 chars).
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize token window chunker.

        Args:
            chunk_size: Target chunk size in tokens
            overlap: Overlap size in tokens
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

        # Character approximation (1 token ≈ 4 chars)
        self.chunk_chars = chunk_size * 4
        self.overlap_chars = overlap * 4

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk by fixed token windows.

        Args:
            document: Canonical IR document

        Returns:
            List of chunks with overlap
        """
        logger.info(
            f"Chunking document by token windows "
            f"(size={self.chunk_size}, overlap={self.overlap})"
        )

        chunks = []
        chunk_order = 0

        # Concatenate all blocks
        all_blocks = document.blocks
        current_window = []
        current_chars = 0

        i = 0
        while i < len(all_blocks):
            block = all_blocks[i]
            block_chars = len(block.content)

            # Check if adding this block exceeds window
            if current_chars + block_chars > self.chunk_chars and current_window:
                # Create chunk from current window
                chunk = self._create_chunk(
                    document=document,
                    blocks=current_window,
                    order=chunk_order,
                    strategy="token_window",
                    token_size=self.chunk_size,
                    overlap_tokens=self.overlap,
                )
                chunks.append(chunk)
                chunk_order += 1

                # Calculate overlap
                overlap_chars_needed = self.overlap_chars
                overlap_blocks = []
                overlap_chars = 0

                # Go backward to find overlap blocks
                for j in range(len(current_window) - 1, -1, -1):
                    overlap_block = current_window[j]
                    overlap_blocks.insert(0, overlap_block)
                    overlap_chars += len(overlap_block.content)

                    if overlap_chars >= overlap_chars_needed:
                        break

                # Start new window with overlap
                current_window = overlap_blocks
                current_chars = overlap_chars

            # Add current block
            current_window.append(block)
            current_chars += block_chars
            i += 1

        # Create chunk from final window
        if current_window:
            chunk = self._create_chunk(
                document=document,
                blocks=current_window,
                order=chunk_order,
                strategy="token_window",
                token_size=self.chunk_size,
                overlap_tokens=self.overlap,
            )
            chunks.append(chunk)

        logger.info(f"Created {len(chunks)} token window chunks")
        return chunks


class LayoutAwareChunker(ChunkStrategy):
    """
    Layout-aware chunker (stub implementation).

    Future: Would use visual layout information to preserve
    meaningful boundaries (columns, sections, etc.)
    """

    def __init__(self):
        """Initialize layout-aware chunker"""
        logger.warning("LayoutAwareChunker is a stub implementation")

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Stub: Falls back to semantic chunking.

        Args:
            document: Canonical IR document

        Returns:
            List of chunks
        """
        logger.info("Using stub layout-aware chunker (fallback to semantic)")

        # Fallback to semantic chunker
        fallback = SemanticSectionChunker(max_heading_level=1)
        return fallback.chunk(document)
