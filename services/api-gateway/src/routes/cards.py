"""
Card API Routes - GET /cards endpoint
TASK-031 a TASK-040: Endpoint para listar tarjetas del usuario

Cumple con:
- REST API: GET /cards retorna lista de tarjetas
- Autenticación JWT: Requiere token válido
- Clean Architecture: Usa GetUserCardsUseCase
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "fraud-evaluation-service"))

from src.application.use_cases.get_user_cards import GetUserCardsUseCase
from src.domain.models import Card
from pydantic import BaseModel, Field


# DTOs (Data Transfer Objects)
class CardResponse(BaseModel):
    """
    TASK-037: Esquema de respuesta para una tarjeta
    
    Cumple con SEC-002: Solo expone últimos 4 dígitos del número
    """
    id: str = Field(..., description="ID único de la tarjeta")
    card_number: str = Field(..., description="Últimos 4 dígitos de la tarjeta (enmascarado)")
    card_type: str = Field(..., description="Tipo de tarjeta: DEBIT o CREDIT")
    balance: str = Field(..., description="Saldo formateado con 2 decimales")
    status: str = Field(..., description="Estado: ACTIVE, BLOCKED, SUSPENDED")
    nickname: str | None = Field(None, description="Alias opcional de la tarjeta")
    created_at: str = Field(..., description="Fecha de creación en formato ISO 8601")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "card_001",
                "card_number": "3456",
                "card_type": "DEBIT",
                "balance": "1500.00",
                "status": "ACTIVE",
                "nickname": "Mi Débito Principal",
                "created_at": "2026-01-28T10:00:00"
            }
        }


class GetCardsResponse(BaseModel):
    """
    TASK-037: Esquema de respuesta para GET /cards
    
    Retorna lista de hasta 3 tarjetas del usuario
    """
    cards: List[CardResponse] = Field(..., description="Lista de tarjetas del usuario (máximo 3)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cards": [
                    {
                        "id": "card_001",
                        "card_number": "3456",
                        "card_type": "DEBIT",
                        "balance": "1500.00",
                        "status": "ACTIVE",
                        "nickname": "Mi Débito Principal",
                        "created_at": "2026-01-28T10:00:00"
                    }
                ]
            }
        }


# Router
router = APIRouter(prefix="/cards", tags=["Cards"])


def _card_to_response(card: Card) -> CardResponse:
    """
    TASK-040: Convertir Card del dominio a CardResponse DTO
    
    Serialización:
    - Decimal → string con 2 decimales
    - Enum → string (nombre del enum)
    - datetime → ISO 8601 string
    """
    return CardResponse(
        id=card.id,
        card_number=card.mask_card_number(),  # Solo últimos 4 dígitos
        card_type=card.card_type.name,  # DEBIT o CREDIT (nombre del enum)
        balance=f"{card.balance:.2f}",  # Formato "XXXX.XX"
        status=card.status.name,  # ACTIVE, BLOCKED, SUSPENDED
        nickname=card.nickname,
        created_at=card.created_at.isoformat()  # Formato ISO 8601
    )


@router.get(
    "",
    response_model=GetCardsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener tarjetas del usuario",
    description="Retorna hasta 3 tarjetas del usuario autenticado, ordenadas por fecha de creación DESC"
)
async def get_user_cards(
    current_user_id: str = Depends(),  # Se inyectará desde JWT
    use_case: GetUserCardsUseCase = Depends()
) -> GetCardsResponse:
    """
    TASK-034: Endpoint GET /cards
    
    Args:
        current_user_id: ID del usuario desde JWT (inyectado)
        use_case: Caso de uso GetUserCardsUseCase (inyectado)
        
    Returns:
        GetCardsResponse con lista de tarjetas
        
    Raises:
        HTTPException 401: Si no está autenticado
        HTTPException 500: Si hay error interno
    """
    try:
        # TASK-038: Llamar caso de uso con user_id extraído del JWT
        cards = use_case.execute(user_id=current_user_id)
        
        # TASK-040: Convertir domain objects a DTOs
        card_responses = [_card_to_response(card) for card in cards]
        
        return GetCardsResponse(cards=card_responses)
        
    except Exception as e:
        # TASK-040: Manejo de errores internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cards: {str(e)}"
        )
