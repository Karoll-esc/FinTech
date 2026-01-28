"""
Redis Card Cache Adapter (TASK-006)

Implements CardCacheService interface using Redis for fast caching.

Follows Cache-Aside pattern:
1. Try to get from cache
2. If miss, fetch from repository
3. Store in cache
4. Return data
"""

import json
import logging
from typing import List, Optional
from redis import asyncio as aioredis
from domain.card_models import Card, CardStatus, CardType
from decimal import Decimal
from datetime import datetime
from application.card_ports import CardCacheService, CacheError

logger = logging.getLogger(__name__)

# Redis key prefixes for organizing cache
REDIS_KEY_USER_CARDS = "cards:user:{user_id}"
REDIS_KEY_CARD = "cards:card:{card_id}"


class RedisCardCache(CardCacheService):
    """
    Redis implementation of CardCacheService
    
    Provides fast caching of card data with TTL.
    Uses JSON serialization for storage.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis connection URL
        """
        self._redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        logger.info(f"Initialized RedisCardCache with URL: {redis_url}")

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self._redis = await aioredis.from_url(self._redis_url)
            # Test connection
            await self._redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise CacheError(f"Failed to connect to Redis: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
            logger.info("Disconnected from Redis")

    async def get_cached_user_cards(self, user_id: str) -> Optional[List[Card]]:
        """
        Fetch user cards from cache
        
        Args:
            user_id: User ID
        
        Returns:
            List of Card entities or None if not cached
        """
        try:
            key = REDIS_KEY_USER_CARDS.format(user_id=user_id)
            data = await self._redis.get(key)
            if not data:
                logger.debug(f"Cache miss for user cards {user_id}")
                return None
            
            cards_data = json.loads(data)
            cards = [self._deserialize_card(card_data) for card_data in cards_data]
            logger.debug(f"Cache hit for user cards {user_id}: {len(cards)} cards")
            return cards
        except Exception as e:
            logger.warning(f"Failed to get cached user cards {user_id}: {e}")
            return None

    async def set_cached_user_cards(
        self, user_id: str, cards: List[Card], ttl_seconds: int = 300
    ) -> None:
        """
        Cache user cards with TTL
        
        Args:
            user_id: User ID
            cards: List of cards to cache
            ttl_seconds: Time-to-live in seconds (default 300s)
        """
        try:
            key = REDIS_KEY_USER_CARDS.format(user_id=user_id)
            cards_data = [self._serialize_card(card) for card in cards]
            await self._redis.setex(key, ttl_seconds, json.dumps(cards_data))
            logger.debug(f"Cached {len(cards)} cards for user {user_id}, TTL={ttl_seconds}s")
        except Exception as e:
            logger.warning(f"Failed to cache user cards {user_id}: {e}")

    async def invalidate_user_cards_cache(self, user_id: str) -> None:
        """
        Remove user's cards from cache
        
        Args:
            user_id: User ID whose cache to invalidate
        """
        try:
            key = REDIS_KEY_USER_CARDS.format(user_id=user_id)
            await self._redis.delete(key)
            logger.debug(f"Invalidated cache for user cards {user_id}")
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")

    async def get_cached_card(self, card_id: str) -> Optional[Card]:
        """
        Fetch single card from cache
        
        Args:
            card_id: Card ID
        
        Returns:
            Card entity or None if not cached
        """
        try:
            key = REDIS_KEY_CARD.format(card_id=card_id)
            data = await self._redis.get(key)
            if not data:
                logger.debug(f"Cache miss for card {card_id}")
                return None
            
            card_data = json.loads(data)
            card = self._deserialize_card(card_data)
            logger.debug(f"Cache hit for card {card_id}")
            return card
        except Exception as e:
            logger.warning(f"Failed to get cached card {card_id}: {e}")
            return None

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
        try:
            key = REDIS_KEY_CARD.format(card_id=card_id)
            card_data = self._serialize_card(card)
            await self._redis.setex(key, ttl_seconds, json.dumps(card_data))
            logger.debug(f"Cached card {card_id}, TTL={ttl_seconds}s")
        except Exception as e:
            logger.warning(f"Failed to cache card {card_id}: {e}")

    async def invalidate_card_cache(self, card_id: str) -> None:
        """
        Remove card from cache
        
        Args:
            card_id: Card ID to invalidate
        """
        try:
            key = REDIS_KEY_CARD.format(card_id=card_id)
            await self._redis.delete(key)
            logger.debug(f"Invalidated cache for card {card_id}")
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for card {card_id}: {e}")

    # Private helper methods
    def _serialize_card(self, card: Card) -> dict:
        """Convert Card entity to JSON-serializable dict"""
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
            "created_at": card.created_at.isoformat(),
            "updated_at": card.updated_at.isoformat() if card.updated_at else None,
        }

    def _deserialize_card(self, data: dict) -> Card:
        """Convert JSON dict back to Card entity"""
        return Card(
            card_id=data["card_id"],
            user_id=data["user_id"],
            card_number=data["card_number"],
            cardholder_name=data["cardholder_name"],
            current_balance=Decimal(str(data["current_balance"])),
            expiry_month=data["expiry_month"],
            expiry_year=data["expiry_year"],
            status=CardStatus[data["status"]],
            card_type=CardType[data["card_type"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
        )
