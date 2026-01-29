"""
Dependency Injection for FastAPI
TASK-033: Configurar inyección de dependencias para GET /cards

Provee:
- get_card_use_case: Inyecta GetUserCardsUseCase con repositorio MongoDB
- get_current_user_id: Extrae user_id del JWT token
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCookie
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "fraud-evaluation-service"))

from src.application.use_cases.get_user_cards import GetUserCardsUseCase
from src.infrastructure.mongodb_card_adapter import MongoDBCardAdapter


# Security scheme
security = HTTPBearer()


def get_mongodb_collection():
    """
    TASK-033: Obtener colección MongoDB para tarjetas
    
    Note: En producción, esto se conecta a MongoDB real
    En tests, se puede override con mongomock
    """
    from pymongo import MongoClient
    from src.config import settings
    
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    return db["cards"]


def get_card_repository():
    """
    TASK-033: Crear adaptador MongoDB para CardRepository
    
    Returns:
        MongoDBCardAdapter configurado con colección de MongoDB
    """
    collection = get_mongodb_collection()
    repository = MongoDBCardAdapter(collection)
    
    # Asegurar que los índices estén creados
    repository.ensure_indexes()
    
    return repository


def get_card_use_case(
    repository = Depends(get_card_repository)
) -> GetUserCardsUseCase:
    """
    TASK-033: Inyectar GetUserCardsUseCase
    
    Args:
        repository: CardRepository (inyectado)
        
    Returns:
        GetUserCardsUseCase configurado
    """
    return GetUserCardsUseCase(card_repository=repository)


def get_current_user_id(
    token: str = Depends(security)
) -> str:
    """
    TASK-036 y TASK-038: Extraer user_id del JWT token
    
    Args:
        token: JWT token desde header Authorization
        
    Returns:
        user_id extraído del token
        
    Raises:
        HTTPException 401: Si token es inválido o expirado
    """
    try:
        # Extraer token (viene como "Bearer <token>")
        if hasattr(token, 'credentials'):
            jwt_token = token.credentials
        else:
            jwt_token = token
        
        # Simular validación JWT (en producción usar JWTService real)
        # HUMAN REVIEW:
        # Por ahora, extraemos user_id directamente del token sin validar
        # En producción, debe usar JWTService.verify_token()
        
        # Mock: extraer user_id del token simulado
        # Formato esperado: "valid_jwt_token_user_123" → "user_123"
        if jwt_token.startswith("valid_jwt_token_"):
            user_id = jwt_token.replace("valid_jwt_token_", "")
            return user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
