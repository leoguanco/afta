"""
TDD Tests for GamePhase value object.
"""
import pytest
from src.domain.value_objects.game_phase import GamePhase


class TestGamePhase:
    """Test suite for GamePhase enum."""

    def test_has_four_main_phases(self):
        """Should have 4 main tactical phases plus UNKNOWN."""
        phases = list(GamePhase)
        assert len(phases) == 5
        assert GamePhase.ORGANIZED_ATTACK in phases
        assert GamePhase.ORGANIZED_DEFENSE in phases
        assert GamePhase.TRANSITION_ATK_DEF in phases
        assert GamePhase.TRANSITION_DEF_ATK in phases
        assert GamePhase.UNKNOWN in phases

    def test_from_string_valid(self):
        """Should convert valid strings to phases."""
        assert GamePhase.from_string("organized_attack") == GamePhase.ORGANIZED_ATTACK
        assert GamePhase.from_string("organized_defense") == GamePhase.ORGANIZED_DEFENSE

    def test_from_string_invalid_returns_unknown(self):
        """Should return UNKNOWN for invalid strings."""
        assert GamePhase.from_string("invalid") == GamePhase.UNKNOWN
        assert GamePhase.from_string("") == GamePhase.UNKNOWN

    def test_is_attacking(self):
        """Should correctly identify attacking phases."""
        assert GamePhase.ORGANIZED_ATTACK.is_attacking() is True
        assert GamePhase.TRANSITION_DEF_ATK.is_attacking() is True
        assert GamePhase.ORGANIZED_DEFENSE.is_attacking() is False
        assert GamePhase.TRANSITION_ATK_DEF.is_attacking() is False

    def test_is_defensive(self):
        """Should correctly identify defensive phases."""
        assert GamePhase.ORGANIZED_DEFENSE.is_defensive() is True
        assert GamePhase.TRANSITION_ATK_DEF.is_defensive() is True
        assert GamePhase.ORGANIZED_ATTACK.is_defensive() is False

    def test_is_transition(self):
        """Should correctly identify transition phases."""
        assert GamePhase.TRANSITION_ATK_DEF.is_transition() is True
        assert GamePhase.TRANSITION_DEF_ATK.is_transition() is True
        assert GamePhase.ORGANIZED_ATTACK.is_transition() is False
        assert GamePhase.ORGANIZED_DEFENSE.is_transition() is False

    def test_is_organized(self):
        """Should correctly identify organized phases."""
        assert GamePhase.ORGANIZED_ATTACK.is_organized() is True
        assert GamePhase.ORGANIZED_DEFENSE.is_organized() is True
        assert GamePhase.TRANSITION_ATK_DEF.is_organized() is False
        assert GamePhase.TRANSITION_DEF_ATK.is_organized() is False
