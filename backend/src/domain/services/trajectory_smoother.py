"""
Trajectory Smoother - Domain Service

Applies smoothing filters to reduce noise in tracking data.
Addresses "exceptional velocity" issues caused by pixel jitter.

This is a Domain service and MUST NOT import external libraries directly.
The actual filtering is done via a Port that can be implemented with scipy/numpy.
"""
from dataclasses import dataclass
from typing import List, Protocol
from abc import abstractmethod


@dataclass
class TrajectoryPoint:
    """Single point in a trajectory."""
    frame_id: int
    object_id: int
    x: float
    y: float
    timestamp: float
    object_type: str = "player"
    confidence: float = 1.0


class SmoothingPort(Protocol):
    """Port for smoothing algorithm implementation."""
    
    @abstractmethod
    def smooth(self, values: List[float], window_size: int = 5) -> List[float]:
        """Apply smoothing to a sequence of values."""
        ...


class TrajectorySmoother:
    """
    Domain service for smoothing trajectory data.
    
    Uses injected SmoothingPort to avoid framework dependencies.
    """
    
    def __init__(self, smoother: SmoothingPort, window_size: int = 5):
        """
        Initialize smoother.
        
        Args:
            smoother: Implementation of smoothing algorithm
            window_size: Number of frames to consider for smoothing
        """
        self.smoother = smoother
        self.window_size = window_size
    
    def smooth_trajectories(
        self, 
        trajectories: List[TrajectoryPoint]
    ) -> List[TrajectoryPoint]:
        """
        Smooth all trajectories by object_id.
        
        Groups points by object_id, smooths x and y separately,
        then reconstructs the trajectory.
        
        Args:
            trajectories: Raw tracking points
            
        Returns:
            Smoothed tracking points
        """
        if not trajectories:
            return []
        
        # Group by object_id
        by_object: dict = {}
        for point in trajectories:
            if point.object_id not in by_object:
                by_object[point.object_id] = []
            by_object[point.object_id].append(point)
        
        smoothed_trajectories = []
        
        for object_id, points in by_object.items():
            # Sort by frame_id
            points.sort(key=lambda p: p.frame_id)
            
            # Skip if too few points to smooth
            if len(points) < self.window_size:
                smoothed_trajectories.extend(points)
                continue
            
            # Extract x, y sequences
            x_values = [p.x for p in points]
            y_values = [p.y for p in points]
            
            # Apply smoothing
            x_smoothed = self.smoother.smooth(x_values, self.window_size)
            y_smoothed = self.smoother.smooth(y_values, self.window_size)
            
            # Reconstruct points with smoothed coordinates
            for i, point in enumerate(points):
                smoothed_point = TrajectoryPoint(
                    frame_id=point.frame_id,
                    object_id=point.object_id,
                    x=x_smoothed[i],
                    y=y_smoothed[i],
                    timestamp=point.timestamp,
                    object_type=point.object_type,
                    confidence=point.confidence
                )
                smoothed_trajectories.append(smoothed_point)
        
        return smoothed_trajectories
