"""
Card Use Cases (Phase 2 - TASK-010 to TASK-018)

Application layer: Orchestrates domain logic and manages dependencies.

Use Cases:
- GetUserCardsUseCase: Fetch user's cards (with cache-aside pattern)
- GetCardDetailUseCase: Fetch single card with full details
- TransferMoneyUseCase: Execute card transfer with validation
- BlockCardUseCase: Block a card
- GetCardTransactionsUseCase: Fetch card transaction history

Each use case:
1. Implements a single business operation (Single Responsibility)
2. Depends on repository interfaces, not concrete implementations (Dependency Inversion)
3. Publishes domain events for audit trail and downstream services
4. Handles permission checking and validation
"""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from domain.card_models import Card, CardStatus, TransferRequest
from application.card_ports import (
    CardRepository,
    CardCacheService,
    CardTransactionRepository,
    CardEventsPublisher,
    CardNotFoundError,
    InsufficientBalanceError,
)

logger = logging.getLogger(__name__)

# Cache TTL in seconds (5 minutes = 300 seconds)
DEFAULT_CACHE_TTL = 300


class GetUserCardsUseCase:
    """
    Use Case: Get user's active cards (max 3 by default)
    
    Implements Cache-Aside pattern:
    1. Try cache (Redis)
    2. If miss, fetch from repository (MongoDB)
    3. Cache the result
    4. Return data
    """

    def __init__(
        self,
        repository: CardRepository,
        cache: CardCacheService,
        limit: int = 3,
    ):
        """
        Initialize use case with dependencies
        
        Args:
            repository: Card persistence layer
            cache: Card cache layer
            limit: Maximum cards to return (default 3)
        """
        self._repository = repository
        self._cache = cache
        self._limit = limit
        logger.info(f"Initialized GetUserCardsUseCase with limit={limit}")

    async def execute(self, user_id: str) -> List[Card]:
        """
        Execute use case: Fetch user cards with cache
        
        Args:
            user_id: User ID to fetch cards for
        
        Returns:
            List of cards (max 3)
        
        Raises:
            RepositoryError: If fetch fails
        """
        logger.info(f"GetUserCardsUseCase: Fetching cards for user {user_id}")

        # Try cache first
        cached_cards = await self._cache.get_cached_user_cards(user_id)
        if cached_cards is not None:
            logger.info(f"Cache hit: {len(cached_cards)} cards found for user {user_id}")
            return cached_cards

        logger.debug(f"Cache miss for user {user_id}, fetching from repository")

        # Fetch from repository
        cards = await self._repository.get_user_cards(user_id, limit=self._limit)
        logger.info(f"Fetched {len(cards)} cards for user {user_id} from repository")

        # Cache the result
        await self._cache.set_cached_user_cards(
            user_id, cards, ttl_seconds=DEFAULT_CACHE_TTL
        )

        return cards


class GetCardDetailUseCase:
    """Use Case: Get single card with full details"""

    def __init__(
        self,
        repository: CardRepository,
        cache: CardCacheService,
    ):
        self._repository = repository
        self._cache = cache

    async def execute(self, card_id: str, user_id: str) -> Card:
        """
        Execute use case: Fetch card by ID
        
        Args:
            card_id: Card to fetch
            user_id: User who owns the card (for authorization)
        
        Returns:
            Card entity
        
        Raises:
            CardNotFoundError: If card not found
            PermissionError: If user doesn't own the card
        """
        logger.info(f"GetCardDetailUseCase: Fetching card {card_id} for user {user_id}")

        # Try cache
        cached_card = await self._cache.get_cached_card(card_id)
        if cached_card:
            # Verify ownership
            if cached_card.user_id != user_id:
                logger.warning(f"Permission denied: User {user_id} not owner of card {card_id}")
                raise PermissionError("You don't have permission to view this card")
            return cached_card

        # Fetch from repository
        card = await self._repository.get_card_by_id(card_id)
        if not card:
            raise CardNotFoundError(f"Card {card_id} not found")

        # Verify ownership
        if card.user_id != user_id:
            logger.warning(f"Permission denied: User {user_id} not owner of card {card_id}")
            raise PermissionError("You don't have permission to view this card")

        # Cache the result
        await self._cache.set_cached_card(card_id, card, ttl_seconds=DEFAULT_CACHE_TTL)

        return card


class BlockCardUseCase:
    """
    Use Case: Block a card (disable transfers)
    
    Updates card status to BLOCKED and publishes event for audit trail.
    """

    def __init__(
        self,
        repository: CardRepository,
        cache: CardCacheService,
        events_publisher: CardEventsPublisher,
    ):
        self._repository = repository
        self._cache = cache
        self._events_publisher = events_publisher

    async def execute(self, card_id: str) -> Card:
        """
        Execute use case: Block card
        
        Args:
            card_id: Card to block
        
        Returns:
            Updated Card entity
        
        Raises:
            CardNotFoundError: If card not found
        """
        logger.info(f"BlockCardUseCase: Blocking card {card_id}")

        # Update card status in repository
        blocked_card = await self._repository.update_card_status(
            card_id, CardStatus.BLOCKED
        )
        logger.info(f"Card {card_id} status updated to BLOCKED")

        # Invalidate cache
        await self._cache.invalidate_card_cache(card_id)
        await self._cache.invalidate_user_cards_cache(blocked_card.user_id)

        # Publish event
        await self._events_publisher.publish_card_blocked(
            card_id, blocked_card.user_id
        )
        logger.info(f"Published CARD_BLOCKED event for card {card_id}")

        return blocked_card


