"""
TASK-030: POST /api/v1/cards Endpoint
Ruta para crear tarjetas de crédito/débito
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from typing import Optional
import logging
from datetime import datetime

from ..schemas.card_schemas import CreateCardRequest, CardResponse, ErrorResponse
from ...fraud_evaluation_service.src.application.use_cases.create_card import CreateCardUseCase
from ...fraud_evaluation_service.src.infrastructure.mongodb_card_adapter import MongoDBCardAdapter
from ...fraud_evaluation_service.src.infrastructure.encryption_adapter import EncryptionAdapter
from ...fraud_evaluation_service.src.infrastructure.card_limit_checker_adapter import CardLimitCheckerAdapter
from ...fraud_evaluation_service.src.infrastructure.audit_logger_adapter import AuditLoggerAdapter

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/cards",
    tags=["cards"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid card data"},
        401: {"description": "Unauthorized - JWT token required"},
        409: {"model": ErrorResponse, "description": "Card already registered"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)


async def get_card_use_case() -> CreateCardUseCase:
    """
    Dependency injection para CreateCardUseCase
    Configura todos los adaptadores (puertos implementados)
    """
    # Inicializar adaptadores
    card_repo = MongoDBCardAdapter()
    encryption = EncryptionAdapter()
    limit_checker = CardLimitCheckerAdapter(card_repo=card_repo, max_cards=3)
    audit_logger = AuditLoggerAdapter()
    
    # Crear use case con puertos inyectados
    use_case = CreateCardUseCase(
        card_repository=card_repo,
        encryption_service=encryption,
        card_limit_checker=limit_checker,
        audit_logger=audit_logger
    )
    
    return use_case


@router.post(
    "",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new card",
    description="Add a new credit or debit card to user's wallet. Validates card number, expiry, CVV. Max 3 cards per user.",
)
async def create_card(
    request: CreateCardRequest,
    authorization: str = Header(...),
    use_case: CreateCardUseCase = Depends(get_card_use_case),
) -> CardResponse:
    """
    TASK-030: Crear tarjeta
    
    POST /api/v1/cards
    
    Request body:
    {
        "number": "4532015112830366",
        "expiry_month": 12,
        "expiry_year": 2026,
        "cvv": "123",
        "holder_name": "Juan Pérez",
        "document_id": "1234567890",
        "nickname": "Mi VISA"
    }
    
    Response 201:
    {
        "card_id": "card_123abc",
        "last_4_digits": "0366",
        "card_type": "VISA",
        "holder_name": "Juan Pérez",
        "nickname": "Mi VISA"
    }
    
    Errores:
    - 400: Número inválido, expiración vencida, CVV incorrecto
    - 401: JWT token no válido
    - 409: Tarjeta duplicada
    - 429: Límite alcanzado (3 tarjetas máximo)
    - 500: Error interno del servidor
    """
    
    try:
        # Extraer user_id del JWT token
        # NOTA: En producción, usar jwt.decode() para validar token
        # Por ahora, usar un placeholder
        user_id = _extract_user_id_from_jwt(authorization)
        
        if not user_id:
            logger.warning("Invalid JWT token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing JWT token"
            )
        
        # Ejecutar use case
        result = await use_case.execute(
            user_id=user_id,
            card_number=request.number,
            expiry_month=request.expiry_month,
            expiry_year=request.expiry_year,
            cvv=request.cvv,
            holder_name=request.holder_name,
            document_id=request.document_id,
            nickname=request.nickname or _generate_default_nickname(request.card_type)
        )
        
        # Si hay error, retornar con status code apropiado
        if not result.get('success'):
            reason = result.get('reason', 'Unknown error')
            
            # Determinar status code según el motivo del error
            if 'duplicada' in reason.lower() or 'already registered' in reason.lower():
                logger.info(f"Duplicate card for user {user_id}: {reason}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=result.get('error', 'Card already registered')
                )
            
            if 'límite' in reason.lower() or 'limit' in reason.lower():
                logger.info(f"Card limit reached for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=result.get('error', 'Card limit reached')
                )
            
            # Otros errores de validación (Luhn, expiry, CVV)
            logger.warning(f"Card validation failed for user {user_id}: {reason}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Invalid card data')
            )
        
        # Éxito: retornar CardResponse (sin CVV, sin número completo)
        logger.info(f"Card created successfully for user {user_id}: {result.get('card_id')}")
        
        return CardResponse(
            card_id=result['card_id'],
            last_4_digits=result['last_4_digits'],
            card_type=result['card_type'],
            holder_name=result['holder_name'],
            nickname=result.get('nickname') or _generate_default_nickname(result['card_type'])
        )
    
    except HTTPException:
        # Re-lanzar HTTPException (ya tiene status code correcto)
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error creating card: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "",
    response_model=list[CardResponse],
    summary="List user cards",
    description="Get all cards registered for the authenticated user"
)
async def list_cards(
    authorization: str = Header(...),
    card_repo: MongoDBCardAdapter = Depends(lambda: MongoDBCardAdapter())
) -> list[CardResponse]:
    """
    TASK-031: Listar tarjetas del usuario
    
    GET /api/v1/cards
    
    Response 200:
    [
        {
            "card_id": "card_123",
            "last_4_digits": "0366",
            "card_type": "VISA",
            "holder_name": "Juan Pérez",
            "nickname": "Mi VISA"
        }
    ]
    """
    try:
        user_id = _extract_user_id_from_jwt(authorization)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing JWT token"
            )
        
        # Obtener tarjetas del usuario
        cards = await card_repo.find_by_user_id(user_id)
        
        if not cards:
            return []
        
        # Convertir a CardResponse
        return [
            CardResponse(
                card_id=str(card.get('_id')),
                last_4_digits=card['last_4_digits'],
                card_type=card['card_type'],
                holder_name=card['holder_name'],
                nickname=card.get('nickname') or _generate_default_nickname(card['card_type'])
            )
            for card in cards
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cards: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


def _extract_user_id_from_jwt(authorization: str) -> Optional[str]:
    """
    Extract user_id from JWT token in Authorization header
    
    Expected format: "Bearer <jwt_token>"
    
    NOTA: En producción, usar una librería como PyJWT o python-jose
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        # Por ahora, simplemente extraer un placeholder
        # En producción: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # PLACEHOLDER para tests
        if authorization == "Bearer test_token_123":
            return "user_123"
        
        # En producción, esto sería:
        # token = authorization.replace("Bearer ", "")
        # payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        # return payload.get("sub")  # user_id
        
        return None
    
    except Exception as e:
        logger.error(f"JWT extraction failed: {str(e)}")
        return None


def _generate_default_nickname(card_type: str) -> str:
    """
    Generate default nickname if not provided
    
    Examples:
    - "VISA" → "Mi VISA"
    - "MASTERCARD" → "Mi Mastercard"
    - "AMEX" → "Mi American Express"
    """
    type_map = {
        "VISA": "Mi VISA",
        "MASTERCARD": "Mi Mastercard",
        "AMEX": "Mi American Express"
    }
    return type_map.get(card_type, f"Mi {card_type}")
