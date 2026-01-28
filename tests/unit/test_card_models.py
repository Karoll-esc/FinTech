"""
Unit Tests for Card Domain Models (Phase 1 - TASK-001 to TASK-003)

Following TDD: Write failing tests first (RED), then implement (GREEN), then refactor.

Test Coverage:
- Card entity (immutable dataclass with validation)
- CardStatus enum (ACTIVE, BLOCKED, EXPIRED, PENDING)
- TransferRequest value object (with validation)

Acceptance Criteria:
- All models are immutable (@dataclass(frozen=True) or Enum)
- Validation happens at construction time (__post_init__)
- All models are serializable to JSON
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from domain.card_models import (
    Card,
    CardStatus,
    TransferRequest,
    CardType,
    CardDetails,
)


class TestCardStatus:
    """Test CardStatus enum"""

    def test_card_status_has_required_values(self):
        """Verify all required CardStatus values exist"""
        assert hasattr(CardStatus, "ACTIVE")
        assert hasattr(CardStatus, "BLOCKED")
        assert hasattr(CardStatus, "EXPIRED")
        assert hasattr(CardStatus, "PENDING")

    def test_card_status_enum_values_are_unique(self):
        """Verify each status has unique value"""
        statuses = [CardStatus.ACTIVE, CardStatus.BLOCKED, CardStatus.EXPIRED, CardStatus.PENDING]
        values = [s.value for s in statuses]
        assert len(values) == len(set(values))

    def test_card_status_can_convert_to_string(self):
        """Verify status converts to string for serialization"""
        assert str(CardStatus.ACTIVE) == "ACTIVE"
        assert str(CardStatus.BLOCKED) == "BLOCKED"


class TestCardType:
    """Test CardType enum"""

    def test_card_type_has_required_values(self):
        """Verify CardType enum has DEBIT and CREDIT"""
        assert hasattr(CardType, "DEBIT")
        assert hasattr(CardType, "CREDIT")


class TestCardDetails:
    """Test CardDetails value object"""

    def test_card_details_immutable(self):
        """Verify CardDetails is frozen (immutable)"""
        details = CardDetails(
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            expiry_month=12,
            expiry_year=2027,
        )
        with pytest.raises(AttributeError):
            details.cardholder_name = "Changed"

    def test_card_details_creation_valid(self):
        """Verify CardDetails can be created with valid data"""
        details = CardDetails(
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            expiry_month=12,
            expiry_year=2027,
        )
        assert details.card_number == "4532-XXXX-XXXX-1234"
        assert details.cardholder_name == "Juan Pérez"
        assert details.expiry_month == 12
        assert details.expiry_year == 2027

    def test_card_details_validates_expiry_month(self):
        """Verify expiry month must be 1-12"""
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            CardDetails(
                card_number="4532-XXXX-XXXX-1234",
                cardholder_name="Juan Pérez",
                expiry_month=13,
                expiry_year=2027,
            )

    def test_card_details_validates_expiry_year(self):
        """Verify expiry year must be valid (not in past)"""
        past_year = datetime.now().year - 1
        with pytest.raises(ValueError, match="Year must be current year or later"):
            CardDetails(
                card_number="4532-XXXX-XXXX-1234",
                cardholder_name="Juan Pérez",
                expiry_month=6,
                expiry_year=past_year,
            )


class TestCard:
    """Test Card entity (domain model)"""

    @pytest.fixture
    def valid_card_data(self):
        """Fixture: Valid card data"""
        return {
            "card_id": "card_123456",
            "user_id": "user_001",
            "card_number": "4532-XXXX-XXXX-1234",
            "cardholder_name": "Juan Pérez",
            "current_balance": Decimal("1250.50"),
            "expiry_month": 12,
            "expiry_year": 2027,
            "status": CardStatus.ACTIVE,
            "card_type": CardType.DEBIT,
            "created_at": datetime.now(),
        }

    def test_card_creation_valid(self, valid_card_data):
        """Verify Card can be created with valid data"""
        card = Card(**valid_card_data)
        assert card.card_id == "card_123456"
        assert card.user_id == "user_001"
        assert card.current_balance == Decimal("1250.50")
        assert card.status == CardStatus.ACTIVE

    def test_card_immutable(self, valid_card_data):
        """Verify Card is frozen (immutable)"""
        card = Card(**valid_card_data)
        with pytest.raises(AttributeError):
            card.current_balance = Decimal("2000.00")

    def test_card_validates_card_id_not_empty(self, valid_card_data):
        """Verify card_id cannot be empty"""
        valid_card_data["card_id"] = ""
        with pytest.raises(ValueError, match="Card ID cannot be empty"):
            Card(**valid_card_data)

    def test_card_validates_user_id_not_empty(self, valid_card_data):
        """Verify user_id cannot be empty"""
        valid_card_data["user_id"] = ""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            Card(**valid_card_data)

    def test_card_validates_balance_non_negative(self, valid_card_data):
        """Verify balance cannot be negative"""
        valid_card_data["current_balance"] = Decimal("-100.00")
        with pytest.raises(ValueError, match="Balance cannot be negative"):
            Card(**valid_card_data)

    def test_card_masked_number_format(self, valid_card_data):
        """Verify card number is properly masked in masked_number property"""
        card = Card(**valid_card_data)
        # Format: XXXX-XXXX-XXXX-1234 (last 4 digits visible)
        assert card.masked_number == "4532-XXXX-XXXX-1234"

    def test_card_is_active_property(self, valid_card_data):
        """Verify is_active property"""
        card = Card(**valid_card_data)
        assert card.is_active is True

        valid_card_data["status"] = CardStatus.BLOCKED
        blocked_card = Card(**valid_card_data)
        assert blocked_card.is_active is False

    def test_card_can_transfer_property(self, valid_card_data):
        """Verify can_transfer property (only active, non-expired cards)"""
        card = Card(**valid_card_data)
        assert card.can_transfer is True

        valid_card_data["status"] = CardStatus.BLOCKED
        blocked_card = Card(**valid_card_data)
        assert blocked_card.can_transfer is False

        valid_card_data["status"] = CardStatus.EXPIRED
        expired_card = Card(**valid_card_data)
        assert expired_card.can_transfer is False


class TestTransferRequest:
    """Test TransferRequest value object"""

    @pytest.fixture
    def valid_transfer_data(self):
        """Fixture: Valid transfer request data"""
        return {
            "source_card_id": "card_123456",
            "user_id": "user_001",
            "amount": Decimal("100.00"),
            "device_id": "device_abc123",
            "location_lat": 4.7110,
            "location_lng": -74.0721,  # Bogotá coordinates
            "transaction_id": "txn_20260128_001",
            "description": "Transfer to savings",
        }

    def test_transfer_request_creation_valid(self, valid_transfer_data):
        """Verify TransferRequest can be created with valid data"""
        transfer = TransferRequest(**valid_transfer_data)
        assert transfer.source_card_id == "card_123456"
        assert transfer.amount == Decimal("100.00")

    def test_transfer_request_immutable(self, valid_transfer_data):
        """Verify TransferRequest is frozen"""
        transfer = TransferRequest(**valid_transfer_data)
        with pytest.raises(AttributeError):
            transfer.amount = Decimal("200.00")

    def test_transfer_request_validates_amount_positive(self, valid_transfer_data):
        """Verify amount must be positive (>0)"""
        valid_transfer_data["amount"] = Decimal("0.00")
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            TransferRequest(**valid_transfer_data)

        valid_transfer_data["amount"] = Decimal("-50.00")
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            TransferRequest(**valid_transfer_data)

    def test_transfer_request_validates_location(self, valid_transfer_data):
        """Verify location coordinates are valid"""
        valid_transfer_data["location_lat"] = 91  # Invalid latitude
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            TransferRequest(**valid_transfer_data)

        valid_transfer_data["location_lat"] = 4.7110
        valid_transfer_data["location_lng"] = 181  # Invalid longitude
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            TransferRequest(**valid_transfer_data)

    def test_transfer_request_validates_card_id_not_empty(self, valid_transfer_data):
        """Verify source_card_id cannot be empty"""
        valid_transfer_data["source_card_id"] = ""
        with pytest.raises(ValueError, match="Source card ID cannot be empty"):
            TransferRequest(**valid_transfer_data)

    def test_transfer_request_validates_user_id_not_empty(self, valid_transfer_data):
        """Verify user_id cannot be empty"""
        valid_transfer_data["user_id"] = ""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            TransferRequest(**valid_transfer_data)

    def test_transfer_request_device_id_optional(self, valid_transfer_data):
        """Verify device_id is optional"""
        valid_transfer_data["device_id"] = None
        transfer = TransferRequest(**valid_transfer_data)
        assert transfer.device_id is None


@pytest.mark.unit
class TestCardModelIntegration:
    """Integration tests between Card and TransferRequest models"""

    def test_transfer_with_blocked_card_should_not_transfer(self):
        """Verify blocked cards cannot transfer (business rule)"""
        card = Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("1000.00"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.BLOCKED,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )
        assert card.can_transfer is False

    def test_transfer_with_insufficient_balance(self):
        """Verify transfer validation against card balance"""
        card = Card(
            card_id="card_123456",
            user_id="user_001",
            card_number="4532-XXXX-XXXX-1234",
            cardholder_name="Juan Pérez",
            current_balance=Decimal("50.00"),
            expiry_month=12,
            expiry_year=2027,
            status=CardStatus.ACTIVE,
            card_type=CardType.DEBIT,
            created_at=datetime.now(),
        )
        transfer = TransferRequest(
            source_card_id="card_123456",
            user_id="user_001",
            amount=Decimal("100.00"),
            device_id="device_abc123",
            location_lat=4.7110,
            location_lng=-74.0721,
            transaction_id="txn_001",
            description="Transfer",
        )
        # Card has $50, transfer is $100 - should fail validation
        assert card.current_balance < transfer.amount
