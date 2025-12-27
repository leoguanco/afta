"""Domain Value Objects package."""

from .coordinates import Coordinates
from .trajectory import Trajectory, ObjectType
from .bounding_box import BoundingBox

__all__ = ["Coordinates", "Trajectory", "ObjectType", "BoundingBox"]
