"""
HomographyMatrix Value Object.

Represents a 3x3 homography transformation matrix.
This is a Domain object and MUST NOT import any external libraries.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class HomographyMatrix:
    """
    Immutable Value Object representing a 3x3 homography matrix.

    Used to transform points from pixel space to pitch space.
    The matrix is stored as a tuple of tuples for immutability.
    """

    matrix: Tuple[Tuple[float, float, float], ...]

    def __post_init__(self):
        """Convert list input to tuple for immutability."""
        if isinstance(self.matrix, list):
            # Use object.__setattr__ to bypass frozen
            object.__setattr__(
                self,
                "matrix",
                tuple(tuple(row) for row in self.matrix)
            )

    @classmethod
    def identity(cls) -> "HomographyMatrix":
        """Create an identity homography matrix."""
        return cls(
            matrix=(
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.0, 0.0, 1.0),
            )
        )

    def transform_point(self, x: float, y: float) -> Tuple[float, float]:
        """
        Transform a point using this homography.

        Args:
            x: Source X coordinate (pixel).
            y: Source Y coordinate (pixel).

        Returns:
            Tuple of (transformed_x, transformed_y) in pitch space.
        """
        H = self.matrix
        # Homogeneous coordinates
        w = H[2][0] * x + H[2][1] * y + H[2][2]
        if w == 0:
            w = 1e-10  # Avoid division by zero

        new_x = (H[0][0] * x + H[0][1] * y + H[0][2]) / w
        new_y = (H[1][0] * x + H[1][1] * y + H[1][2]) / w

        return (new_x, new_y)

    def __repr__(self) -> str:
        return f"HomographyMatrix(3x3)"
