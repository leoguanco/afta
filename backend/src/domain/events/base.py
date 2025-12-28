"""
Base Domain Event.

Domain events represent something significant that happened in the domain.
They are used to communicate between bounded contexts without tight coupling.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.
    
    Domain events are immutable records of something that happened.
    They carry the aggregate_id of the entity that produced them.
    
    Attributes:
        event_id: Unique identifier for this event instance
        aggregate_id: ID of the aggregate root that produced this event
        occurred_at: Timestamp when the event occurred
        event_type: String name of the event type (auto-populated)
    """
    aggregate_id: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_type(self) -> str:
        """Return the event type name (class name)."""
        return self.__class__.__name__
    
    def to_dict(self) -> dict:
        """Serialize event to dictionary for transport."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_at": self.occurred_at.isoformat(),
            "data": self._event_data(),
        }
    
    def _event_data(self) -> dict:
        """Override in subclasses to add event-specific data."""
        return {}
