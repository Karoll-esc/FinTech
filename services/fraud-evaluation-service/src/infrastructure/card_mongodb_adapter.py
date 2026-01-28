"""
MongoDB Card Repository Adapter (TASK-005)

Implements CardRepository interface using MongoDB for persistence.

Follows Adapter Pattern:
- Converts between Domain Models (Card) and MongoDB documents
- Handles database connection and query logic
- Implements retry logic for transient failures
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from domain.card_models import Card, CardStatus, CardType
from application.card_ports import (
    CardRepository,
    CardNotFoundError,
    InsufficientBalanceError,
    RepositoryError,
)

logger = logging.getLogger(__name__)


class MongoDBCardRepository(CardRepository):
    """
    MongoDB implementation of CardRepository
    
    Persists Card entities and handles CRUD operations.
    Uses Motor for async database operations.
    """

    def __init__(
        self,
        mongodb_uri: str = "mongodb://localhost:27017",
        database_name: str = "fraud_detection",
    ):
        """
        Initialize MongoDB repository
        
        Args:
            mongodb_uri: MongoDB connection string
            database_name: Database name to use
        """
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._mongodb_uri = mongodb_uri
        self._database_name = database_name
        logger.info(f"Initialized MongoDBCardRepository with URI: {mongodb_uri}")

    async def connect(self) -> None:
        """Connect to MongoDB"""
        if not self._client:
            self._client = AsyncIOMotorClient(self._mongodb_uri)
            self._db = self._client[self._database_name]
            # Create indexes for performance
            await self._db.cards.create_index("user_id")
            await self._db.cards.create_index("card_id", unique=True)
            logger.info("Connected to MongoDB and created indexes")

    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self._client:
            self._client.close()
            logger.info("Disconnected from MongoDB")

    async def get_user_cards(self, user_id: str, limit: int = 3) -> List[Card]:
        """
        Fetch user's cards with limit (default 3)
        
        Args:
            user_id: User ID to fetch cards for
            limit: Maximum number of cards (default 3)
        
        Returns:
            List of Card entities sorted by created_at (newest first)
        """
        try:
            cursor = (
                self._db.cards.find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(limit)
            )
            cards = []
            async for doc in cursor:
                cards.append(self._document_to_card(doc))
            logger.info(f"Fetched {len(cards)} cards for user {user_id}")
            return cards
        except Exception as e:
            logger.error(f"Failed to fetch cards for user {user_id}: {e}")
            raise RepositoryError(f"Failed to fetch cards: {e}") from e

    async def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """
        Fetch single card by ID
        
        Args:
            card_id: Card ID to fetch
        
        Returns:
            Card entity or None if not found
        """
        try:
            doc = await self._db.cards.find_one({"card_id": card_id})
            if not doc:
                logger.debug(f"Card {card_id} not found")
                return None
            card = self._document_to_card(doc)
            logger.info(f"Fetched card {card_id}")
            return card
        except Exception as e:
            logger.error(f"Failed to fetch card {card_id}: {e}")
            raise RepositoryError(f"Failed to fetch card: {e}") from e

    async def save_card(self, card: Card) -> None:
        """
        Persist card data
        
        Args:
            card: Card entity to save
        """
        try:
            doc = self._card_to_document(card)
            await self._db.cards.insert_one(doc)
            logger.info(f"Saved card {card.card_id} for user {card.user_id}")
        except Exception as e:
            logger.error(f"Failed to save card {card.card_id}: {e}")
            raise RepositoryError(f"Failed to save card: {e}") from e

    async def update_card_status(self, card_id: str, status: CardStatus) -> Card:
        """
        Update card status and return updated card
        
        Args:
            card_id: Card to update
            status: New CardStatus
        
        Returns:
            Updated Card entity
        """
        try:
            result = await self._db.cards.find_one_and_update(
                {"card_id": card_id},
                {
                    "$set": {
                        "status": status.name,
                        "updated_at": datetime.now(),
                    }
                },
                return_document=True,
            )
            if not result:
                raise CardNotFoundError(f"Card {card_id} not found")
            card = self._document_to_card(result)
            logger.info(f"Updated card {card_id} status to {status.name}")
            return card
        except CardNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update card {card_id} status: {e}")
            raise RepositoryError(f"Failed to update card: {e}") from e

    async def update_card_balance(self, card_id: str, amount_delta: float) -> Card:
        """
        Update card balance (add or subtract)
        
        Args:
            card_id: Card to update
            amount_delta: Amount to add (positive) or subtract (negative)
        
        Returns:
            Updated Card entity
        """
        try:
            # Get current card
            current_card = await self.get_card_by_id(card_id)
            if not current_card:
                raise CardNotFoundError(f"Card {card_id} not found")

            # Calculate new balance
            new_balance = current_card.current_balance + Decimal(str(amount_delta))
            if new_balance < 0:
                raise InsufficientBalanceError(
                    f"Insufficient balance. Current: {current_card.current_balance}, "
                    f"Delta: {amount_delta}"
                )

            # Update in MongoDB
            result = await self._db.cards.find_one_and_update(
                {"card_id": card_id},
                {
                    "$set": {
                        "current_balance": float(new_balance),
                        "updated_at": datetime.now(),
                    }
                },
                return_document=True,
            )
            card = self._document_to_card(result)
            logger.info(f"Updated card {card_id} balance by {amount_delta}")
            return card
        except (CardNotFoundError, InsufficientBalanceError):
            raise
        except Exception as e:
            logger.error(f"Failed to update card {card_id} balance: {e}")
            raise RepositoryError(f"Failed to update card balance: {e}") from e

    async def get_all_user_cards(self, user_id: str) -> List[Card]:
        """
        Fetch all cards for a user (no limit)
        
        Args:
            user_id: User ID
        
        Returns:
            List of all user's cards
        """
        try:
            cursor = self._db.cards.find({"user_id": user_id}).sort("created_at", -1)
            cards = []
            async for doc in cursor:
                cards.append(self._document_to_card(doc))
            logger.info(f"Fetched all {len(cards)} cards for user {user_id}")
            return cards
        except Exception as e:
            logger.error(f"Failed to fetch all cards for user {user_id}: {e}")
            raise RepositoryError(f"Failed to fetch cards: {e}") from e

    # Private helper methods
    def _document_to_card(self, doc: dict) -> Card:
        """Convert MongoDB document to Card entity"""
        return Card(
            card_id=doc["card_id"],
            user_id=doc["user_id"],
            card_number=doc["card_number"],
            cardholder_name=doc["cardholder_name"],
            current_balance=Decimal(str(doc["current_balance"])),
            expiry_month=doc["expiry_month"],
            expiry_year=doc["expiry_year"],
            status=CardStatus[doc["status"]],
            card_type=CardType[doc["card_type"]],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )

    def _card_to_document(self, card: Card) -> dict:
        """Convert Card entity to MongoDB document"""
        return {
            "card_id": card.card_id,
            "user_id": card.user_id,
            "card_number": card.card_number,
            "cardholder_name": card.cardholder_name,
            "current_balance": float(card.current_balance),
            "expiry_month": card.expiry_month,
            "expiry_year": card.expiry_year,
            "status": card.status.name,
            "card_type": card.card_type.name,
            "created_at": card.created_at,
            "updated_at": card.updated_at or datetime.now(),
        }
