"""
TDD Tests for Metrica Sports Adapter.

Tests for CSV ingestion and coordinate transformation.
"""
import pytest
import tempfile
import os
from pathlib import Path

from src.infrastructure.adapters.metrica_adapter import MetricaAdapter
from src.domain.entities.match import Match


class TestMetricaAdapter:
    """Test suite for Metrica Sports data ingestion."""

    def test_load_tracking_data_from_csv(self, tmp_path):
        """Should load tracking data from Metrica CSV format."""
        # Given: A Metrica-style tracking CSV
        tracking_csv = tmp_path / "tracking_home.csv"
        tracking_csv.write_text(
            "Period,Frame,Time [s],Player1,Player1,Player2,Player2,Ball,Ball\n"
            ",,,,,,,,\n"  # Header row 2
            "1,1,0.04,0.5,0.5,0.6,0.4,0.5,0.5\n"
            "1,2,0.08,0.52,0.5,0.62,0.4,0.51,0.5\n"
        )
        
        adapter = MetricaAdapter()
        
        # When: Load tracking data
        tracking = adapter.load_tracking_csv(str(tracking_csv))
        
        # Then: Should parse frames and players
        assert len(tracking) == 2  # 2 frames
        assert "Player1" in tracking[0]["players"]

    def test_normalize_coordinates_to_metric_pitch(self):
        """Should transform Metrica 0-1 coordinates to 105x68m pitch."""
        adapter = MetricaAdapter()
        
        # Given: Metrica coordinates (0-1 scale)
        metrica_x = 0.5  # Center
        metrica_y = 0.5  # Center
        
        # When: Normalize to metric
        pitch_x, pitch_y = adapter.normalize_coordinates(metrica_x, metrica_y)
        
        # Then: Should be center of 105x68 pitch
        assert pitch_x == pytest.approx(52.5, abs=0.1)
        assert pitch_y == pytest.approx(34.0, abs=0.1)

    def test_normalize_goal_line_coordinates(self):
        """Goal line should be at x=0 and x=105."""
        adapter = MetricaAdapter()
        
        # Left goal (0,0) → (0, 34)
        x1, y1 = adapter.normalize_coordinates(0.0, 0.5)
        assert x1 == pytest.approx(0.0, abs=0.1)
        
        # Right goal (1,0) → (105, 34)
        x2, y2 = adapter.normalize_coordinates(1.0, 0.5)
        assert x2 == pytest.approx(105.0, abs=0.1)

    def test_create_trajectories_from_tracking(self, tmp_path):
        """Should convert tracking data to Trajectory objects."""
        # Given: Metrica tracking data simulating player movement
        tracking_csv = tmp_path / "tracking.csv"
        # Simulating 10 frames at 25 fps
        lines = [
            "Period,Frame,Time [s],Player1,Player1,Ball,Ball",
            ",,,,,,",  # Second header row
        ]
        for i in range(10):
            t = i * 0.04
            x = 0.3 + (i * 0.01)  # Moving right
            y = 0.5
            lines.append(f"1,{i+1},{t:.2f},{x},{y},{x},{y}")
        
        tracking_csv.write_text("\n".join(lines))
        
        adapter = MetricaAdapter()
        
        # When: Create trajectories
        trajectories = adapter.create_trajectories(str(tracking_csv))
        
        # Then: Should have Player1 trajectory
        assert len(trajectories) >= 1
        player1_traj = [t for t in trajectories if t.player_id == "Player1"]
        assert len(player1_traj) == 1
        assert len(player1_traj[0].positions) == 10

    def test_handle_missing_player_data(self, tmp_path):
        """Should handle NaN values for missing players."""
        tracking_csv = tmp_path / "tracking.csv"
        tracking_csv.write_text(
            "Period,Frame,Time [s],Player1,Player1,Player2,Player2\n"
            ",,,,,,\n"
            "1,1,0.04,0.5,0.5,NaN,NaN\n"  # Player2 missing
            "1,2,0.08,0.5,0.5,0.6,0.4\n"   # Player2 appears
        )
        
        adapter = MetricaAdapter()
        
        # When: Load tracking
        tracking = adapter.load_tracking_csv(str(tracking_csv))
        
        # Then: Should handle missing data gracefully
        assert tracking[0]["players"].get("Player2") is None
        assert tracking[1]["players"]["Player2"] is not None
