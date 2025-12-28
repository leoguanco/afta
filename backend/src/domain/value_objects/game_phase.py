"""
GamePhase Value Object - Domain Layer

Enum representing the four tactical phases of a football match.
"""
from enum import Enum


class GamePhase(Enum):
    """
    Football match phases based on possession and team structure.
    
    Based on tactical theory:
    - ORGANIZED_ATTACK: Team has possession and is structured in attack
    - ORGANIZED_DEFENSE: Opponent has possession, team is defending with structure
    - TRANSITION_ATK_DEF: Team just lost possession, transitioning to defense
    - TRANSITION_DEF_ATK: Team just won possession, transitioning to attack
    - UNKNOWN: Phase cannot be determined (e.g., ball out of play)
    """
    
    ORGANIZED_ATTACK = "organized_attack"
    ORGANIZED_DEFENSE = "organized_defense"
    TRANSITION_ATK_DEF = "transition_attack_to_defense"
    TRANSITION_DEF_ATK = "transition_defense_to_attack"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, value: str) -> "GamePhase":
        """Convert string to GamePhase enum."""
        for phase in cls:
            if phase.value == value:
                return phase
        return cls.UNKNOWN
    
    def is_attacking(self) -> bool:
        """Check if this is an attacking phase."""
        return self in (self.ORGANIZED_ATTACK, self.TRANSITION_DEF_ATK)
    
    def is_defensive(self) -> bool:
        """Check if this is a defensive phase."""
        return self in (self.ORGANIZED_DEFENSE, self.TRANSITION_ATK_DEF)
    
    def is_transition(self) -> bool:
        """Check if this is a transition phase."""
        return self in (self.TRANSITION_ATK_DEF, self.TRANSITION_DEF_ATK)
    
    def is_organized(self) -> bool:
        """Check if this is an organized (settled) phase."""
        return self in (self.ORGANIZED_ATTACK, self.ORGANIZED_DEFENSE)
