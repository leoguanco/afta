"""
TDD Tests for PhaseSequence entity.
"""
import pytest
from src.domain.entities.phase_sequence import PhaseSequence, FramePhase, PhaseTransition
from src.domain.value_objects.game_phase import GamePhase


class TestPhaseSequence:
    """Test suite for PhaseSequence entity."""

    @pytest.fixture
    def empty_sequence(self):
        """Create an empty sequence."""
        return PhaseSequence(match_id="test_match", team_id="home", fps=25.0)

    @pytest.fixture
    def sequence_with_phases(self):
        """Create a sequence with example phases."""
        seq = PhaseSequence(match_id="test_match", team_id="home", fps=25.0)
        # 100 frames of organized attack (4 seconds)
        for i in range(100):
            seq.add_frame_phase(i, GamePhase.ORGANIZED_ATTACK)
        # 50 frames of transition (2 seconds)
        for i in range(100, 150):
            seq.add_frame_phase(i, GamePhase.TRANSITION_ATK_DEF)
        # 100 frames of organized defense (4 seconds)
        for i in range(150, 250):
            seq.add_frame_phase(i, GamePhase.ORGANIZED_DEFENSE)
        return seq

    def test_add_frame_phase(self, empty_sequence):
        """Should add frames and keep sorted."""
        empty_sequence.add_frame_phase(5, GamePhase.ORGANIZED_ATTACK)
        empty_sequence.add_frame_phase(0, GamePhase.ORGANIZED_DEFENSE)
        empty_sequence.add_frame_phase(10, GamePhase.TRANSITION_ATK_DEF)
        
        assert len(empty_sequence) == 3
        assert empty_sequence.frame_phases[0].frame_id == 0
        assert empty_sequence.frame_phases[1].frame_id == 5
        assert empty_sequence.frame_phases[2].frame_id == 10

    def test_get_phase_at_frame(self, sequence_with_phases):
        """Should return correct phase for frame."""
        assert sequence_with_phases.get_phase_at_frame(0) == GamePhase.ORGANIZED_ATTACK
        assert sequence_with_phases.get_phase_at_frame(99) == GamePhase.ORGANIZED_ATTACK
        assert sequence_with_phases.get_phase_at_frame(100) == GamePhase.TRANSITION_ATK_DEF
        assert sequence_with_phases.get_phase_at_frame(200) == GamePhase.ORGANIZED_DEFENSE

    def test_get_phase_at_missing_frame(self, sequence_with_phases):
        """Should return UNKNOWN for missing frame."""
        assert sequence_with_phases.get_phase_at_frame(999) == GamePhase.UNKNOWN

    def test_calculate_phase_transitions(self, sequence_with_phases):
        """Should detect all transitions."""
        transitions = sequence_with_phases.calculate_phase_transitions()
        
        assert len(transitions) == 2
        # First transition: ORGANIZED_ATTACK -> TRANSITION_ATK_DEF at frame 100
        assert transitions[0].frame_id == 100
        assert transitions[0].from_phase == GamePhase.ORGANIZED_ATTACK
        assert transitions[0].to_phase == GamePhase.TRANSITION_ATK_DEF
        # Second transition: TRANSITION_ATK_DEF -> ORGANIZED_DEFENSE at frame 150
        assert transitions[1].frame_id == 150
        assert transitions[1].from_phase == GamePhase.TRANSITION_ATK_DEF
        assert transitions[1].to_phase == GamePhase.ORGANIZED_DEFENSE

    def test_get_phase_durations(self, sequence_with_phases):
        """Should calculate correct durations."""
        durations = sequence_with_phases.get_phase_durations()
        
        # 100 frames at 25fps = 4 seconds for organized attack
        # 50 frames at 25fps = 2 seconds for transition
        # 100 frames at 25fps = 4 seconds for organized defense
        assert durations[GamePhase.ORGANIZED_ATTACK] == pytest.approx(4.0, abs=0.1)
        assert durations[GamePhase.TRANSITION_ATK_DEF] == pytest.approx(2.0, abs=0.1)
        assert durations[GamePhase.ORGANIZED_DEFENSE] == pytest.approx(4.0, abs=0.1)

    def test_get_phase_percentages(self, sequence_with_phases):
        """Should calculate correct percentages."""
        percentages = sequence_with_phases.get_phase_percentages()
        
        # Total ~10 seconds, attack 4s (40%), transition 2s (20%), defense 4s (40%)
        assert percentages[GamePhase.ORGANIZED_ATTACK] == pytest.approx(40.0, abs=1.0)
        assert percentages[GamePhase.TRANSITION_ATK_DEF] == pytest.approx(20.0, abs=1.0)
        assert percentages[GamePhase.ORGANIZED_DEFENSE] == pytest.approx(40.0, abs=1.0)

    def test_get_dominant_phase(self, sequence_with_phases):
        """Should return most common phase."""
        # Attack and defense are tied, but attack comes first
        dominant = sequence_with_phases.get_dominant_phase()
        assert dominant in (GamePhase.ORGANIZED_ATTACK, GamePhase.ORGANIZED_DEFENSE)

    def test_get_transition_count(self, sequence_with_phases):
        """Should count transitions correctly."""
        assert sequence_with_phases.get_transition_count() == 2

    def test_empty_sequence_handling(self, empty_sequence):
        """Should handle empty sequence gracefully."""
        assert empty_sequence.get_phase_durations()[GamePhase.ORGANIZED_ATTACK] == 0.0
        assert empty_sequence.get_dominant_phase() == GamePhase.UNKNOWN
        assert empty_sequence.get_transition_count() == 0
