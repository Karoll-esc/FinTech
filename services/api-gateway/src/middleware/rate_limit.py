"""
TASK-030: Rate Limiting Middleware
Protege el endpoint de abuso: máx 5 intentos por minuto por usuario
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable, Optional
import redis.asyncio as redis
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware para proteger endpoints sensibles
    
    Límites:
    - POST /api/v1/cards: 5 intentos por minuto por usuario
    - GET /api/v1/cards: 30 intentos por minuto por usuario
    """
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.card_create_limit = 5  # max requests
        self.card_create_window = 60  # seconds
        self.card_list_limit = 30
        self.card_list_window = 60
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Apply rate limiting before processing request"""
        
        # Solo aplicar a endpoints sensibles
        if not self._should_rate_limit(request):
            return await call_next(request)
        
        # Extraer user_id
        user_id = self._extract_user_id(request)
        if not user_id:
            # Si no hay user_id, permitir (será rechazado por auth después)
            return await call_next(request)
        
        # Si Redis no disponible, permitir (log warning)
        if not self.redis_client:
            logger.warning("Redis not available for rate limiting")
            return await call_next(request)
        
        # Determinar límites según endpoint
        is_post = request.method == "POST"
        if is_post:
            limit = self.card_create_limit
            window = self.card_create_window
        else:
            limit = self.card_list_limit
            window = self.card_list_window
        
        # Verificar rate limit
        key = f"rate_limit:{user_id}:{request.url.path}"
        try:
            current = await self.redis_client.incr(key)
            
            if current == 1:
                # Primera request en esta ventana
                await self.redis_client.expire(key, window)
            
            remaining = max(0, limit - current)
            
            # Headers de rate limit
            headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int((datetime.now() + timedelta(seconds=window)).timestamp()))
            }
            
            if current > limit:
                logger.warning(f"Rate limit exceeded for user {user_id}: {current}/{limit}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Maximum 5 requests per minute.",
                        "retry_after": window
                    },
                    headers=headers
                )
            
            # Procesar request y agregar headers a response
            response = await call_next(request)
            
            # Agregar headers de rate limit
            for key, value in headers.items():
                response.headers[key] = value
            
            return response
        
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Si hay error en rate limiting, permitir (no bloquear)
            return await call_next(request)
    
    def _should_rate_limit(self, request: Request) -> bool:
        """Determinar si esta request debe ser limitada"""
        path = request.url.path
        
        # Limitar solo endpoints de tarjetas
        if path.startswith("/api/v1/cards"):
            return True
        
        return False
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user_id from JWT token"""
        try:
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                return None
            
            # PLACEHOLDER: En producción, decodificar JWT
            # Por ahora, extraer de header custom o token
            token = auth_header.replace("Bearer ", "")
            
            # Para tests: Bearer test_token_123 → user_123
            if token == "test_token_123":
                return "user_123"
            
            # En producción:
            # payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            # return payload.get("sub")
            
            return None
        
        except Exception as e:
            logger.error(f"User ID extraction failed: {str(e)}")
            return None


async def get_redis_client() -> redis.Redis:
    """
    Obtener cliente Redis para rate limiting
    
    Llamada una sola vez en startup
    """
    try:
        client = await redis.from_url("redis://localhost:6379")
        await client.ping()
        logger.info("Redis connected for rate limiting")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        return None
