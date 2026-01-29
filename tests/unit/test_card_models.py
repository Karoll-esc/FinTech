"""
Unit Tests for Card Domain Models
Tests siguiendo TDD: Red → Green → Refactor

TASK-001 a TASK-005: Tests para Card, CardStatus, CardType
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Card, CardStatus, CardType


class TestCardStatus:
    """Tests para CardStatus enum (TASK-003)"""
    
    def test_card_status_enum_has_active(self):
        """Enum debe tener valor ACTIVE"""
        assert hasattr(CardStatus, 'ACTIVE')
        assert CardStatus.ACTIVE.value == 1
    
    def test_card_status_enum_has_blocked(self):
        """Enum debe tener valor BLOCKED"""
        assert hasattr(CardStatus, 'BLOCKED')
        assert CardStatus.BLOCKED.value == 2
    
    def test_card_status_enum_has_suspended(self):
        """Enum debe tener valor SUSPENDED"""
        assert hasattr(CardStatus, 'SUSPENDED')
        assert CardStatus.SUSPENDED.value == 3
    
    def test_card_status_enum_values_are_comparable(self):
        """Los valores numéricos permiten comparación por gravedad"""
        assert CardStatus.ACTIVE.value < CardStatus.BLOCKED.value
        assert CardStatus.BLOCKED.value < CardStatus.SUSPENDED.value


class TestCardType:
    """Tests para CardType enum (TASK-004)"""
    
    def test_card_type_enum_has_debit(self):
        """Enum debe tener valor DEBIT"""
        assert hasattr(CardType, 'DEBIT')
        assert CardType.DEBIT.value == 1
    
    def test_card_type_enum_has_credit(self):
        """Enum debe tener valor CREDIT"""
        assert hasattr(CardType, 'CREDIT')
        assert CardType.CREDIT.value == 2


class TestCardModel:
    """Tests para Card value object (TASK-001, TASK-002, TASK-005)"""
    
    def test_card_creation_with_valid_data(self):
        """TASK-001: Crear Card válida con todos los campos"""
        card = Card(
            id="card_123",
            user_id="user_456",
            card_number="1234567890123456",  # 16 dígitos
            card_type=CardType.DEBIT,
            balance=Decimal("1500.00"),
            status=CardStatus.ACTIVE,
            nickname="Mi Débito",
            created_at=datetime.now()
        )
        
        assert card.id == "card_123"
        assert card.user_id == "user_456"
        assert card.card_number == "1234567890123456"
        assert card.card_type == CardType.DEBIT
        assert card.balance == Decimal("1500.00")
        assert card.status == CardStatus.ACTIVE
        assert card.nickname == "Mi Débito"
    
    def test_card_mask_number_shows_only_last_4_digits(self):
        """TASK-002: Verificar enmascaramiento muestra solo últimos 4 dígitos"""
        card = Card(
            id="card_123",
            user_id="user_456",
            card_number="1234567890123456",
            card_type=CardType.CREDIT,
            balance=Decimal("500.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        masked = card.mask_card_number()
        
        # Debe retornar solo últimos 4 dígitos: "3456"
        assert masked == "3456"
        assert len(masked) == 4
    
    def test_card_mask_number_different_card(self):
        """TASK-002: Enmascaramiento con diferentes números"""
        card = Card(
            id="card_789",
            user_id="user_456",
            card_number="9876543210987654",
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        masked = card.mask_card_number()
        
        assert masked == "7654"
    
    def test_card_negative_balance_raises_error(self):
        """TASK-005: Saldo negativo debe lanzar ValueError"""
        with pytest.raises(ValueError, match="Balance cannot be negative"):
            Card(
                id="card_123",
                user_id="user_456",
                card_number="1234567890123456",
                card_type=CardType.DEBIT,
                balance=Decimal("-100.00"),  # Saldo negativo!
                status=CardStatus.ACTIVE,
                created_at=datetime.now()
            )
    
    def test_card_zero_balance_allowed(self):
        """TASK-005: Saldo cero debe ser permitido (edge case)"""
        card = Card(
            id="card_123",
            user_id="user_456",
            card_number="1234567890123456",
            card_type=CardType.DEBIT,
            balance=Decimal("0.00"),  # Saldo cero es válido
            status=CardStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        assert card.balance == Decimal("0.00")
    
    def test_card_number_must_be_16_digits(self):
        """TASK-010: Validar longitud del número de tarjeta"""
        with pytest.raises(ValueError, match="Card number must be 16 digits"):
            Card(
                id="card_123",
                user_id="user_456",
                card_number="12345",  # Solo 5 dígitos
                card_type=CardType.DEBIT,
                balance=Decimal("100.00"),
                status=CardStatus.ACTIVE,
                created_at=datetime.now()
            )
    
    def test_card_number_must_be_numeric(self):
        """TASK-010: Número de tarjeta debe ser numérico"""
        with pytest.raises(ValueError, match="Card number must contain only digits"):
            Card(
                id="card_123",
                user_id="user_456",
                card_number="123456789012345X",  # Contiene letra
                card_type=CardType.DEBIT,
                balance=Decimal("100.00"),
                status=CardStatus.ACTIVE,
                created_at=datetime.now()
            )
    
    def test_card_id_cannot_be_empty(self):
        """TASK-010: ID de tarjeta no puede estar vacío"""
        with pytest.raises(ValueError, match="Card ID cannot be empty"):
            Card(
                id="",  # ID vacío
                user_id="user_456",
                card_number="1234567890123456",
                card_type=CardType.DEBIT,
                balance=Decimal("100.00"),
                status=CardStatus.ACTIVE,
                created_at=datetime.now()
            )
    
    def test_card_user_id_cannot_be_empty(self):
        """TASK-010: User ID no puede estar vacío"""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            Card(
                id="card_123",
                user_id="",  # User ID vacío
                card_number="1234567890123456",
                card_type=CardType.DEBIT,
                balance=Decimal("100.00"),
                status=CardStatus.ACTIVE,
                created_at=datetime.now()
            )
    
    def test_card_nickname_is_optional(self):
        """TASK-010: Nickname es opcional"""
        card = Card(
            id="card_123",
            user_id="user_456",
            card_number="1234567890123456",
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            nickname=None,  # Sin nickname
            created_at=datetime.now()
        )
        
        assert card.nickname is None
    
    def test_card_is_immutable(self):
        """TASK-011: Card debe ser inmutable (frozen=True)"""
        card = Card(
            id="card_123",
            user_id="user_456",
            card_number="1234567890123456",
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        # Intentar modificar debe fallar
        with pytest.raises(AttributeError):
            card.balance = Decimal("200.00")
    
    def test_card_with_blocked_status(self):
        """Edge case: Tarjeta bloqueada"""
        card = Card(
            id="card_123",
            user_id="user_456",
            card_number="1234567890123456",
            card_type=CardType.CREDIT,
            balance=Decimal("5000.00"),
            status=CardStatus.BLOCKED,
            created_at=datetime.now()
        )
        
        assert card.status == CardStatus.BLOCKED
    
    def test_card_with_suspended_status(self):
        """Edge case: Tarjeta suspendida"""
        card = Card(
            id="card_123",
            user_id="user_456",
            card_number="1234567890123456",
            card_type=CardType.DEBIT,
            balance=Decimal("250.00"),
            status=CardStatus.SUSPENDED,
            created_at=datetime.now()
        )
        
        assert card.status == CardStatus.SUSPENDED
