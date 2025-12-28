"""
Expected Threat (xT) Grid Value Object.

xT is a model that assigns a value to every location on the pitch,
representing the probability of scoring within the next N actions.

Based on Karun Singh's original xT model.
"""
from dataclasses import dataclass, field
from typing import Tuple
import numpy as np


# Pre-computed xT values for a 12x8 grid
# Values represent probability of scoring from each zone
# Source: Adapted from Karun Singh's xT model
DEFAULT_XT_GRID = np.array([
    [0.00638, 0.00779, 0.00844, 0.00977, 0.01199, 0.01438, 0.01678, 0.02332],
    [0.00750, 0.00878, 0.00982, 0.01155, 0.01465, 0.01846, 0.02284, 0.03366],
    [0.00835, 0.00969, 0.01094, 0.01319, 0.01756, 0.02398, 0.03256, 0.05161],
    [0.00882, 0.01022, 0.01164, 0.01432, 0.01990, 0.02957, 0.04558, 0.08059],
    [0.00878, 0.01026, 0.01183, 0.01480, 0.02116, 0.03305, 0.05593, 0.11640],
    [0.00864, 0.01016, 0.01179, 0.01489, 0.02162, 0.03475, 0.06116, 0.13681],
    [0.00864, 0.01016, 0.01179, 0.01489, 0.02162, 0.03475, 0.06116, 0.13681],
    [0.00878, 0.01026, 0.01183, 0.01480, 0.02116, 0.03305, 0.05593, 0.11640],
    [0.00882, 0.01022, 0.01164, 0.01432, 0.01990, 0.02957, 0.04558, 0.08059],
    [0.00835, 0.00969, 0.01094, 0.01319, 0.01756, 0.02398, 0.03256, 0.05161],
    [0.00750, 0.00878, 0.00982, 0.01155, 0.01465, 0.01846, 0.02284, 0.03366],
    [0.00638, 0.00779, 0.00844, 0.00977, 0.01199, 0.01438, 0.01678, 0.02332],
]).T  # Transpose so rows are y (0-7) and cols are x (0-11)


@dataclass(frozen=True)
class ExpectedThreatGrid:
    """
    Expected Threat (xT) Grid Value Object.
    
    Maps pitch locations to probability of scoring.
    The grid divides the pitch into 12x8 zones.
    
    Standard pitch dimensions: 105m x 68m
    
    Attributes:
        grid: 2D numpy array of xT values (8 rows x 12 cols)
        width: Number of horizontal zones (default 12)
        height: Number of vertical zones (default 8)
        pitch_length: Standard pitch length in meters
        pitch_width: Standard pitch width in meters
    """
    grid: np.ndarray = field(default_factory=lambda: DEFAULT_XT_GRID.copy())
    width: int = 12
    height: int = 8
    pitch_length: float = 105.0
    pitch_width: float = 68.0
    
    def get_threat(self, zone_x: int, zone_y: int) -> float:
        """
        Get xT value for a specific zone.
        
        Args:
            zone_x: Horizontal zone (0-11, left to right)
            zone_y: Vertical zone (0-7, bottom to top)
            
        Returns:
            xT probability value for the zone
        """
        # Clamp to valid range
        zone_x = max(0, min(zone_x, self.width - 1))
        zone_y = max(0, min(zone_y, self.height - 1))
        
        return float(self.grid[zone_y, zone_x])
    
    def pitch_to_zone(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert pitch coordinates to zone indices.
        
        Args:
            x: Pitch x coordinate (0-105m)
            y: Pitch y coordinate (0-68m)
            
        Returns:
            Tuple of (zone_x, zone_y) indices
        """
        zone_x = int((x / self.pitch_length) * self.width)
        zone_y = int((y / self.pitch_width) * self.height)
        
        # Clamp to valid range
        zone_x = max(0, min(zone_x, self.width - 1))
        zone_y = max(0, min(zone_y, self.height - 1))
        
        return zone_x, zone_y
    
    def get_threat_at_pitch_location(self, x: float, y: float) -> float:
        """
        Get xT value at a pitch coordinate.
        
        Args:
            x: Pitch x coordinate (0-105m)
            y: Pitch y coordinate (0-68m)
            
        Returns:
            xT probability value
        """
        zone_x, zone_y = self.pitch_to_zone(x, y)
        return self.get_threat(zone_x, zone_y)
    
    def calculate_xt_change(
        self, 
        from_x: float, 
        from_y: float, 
        to_x: float, 
        to_y: float
    ) -> float:
        """
        Calculate xT gained or lost for an action (pass, carry, dribble).
        
        Args:
            from_x: Starting x coordinate
            from_y: Starting y coordinate
            to_x: Ending x coordinate
            to_y: Ending y coordinate
            
        Returns:
            Positive value = xT gained, negative = xT lost
        """
        start_xt = self.get_threat_at_pitch_location(from_x, from_y)
        end_xt = self.get_threat_at_pitch_location(to_x, to_y)
        
        return end_xt - start_xt
    
    def __hash__(self):
        return hash((self.width, self.height, self.pitch_length, self.pitch_width))
