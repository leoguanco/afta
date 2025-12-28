"""
Metrica Sports Adapter - Infrastructure Layer

Implements MatchRepository for Metrica Sports CSV data.
Transforms Metrica coordinates (0-1) to standard pitch (105x68m).
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.domain.entities.player_trajectory import PlayerTrajectory, FramePosition
from src.domain.ports.match_repository import MatchRepository


@dataclass
class MetricaTrackingFrame:
    """Value object for a single tracking frame."""
    period: int
    frame: int
    timestamp: float
    players: Dict[str, Optional[Tuple[float, float]]]
    ball: Optional[Tuple[float, float]]


class MetricaAdapter(MatchRepository):
    """
    Adapter for Metrica Sports tracking data.
    
    Metrica CSV format:
    - Coordinates are normalized 0-1 (both x and y)
    - Players are in pairs of columns: PlayerN (x), PlayerN (y)
    - Ball position in last two columns
    
    Transforms to standard 105m x 68m pitch coordinates.
    """
    
    PITCH_LENGTH = 105.0  # meters
    PITCH_WIDTH = 68.0    # meters
    
    def __init__(self, pitch_length: float = 105.0, pitch_width: float = 68.0):
        """
        Initialize adapter.
        
        Args:
            pitch_length: Standard pitch length (default 105m)
            pitch_width: Standard pitch width (default 68m)
        """
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
    
    def normalize_coordinates(self, metrica_x: float, metrica_y: float) -> Tuple[float, float]:
        """
        Transform Metrica 0-1 coordinates to metric pitch.
        
        Metrica: (0,0) = left corner, (1,1) = right corner
        Metric:  (0,0) = left corner, (105,68) = right corner
        
        Args:
            metrica_x: Metrica x coordinate (0-1)
            metrica_y: Metrica y coordinate (0-1)
            
        Returns:
            Tuple of (pitch_x, pitch_y) in meters
        """
        pitch_x = metrica_x * self.pitch_length
        pitch_y = metrica_y * self.pitch_width
        return pitch_x, pitch_y
    
    def load_tracking_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load and parse Metrica tracking CSV.
        
        Args:
            filepath: Path to tracking CSV file
            
        Returns:
            List of frame dictionaries with player positions
        """
        # Read CSV, skip second header row
        df = pd.read_csv(filepath, header=0, skiprows=[1])
        
        # Find player columns (pairs of x, y)
        player_columns = []
        for i, col in enumerate(df.columns[3:]):  # Skip Period, Frame, Time
            if i % 2 == 0:  # Take only the first of each pair
                player_columns.append(col)
        
        frames = []
        for _, row in df.iterrows():
            players = {}
            
            for player_name in player_columns:
                # Find corresponding columns
                cols = [c for c in df.columns if c.startswith(player_name) or c == player_name]
                if len(cols) >= 2:
                    x_val = row[cols[0]]
                    y_val = row[cols[1]] if len(cols) > 1 else None
                    
                    # Handle NaN/missing data
                    if pd.notna(x_val) and pd.notna(y_val):
                        players[player_name] = (float(x_val), float(y_val))
                    else:
                        players[player_name] = None
            
            # Ball position (last two columns)
            ball_cols = [c for c in df.columns if 'Ball' in c or 'ball' in c]
            ball = None
            if len(ball_cols) >= 2:
                ball_x = row[ball_cols[0]]
                ball_y = row[ball_cols[1]]
                if pd.notna(ball_x) and pd.notna(ball_y):
                    ball = (float(ball_x), float(ball_y))
            
            frames.append({
                "period": int(row.get("Period", 1)),
                "frame": int(row.get("Frame", 0)),
                "timestamp": float(row.get("Time [s]", 0)),
                "players": players,
                "ball": ball
            })
        
        return frames
    
    def create_trajectories(
        self, 
        filepath: str, 
        team_id: str = "home"
    ) -> List[PlayerTrajectory]:
        """
        Create PlayerTrajectory objects from Metrica CSV.
        
        Args:
            filepath: Path to tracking CSV
            team_id: Team identifier for these players
            
        Returns:
            List of PlayerTrajectory entities with normalized coordinates
        """
        frames = self.load_tracking_csv(filepath)
        
        # Collect positions by player
        player_positions: Dict[str, List[FramePosition]] = {}
        
        for frame_data in frames:
            frame_num = frame_data["frame"]
            timestamp = frame_data["timestamp"]
            
            for player_name, position in frame_data["players"].items():
                if position is None:
                    continue
                
                # Normalize coordinates
                metrica_x, metrica_y = position
                pitch_x, pitch_y = self.normalize_coordinates(metrica_x, metrica_y)
                
                if player_name not in player_positions:
                    player_positions[player_name] = []
                
                player_positions[player_name].append(FramePosition(
                    frame=frame_num,
                    timestamp=timestamp,
                    x=pitch_x,
                    y=pitch_y
                ))
        
        # Create trajectories
        trajectories = []
        for player_name, positions in player_positions.items():
            if len(positions) > 0:
                trajectories.append(PlayerTrajectory(
                    player_id=player_name,
                    team_id=team_id,
                    positions=positions
                ))
        
        return trajectories
    
    def get_match_events(self, match_id: str) -> List[Dict[str, Any]]:
        """
        Get match events (not supported for Metrica tracking-only data).
        
        Metrica event data requires separate CSV files.
        This method is a placeholder for the MatchRepository interface.
        """
        return []
    
    def get_match_metadata(self, match_id: str) -> Dict[str, Any]:
        """Get match metadata (placeholder)."""
        return {"match_id": match_id, "source": "metrica"}
