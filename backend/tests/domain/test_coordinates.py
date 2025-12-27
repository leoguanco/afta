"""
TDD Tests for Coordinates Value Object.

Tests the coordinate transformation logic:
- StatsBomb (120x80) -> Metric (105x68)
- Metrica (0-1) -> Metric (105x68)
"""

import pytest
from src.domain.value_objects.coordinates import Coordinates


class TestCoordinatesFromStatsBomb:
    """Test StatsBomb coordinate transformation."""

    def test_center_point(self):
        """StatsBomb (60, 40) should map to Metric (52.5, 34)."""
        coords = Coordinates.from_statsbomb(60, 40)
        assert coords.x == pytest.approx(52.5)
        assert coords.y == pytest.approx(34.0)

    def test_origin(self):
        """StatsBomb (0, 0) should map to Metric (0, 0)."""
        coords = Coordinates.from_statsbomb(0, 0)
        assert coords.x == 0.0
        assert coords.y == 0.0

    def test_max_corner(self):
        """StatsBomb (120, 80) should map to Metric (105, 68)."""
        coords = Coordinates.from_statsbomb(120, 80)
        assert coords.x == pytest.approx(105.0)
        assert coords.y == pytest.approx(68.0)


class TestCoordinatesFromMetrica:
    """Test Metrica coordinate transformation."""

    def test_center_point(self):
        """Metrica (0.5, 0.5) should map to Metric (52.5, 34)."""
        coords = Coordinates.from_metrica(0.5, 0.5)
        assert coords.x == pytest.approx(52.5)
        assert coords.y == pytest.approx(34.0)

    def test_origin(self):
        """Metrica (0, 0) should map to Metric (0, 0)."""
        coords = Coordinates.from_metrica(0, 0)
        assert coords.x == 0.0
        assert coords.y == 0.0

    def test_max_corner(self):
        """Metrica (1, 1) should map to Metric (105, 68)."""
        coords = Coordinates.from_metrica(1, 1)
        assert coords.x == pytest.approx(105.0)
        assert coords.y == pytest.approx(68.0)


class TestCoordinatesImmutability:
    """Test that Coordinates is immutable (frozen dataclass)."""

    def test_cannot_modify_x(self):
        """Attempting to modify x should raise an error."""
        coords = Coordinates(x=10.0, y=20.0)
        with pytest.raises(AttributeError):
            coords.x = 50.0

    def test_cannot_modify_y(self):
        """Attempting to modify y should raise an error."""
        coords = Coordinates(x=10.0, y=20.0)
        with pytest.raises(AttributeError):
            coords.y = 50.0
