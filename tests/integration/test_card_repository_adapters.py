"""
Integration Tests for Card Repository Adapters (TASK-005 & TASK-006)

Tests for:
- MongoDBCardRepository adapter
- RedisCardCache adapter

Uses mocks for database connections (no real DB required for tests)
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from domain.card_models import Card, CardStatus, CardType
from application.card_ports import (
    CardRepository,
    CardCacheService,
    CardNotFoundError,
)
from infrastructure.card_mongodb_adapter import MongoDBCardRepository
from infrastructure.card_redis_adapter import RedisCardCache


@pytest.mark.asyncio
class TestMongoDBCardRepository:
    """Integration tests for MongoDB card repository adapter"""

    @pytest.fixture
    async def mongo_adapter(self):
        """Create MongoDB adapter with mocked client"""
        adapter = MongoDBCardRepository(
            mongodb_uri="mongodb://localhost:27017",
            database_name="test_db",
        )
        # Mock the async connection
        adapter._db = AsyncMock()
        return adapter

    @pytest.fixture
    def valid_card(self):
        """Fixture: Valid card entity"""
        return Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("1250.50"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.ACTIVE,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_save_card_success(self, mongo_adapter, valid_card):
        """Verify card is saved to MongoDB"""
        # Mock successful insert
        mongo_adapter._db.cards.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="mock_id")
        )

        # Execute
        await mongo_adapter.save_card(valid_card)

        # Assert
        mongo_adapter._db.cards.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_card_by_id_found(self, mongo_adapter, valid_card):
        """Verify fetching card by ID returns card"""
        # Mock database response
        card_doc = {
            "_id": valid_card.card_id,
            "card_id": valid_card.card_id,
            "user_id": valid_card.user_id,
            "card_number": valid_card.card_number,
            "cardholder_name": valid_card.cardholder_name,
            "current_balance": float(valid_card.current_balance),
            "expiry_month": valid_card.expiry_month,
            "expiry_year": valid_card.expiry_year,
            "status": CardStatus.ACTIVE.name,
            "card_type": CardType.DEBIT.name,
            "created_at": valid_card.created_at,
        }
        mongo_adapter._db.cards.find_one = AsyncMock(return_value=card_doc)

        # Execute
        result = await mongo_adapter.get_card_by_id("card_123456")

        # Assert
        assert result is not None
        assert result.card_id == "card_123456"
        mongo_adapter._db.cards.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_card_by_id_not_found(self, mongo_adapter):
        """Verify get_card_by_id returns None when card not found"""
        mongo_adapter._db.cards.find_one = AsyncMock(return_value=None)

        result = await mongo_adapter.get_card_by_id("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_cards_with_limit(self, mongo_adapter):
        """Verify user cards fetched with limit (default 3)"""
        # Mock database response with 3 cards
        card_docs = [
            {
                "card_id": f"card_{i}",
                "user_id": "user_001",
                "card_number": "4532-XXXX-XXXX-1234",
                "cardholder_name": "Juan Pérez",
                "current_balance": 1000.0,
                "expiry_month": 12,
                "expiry_year": 2027,
                "status": "ACTIVE",
                "card_type": "DEBIT",
                "created_at": datetime.now(),
            }
            for i in range(3)
        ]
        mongo_adapter._db.cards.find = MagicMock()
        mongo_adapter._db.cards.find.return_value.limit = MagicMock(
            return_value=MagicMock(__aiter__=AsyncMock(return_value=iter(card_docs)))
        )

        result = await mongo_adapter.get_user_cards("user_001", limit=3)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_update_card_status_success(self, mongo_adapter, valid_card):
        """Verify card status is updated"""
        updated_card_doc = {
            **valid_card.__dict__,
            "status": "BLOCKED",
        }
        mongo_adapter._db.cards.find_one_and_update = AsyncMock(
            return_value=updated_card_doc
        )

        result = await mongo_adapter.update_card_status(
            "card_123456", CardStatus.BLOCKED
        )

        assert result.status == CardStatus.BLOCKED
        mongo_adapter._db.cards.find_one_and_update.assert_called_once()


@pytest.mark.asyncio
class TestRedisCardCache:
    """Integration tests for Redis card cache adapter"""

    @pytest.fixture
    async def redis_cache(self):
        """Create Redis cache with mocked client"""
        cache = RedisCardCache(redis_url="redis://localhost:6379")
        cache._redis = AsyncMock()
        return cache

    @pytest.fixture
    def valid_card(self):
        """Fixture: Valid card entity"""
        return Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("1250.50"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.ACTIVE,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_set_cached_card_with_ttl(self, redis_cache, valid_card):
        """Verify card is cached with TTL"""
        redis_cache._redis.setex = AsyncMock(return_value=True)

        await redis_cache.set_cached_card("card_123456", valid_card, ttl_seconds=300)

        redis_cache._redis.setex.assert_called_once()
        call_args = redis_cache._redis.setex.call_args
        assert call_args[0][1] == 300  # TTL is 300 seconds

    @pytest.mark.asyncio
    async def test_get_cached_card_hit(self, redis_cache, valid_card):
        """Verify cached card is returned on cache hit"""
        # Mock Redis returning serialized card
        card_json = valid_card.__dict__
        redis_cache._redis.get = AsyncMock(return_value=card_json)

        result = await redis_cache.get_cached_card("card_123456")

        assert result is not None
        redis_cache._redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cached_card_miss(self, redis_cache):
        """Verify None returned on cache miss"""
        redis_cache._redis.get = AsyncMock(return_value=None)

        result = await redis_cache.get_cached_card("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_invalidate_card_cache(self, redis_cache):
        """Verify card cache is invalidated"""
        redis_cache._redis.delete = AsyncMock(return_value=1)

        await redis_cache.invalidate_card_cache("card_123456")

        redis_cache._redis.delete.assert_called_once()


@pytest.mark.unit
class TestCardRepositoryContract:
    """
    Abstract test class verifying CardRepository interface contract
    
    Any concrete implementation must pass all these tests.
    """

    @pytest.fixture
    async def repository(self) -> CardRepository:
        """Override in concrete test classes"""
        raise NotImplementedError

    def test_repository_has_required_methods(self):
        """Verify repository implements all required methods"""
        assert hasattr(CardRepository, "get_user_cards")
        assert hasattr(CardRepository, "get_card_by_id")
        assert hasattr(CardRepository, "save_card")
        assert hasattr(CardRepository, "update_card_status")
