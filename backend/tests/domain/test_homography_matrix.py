"""
TDD Tests for HomographyMatrix Value Object.

Tests the homography matrix data structure.
"""

import pytest
from src.domain.value_objects.homography_matrix import HomographyMatrix


class TestHomographyMatrix:
    """Test HomographyMatrix value object."""

    def test_create_identity_matrix(self):
        """Should create an identity homography matrix."""
        H = HomographyMatrix.identity()
        assert H.matrix[0][0] == 1.0
        assert H.matrix[1][1] == 1.0
        assert H.matrix[2][2] == 1.0
        assert H.matrix[0][1] == 0.0

    def test_create_from_list(self):
        """Should create matrix from 3x3 list."""
        data = [
            [1.0, 0.0, 10.0],
            [0.0, 1.0, 20.0],
            [0.0, 0.0, 1.0],
        ]
        H = HomographyMatrix(matrix=data)
        assert H.matrix[0][2] == 10.0
        assert H.matrix[1][2] == 20.0

    def test_transform_point(self):
        """Should transform a point using the homography."""
        # Translation matrix: shift x by 10, y by 20
        data = [
            [1.0, 0.0, 10.0],
            [0.0, 1.0, 20.0],
            [0.0, 0.0, 1.0],
        ]
        H = HomographyMatrix(matrix=data)
        new_x, new_y = H.transform_point(5.0, 5.0)
        assert new_x == pytest.approx(15.0)
        assert new_y == pytest.approx(25.0)

    def test_matrix_is_immutable(self):
        """HomographyMatrix should be immutable."""
        H = HomographyMatrix.identity()
        with pytest.raises(TypeError):
            H.matrix[0][0] = 999.0  # Should fail on tuple
