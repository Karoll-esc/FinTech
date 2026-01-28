"""
Pydantic schemas for Card Management API.

Purpose: Request/response validation and serialization
Layer: API Gateway (presentation layer)
Dependencies: pydantic, python datetime

CLEAN ARCHITECTURE:
- Schemas handle API contract (request validation, response formatting)
- Separate from domain models (Card) - API layer concern
- Use mask_card_number() from domain for secure response
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class AddCardRequest(BaseModel):
    """
    Request schema for adding a new card.
    
    Validation:
    - card_number: 16 digits, required
    - expiry_date: MM/YY format, required
    - card_holder_name: 3-50 chars, required
    - card_type: DEBIT or CREDIT, required
    - nickname: Optional, max 20 chars
    """
    
    card_number: str = Field(
        ...,
        min_length=16,
        max_length=16,
        description="16-digit card number"
    )
    card_holder_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Name on card (3-50 chars)"
    )
    expiry_date: str = Field(
        ...,
        pattern=r'^\d{2}/\d{2}$',
        description="Expiry date in MM/YY format"
    )
    card_type: str = Field(
        ...,
        pattern='^(DEBIT|CREDIT)$',
        description="Card type: DEBIT or CREDIT"
    )
    nickname: Optional[str] = Field(
        None,
        max_length=20,
        description="Optional card nickname (max 20 chars)"
    )
    
    @field_validator('card_number')
    @classmethod
    def card_number_must_be_numeric(cls, v):
        """Card number must contain only digits."""
        if not v.isdigit():
            raise ValueError('Card number must be numeric')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_number": "4532015112830366",
                "card_holder_name": "John Doe",
                "expiry_date": "12/25",
                "card_type": "DEBIT",
                "nickname": "Main Card"
            }
        }


class CardResponse(BaseModel):
    """
    Response schema for card details.
    
    Security:
    - card_number is always masked (****0366)
    - expiry_date is always included
    - Other sensitive fields excluded from response
    """
    
    card_id: str = Field(description="Unique card identifier")
    card_number: str = Field(description="Masked card number (****XXXX)")
    card_holder_name: str = Field(description="Name on card")
    expiry_date: str = Field(description="Expiry date MM/YY")
    card_type: str = Field(description="DEBIT or CREDIT")
    nickname: Optional[str] = Field(None, description="Optional card nickname")
    status: str = Field(description="ACTIVE or INACTIVE")
    created_at: str = Field(description="ISO-8601 timestamp")
    updated_at: str = Field(description="ISO-8601 timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "card_001",
                "card_number": "****0366",
                "card_holder_name": "John Doe",
                "expiry_date": "12/25",
                "card_type": "DEBIT",
                "nickname": "Main Card",
                "status": "ACTIVE",
                "created_at": "2026-01-28T10:00:00",
                "updated_at": "2026-01-28T10:00:00"
            }
        }


class CardListResponse(BaseModel):
    """Response schema for list of cards."""
    
    cards: List[CardResponse] = Field(default_factory=list, description="User's cards")
    total: int = Field(description="Total number of cards")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cards": [
                    {
                        "card_id": "card_001",
                        "card_number": "****0366",
                        "card_holder_name": "John Doe",
                        "expiry_date": "12/25",
                        "card_type": "DEBIT",
                        "nickname": "Main Card",
                        "status": "ACTIVE",
                        "created_at": "2026-01-28T10:00:00",
                        "updated_at": "2026-01-28T10:00:00"
                    }
                ],
                "total": 1
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str = Field(description="Error type/code")
    message: str = Field(description="Human-readable error message")
    status_code: int = Field(description="HTTP status code")
    timestamp: str = Field(description="ISO-8601 timestamp when error occurred")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "DUPLICATE_CARD",
                "message": "Card with last 4 digits 0366 already linked to this account",
                "status_code": 409,
                "timestamp": "2026-01-28T10:00:00"
            }
        }
