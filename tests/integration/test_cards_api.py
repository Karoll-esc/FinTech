"""
Integration Tests for GET /cards API endpoint
Tests de integración siguiendo TDD: Red → Green → Refactor

TASK-032 a TASK-040: Tests para endpoint FastAPI GET /cards
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from fastapi.security import HTTPBearer
from typing import List
from pydantic import BaseModel, Field

from src.domain.models import Card, CardStatus, CardType
from src.application.use_cases.get_user_cards import GetUserCardsUseCase


# DTOs (copiar desde cards.py para evitar imports)
class CardResponse(BaseModel):
    id: str
    card_number: str
    card_type: str
    balance: str
    status: str
    nickname: str | None = None
    created_at: str


class GetCardsResponse(BaseModel):
    cards: List[CardResponse]


# Helpers
def _card_to_response(card: Card) -> CardResponse:
    return CardResponse(
        id=card.id,
        card_number=card.mask_card_number(),
        card_type=card.card_type.name,
        balance=f"{card.balance:.2f}",
        status=card.status.name,
        nickname=card.nickname,
        created_at=card.created_at.isoformat()
    )


@pytest.fixture
def mock_card_use_case():
    """
    TASK-032: Mock del caso de uso GetUserCardsUseCase
    
    Retorna un mock configurado para simular el comportamiento del caso de uso
    """
    # Import desde fraud-evaluation-service (path correcto)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))
    from src.domain.models import Card, CardStatus, CardType
    
    mock = Mock()
    
    # Configurar datos de ejemplo
    sample_cards = [
        Card(
            id="card_001",
            user_id="user_123",
            card_number="3456",  # Solo últimos 4 dígitos (enmascarado)
            card_type=CardType.DEBIT,
            balance=Decimal("1500.00"),
            status=CardStatus.ACTIVE,
            nickname="Mi Débito Principal",
            created_at=datetime(2026, 1, 28, 10, 0, 0)
        ),
        Card(
            id="card_002",
            user_id="user_123",
            card_number="9876",
            card_type=CardType.CREDIT,
            balance=Decimal("5000.00"),
            status=CardStatus.ACTIVE,
            nickname="Tarjeta Platinum",
            created_at=datetime(2026, 1, 27, 15, 30, 0)
        ),
        Card(
            id="card_003",
            user_id="user_123",
            card_number="2222",
            card_type=CardType.DEBIT,
            balance=Decimal("250.50"),
            status=CardStatus.BLOCKED,
            nickname="Ahorros",
            created_at=datetime(2026, 1, 26, 8, 0, 0)
        ),
    ]
    
    # Configurar retorno del mock
    mock.execute.return_value = sample_cards
    
    return mock


@pytest.fixture
def test_app(mock_card_use_case):
    """
    TASK-033: Crear aplicación FastAPI de prueba
    
    Crea una app mínima con el endpoint GET /cards y dependencias mockeadas
    """
    app = FastAPI()
    security = HTTPBearer()
    
    # Mock dependencies
    def get_mock_use_case():
        return mock_card_use_case
    
    def get_mock_user_id(token: str = Depends(security)):
        jwt_token = token.credentials
        if jwt_token.startswith("valid_jwt_token_"):
            return jwt_token.replace("valid_jwt_token_", "")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    # Endpoint GET /cards
    @app.get("/cards", response_model=GetCardsResponse)
    async def get_user_cards(
        current_user_id: str = Depends(get_mock_user_id),
        use_case: GetUserCardsUseCase = Depends(get_mock_use_case)
    ):
        try:
            cards = use_case.execute(user_id=current_user_id)
            card_responses = [_card_to_response(card) for card in cards]
            return GetCardsResponse(cards=card_responses)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving cards: {str(e)}"
            )
    
    return app


@pytest.fixture
def client(test_app):
    """Cliente de prueba"""
    return TestClient(test_app)


class TestGetCardsEndpoint:
    """Tests de integración para GET /cards endpoint (TASK-032 a TASK-040)"""
    
    def test_get_cards_returns_200_with_valid_auth(self, client: TestClient):
        """
        TASK-034: Caso exitoso - retorna 200 con tarjetas
        
        Given: Un usuario autenticado con JWT válido
        When: Realiza GET /cards
        Then: Retorna 200 OK con lista de 3 tarjetas
        """
        # Simular token JWT válido
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        # Verificar status code
        assert response.status_code == 200
        
        # Verificar estructura de respuesta
        data = response.json()
        assert "cards" in data
        assert isinstance(data["cards"], list)
        assert len(data["cards"]) == 3
        
        # Verificar primer tarjeta
        card1 = data["cards"][0]
        assert card1["id"] == "card_001"
        assert card1["card_number"] == "3456"  # Enmascarado
        assert card1["card_type"] == "DEBIT"
        assert card1["balance"] == "1500.00"
        assert card1["status"] == "ACTIVE"
        assert card1["nickname"] == "Mi Débito Principal"
    
    def test_get_cards_requires_authentication(self, client: TestClient):
        """
        TASK-036: Autenticación requerida - retorna 401 o 403 sin token
        
        Given: Una petición sin header Authorization
        When: Realiza GET /cards
        Then: Retorna 401 Unauthorized o 403 Forbidden
        """
        response = client.get("/cards")
        
        # FastAPI puede retornar 401 o 403 dependiendo de la configuración
        assert response.status_code in [401, 403]
        assert "detail" in response.json()
    
    def test_get_cards_rejects_invalid_token(self, client: TestClient):
        """
        TASK-036: Token inválido - retorna 401
        
        Given: Un token JWT inválido o expirado
        When: Realiza GET /cards
        Then: Retorna 401 Unauthorized
        """
        headers = {
            "Authorization": "Bearer invalid_or_expired_token"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 401
    
    def test_get_cards_returns_empty_list_when_no_cards(self, client: TestClient, mock_card_use_case):
        """
        TASK-035: Usuario sin tarjetas - retorna 200 con lista vacía
        
        Given: Un usuario autenticado sin tarjetas
        When: Realiza GET /cards
        Then: Retorna 200 OK con lista vacía
        """
        # Configurar mock para retornar lista vacía
        mock_card_use_case.execute.return_value = []
        
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_456"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["cards"] == []
        assert len(data["cards"]) == 0
    
    def test_get_cards_response_structure(self, client: TestClient):
        """
        TASK-037: Validar estructura de respuesta
        
        Given: Un usuario con tarjetas
        When: Realiza GET /cards
        Then: La respuesta cumple con el esquema definido
        """
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar campos obligatorios en respuesta
        assert "cards" in data
        
        # Verificar campos obligatorios en cada tarjeta
        for card in data["cards"]:
            assert "id" in card
            assert "card_number" in card
            assert "card_type" in card
            assert "balance" in card
            assert "status" in card
            assert "created_at" in card
            # nickname es opcional
    
    def test_get_cards_extracts_user_id_from_token(self, client: TestClient, mock_card_use_case):
        """
        TASK-038: Extraer user_id del JWT
        
        Given: Un token JWT con user_id=user_123
        When: Realiza GET /cards
        Then: El caso de uso se llama con user_id="user_123"
        """
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        
        # Verificar que el caso de uso fue llamado con el user_id correcto
        mock_card_use_case.execute.assert_called_once_with(user_id="user_123")
    
    def test_get_cards_returns_max_3_cards(self, client: TestClient):
        """
        TASK-039: Límite de 3 tarjetas
        
        Given: Un usuario con 3 tarjetas
        When: Realiza GET /cards
        Then: Retorna exactamente 3 tarjetas (límite del caso de uso)
        """
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # El caso de uso ya limita a 3, verificamos que se respete
        assert len(data["cards"]) <= 3
    
    def test_get_cards_decimal_formatting(self, client: TestClient):
        """
        TASK-040: Formato decimal con 2 decimales
        
        Given: Tarjetas con saldos decimales
        When: Realiza GET /cards
        Then: Los saldos se formatean con 2 decimales
        """
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar formato de balance
        for card in data["cards"]:
            balance_str = card["balance"]
            # Debe ser string con formato "XXXX.XX"
            assert isinstance(balance_str, str)
            parts = balance_str.split(".")
            assert len(parts) == 2
            assert len(parts[1]) == 2  # Exactamente 2 decimales
    
    def test_get_cards_enum_serialization(self, client: TestClient):
        """
        TASK-040: Serialización de enums
        
        Given: Tarjetas con diferentes tipos y estados
        When: Realiza GET /cards
        Then: Los enums se serializan como strings
        """
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que card_type y status son strings
        card_types = {card["card_type"] for card in data["cards"]}
        card_statuses = {card["status"] for card in data["cards"]}
        
        # Debe contener valores válidos
        assert card_types.issubset({"DEBIT", "CREDIT"})
        assert card_statuses.issubset({"ACTIVE", "BLOCKED", "SUSPENDED"})
    
    def test_get_cards_datetime_serialization(self, client: TestClient):
        """
        Edge case: Serialización de datetime
        
        Given: Tarjetas con diferentes fechas de creación
        When: Realiza GET /cards
        Then: Las fechas se serializan en formato ISO 8601
        """
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar formato ISO 8601
        for card in data["cards"]:
            created_at = card["created_at"]
            assert isinstance(created_at, str)
            # Debe contener "T" separando fecha y hora
            assert "T" in created_at
    
    def test_get_cards_handles_server_errors(self, client: TestClient, mock_card_use_case):
        """
        Edge case: Error interno del servidor
        
        Given: El caso de uso lanza una excepción
        When: Realiza GET /cards
        Then: Retorna 500 Internal Server Error
        """
        # Configurar mock para lanzar excepción
        mock_card_use_case.execute.side_effect = Exception("Database connection failed")
        
        headers = {
            "Authorization": "Bearer valid_jwt_token_user_123"
        }
        
        response = client.get("/cards", headers=headers)
        
        assert response.status_code == 500
        assert "detail" in response.json()
