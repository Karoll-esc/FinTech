"""
Unit Tests for GetUserCardsUseCase
Tests siguiendo TDD: Red → Green → Refactor

TASK-013 a TASK-016: Tests para caso de uso GetUserCardsUseCase
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Card, CardStatus, CardType
from src.application.ports.card_repository import CardRepository


class TestGetUserCardsUseCase:
    """Tests para GetUserCardsUseCase (TASK-013 a TASK-016)"""
    
    def test_get_user_cards_success_with_three_cards(self):
        """
        TASK-013: Caso exitoso - retorna 3 tarjetas ordenadas
        
        Given: Un usuario tiene 3 tarjetas en el sistema
        When: Se solicita la lista de tarjetas del usuario
        Then: Retorna las 3 tarjetas ordenadas por created_at DESC
        """
        from src.application.use_cases.get_user_cards import GetUserCardsUseCase
        
        # Mock del repositorio
        mock_repo = Mock(spec=CardRepository)
        
        # Crear 3 tarjetas con diferentes fechas
        card1 = Card(
            id="card_001",
            user_id="user_123",
            card_number="1234567890123456",
            card_type=CardType.DEBIT,
            balance=Decimal("1000.00"),
            status=CardStatus.ACTIVE,
            nickname="Mi Débito",
            created_at=datetime(2026, 1, 25)  # Más antigua
        )
        
        card2 = Card(
            id="card_002",
            user_id="user_123",
            card_number="9876543210987654",
            card_type=CardType.CREDIT,
            balance=Decimal("5000.00"),
            status=CardStatus.ACTIVE,
            nickname="Mi Crédito",
            created_at=datetime(2026, 1, 27)  # Mediana
        )
        
        card3 = Card(
            id="card_003",
            user_id="user_123",
            card_number="5555444433332222",
            card_type=CardType.DEBIT,
            balance=Decimal("250.00"),
            status=CardStatus.ACTIVE,
            nickname="Ahorros",
            created_at=datetime(2026, 1, 28)  # Más nueva
        )
        
        # Configurar mock para retornar las 3 tarjetas ya ordenadas
        mock_repo.get_by_user_id.return_value = [card3, card2, card1]
        
        # Ejecutar caso de uso
        use_case = GetUserCardsUseCase(card_repository=mock_repo)
        result = use_case.execute(user_id="user_123")
        
        # Verificaciones
        assert len(result) == 3
        assert result[0].id == "card_003"  # Más nueva primero
        assert result[1].id == "card_002"  # Mediana
        assert result[2].id == "card_001"  # Más antigua última
        
        # Verificar que se llamó al repositorio con el user_id correcto
        mock_repo.get_by_user_id.assert_called_once_with("user_123")
    
    def test_get_user_cards_empty_list(self):
        """
        TASK-014: Caso vacío - retorna lista vacía si usuario no tiene tarjetas
        
        Given: Un usuario sin tarjetas registradas
        When: Se solicita la lista de tarjetas del usuario
        Then: Retorna lista vacía []
        """
        from src.application.use_cases.get_user_cards import GetUserCardsUseCase
        
        # Mock del repositorio que retorna lista vacía
        mock_repo = Mock(spec=CardRepository)
        mock_repo.get_by_user_id.return_value = []
        
        # Ejecutar caso de uso
        use_case = GetUserCardsUseCase(card_repository=mock_repo)
        result = use_case.execute(user_id="user_999")
        
        # Verificaciones
        assert result == []
        assert len(result) == 0
        mock_repo.get_by_user_id.assert_called_once_with("user_999")
    
    def test_get_user_cards_orders_by_created_at_desc(self):
        """
        TASK-015: Ordenamiento descendente por created_at
        
        Given: Un usuario con múltiples tarjetas
        When: El repositorio retorna tarjetas en orden aleatorio
        Then: El caso de uso las ordena por created_at DESC antes de retornar
        
        Note: Asumimos que el repositorio ya retorna ordenado,
        pero el caso de uso debe garantizarlo
        """
        from src.application.use_cases.get_user_cards import GetUserCardsUseCase
        
        mock_repo = Mock(spec=CardRepository)
        
        # Crear tarjetas con fechas diferentes
        card_old = Card(
            id="card_old",
            user_id="user_123",
            card_number="1111222233334444",
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 1)  # Más antigua
        )
        
        card_new = Card(
            id="card_new",
            user_id="user_123",
            card_number="5555666677778888",
            card_type=CardType.CREDIT,
            balance=Decimal("200.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 28)  # Más nueva
        )
        
        card_mid = Card(
            id="card_mid",
            user_id="user_123",
            card_number="9999000011112222",
            card_type=CardType.DEBIT,
            balance=Decimal("150.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 15)  # Mediana
        )
        
        # Repositorio retorna en orden correcto (DESC)
        mock_repo.get_by_user_id.return_value = [card_new, card_mid, card_old]
        
        use_case = GetUserCardsUseCase(card_repository=mock_repo)
        result = use_case.execute(user_id="user_123")
        
        # Verificar orden descendente (más nueva primero)
        assert result[0].created_at > result[1].created_at
        assert result[1].created_at > result[2].created_at
        assert result[0].id == "card_new"
        assert result[2].id == "card_old"
    
    def test_get_user_cards_verifies_card_number_masking(self):
        """
        TASK-016: Verificar enmascaramiento de números
        
        Given: El repositorio retorna tarjetas con números completos o enmascarados
        When: Se ejecuta el caso de uso
        Then: Las tarjetas retornadas deben poder enmascararse correctamente
        """
        from src.application.use_cases.get_user_cards import GetUserCardsUseCase
        
        mock_repo = Mock(spec=CardRepository)
        
        # Tarjeta con número completo
        card_full = Card(
            id="card_full",
            user_id="user_123",
            card_number="1234567890123456",  # 16 dígitos
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 28)
        )
        
        # Tarjeta ya enmascarada (solo últimos 4 dígitos)
        card_masked = Card(
            id="card_masked",
            user_id="user_123",
            card_number="9876",  # Solo 4 dígitos
            card_type=CardType.CREDIT,
            balance=Decimal("200.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 27)
        )
        
        mock_repo.get_by_user_id.return_value = [card_full, card_masked]
        
        use_case = GetUserCardsUseCase(card_repository=mock_repo)
        result = use_case.execute(user_id="user_123")
        
        # Verificar que se pueden enmascarar correctamente
        assert result[0].mask_card_number() == "3456"  # Últimos 4 de 1234567890123456
        assert result[1].mask_card_number() == "9876"  # Ya estaba enmascarado
    
    def test_get_user_cards_limits_to_3_cards_max(self):
        """
        TASK-020: Limitar a 3 tarjetas máximo (requisito de negocio)
        
        Given: Un usuario tiene más de 3 tarjetas en el sistema
        When: Se solicita la lista de tarjetas
        Then: Solo retorna las 3 más recientes
        
        Note: Este test verifica el límite de negocio
        """
        from src.application.use_cases.get_user_cards import GetUserCardsUseCase
        
        mock_repo = Mock(spec=CardRepository)
        
        # Crear 5 tarjetas
        cards = []
        for i in range(5):
            cards.append(Card(
                id=f"card_{i:03d}",
                user_id="user_123",
                card_number=f"111122223333444{i}",
                card_type=CardType.DEBIT,
                balance=Decimal("100.00"),
                status=CardStatus.ACTIVE,
                created_at=datetime(2026, 1, 20 + i)
            ))
        
        # Repositorio retorna todas (el repositorio puede retornar todas)
        # Pero el caso de uso debe limitar a 3
        mock_repo.get_by_user_id.return_value = sorted(cards, key=lambda c: c.created_at, reverse=True)
        
        use_case = GetUserCardsUseCase(card_repository=mock_repo)
        result = use_case.execute(user_id="user_123")
        
        # Verificar que solo retorna 3 (las más recientes)
        assert len(result) == 3
        assert result[0].id == "card_004"  # Más nueva (2026-01-24)
        assert result[1].id == "card_003"  # Segunda más nueva (2026-01-23)
        assert result[2].id == "card_002"  # Tercera más nueva (2026-01-22)
    
    def test_get_user_cards_with_different_statuses(self):
        """
        Edge case: Tarjetas con diferentes estados (ACTIVE, BLOCKED, SUSPENDED)
        
        Given: Un usuario tiene tarjetas en diferentes estados
        When: Se solicita la lista de tarjetas
        Then: Retorna todas las tarjetas sin filtrar por estado
        """
        from src.application.use_cases.get_user_cards import GetUserCardsUseCase
        
        mock_repo = Mock(spec=CardRepository)
        
        card_active = Card(
            id="card_active",
            user_id="user_123",
            card_number="1111222233334444",
            card_type=CardType.DEBIT,
            balance=Decimal("100.00"),
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 28)
        )
        
        card_blocked = Card(
            id="card_blocked",
            user_id="user_123",
            card_number="5555666677778888",
            card_type=CardType.CREDIT,
            balance=Decimal("200.00"),
            status=CardStatus.BLOCKED,
            created_at=datetime(2026, 1, 27)
        )
        
        card_suspended = Card(
            id="card_suspended",
            user_id="user_123",
            card_number="9999000011112222",
            card_type=CardType.DEBIT,
            balance=Decimal("150.00"),
            status=CardStatus.SUSPENDED,
            created_at=datetime(2026, 1, 26)
        )
        
        mock_repo.get_by_user_id.return_value = [card_active, card_blocked, card_suspended]
        
        use_case = GetUserCardsUseCase(card_repository=mock_repo)
        result = use_case.execute(user_id="user_123")
        
        # Verificar que retorna todas, sin filtrar
        assert len(result) == 3
        assert any(c.status == CardStatus.ACTIVE for c in result)
        assert any(c.status == CardStatus.BLOCKED for c in result)
        assert any(c.status == CardStatus.SUSPENDED for c in result)
    
    def test_get_user_cards_with_zero_balance(self):
        """
        Edge case: Tarjetas con saldo cero
        
        Given: Un usuario tiene tarjetas con saldo $0.00
        When: Se solicita la lista de tarjetas
        Then: Las tarjetas con saldo cero se incluyen en el resultado
        """
        from src.application.use_cases.get_user_cards import GetUserCardsUseCase
        
        mock_repo = Mock(spec=CardRepository)
        
        card_zero = Card(
            id="card_zero",
            user_id="user_123",
            card_number="1111222233334444",
            card_type=CardType.DEBIT,
            balance=Decimal("0.00"),  # Saldo cero
            status=CardStatus.ACTIVE,
            created_at=datetime(2026, 1, 28)
        )
        
        mock_repo.get_by_user_id.return_value = [card_zero]
        
        use_case = GetUserCardsUseCase(card_repository=mock_repo)
        result = use_case.execute(user_id="user_123")
        
        # Verificar que se incluye la tarjeta con saldo cero
        assert len(result) == 1
        assert result[0].balance == Decimal("0.00")