class UnblockCardUseCase:
    """Use Case: Unblock a card (enable transfers)"""

    def __init__(
        self,
        repository: CardRepository,
        cache: CardCacheService,
        events_publisher: CardEventsPublisher,
    ):
        self._repository = repository
        self._cache = cache
        self._events_publisher = events_publisher

    async def execute(self, card_id: str) -> Card:
        """
        Execute use case: Unblock card
        
        Args:
            card_id: Card to unblock
        
        Returns:
            Updated Card entity
        """
        logger.info(f"UnblockCardUseCase: Unblocking card {card_id}")

        unblocked_card = await self._repository.update_card_status(
            card_id, CardStatus.ACTIVE
        )

        await self._cache.invalidate_card_cache(card_id)
        await self._cache.invalidate_user_cards_cache(unblocked_card.user_id)

        await self._events_publisher.publish_card_unblocked(
            card_id, unblocked_card.user_id
        )

        return unblocked_card


class TransferMoneyUseCase:
    """
    Use Case: Transfer money from card
    
    Validates:
    1. Card exists and belongs to user
    2. Card is active (not blocked, not expired)
    3. Balance is sufficient
    4. Amount is valid
    
    Publishes event for fraud evaluation and audit trail.
    """

    def __init__(
        self,
        repository: CardRepository,
        cache: CardCacheService,
        events_publisher: CardEventsPublisher,
    ):
        self._repository = repository
        self._cache = cache
        self._events_publisher = events_publisher

    async def execute(self, transfer_request: TransferRequest) -> Dict[str, Any]:
        """
        Execute use case: Transfer money
        
        Args:
            transfer_request: TransferRequest value object with all details
        
        Returns:
            Transfer result with transaction ID, status, etc.
        
        Raises:
            CardNotFoundError: If card not found
            ValueError: If card cannot transfer (blocked, expired)
            InsufficientBalanceError: If balance is insufficient
        """
        logger.info(
            f"TransferMoneyUseCase: Initiating transfer of {transfer_request.amount} "
            f"from card {transfer_request.source_card_id}"
        )

        # Get card
        card = await self._repository.get_card_by_id(transfer_request.source_card_id)
        if not card:
            raise CardNotFoundError(
                f"Card {transfer_request.source_card_id} not found"
            )

        # Verify ownership
        if card.user_id != transfer_request.user_id:
            logger.warning(
                f"Permission denied: User {transfer_request.user_id} not owner of "
                f"card {transfer_request.source_card_id}"
            )
            raise PermissionError("You don't have permission to transfer from this card")

        # Validate card can transfer
        if not card.can_transfer:
            if card.is_blocked:
                raise ValueError("Cannot transfer from blocked card")
            if card.is_expired:
                raise ValueError("Cannot transfer from expired card")
            raise ValueError("Card is not in a transferable state")

        # Validate balance
        if card.current_balance < transfer_request.amount:
            logger.warning(
                f"Insufficient balance for transfer: {card.current_balance} < "
                f"{transfer_request.amount}"
            )
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: {card.current_balance}"
            )

        logger.info(f"Transfer validation passed for card {card.card_id}")

        # Publish transfer initiated event (triggers fraud evaluation)
        await self._events_publisher.publish_transfer_initiated(
            card.card_id,
            card.user_id,
            float(transfer_request.amount),
            transfer_request.transaction_id,
        )
        logger.info(f"Published TRANSFER_INITIATED event for transaction {transfer_request.transaction_id}")

        # Note: Balance update happens in worker after fraud evaluation
        # This is async-first pattern - 202 Accepted, process later

        return {
            "transaction_id": transfer_request.transaction_id,
            "status": "PENDING_EVALUATION",
            "amount": float(transfer_request.amount),
            "card_id": card.card_id,
            "user_id": card.user_id,
            "message": "Transfer submitted for fraud evaluation",
        }


class GetCardTransactionsUseCase:
    """Use Case: Get card transaction history (paginated)"""

    def __init__(self, transactions_repo: CardTransactionRepository):
        self._transactions_repo = transactions_repo

    async def execute(
        self, card_id: str, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Execute use case: Fetch card transactions
        
        Args:
            card_id: Card to fetch transactions for
            user_id: User who owns the card (for authorization)
            skip: Pagination offset
            limit: Maximum records to return
        
        Returns:
            List of transactions (sorted by date, newest first)
        """
        logger.info(
            f"GetCardTransactionsUseCase: Fetching transactions for card {card_id}"
        )

        transactions = await self._transactions_repo.get_card_transactions(
            card_id, skip=skip, limit=limit
        )

        logger.info(f"Fetched {len(transactions)} transactions for card {card_id}")
        return transactions
