"""
PatternLabeler - Domain Layer

Domain Service for rule-based pattern labeling.
"""
from src.domain.entities.tactical_pattern import TacticalPattern


class PatternLabeler:
    """
    Labels tactical patterns based on their characteristics.
    
    Uses rule-based logic to assign human-readable names.
    """
    
    def label_pattern(self, pattern: TacticalPattern) -> str:
        """
        Assign a label to a pattern based on its statistics.
        
        Args:
            pattern: TacticalPattern with computed statistics
            
        Returns:
            Human-readable label
        """
        # High xT progression = attacking pattern
        if pattern.avg_xt_progression > 0.1:
            if pattern.goal_rate > 0.15:
                return "High-Value Attack"
            if pattern.avg_duration_seconds < 8:
                return "Quick Counter Attack"
            if pattern.avg_event_count > 8:
                return "Build-Up Attack"
            return "Progressive Attack"
        
        # Negative xT = failed attack or defensive recovery
        if pattern.avg_xt_progression < -0.05:
            if pattern.avg_duration_seconds < 5:
                return "Quick Possession Loss"
            return "Defensive Reset"
        
        # Short duration patterns
        if pattern.avg_duration_seconds < 5:
            if pattern.success_rate > 0.3:
                return "Direct Attack"
            return "Short Possession"
        
        # Long possession patterns
        if pattern.avg_duration_seconds > 15:
            if pattern.avg_event_count > 10:
                return "Patient Build-Up"
            return "Long Possession"
        
        # Medium patterns
        if pattern.avg_event_count > 6:
            return "Structured Attack"
        
        return "Standard Possession"
    
    def describe_pattern(self, pattern: TacticalPattern) -> str:
        """
        Generate description for a pattern.
        
        Args:
            pattern: TacticalPattern with computed statistics
            
        Returns:
            Descriptive text
        """
        parts = []
        
        # Duration description
        if pattern.avg_duration_seconds < 5:
            parts.append("Quick")
        elif pattern.avg_duration_seconds > 12:
            parts.append("Prolonged")
        
        # Event count
        if pattern.avg_event_count < 4:
            parts.append("direct")
        elif pattern.avg_event_count > 8:
            parts.append("elaborate")
        
        # xT progression
        if pattern.avg_xt_progression > 0.1:
            parts.append("attacking")
        elif pattern.avg_xt_progression < -0.05:
            parts.append("regressive")
        else:
            parts.append("neutral")
        
        # Outcome
        if pattern.goal_rate > 0.1:
            parts.append("goal-threatening")
        elif pattern.success_rate > 0.4:
            parts.append("chance-creating")
        else:
            parts.append("possession-focused")
        
        # Combine
        desc = " ".join(parts) + " pattern"
        desc = desc.capitalize()
        desc += f" (n={pattern.occurrence_count}, success={pattern.success_rate:.0%})"
        
        return desc
