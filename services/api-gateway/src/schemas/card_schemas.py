"""
Pydantic Schemas for Card Management API
Validación de request/response para POST /api/v1/cards endpoint

IMPORTANTE: CVV nunca se almacena en la respuesta
           Número de tarjeta nunca se retorna
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CreateCardRequest(BaseModel):
    """Schema para solicitud POST /api/v1/cards"""
    
    number: str = Field(..., description="Número de tarjeta (13-19 dígitos)")
    expiry_month: int = Field(..., ge=1, le=12, description="Mes de vencimiento (1-12)")
    expiry_year: int = Field(..., description="Año de vencimiento (4 dígitos, ej: 2026)")
    cvv: str = Field(..., description="Código de seguridad (3 o 4 dígitos)")
    holder_name: str = Field(..., description="Nombre del titular")
    document_id: str = Field(..., description="Cédula o ID del titular")
    nickname: Optional[str] = Field(None, description="Apodo para la tarjeta (opcional)")
    
    @validator('number')
    def number_must_be_numeric(cls, v):
        """Validar que el número sea numérico"""
        if not v.isdigit():
            raise ValueError("Card number must contain only digits")
        if len(v) < 13 or len(v) > 19:
            raise ValueError("Card number must be 13-19 digits")
        return v
    
    @validator('cvv')
    def cvv_must_be_numeric(cls, v):
        """Validar que CVV sea numérico"""
        if not v.isdigit():
            raise ValueError("CVV must contain only digits")
        if len(v) < 3 or len(v) > 4:
            raise ValueError("CVV must be 3 or 4 digits")
        return v
    
    @validator('holder_name')
    def holder_name_not_empty(cls, v):
        """Validar que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError("Holder name is required")
        return v.strip()
    
    @validator('document_id')
    def document_id_not_empty(cls, v):
        """Validar que el documento no esté vacío"""
        if not v or not v.strip():
            raise ValueError("Document ID is required")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "number": "4532015112830366",
                "expiry_month": 12,
                "expiry_year": 2026,
                "cvv": "123",
                "holder_name": "Juan Pérez",
                "document_id": "1234567890",
                "nickname": "Mi VISA"
            }
        }


class CardResponse(BaseModel):
    """Schema para respuesta exitosa de creación de tarjeta"""
    
    success: bool
    card_id: str
    last_4_digits: str
    card_type: str  # VISA, MASTERCARD, AMEX
    holder_name: str
    nickname: str
    created_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "card_id": "507f1f77bcf86cd799439011",
                "last_4_digits": "0366",
                "card_type": "VISA",
                "holder_name": "Juan Pérez",
                "nickname": "Tarjeta VISA 0366",
                "created_at": "2026-01-28T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Schema para respuesta de error"""
    
    success: bool = False
    error: str
    reason: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "El número de tarjeta es inválido",
                "reason": "Luhn check failed"
            }
        }
