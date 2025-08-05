"""Shared domain events."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
import uuid


class DomainEvent(ABC):
    """Base class for all domain events."""
    
    def __init__(self) -> None:
        self.event_id = str(uuid.uuid4())
        self.occurred_on = datetime.utcnow()
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        pass


@dataclass
class UserRegistered(DomainEvent):
    """Event fired when a user registers."""
    
    user_id: str
    email: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": "UserRegistered",
            "occurred_on": self.occurred_on.isoformat(),
            "user_id": self.user_id,
            "email": self.email
        }


@dataclass
class PokemonAddedToCart(DomainEvent):
    """Event fired when a pokemon is added to cart."""
    
    user_id: str
    pokemon_id: int
    quantity: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": "PokemonAddedToCart",
            "occurred_on": self.occurred_on.isoformat(),
            "user_id": self.user_id,
            "pokemon_id": self.pokemon_id,
            "quantity": self.quantity
        }
