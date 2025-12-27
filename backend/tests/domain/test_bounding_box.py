"""
TDD Tests for BoundingBox Value Object.

Tests the bounding box data structure for detection results.
"""

import pytest
from src.domain.value_objects.bounding_box import BoundingBox


class TestBoundingBox:
    """Test BoundingBox value object."""

    def test_create_bounding_box(self):
        """Should create a BoundingBox with all required fields."""
        bbox = BoundingBox(
            x1=100.0,
            y1=200.0,
            x2=150.0,
            y2=300.0,
            confidence=0.95,
            class_id=0,
        )
        assert bbox.x1 == 100.0
        assert bbox.y1 == 200.0
        assert bbox.x2 == 150.0
        assert bbox.y2 == 300.0
        assert bbox.confidence == 0.95
        assert bbox.class_id == 0

    def test_bounding_box_center(self):
        """Should calculate center point correctly."""
        bbox = BoundingBox(
            x1=100.0,
            y1=200.0,
            x2=200.0,
            y2=400.0,
            confidence=0.9,
            class_id=0,
        )
        cx, cy = bbox.center
        assert cx == 150.0
        assert cy == 300.0

    def test_bounding_box_width_height(self):
        """Should calculate width and height correctly."""
        bbox = BoundingBox(
            x1=100.0,
            y1=200.0,
            x2=200.0,
            y2=400.0,
            confidence=0.9,
            class_id=0,
        )
        assert bbox.width == 100.0
        assert bbox.height == 200.0

    def test_bounding_box_is_immutable(self):
        """BoundingBox should be immutable (frozen dataclass)."""
        bbox = BoundingBox(
            x1=100.0, y1=200.0, x2=150.0, y2=300.0, confidence=0.95, class_id=0
        )
        with pytest.raises(AttributeError):
            bbox.x1 = 50.0
