import datetime
from typing import TYPE_CHECKING, Any, Dict

from .models import (
    AliasCard,
    BaseCard,
    CardType,
    DeviceTokenCard,
    NetworkTokenCard,
    PlainCard,
    ValidationError,
)

if TYPE_CHECKING:
    from .models import BaseModel


def create_card_from_dict(card_data: Dict[str, Any]) -> BaseCard:
    """Create appropriate card instance from dictionary."""
    card_type = card_data.get("type")

    if card_type == CardType.PLAIN.value:
        return PlainCard.from_dict(card_data)
    elif card_type == CardType.ALIAS.value:
        return AliasCard.from_dict(card_data)
    elif card_type == CardType.NETWORK_TOKEN.value:
        return NetworkTokenCard.from_dict(card_data)
    elif card_type == CardType.DEVICE_TOKEN.value:
        return DeviceTokenCard.from_dict(card_data)
    else:
        raise ValidationError(f"Unknown card type: {card_type}")


def format_datetime(dt: datetime.datetime) -> str:
    """Format datetime for JSON serialization."""
    return dt.isoformat().replace("+00:00", "Z")


def register_from_dict(cls):
    """Decorator to add from_dict method to classes."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create instance from dictionary."""
        # Filter data to only include valid attributes
        valid_attrs = cls.__init__.__code__.co_varnames[
            1 : cls.__init__.__code__.co_argcount
        ]
        filtered_data = {k: v for k, v in data.items() if k in valid_attrs}

        # Handle special cases for nested models
        instance = cls(**filtered_data)
        instance.validate()
        return instance

    cls.from_dict = from_dict
    return cls
