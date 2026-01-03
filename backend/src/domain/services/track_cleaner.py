"""
Track Cleaner - Domain Service

Removes "ghost" tracks and merges fragmented detections.
Addresses "900 players" issue caused by false positives and track ID resets.

This is a Domain service and MUST NOT import external libraries.
"""
from dataclasses import dataclass
from typing import List, Dict, Set
from collections import defaultdict

from src.domain.services.trajectory_smoother import TrajectoryPoint


@dataclass
class CleaningConfig:
    """Configuration for track cleaning."""
    min_track_duration_frames: int = 15  # Minimum frames for valid track (~0.5s @ 30fps)
    merge_distance_threshold: float = 2.0  # Meters - max distance for merging
    merge_time_gap_frames: int = 10  # Max frames between track end and start for merge


class TrackCleaner:
    """
    Domain service for cleaning tracking data.
    
    Removes ghost/short tracks and merges fragmented detections.
    """
    
    def __init__(self, config: CleaningConfig = None):
        """
        Initialize cleaner.
        
        Args:
            config: Cleaning configuration
        """
        self.config = config or CleaningConfig()
    
    def clean_tracks(self, trajectories: List[TrajectoryPoint]) -> List[TrajectoryPoint]:
        """
        Clean tracking data by removing ghosts and merging fragments.
        
        Args:
            trajectories: Raw tracking points
            
        Returns:
            Cleaned tracking points with updated object_ids
        """
        if not trajectories:
            return []
        
        # Group by object_id
        by_object = self._group_by_object(trajectories)
        
        # Step 1: Remove short tracks (ghosts)
        valid_tracks = self._remove_short_tracks(by_object)
        
        # Step 2: Merge fragmented tracks
        merged_tracks = self._merge_fragments(valid_tracks)
        
        # Step 3: Flatten and reassign IDs
        return self._flatten_with_new_ids(merged_tracks)
    
    def _group_by_object(
        self, 
        trajectories: List[TrajectoryPoint]
    ) -> Dict[int, List[TrajectoryPoint]]:
        """Group trajectory points by object_id."""
        by_object: Dict[int, List[TrajectoryPoint]] = defaultdict(list)
        for point in trajectories:
            by_object[point.object_id].append(point)
        
        # Sort each track by frame_id
        for object_id in by_object:
            by_object[object_id].sort(key=lambda p: p.frame_id)
        
        return dict(by_object)
    
    def _remove_short_tracks(
        self, 
        by_object: Dict[int, List[TrajectoryPoint]]
    ) -> Dict[int, List[TrajectoryPoint]]:
        """Remove tracks shorter than minimum duration."""
        valid_tracks = {}
        
        for object_id, points in by_object.items():
            if len(points) >= self.config.min_track_duration_frames:
                valid_tracks[object_id] = points
        
        return valid_tracks
    
    def _merge_fragments(
        self, 
        tracks: Dict[int, List[TrajectoryPoint]]
    ) -> List[List[TrajectoryPoint]]:
        """
        Merge fragmented tracks that likely belong to same player.
        
        Uses spatial proximity at track end/start to determine matches.
        """
        if not tracks:
            return []
        
        # Convert to list of tracks for easier processing
        track_list = list(tracks.values())
        merged: List[List[TrajectoryPoint]] = []
        merged_indices: Set[int] = set()
        
        for i, track_a in enumerate(track_list):
            if i in merged_indices:
                continue
            
            current_track = list(track_a)
            merged_indices.add(i)
            
            # Look for tracks to merge
            for j, track_b in enumerate(track_list):
                if j in merged_indices or i == j:
                    continue
                
                if self._should_merge(current_track, track_b):
                    current_track.extend(track_b)
                    current_track.sort(key=lambda p: p.frame_id)
                    merged_indices.add(j)
            
            merged.append(current_track)
        
        return merged
    
    def _should_merge(
        self, 
        track_a: List[TrajectoryPoint], 
        track_b: List[TrajectoryPoint]
    ) -> bool:
        """
        Determine if two tracks should be merged.
        
        Checks if track_b starts shortly after track_a ends,
        and if the positions are close enough.
        """
        if not track_a or not track_b:
            return False
        
        # Get end of track_a and start of track_b
        end_a = track_a[-1]
        start_b = track_b[0]
        
        # Check frame gap
        frame_gap = start_b.frame_id - end_a.frame_id
        if frame_gap < 0 or frame_gap > self.config.merge_time_gap_frames:
            return False
        
        # Check spatial distance
        distance = ((end_a.x - start_b.x) ** 2 + (end_a.y - start_b.y) ** 2) ** 0.5
        if distance > self.config.merge_distance_threshold:
            return False
        
        # Check object type consistency
        if end_a.object_type != start_b.object_type:
            return False
        
        return True
    
    def _flatten_with_new_ids(
        self, 
        merged_tracks: List[List[TrajectoryPoint]]
    ) -> List[TrajectoryPoint]:
        """Flatten merged tracks into single list with reassigned IDs."""
        result = []
        
        for new_id, track in enumerate(merged_tracks, start=1):
            for point in track:
                new_point = TrajectoryPoint(
                    frame_id=point.frame_id,
                    object_id=new_id,
                    x=point.x,
                    y=point.y,
                    timestamp=point.timestamp,
                    object_type=point.object_type,
                    confidence=point.confidence
                )
                result.append(new_point)
        
        return result
