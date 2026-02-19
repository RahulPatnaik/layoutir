"""Spatial ordering validation for blocks

STABILITY-CRITICAL: The sort key tiers and float precision are frozen in
_stability_constants.py. Do not change SPATIAL_ROUND_PRECISION or
BLOCK_TYPE_SORT_PRIORITY inline here; change them there with a schema bump.
"""

from typing import List, Tuple
import logging
from ..schema import Block, OrderingMetadata, BlockType
from .._stability_constants import (
    SPATIAL_ROUND_PRECISION,
    BLOCK_TYPE_SORT_PRIORITY,
    BLOCK_ID_HEX_LENGTH,
)

logger = logging.getLogger(__name__)


class OrderingValidator:
    """Validates Docling order against spatial order"""

    # Aliases pointing to frozen constants — do not override locally
    ROUND_PRECISION = SPATIAL_ROUND_PRECISION
    BLOCK_TYPE_PRIORITY = {BlockType(k): v for k, v in BLOCK_TYPE_SORT_PRIORITY.items()}

    def __init__(self):
        pass

    def compute_spatial_order(self, blocks: List[Block]) -> List[Tuple[Block, int]]:
        """
        Compute spatial reading order from bounding boxes.

        DETERMINISTIC SORTING ALGORITHM (EXPLICIT SPECIFICATION):
        1. Primary key: page_number (ascending)
        2. Secondary key: top position y0 (ascending, rounded to 4 decimals)
        3. Tertiary key: left position x0 (ascending, rounded to 4 decimals)
        4. Quaternary key: block_type priority (predefined order)
        5. Quinary key: original Docling order (final tiebreaker)

        This 5-tier sorting guarantees:
        - Deterministic ordering across Python versions
        - Stable handling of floating-point coordinates
        - Consistent behavior for overlapping blocks
        - Reproducible results across runs
        """
        blocks_with_bbox = [b for b in blocks if b.bbox is not None]
        blocks_without_bbox = [b for b in blocks if b.bbox is None]

        if not blocks_with_bbox:
            return [(b, i) for i, b in enumerate(blocks)]

        # EXPLICIT DETERMINISTIC SORT KEY
        def sort_key(block: Block):
            y = round(block.bbox.y0, self.ROUND_PRECISION)  # 4 decimals
            x = round(block.bbox.x0, self.ROUND_PRECISION)  # 4 decimals
            type_priority = self.BLOCK_TYPE_PRIORITY.get(block.type, 99)

            return (
                block.page_number,  # 1. Page (ascending)
                y,  # 2. Top (ascending, rounded)
                x,  # 3. Left (ascending, rounded)
                type_priority,  # 4. Block type priority
                block.order,  # 5. Original Docling order (final tiebreaker)
            )

        sorted_blocks = sorted(blocks_with_bbox, key=sort_key)

        result = [(b, i) for i, b in enumerate(sorted_blocks)]
        result.extend([(b, len(sorted_blocks) + i) for i, b in enumerate(blocks_without_bbox)])

        return result

    def validate_and_annotate(self, blocks: List[Block]) -> List[Block]:
        """
        Validate ordering and add OrderingMetadata.

        IMPORTANT: Docling order (block.order) remains CANONICAL.
        This method only validates and logs discrepancies - it does NOT reorder.

        Logs warnings if discrepancies exist but does NOT fail pipeline.
        Infrastructure should surface anomalies, not mask them.
        """
        spatial_ordering = self.compute_spatial_order(blocks)
        spatial_map = {block.block_id: spatial_order for block, spatial_order in spatial_ordering}

        discrepancies = []
        for block in blocks:
            docling_order = block.order
            spatial_order = spatial_map.get(block.block_id)

            ordering_meta = OrderingMetadata(
                docling_order=docling_order,
                spatial_order=spatial_order,
                order_discrepancy=(spatial_order is not None and spatial_order != docling_order),
            )
            block.ordering_metadata = ordering_meta

            if ordering_meta.order_discrepancy:
                discrepancies.append(
                    {
                        "block_id": block.block_id[:BLOCK_ID_HEX_LENGTH],
                        "docling_order": docling_order,
                        "spatial_order": spatial_order,
                        "content": block.content[:30],
                    }
                )

        if discrepancies:
            logger.warning(
                f"ORDERING VALIDATION FAILED: {len(discrepancies)} discrepancies "
                f"between Docling and spatial order. Docling order remains canonical."
            )
            # Log first few discrepancies for debugging
            for disc in discrepancies[:3]:
                logger.debug(f"  Order mismatch: {disc}")
        else:
            logger.info("Ordering validation passed: Docling matches spatial order")

        return blocks
