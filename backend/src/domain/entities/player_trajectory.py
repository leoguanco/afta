"""
PlayerTrajectory Entity - Domain Layer

Rich entity representing a player's movement over time with embedded behavior.
"""
from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class FramePosition:
    """Value object for position data."""
    frame_id: int
    x: float  # meters
    y: float  # meters
    timestamp: float  # seconds


@dataclass
class PhysicalMetrics:
    """Value object for calculated physical metrics."""
    total_distance: float  # km
    max_speed: float  # km/h
    sprint_count: int
    avg_speed: float  # km/h


@dataclass
class Sprint:
    """Value object representing a sprint event."""
    start_frame: int
    end_frame: int
    max_speed: float  # km/h
    distance: float  # meters


class PlayerTrajectory:
    """
    Rich domain entity representing a player's trajectory over time.
    
    Encapsulates player movement data and provides methods to calculate
    physical metrics (velocity, distance, sprints).
    """
    
    def __init__(
        self,
        player_id: str,
        frames: List[FramePosition],
        fps: float = 25.0,
        sprint_threshold: float = 25.0
    ):
        """
        Initialize player trajectory.
        
        Args:
            player_id: Player identifier
            frames: List of frame positions (should be sorted by frame_id)
            fps: Frames per second
            sprint_threshold: Speed threshold for sprint detection (km/h)
        """
        self.player_id = player_id
        self.frames = sorted(frames, key=lambda f: f.frame_id)
        self.fps = fps
        self.sprint_threshold = sprint_threshold
        
        # Cache for expensive calculations
        self._velocities: np.ndarray | None = None
        self._metrics: PhysicalMetrics | None = None
    
    def calculate_physical_metrics(self) -> PhysicalMetrics:
        """
        Calculate all physical metrics for this trajectory.
        
        Returns:
            PhysicalMetrics with distance, speed, and sprint data
        """
        if self._metrics is not None:
            return self._metrics
        
        if not self.frames:
            return PhysicalMetrics(
                total_distance=0.0,
                max_speed=0.0,
                sprint_count=0,
                avg_speed=0.0
            )
        
        velocities = self._get_velocities()
        
        # Total distance
        distances = velocities / self.fps
        total_distance_km = np.sum(distances) / 1000.0
        
        # Speed metrics
        max_speed_kmh = np.max(velocities) * 3.6
        avg_speed_kmh = np.mean(velocities) * 3.6
        
        # Sprint count
        sprint_count = len(self.detect_sprints())
        
        self._metrics = PhysicalMetrics(
            total_distance=total_distance_km,
            max_speed=max_speed_kmh,
            sprint_count=sprint_count,
            avg_speed=avg_speed_kmh
        )
        
        return self._metrics
    
    def detect_sprints(self) -> List[Sprint]:
        """
        Detect sprint events where velocity exceeds threshold.
        
        Returns:
            List of Sprint events
        """
        velocities = self._get_velocities()
        threshold_ms = self.sprint_threshold / 3.6
        
        is_sprinting = velocities > threshold_ms
        sprints = []
        
        in_sprint = False
        sprint_start = 0
        sprint_max_speed = 0.0
        sprint_distance = 0.0
        
        for i, sprinting in enumerate(is_sprinting):
            if sprinting and not in_sprint:
                # Sprint start
                in_sprint = True
                sprint_start = i
                sprint_max_speed = velocities[i] * 3.6
                sprint_distance = 0.0
            elif sprinting and in_sprint:
                # Continue sprint
                sprint_max_speed = max(sprint_max_speed, velocities[i] * 3.6)
                sprint_distance += velocities[i] / self.fps
            elif not sprinting and in_sprint:
                # Sprint end
                in_sprint = False
                sprints.append(Sprint(
                    start_frame=self.frames[sprint_start].frame_id,
                    end_frame=self.frames[i-1].frame_id,
                    max_speed=sprint_max_speed,
                    distance=sprint_distance
                ))
        
        # Handle sprint that continues to end
        if in_sprint:
            sprints.append(Sprint(
                start_frame=self.frames[sprint_start].frame_id,
                end_frame=self.frames[-1].frame_id,
                max_speed=sprint_max_speed,
                distance=sprint_distance
            ))
        
        return sprints
    
    def _get_velocities(self) -> np.ndarray:
        """
        Calculate and cache velocity vector.
        
        Returns:
            Array of velocities (m/s)
        """
        if self._velocities is not None:
            return self._velocities
        
        x = np.array([f.x for f in self.frames])
        y = np.array([f.y for f in self.frames])
        timestamps = np.array([f.timestamp for f in self.frames])
        
        # Calculate displacement
        dx = np.diff(x)
        dy = np.diff(y)
        dt = np.diff(timestamps)
        dt = np.where(dt == 0, 1e-6, dt)
        
        # Velocity magnitude
        velocity = np.sqrt(dx**2 + dy**2) / dt
        
        # Smooth using Savitzky-Golay filter (better preserves signal shape)
        velocity_smoothed = self._smooth_signal_savgol(velocity, window_length=11, polyorder=3)
        
        # Pad to match input size
        velocity_smoothed = np.append(velocity_smoothed, velocity_smoothed[-1])
        
        self._velocities = velocity_smoothed
        return self._velocities
    
    def _smooth_signal_savgol(
        self, 
        signal: np.ndarray, 
        window_length: int = 11, 
        polyorder: int = 3
    ) -> np.ndarray:
        """
        Smooth signal using Savitzky-Golay filter.
        
        Savitzky-Golay is preferred for velocity data because it:
        - Preserves local maxima/minima (important for sprint detection)
        - Maintains signal shape during acceleration/deceleration
        - Has better frequency response than moving average
        
        Args:
            signal: Input signal array
            window_length: Must be odd, larger = smoother (default 11 = ~0.4s at 25fps)
            polyorder: Polynomial order (lower = smoother, default 3)
            
        Returns:
            Smoothed signal array
        """
        from scipy.signal import savgol_filter
        
        # Window length must be odd and >= polyorder + 2
        min_length = polyorder + 2
        if len(signal) < min_length:
            # Fallback to simple smoothing for very short signals
            return self._smooth_signal_moving_avg(signal, window=3)
        
        # Ensure window_length is valid
        actual_window = min(window_length, len(signal))
        if actual_window % 2 == 0:
            actual_window -= 1  # Make odd
        actual_window = max(actual_window, polyorder + 2)
        
        return savgol_filter(signal, actual_window, polyorder)
    
    def _smooth_signal_moving_avg(self, signal: np.ndarray, window: int = 5) -> np.ndarray:
        """Fallback: Smooth signal using moving average."""
        if len(signal) < window:
            return signal
        
        kernel = np.ones(window) / window
        return np.convolve(signal, kernel, mode='same')
    
    def flag_outliers(self, max_speed_kmh: float = 36.0) -> List[int]:
        """
        Flag frames with unrealistic speed values.
        
        Per spec: Speed > 36km/h should be flagged or clipped.
        Usain Bolt's max is ~44km/h, so 36km/h is a reasonable threshold
        for sustained football player movement.
        
        Args:
            max_speed_kmh: Maximum realistic speed in km/h
            
        Returns:
            List of frame IDs with outlier speeds
        """
        velocities = self._get_velocities()
        threshold_ms = max_speed_kmh / 3.6
        
        outlier_frames = []
        for i, velocity in enumerate(velocities):
            if velocity > threshold_ms:
                outlier_frames.append(self.frames[i].frame_id)
        
        return outlier_frames
    
    def clip_outliers(self, max_speed_kmh: float = 36.0) -> None:
        """
        Clip unrealistic speed values by adjusting positions.
        
        This modifies the trajectory in-place to limit maximum
        displacement between frames.
        
        Args:
            max_speed_kmh: Maximum speed to allow
        """
        max_displacement = (max_speed_kmh / 3.6) / self.fps
        
        for i in range(1, len(self.frames)):
            prev = self.frames[i-1]
            curr = self.frames[i]
            
            dx = curr.x - prev.x
            dy = curr.y - prev.y
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance > max_displacement and distance > 0:
                # Scale down movement to max allowed
                scale = max_displacement / distance
                # Create new frame with clipped position
                # Note: frames list needs to be mutable for this
                self.frames[i] = TrajectoryFrame(
                    frame_id=curr.frame_id,
                    x=prev.x + dx * scale,
                    y=prev.y + dy * scale,
                    timestamp=curr.timestamp
                )
        
        # Invalidate cached calculations
        self._velocities = None
        self._metrics = None
    
    def __repr__(self) -> str:
        return f"PlayerTrajectory(player_id={self.player_id}, frames={len(self.frames)})"

