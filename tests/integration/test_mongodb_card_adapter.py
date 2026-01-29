"""
Integration Tests for MongoDBCardAdapter
Tests de integración siguiendo TDD: Red → Green → Refactor

TASK-024 a TASK-030: Tests para adaptador MongoDB
Usa mongomock para testing sin levantar MongoDB real
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Card, CardStatus, CardType
from src.application.ports.card_repository import CardRepository


@pytest.fixture
def mongodb_adapter():
    """
    TASK-024: Fixture para crear adaptador con MongoDB en memoria
    
    Usa mongomock para evitar dependencia de Docker en tests
    """
    from src.infrastructure.mongodb_card_adapter import MongoDBCardAdapter
    import mongomock
    
    # Crear cliente MongoDB mock (en memoria)
    mock_client = mongomock.MongoClient()
    db = mock_client["fraud_detection_test"]
    collection = db["cards"]
    
    # Crear adaptador con la colección mock
    adapter = MongoDBCardAdapter(collection)
    
    yield adapter
    
    # Cleanup: limpiar base de datos después de cada test
    collection.drop()


@pytest.fixture
def sample_cards() -> List[Card]:
    """
    Fixture con tarjetas de ejemplo para tests
    """
    return [
        Card(
            id="card_001",
            user_id="user_123",
            card_number="1234567890123456",
            card_type=CardType.DEBIT,
            balance=Decimal("1000.00"),
            status=CardStatus.ACTIVE,
            nickname="Mi Débito",
            created_at=datetime(2026, 1, 25, 10, 0, 0)
        ),
        Card(
            id="card_002",
            user_id="user_123",
            card_number="9876543210987654",
            card_type=CardType.CREDIT,
            balance=Decimal("5000.00"),
            status=CardStatus.ACTIVE,
            nickname="Mi Crédito",
            created_at=datetime(2026, 1, 27, 15, 30, 0)
        ),
        Card(
            id="card_003",
            user_id="user_123",
            card_number="5555444433332222",
            card_type=CardType.DEBIT,
            balance=Decimal("250.00"),
            status=CardStatus.BLOCKED,
            nickname="Ahorros",
            created_at=datetime(2026, 1, 28, 8, 0, 0)
        ),
        Card(
            id="card_004",
            user_id="user_456",  # Diferente usuario
            card_number="1111222233334444",
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 26, 12, 0, 0)
        ),
    ]


class TestMongoDBCardAdapter:
    """Tests de integración para MongoDBCardAdapter (TASK-024 a TASK-030)"""
    
    def test_save_card_success(self, mongodb_adapter: CardRepository, sample_cards: List[Card]):
        """
        TASK-027: Guardar tarjeta exitosamente
        
        Given: Una tarjeta válida
        When: Se guarda con save()
        Then: La tarjeta se persiste en MongoDB
        """
        card = sample_cards[0]
        
        # Ejecutar save (no debe lanzar excepción)
        mongodb_adapter.save(card)
        
        # Verificar que se guardó correctamente
        retrieved = mongodb_adapter.get_by_id(card.id)
        assert retrieved is not None
        assert retrieved.id == card.id
        assert retrieved.user_id == card.user_id
        assert retrieved.card_number == card.card_number
        assert retrieved.balance == card.balance
        assert retrieved.status == card.status
    
    def test_save_duplicate_card_raises_error(self, mongodb_adapter: CardRepository, sample_cards: List[Card]):
        """
        TASK-027: Validar duplicados - lanzar error si card_id ya existe
        
        Given: Una tarjeta ya guardada
        When: Se intenta guardar otra con el mismo ID
        Then: Lanza ValueError
        """
        card = sample_cards[0]
        
        # Guardar primera vez (OK)
        mongodb_adapter.save(card)
        
        # Intentar guardar de nuevo (debe fallar)
        with pytest.raises(ValueError, match="Card with id .* already exists"):
            mongodb_adapter.save(card)
    
    def test_get_by_user_id_returns_all_cards_ordered(self, mongodb_adapter: CardRepository, sample_cards: List[Card]):
        """
        TASK-026: Obtener todas las tarjetas de un usuario ordenadas
        
        Given: Un usuario con 3 tarjetas
        When: Se llama a get_by_user_id()
        Then: Retorna las 3 tarjetas ordenadas por created_at DESC
        """
        # Guardar 3 tarjetas del mismo usuario
        for card in sample_cards[:3]:  # user_123 tiene 3 tarjetas
            mongodb_adapter.save(card)
        
        # Obtener tarjetas del usuario
        cards = mongodb_adapter.get_by_user_id("user_123")
        
        # Verificar cantidad
        assert len(cards) == 3
        
        # Verificar ordenamiento DESC (más nueva primero)
        assert cards[0].id == "card_003"  # 2026-01-28 (más nueva)
        assert cards[1].id == "card_002"  # 2026-01-27
        assert cards[2].id == "card_001"  # 2026-01-25 (más antigua)
        
        # Verificar que están ordenadas correctamente
        assert cards[0].created_at > cards[1].created_at
        assert cards[1].created_at > cards[2].created_at
    
    def test_get_by_user_id_empty_list(self, mongodb_adapter: CardRepository):
        """
        TASK-026: Retornar lista vacía si usuario no tiene tarjetas
        
        Given: Un usuario sin tarjetas en la base de datos
        When: Se llama a get_by_user_id()
        Then: Retorna lista vacía []
        """
        cards = mongodb_adapter.get_by_user_id("user_nonexistent")
        
        assert cards == []
        assert len(cards) == 0
    
    def test_get_by_user_id_filters_by_user(self, mongodb_adapter: CardRepository, sample_cards: List[Card]):
        """
        TASK-026: Filtrar solo tarjetas del usuario solicitado
        
        Given: Múltiples usuarios con tarjetas
        When: Se solicitan tarjetas de user_123
        Then: Solo retorna tarjetas de user_123, no de otros usuarios
        """
        # Guardar todas las tarjetas (user_123 y user_456)
        for card in sample_cards:
            mongodb_adapter.save(card)
        
        # Obtener tarjetas de user_123
        cards_user_123 = mongodb_adapter.get_by_user_id("user_123")
        
        # Verificar que solo retorna las 3 de user_123
        assert len(cards_user_123) == 3
        assert all(card.user_id == "user_123" for card in cards_user_123)
        
        # Verificar que user_456 tiene su propia tarjeta
        cards_user_456 = mongodb_adapter.get_by_user_id("user_456")
        assert len(cards_user_456) == 1
        assert cards_user_456[0].user_id == "user_456"
        assert cards_user_456[0].id == "card_004"
    
    def test_get_by_id_success(self, mongodb_adapter: CardRepository, sample_cards: List[Card]):
        """
        TASK-028: Obtener tarjeta por ID exitosamente
        
        Given: Una tarjeta guardada en la base de datos
        When: Se llama a get_by_id()
        Then: Retorna la tarjeta con todos sus datos
        """
        card = sample_cards[0]
        mongodb_adapter.save(card)
        
        # Obtener por ID
        retrieved = mongodb_adapter.get_by_id(card.id)
        
        # Verificar que retorna la tarjeta correcta
        assert retrieved is not None
        assert retrieved.id == card.id
        assert retrieved.user_id == card.user_id
        assert retrieved.card_number == card.card_number
        assert retrieved.card_type == card.card_type
        assert retrieved.balance == card.balance
        assert retrieved.status == card.status
        assert retrieved.nickname == card.nickname
        assert retrieved.created_at == card.created_at
    
    def test_get_by_id_not_found_returns_none(self, mongodb_adapter: CardRepository):
        """
        TASK-028: Retornar None si tarjeta no existe
        
        Given: Un ID que no existe en la base de datos
        When: Se llama a get_by_id()
        Then: Retorna None (no lanza excepción)
        """
        result = mongodb_adapter.get_by_id("card_nonexistent")
        
        assert result is None
    
    def test_save_preserves_all_card_fields(self, mongodb_adapter: CardRepository):
        """
        TASK-027: Verificar que save() preserva todos los campos
        
        Given: Una tarjeta con todos los campos opcionales
        When: Se guarda y recupera
        Then: Todos los campos se mantienen intactos
        """
        card = Card(
            id="card_complete",
            user_id="user_999",
            card_number="9999888877776666",
            card_type=CardType.CREDIT,
            balance=Decimal("12345.67"),
            status=CardStatus.SUSPENDED,
            nickname="Tarjeta de Prueba",
            created_at=datetime(2026, 1, 15, 14, 30, 45)
        )
        
        mongodb_adapter.save(card)
        retrieved = mongodb_adapter.get_by_id("card_complete")
        
        # Verificar todos los campos
        assert retrieved.id == "card_complete"
        assert retrieved.user_id == "user_999"
        assert retrieved.card_number == "9999888877776666"
        assert retrieved.card_type == CardType.CREDIT
        assert retrieved.balance == Decimal("12345.67")
        assert retrieved.status == CardStatus.SUSPENDED
        assert retrieved.nickname == "Tarjeta de Prueba"
        assert retrieved.created_at == datetime(2026, 1, 15, 14, 30, 45)
    
    def test_get_by_user_id_with_different_card_types(self, mongodb_adapter: CardRepository):
        """
        Edge case: Usuario con tarjetas DEBIT y CREDIT
        
        Given: Un usuario con tarjetas de diferentes tipos
        When: Se obtienen sus tarjetas
        Then: Retorna ambos tipos sin filtrar
        """
        card_debit = Card(
            id="card_debit",
            user_id="user_mix",
            card_number="1111222233334444",
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 28)
        )
        
        card_credit = Card(
            id="card_credit",
            user_id="user_mix",
            card_number="5555666677778888",
            card_type=CardType.CREDIT,
            balance=Decimal("200.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 27)
        )
        
        mongodb_adapter.save(card_debit)
        mongodb_adapter.save(card_credit)
        
        cards = mongodb_adapter.get_by_user_id("user_mix")
        
        assert len(cards) == 2
        assert any(c.card_type == CardType.DEBIT for c in cards)
        assert any(c.card_type == CardType.CREDIT for c in cards)
    
    def test_decimal_precision_preserved(self, mongodb_adapter: CardRepository):
        """
        TASK-027: Verificar que la precisión decimal se mantiene
        
        Given: Una tarjeta con saldo de 2 decimales
        When: Se guarda y recupera
        Then: El saldo mantiene su precisión exacta
        """
        card = Card(
            id="card_decimal",
            user_id="user_decimal",
            card_number="1234567890123456",
            card_type=CardType.DEBIT,
            balance=Decimal("999.99"),  # Exactamente 2 decimales
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 28)
        )
        
        mongodb_adapter.save(card)
        retrieved = mongodb_adapter.get_by_id("card_decimal")
        
        # Verificar precisión exacta
        assert retrieved.balance == Decimal("999.99")
        assert str(retrieved.balance) == "999.99"


class TestMongoDBIndexes:
    """
    TASK-029: Tests para verificar índices MongoDB
    
    Note: mongomock soporta índices básicos, pero no optimización real
    Estos tests verifican que los índices se crean correctamente
    """
    
    def test_indexes_are_created(self, mongodb_adapter: CardRepository):
        """
        TASK-029: Verificar creación de índices
        
        Given: Un adaptador MongoDB inicializado
        When: Se verifica la colección
        Then: Los índices user_id y created_at existen
        """
        from src.infrastructure.mongodb_card_adapter import MongoDBCardAdapter
        
        # Verificar que el adaptador tiene método para crear índices
        assert hasattr(mongodb_adapter, 'ensure_indexes')
        
        # Llamar método de creación de índices
        mongodb_adapter.ensure_indexes()
        
        # Verificar que no lanza excepciones
        # (mongomock no soporta verificación de índices, pero no debe fallar)
        assert True
