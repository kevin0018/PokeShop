"""Shared domain value objects."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Self
import re


class ValueObject(ABC):
    """Base class for all value objects."""
    
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        pass


@dataclass(frozen=True)
class Money(ValueObject):
    """Money value object with currency support."""
    
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency cannot be empty")
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __hash__(self) -> int:
        return hash((self.amount, self.currency))
    
    def add(self, other: "Money") -> "Money":
        """Add two money values with same currency."""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: int | float) -> "Money":
        """Multiply money by a factor."""
        return Money(self.amount * Decimal(str(factor)), self.currency)


@dataclass(frozen=True)
class Email(ValueObject):
    """Email value object with validation."""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value.lower() == other.value.lower()
    
    def __hash__(self) -> int:
        return hash(self.value.lower())
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


@dataclass(frozen=True)
class UserId(ValueObject):
    """User identifier value object."""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("UserId cannot be empty")
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, UserId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class PokemonId(ValueObject):
    """Pokemon identifier value object."""
    
    value: int
    
    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("PokemonId must be positive")
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PokemonId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class CartId(ValueObject):
    """Cart identifier value object."""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("CartId cannot be empty")
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CartId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
