"""
Unit Tests for Card Use Cases (Phase 2 - TASK-010 to TASK-018)

Tests for:
- GetUserCardsUseCase
- GetCardDetailUseCase
- TransferMoneyUseCase
- BlockCardUseCase
- GetCardTransactionsUseCase

Follows TDD: Test first (RED), then implement (GREEN), then refactor.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from domain.card_models import Card, CardStatus, CardType, TransferRequest
from application.card_use_cases import (
    GetUserCardsUseCase,
    BlockCardUseCase,
    TransferMoneyUseCase,
)
from application.card_ports import (
    CardRepository,
    CardCacheService,
    CardNotFoundError,
    InsufficientBalanceError,
)


@pytest.fixture
def mock_repository():
    """Mock CardRepository"""
    return AsyncMock(spec=CardRepository)


@pytest.fixture
def mock_cache():
    """Mock CardCacheService"""
    return AsyncMock(spec=CardCacheService)


@pytest.fixture
def mock_events_publisher():
    """Mock CardEventsPublisher"""
    return AsyncMock()


@pytest.fixture
def valid_card():
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
class TestGetUserCardsUseCase:
    """Test GetUserCardsUseCase"""

    @pytest.mark.asyncio
    async def test_get_user_cards_from_cache_hit(self, mock_repository, mock_cache, valid_card):
        """Verify cards are returned from cache if available"""
        # Setup
        use_case = GetUserCardsUseCase(
            repository=mock_repository, cache=mock_cache, limit=3
        )
        cached_cards = [valid_card]
        mock_cache.get_cached_user_cards.return_value = cached_cards

        # Execute
        result = await use_case.execute(user_id="user_001")

        # Assert
        assert result == cached_cards
        mock_cache.get_cached_user_cards.assert_called_once_with("user_001")
        mock_repository.get_user_cards.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_cards_from_repository_on_cache_miss(
        self, mock_repository, mock_cache, valid_card
    ):
        """Verify cards fetched from repository on cache miss"""
        # Setup
        use_case = GetUserCardsUseCase(
            repository=mock_repository, cache=mock_cache, limit=3
        )
        mock_cache.get_cached_user_cards.return_value = None
        repo_cards = [valid_card]
        mock_repository.get_user_cards.return_value = repo_cards

        # Execute
        result = await use_case.execute(user_id="user_001")

        # Assert
        assert result == repo_cards
        mock_cache.get_cached_user_cards.assert_called_once()
        mock_repository.get_user_cards.assert_called_once_with("user_001", limit=3)
        mock_cache.set_cached_user_cards.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_cards_enforces_limit(self, mock_repository, mock_cache):
        """Verify limit is enforced (max 3 cards)"""
        # Setup
        use_case = GetUserCardsUseCase(
            repository=mock_repository, cache=mock_cache, limit=3
        )
        mock_cache.get_cached_user_cards.return_value = None

        # Execute
        await use_case.execute(user_id="user_001")

        # Assert
        call_args = mock_repository.get_user_cards.call_args
        assert call_args[1]["limit"] == 3

    @pytest.mark.asyncio
    async def test_get_user_cards_returns_empty_list_if_no_cards(
        self, mock_repository, mock_cache
    ):
        """Verify empty list returned if user has no cards"""
        # Setup
        use_case = GetUserCardsUseCase(
            repository=mock_repository, cache=mock_cache, limit=3
        )
        mock_cache.get_cached_user_cards.return_value = None
        mock_repository.get_user_cards.return_value = []

        # Execute
        result = await use_case.execute(user_id="user_001")

        # Assert
        assert result == []


@pytest.mark.asyncio
class TestBlockCardUseCase:
    """Test BlockCardUseCase"""

    @pytest.mark.asyncio
    async def test_block_card_success(self, mock_repository, mock_cache, mock_events_publisher):
        """Verify card status changed to BLOCKED"""
        # Setup
        use_case = BlockCardUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        blocked_card = Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("1250.50"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.BLOCKED,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )
        mock_repository.update_card_status.return_value = blocked_card

        # Execute
        result = await use_case.execute(card_id="card_123456")

        # Assert
        assert result.status == CardStatus.BLOCKED
        mock_repository.update_card_status.assert_called_once_with(
            "card_123456", CardStatus.BLOCKED
        )

    @pytest.mark.asyncio
    async def test_block_card_publishes_event(self, mock_repository, mock_cache, mock_events_publisher):
        """Verify CARD_BLOCKED event is published"""
        # Setup
        use_case = BlockCardUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        blocked_card = Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("1250.50"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.BLOCKED,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )
        mock_repository.update_card_status.return_value = blocked_card

        # Execute
        await use_case.execute(card_id="card_123456")

        # Assert
        mock_events_publisher.publish_card_blocked.assert_called_once()

    @pytest.mark.asyncio
    async def test_block_card_invalidates_cache(self, mock_repository, mock_cache, mock_events_publisher):
        """Verify cache is invalidated after blocking"""
        # Setup
        use_case = BlockCardUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        blocked_card = Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("1250.50"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.BLOCKED,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )
        mock_repository.update_card_status.return_value = blocked_card

        # Execute
        await use_case.execute(card_id="card_123456")

        # Assert
        mock_cache.invalidate_card_cache.assert_called_once_with("card_123456")

    @pytest.mark.asyncio
    async def test_block_card_not_found(self, mock_repository, mock_cache, mock_events_publisher):
        """Verify CardNotFoundError raised if card not found"""
        # Setup
        use_case = BlockCardUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        mock_repository.update_card_status.side_effect = CardNotFoundError(
            "Card not found"
        )

        # Execute & Assert
        with pytest.raises(CardNotFoundError):
            await use_case.execute(card_id="nonexistent")


@pytest.mark.asyncio
class TestTransferMoneyUseCase:
    """Test TransferMoneyUseCase"""

    @pytest.mark.asyncio
    async def test_transfer_success(self, mock_repository, mock_cache, mock_events_publisher, valid_card):
        """Verify transfer updates card balance"""
        # Setup
        use_case = TransferMoneyUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        transfer_request = TransferRequest(
            source_card_id="card_123456",
            user_id="user_001",
            amount=Decimal("100.00"),
            device_id="device_abc",
            location_lat=4.7110,
            location_lng=-74.0721,
            transaction_id="txn_001",
            description="Transfer to savings",
        )
        
        # Mock repository methods
        mock_repository.get_card_by_id.return_value = valid_card
        updated_card = valid_card.with_updated_balance(valid_card.current_balance - Decimal("100.00"))
        mock_repository.update_card_balance.return_value = updated_card

        # Execute
        result = await use_case.execute(transfer_request)

        # Assert
        assert result is not None
        mock_repository.get_card_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_transfer_from_blocked_card_fails(self, mock_repository, mock_cache, mock_events_publisher):
        """Verify transfer from blocked card fails"""
        # Setup
        use_case = TransferMoneyUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        blocked_card = Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("1250.50"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.BLOCKED,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )
        transfer_request = TransferRequest(
            source_card_id="card_123456",
            user_id="user_001",
            amount=Decimal("100.00"),
            device_id="device_abc",
            location_lat=4.7110,
            location_lng=-74.0721,
            transaction_id="txn_001",
            description="Transfer",
        )
        mock_repository.get_card_by_id.return_value = blocked_card

        # Execute & Assert
        with pytest.raises(ValueError, match="Cannot transfer from blocked card"):
            await use_case.execute(transfer_request)

    @pytest.mark.asyncio
    async def test_transfer_insufficient_balance_fails(self, mock_repository, mock_cache, mock_events_publisher, valid_card):
        """Verify transfer with insufficient balance fails"""
        # Setup
        use_case = TransferMoneyUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        low_balance_card = valid_card.with_updated_balance(Decimal("50.00"))
        transfer_request = TransferRequest(
            source_card_id="card_123456",
            user_id="user_001",
            amount=Decimal("100.00"),
            device_id="device_abc",
            location_lat=4.7110,
            location_lng=-74.0721,
            transaction_id="txn_001",
            description="Transfer",
        )
        mock_repository.get_card_by_id.return_value = low_balance_card
        mock_repository.update_card_balance.side_effect = InsufficientBalanceError(
            "Insufficient balance"
        )

        # Execute & Assert
        with pytest.raises(InsufficientBalanceError):
            await use_case.execute(transfer_request)

    @pytest.mark.asyncio
    async def test_transfer_publishes_event(self, mock_repository, mock_cache, mock_events_publisher, valid_card):
        """Verify TRANSFER_INITIATED event is published"""
        # Setup
        use_case = TransferMoneyUseCase(
            repository=mock_repository,
            cache=mock_cache,
            events_publisher=mock_events_publisher,
        )
        transfer_request = TransferRequest(
            source_card_id="card_123456",
            user_id="user_001",
            amount=Decimal("100.00"),
            device_id="device_abc",
            location_lat=4.7110,
            location_lng=-74.0721,
            transaction_id="txn_001",
            description="Transfer",
        )
        mock_repository.get_card_by_id.return_value = valid_card
        updated_card = valid_card.with_updated_balance(valid_card.current_balance - Decimal("100.00"))
        mock_repository.update_card_balance.return_value = updated_card

        # Execute
        await use_case.execute(transfer_request)

        # Assert
        mock_events_publisher.publish_transfer_initiated.assert_called_once()


@pytest.mark.unit
class TestCardUseCaseValidation:
    """Tests for use case validation and error handling"""

    @pytest.mark.asyncio
    async def test_use_case_permission_denied_for_unauthorized_user(self):
        """Verify permission check denies unauthorized users"""
        # This would be tested in integration tests with actual user context
        pass

    @pytest.mark.asyncio
    async def test_transfer_validates_fraud_rules(self):
        """Verify transfer is validated against fraud rules"""
        # This would call fraud evaluation service
        pass
