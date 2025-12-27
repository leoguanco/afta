"""
Physics Service - Domain Layer

Calculates physical metrics (velocity, distance, sprints) from tracking data.
Uses numpy for vectorized operations per spec constraints.
"""
from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class FramePosition:
    """Position data for a single frame."""
    frame_id: int
    player_id: str
    x: float  # meters
    y: float  # meters
    timestamp: float  # seconds


@dataclass
class PhysicalMetrics:
    """Physical metrics for a player."""
    player_id: str
    total_distance: float  # km
    max_speed: float  # km/h
    sprint_count: int  # number of sprints >25km/h
    avg_speed: float  # km/h


class PhysicsService:
    """
    Domain service for calculating physical metrics.
    Pure domain logic using numpy for vectorization.
    """
    
    def __init__(self, fps: float = 25.0, sprint_threshold: float = 25.0):
        """
        Initialize physics service.
        
        Args:
            fps: Frames per second of tracking data
            sprint_threshold: Speed threshold for sprint detection (km/h)
        """
        self.fps = fps
        self.sprint_threshold = sprint_threshold
    
    def calculate_metrics(self, frames: List[FramePosition]) -> PhysicalMetrics:
        """
        Calculate physical metrics from frame data.
        
        Args:
            frames: List of frame positions for a single player
            
        Returns:
            PhysicalMetrics with calculated values
        """
        if not frames:
            return PhysicalMetrics(
                player_id="",
                total_distance=0.0,
                max_speed=0.0,
                sprint_count=0,
                avg_speed=0.0
            )
        
        player_id = frames[0].player_id
        
        # Convert to numpy arrays for vectorization
        x = np.array([f.x for f in frames])
        y = np.array([f.y for f in frames])
        timestamps = np.array([f.timestamp for f in frames])
        
        # Calculate velocities (smoothed)
        velocities = self._calculate_velocity(x, y, timestamps)
        
        # Total distance (integrate velocity)
        distances = velocities / self.fps  # distance per frame
        total_distance_m = np.sum(distances)
        total_distance_km = total_distance_m / 1000.0
        
        # Max speed
        max_speed_ms = np.max(velocities)
        max_speed_kmh = max_speed_ms * 3.6
        
        # Average speed
        avg_speed_ms = np.mean(velocities)
        avg_speed_kmh = avg_speed_ms * 3.6
        
        # Sprint detection
        sprint_count = self._detect_sprints(velocities)
        
        return PhysicalMetrics(
            player_id=player_id,
            total_distance=total_distance_km,
            max_speed=max_speed_kmh,
            sprint_count=sprint_count,
            avg_speed=avg_speed_kmh
        )
    
    def _calculate_velocity(
        self, 
        x: np.ndarray, 
        y: np.ndarray, 
        timestamps: np.ndarray
    ) -> np.ndarray:
        """
        Calculate velocity using central difference with smoothing.
        
        Args:
            x: X coordinates (meters)
            y: Y coordinates (meters)
            timestamps: Frame timestamps (seconds)
            
        Returns:
            Array of velocities (m/s)
        """
        # Calculate displacement
        dx = np.diff(x)
        dy = np.diff(y)
        dt = np.diff(timestamps)
        
        # Avoid division by zero
        dt = np.where(dt == 0, 1e-6, dt)
        
        # Velocity magnitude
        velocity = np.sqrt(dx**2 + dy**2) / dt
        
        # Smooth using simple moving average (Savitzky-Golay approximation)
        velocity_smoothed = self._smooth_signal(velocity, window=5)
        
        # Pad to match input size
        velocity_smoothed = np.append(velocity_smoothed, velocity_smoothed[-1])
        
        return velocity_smoothed
    
    def _smooth_signal(self, signal: np.ndarray, window: int = 5) -> np.ndarray:
        """
        Smooth signal using moving average.
        
        Args:
            signal: Input signal
            window: Window size for smoothing
            
        Returns:
            Smoothed signal
        """
        if len(signal) < window:
            return signal
        
        # Simple moving average
        kernel = np.ones(window) / window
        smoothed = np.convolve(signal, kernel, mode='same')
        
        return smoothed
    
    def _detect_sprints(self, velocities: np.ndarray) -> int:
        """
        Detect sprint events (velocity > threshold).
        
        Args:
            velocities: Array of velocities (m/s)
            
        Returns:
            Number of sprint events
        """
        threshold_ms = self.sprint_threshold / 3.6  # Convert km/h to m/s
        
        # Find where velocity exceeds threshold
        is_sprinting = velocities > threshold_ms
        
        # Count transitions from not-sprinting to sprinting
        sprint_starts = np.diff(is_sprinting.astype(int)) > 0
        sprint_count = np.sum(sprint_starts)
        
        # If starts sprinting in first frame
        if is_sprinting[0]:
            sprint_count += 1
        
        return int(sprint_count)
