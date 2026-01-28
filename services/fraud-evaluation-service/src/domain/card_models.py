"""
Domain Models for Card Management (Phase 1 - TASK-001 to TASK-003)

Following Clean Architecture principles:
- Immutable dataclasses (@dataclass(frozen=True))
- Validation at construction time (__post_init__)
- No external framework imports (pure Python)
- Business logic encapsulated in properties and methods

Entities:
- Card: Represents a user's payment card
- CardStatus: Enum for card state
- CardType: Enum for card type (DEBIT/CREDIT)
- CardDetails: Value Object for card metadata
- TransferRequest: Value Object for transfer operations
- Location: Value Object for geographic coordinates
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class CardStatus(Enum):
    """
    Enum representing card status states
    
    Values are immutable and represent different card states.
    Numeric ordering allows status comparisons if needed.
    """
    ACTIVE = 1
    BLOCKED = 2
    EXPIRED = 3
    PENDING = 4

    def __str__(self) -> str:
        """Return enum name for serialization"""
        return self.name


class CardType(Enum):
    """Enum representing card type (DEBIT or CREDIT)"""
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

    def __str__(self) -> str:
        """Return enum name for serialization"""
        return self.name


@dataclass(frozen=True)
class Location:
    """
    Value Object representing geographic coordinates
    
    Immutable to ensure consistency and enable safe sharing between entities.
    Validation occurs at construction time (fail-fast principle).
    """
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate coordinates at construction"""
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")


@dataclass(frozen=True)
class CardDetails:
    """
    Value Object containing card metadata
    
    Immutable representation of card details (number, name, expiry).
    Separated from Card entity to maintain single responsibility.
    """
    card_number: str  # Masked format: XXXX-XXXX-XXXX-1234
    cardholder_name: str
    expiry_month: int  # 1-12
    expiry_year: int  # 2025, 2026, etc.

    def __post_init__(self) -> None:
        """Validate card details at construction"""
        if not 1 <= self.expiry_month <= 12:
            raise ValueError("Month must be between 1 and 12")
        
        current_year = datetime.now().year
        if self.expiry_year < current_year:
            raise ValueError("Year must be current year or later")

    @property
    def is_expired(self) -> bool:
        """Check if card is expired"""
        now = datetime.now()
        return self.expiry_year < now.year or (
            self.expiry_year == now.year and self.expiry_month < now.month
        )


@dataclass(frozen=True)
class Card:
    """
    Entity representing a user's payment card
    
    Immutable to maintain consistency and enable event sourcing patterns.
    Contains validation for business rules at construction.
    
    Properties:
    - card_id: Unique identifier for the card
    - user_id: Identifies the card owner
    - current_balance: Available balance in the card
    - status: Current state (ACTIVE, BLOCKED, EXPIRED, PENDING)
    - card_type: DEBIT or CREDIT
    """
    card_id: str
    user_id: str
    card_number: str  # Masked: XXXX-XXXX-XXXX-1234
    cardholder_name: str
    current_balance: Decimal
    expiry_month: int
    expiry_year: int
    status: CardStatus
    card_type: CardType
    created_at: datetime
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate card state at construction (fail-fast)"""
        if not self.card_id or not self.card_id.strip():
            raise ValueError("Card ID cannot be empty")
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if self.current_balance < 0:
            raise ValueError("Balance cannot be negative")

    @property
    def masked_number(self) -> str:
        """
        Return masked card number (last 4 digits visible)
        
        Format: XXXX-XXXX-XXXX-1234
        """
        return self.card_number

    @property
    def is_active(self) -> bool:
        """Check if card is in ACTIVE status"""
        return self.status == CardStatus.ACTIVE

    @property
    def is_expired(self) -> bool:
        """Check if card expiry date has passed"""
        now = datetime.now()
        return self.expiry_year < now.year or (
            self.expiry_year == now.year and self.expiry_month < now.month
        )

    @property
    def is_blocked(self) -> bool:
        """Check if card is BLOCKED"""
        return self.status == CardStatus.BLOCKED

    @property
    def can_transfer(self) -> bool:
        """
        Business rule: Can only transfer from ACTIVE, non-expired cards
        
        Returns:
            True if card is ACTIVE and not expired
        """
        return self.is_active and not self.is_expired

    def with_updated_balance(self, new_balance: Decimal) -> "Card":
        """
        Create new Card instance with updated balance
        
        Maintains immutability by returning new instance.
        """
        if new_balance < 0:
            raise ValueError("Balance cannot be negative")
        # Using object.__setattr__ to bypass frozen dataclass restriction
        import copy
        new_card = copy.replace(self, current_balance=new_balance, updated_at=datetime.now())
        return new_card

    def with_status(self, status: CardStatus) -> "Card":
        """
        Create new Card instance with updated status
        
        Maintains immutability by returning new instance.
        """
        import copy
        new_card = copy.replace(self, status=status, updated_at=datetime.now())
        return new_card


@dataclass(frozen=True)
class TransferRequest:
    """
    Value Object representing a transfer request
    
    Immutable representation of transfer parameters.
    Validation occurs at construction to prevent invalid transfers.
    
    Fields:
    - source_card_id: Card to transfer from
    - user_id: User making the transfer
    - amount: Transfer amount (must be > 0)
    - device_id: Device used for transfer (optional)
    - location_lat/lng: Geographic location of transfer
    - transaction_id: Unique transaction identifier
    - description: Transfer description/purpose
    """
    source_card_id: str
    user_id: str
    amount: Decimal
    device_id: Optional[str]
    location_lat: float
    location_lng: float
    transaction_id: str
    description: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate transfer request at construction"""
        if not self.source_card_id or not self.source_card_id.strip():
            raise ValueError("Source card ID cannot be empty")
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not -90 <= self.location_lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.location_lng <= 180:
            raise ValueError("Longitude must be between -180 and 180")

    @property
    def location(self) -> Location:
        """Get location as Location value object"""
        return Location(latitude=self.location_lat, longitude=self.location_lng)
