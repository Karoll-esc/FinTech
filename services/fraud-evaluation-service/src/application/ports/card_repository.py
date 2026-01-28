"""
Card Repository Port - Interface for persistence layer
Clean Architecture: Application layer defines the interface,
infrastructure layer provides implementation

The repository abstracts MongoDB/database operations for Card entities.
Allows use cases to be decoupled from database implementation.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models import Card


class CardRepository(ABC):
    """
    Abstract interface for Card persistence operations
    
    Implemented by infrastructure adapters (MongoCardRepository, etc.)
    Use cases depend on this interface, not concrete implementations.
    """

    @abstractmethod
    async def save(self, card: Card) -> Card:
        """
        Save or update a card (upsert)
        
        Args:
            card: Card entity to persist
            
        Returns:
            Saved Card (with card_id populated if new)
            
        Raises:
            ValueError: If save fails
        """
        pass

    @abstractmethod
    async def find_by_id(self, card_id: str) -> Optional[Card]:
        """
        Retrieve a card by ID
        
        Args:
            card_id: Unique card identifier
            
        Returns:
            Card if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[Card]:
        """
        Retrieve all cards for a user (including inactive)
        
        Args:
            user_id: User identifier
            
        Returns:
            List of Card entities (may be empty)
        """
        pass

    @abstractmethod
    async def find_by_user_and_last_four(
        self, user_id: str, last_four_digits: str
    ) -> Optional[Card]:
        """
        Check for duplicate card (by last 4 digits for user)
        
        Used to prevent adding same card twice
        
        Args:
            user_id: User identifier
            last_four_digits: Last 4 digits of card number
            
        Returns:
            Card if duplicate found, None otherwise
        """
        pass

    @abstractmethod
    async def count_user_cards(self, user_id: str) -> int:
        """
        Count active cards for user
        
        Used to enforce max cards limit (10 cards)
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of active cards
        """
        pass

    @abstractmethod
    async def soft_delete(self, card_id: str) -> None:
        """
        Soft-delete a card (set status to INACTIVE)
        
        Preserves card in database for audit trail
        
        Args:
            card_id: Card to soft-delete
            
        Raises:
            ValueError: If card not found
        """
        pass
