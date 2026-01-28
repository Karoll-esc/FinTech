"""
Card Repository and Cache Interfaces (TASK-004)

Following Clean Architecture: Application layer defines ports (interfaces)
that infrastructure adapters must implement.

These interfaces allow the application layer to be independent of
database implementation details (MongoDB, PostgreSQL, Redis, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from domain.card_models import Card, CardStatus


class CardRepository(ABC):
    """
    Port: Card persistence interface
    
    Defines contract for card data access.
    Implementation can use MongoDB, PostgreSQL, or any data store.
    
    Methods:
    - get_user_cards: Fetch up to N cards for a user
    - get_card_by_id: Fetch single card
    - save_card: Persist card data
    - update_card_status: Update card status
    """

    @abstractmethod
    async def get_user_cards(self, user_id: str, limit: int = 3) -> List[Card]:
        """
        Fetch user's cards with limit (default 3)
        
        Args:
            user_id: User ID to fetch cards for
            limit: Maximum number of cards to return (default 3)
        
        Returns:
            List of Card entities sorted by created_at (newest first)
        
        Raises:
            RepositoryError: If fetch fails
        """
        pass

    @abstractmethod
    async def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """
        Fetch single card by ID
        
        Args:
            card_id: Card ID to fetch
        
        Returns:
            Card entity or None if not found
        
        Raises:
            RepositoryError: If fetch fails
        """
        pass

    @abstractmethod
    async def save_card(self, card: Card) -> None:
        """
        Persist card data
        
        Args:
            card: Card entity to save
        
        Raises:
            RepositoryError: If save fails
        """
        pass

    @abstractmethod
    async def update_card_status(self, card_id: str, status: CardStatus) -> Card:
        """
        Update card status and return updated card
        
        Args:
            card_id: Card to update
            status: New CardStatus
        
        Returns:
            Updated Card entity
        
        Raises:
            RepositoryError: If update fails
            CardNotFoundError: If card does not exist
        """
        pass

    @abstractmethod
    async def update_card_balance(self, card_id: str, amount_delta: float) -> Card:
        """
        Update card balance (add or subtract)
        
        Args:
            card_id: Card to update
            amount_delta: Amount to add (positive) or subtract (negative)
        
        Returns:
            Updated Card entity
        
        Raises:
            RepositoryError: If update fails
            InsufficientBalanceError: If balance would go negative
        """
        pass

    @abstractmethod
    async def get_all_user_cards(self, user_id: str) -> List[Card]:
        """
        Fetch all cards for a user (no limit)
        
        Useful for pagination or viewing all cards.
        
        Args:
            user_id: User ID
        
        Returns:
            List of all user's cards
        """
        pass


class CardCacheService(ABC):
    """
    Port: Card cache service interface
    
    Provides fast access to frequently-accessed card data.
    Implementation can use Redis, Memcached, or in-memory cache.
    
    Follows Cache-Aside pattern:
    1. Try to get from cache
    2. If miss, fetch from repository
    3. Store in cache
    4. Return data
    """

    @abstractmethod
    async def get_cached_user_cards(self, user_id: str) -> Optional[List[Card]]:
        """
        Fetch user cards from cache
        
        Args:
            user_id: User ID
        
        Returns:
            List of Card entities or None if not cached
        """
        pass

    @abstractmethod
    async def set_cached_user_cards(
        self, user_id: str, cards: List[Card], ttl_seconds: int = 300
    ) -> None:
        """
        Cache user cards with TTL
        
        Args:
            user_id: User ID
            cards: List of cards to cache
            ttl_seconds: Time-to-live in seconds (default 300s = 5 minutes)
        """
        pass

    @abstractmethod
    async def invalidate_user_cards_cache(self, user_id: str) -> None:
        """
        Remove user's cards from cache
        
        Called after card operations (status change, balance update)
        
        Args:
            user_id: User ID whose cache to invalidate
        """
        pass

    @abstractmethod
    async def get_cached_card(self, card_id: str) -> Optional[Card]:
        """
        Fetch single card from cache
        
        Args:
            card_id: Card ID
        
        Returns:
            Card entity or None if not cached
        """
        pass

    @abstractmethod
    async def set_cached_card(
        self, card_id: str, card: Card, ttl_seconds: int = 300
    ) -> None:
        """
        Cache single card
        
        Args:
            card_id: Card ID
            card: Card entity to cache
            ttl_seconds: Time-to-live in seconds
        """
        pass

    @abstractmethod
    async def invalidate_card_cache(self, card_id: str) -> None:
        """
        Remove card from cache
        
        Args:
            card_id: Card ID to invalidate
        """
        pass


class CardTransactionRepository(ABC):
    """
    Port: Card transaction history interface
    
    Provides access to transaction history for a card.
    """

    @abstractmethod
    async def get_card_transactions(
        self, card_id: str, skip: int = 0, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch transaction history for a card (paginated)
        
        Args:
            card_id: Card ID
            skip: Number of records to skip (pagination)
            limit: Maximum records to return
        
        Returns:
            List of transaction dictionaries sorted by date (newest first)
        """
        pass

    @abstractmethod
    async def save_card_transaction(
        self, card_id: str, transaction_data: Dict[str, Any]
    ) -> None:
        """
        Record a transaction for a card
        
        Args:
            card_id: Card ID
            transaction_data: Transaction details
        """
        pass


class CardEventsPublisher(ABC):
    """
    Port: Card events publisher interface
    
    Publishes domain events for card operations (CARD_BLOCKED, TRANSFER_INITIATED, etc.)
    
    Allows other services to react to card events asynchronously.
    """

    @abstractmethod
    async def publish_card_blocked(self, card_id: str, user_id: str) -> None:
        """
        Publish event when card is blocked
        
        Args:
            card_id: Card that was blocked
            user_id: Card owner
        """
        pass

    @abstractmethod
    async def publish_transfer_initiated(
        self, card_id: str, user_id: str, amount: float, transaction_id: str
    ) -> None:
        """
        Publish event when transfer is initiated
        
        Args:
            card_id: Source card
            user_id: User initiating transfer
            amount: Transfer amount
            transaction_id: Transaction ID for tracking
        """
        pass

    @abstractmethod
    async def publish_transfer_completed(
        self, card_id: str, user_id: str, amount: float, transaction_id: str
    ) -> None:
        """
        Publish event when transfer completes
        
        Args:
            card_id: Source card
            user_id: User who transferred
            amount: Transfer amount
            transaction_id: Transaction ID
        """
        pass

    @abstractmethod
    async def publish_card_unblocked(self, card_id: str, user_id: str) -> None:
        """
        Publish event when card is unblocked
        
        Args:
            card_id: Card that was unblocked
            user_id: Card owner
        """
        pass


# Exception classes for repository operations
class RepositoryError(Exception):
    """Base exception for repository operations"""
    pass


class CardNotFoundError(RepositoryError):
    """Raised when card is not found"""
    pass


class InsufficientBalanceError(RepositoryError):
    """Raised when card has insufficient balance for operation"""
    pass


class CacheError(Exception):
    """Base exception for cache operations"""
    pass
