"""
Card API Models and Routes (Phase 3 - TASK-019 to TASK-028)

Pydantic models for request/response validation and FastAPI routes.

Routes:
- GET /api/v1/cards - List user's active cards (max 3)
- GET /api/v1/cards/{card_id} - Get card details
- GET /api/v1/cards/{card_id}/transactions - Get card transaction history
- POST /api/v1/transfers - Submit money transfer (202 Accepted)
- PUT /api/v1/cards/{card_id}/block - Block a card
- PUT /api/v1/cards/{card_id}/unblock - Unblock a card

All routes:
- Require JWT authentication (Bearer token)
- Validate input with Pydantic
- Return proper HTTP status codes
- Include error handling and logging
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Card API models
class CardResponse(BaseModel):
    """Response model for card details"""
    
    card_id: str = Field(..., description="Unique card identifier")
    card_number: str = Field(..., description="Masked card number (XXXX-XXXX-XXXX-1234)")
    cardholder_name: str = Field(..., description="Name on card")
    current_balance: Decimal = Field(..., description="Available balance")
    expiry_month: int = Field(..., description="Expiry month (1-12)")
    expiry_year: int = Field(..., description="Expiry year (e.g., 2027)")
    status: str = Field(..., description="Card status: ACTIVE, BLOCKED, EXPIRED, PENDING")
    card_type: str = Field(..., description="Card type: DEBIT or CREDIT")
    created_at: datetime = Field(..., description="Card creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "card_123456",
                "card_number": "4532-XXXX-XXXX-1234",
                "cardholder_name": "Juan Pérez",
                "current_balance": "1250.50",
                "expiry_month": 12,
                "expiry_year": 2027,
                "status": "ACTIVE",
                "card_type": "DEBIT",
                "created_at": "2026-01-28T10:00:00Z",
                "updated_at": None,
            }
        }


class TransferRequest(BaseModel):
    """Request model for money transfer"""
    
    source_card_id: str = Field(..., description="Card to transfer from")
    amount: Decimal = Field(..., gt=0, description="Amount to transfer (> 0)")
    id_user: str = Field(..., description="User ID (for audit)")
    location: str = Field(..., description="Location description")
    device_id: str = Field(..., description="Device ID")
    transaction_id: str = Field(..., description="Unique transaction ID")
    description: Optional[str] = Field(None, description="Transfer description/purpose")

    class Config:
        json_schema_extra = {
            "example": {
                "source_card_id": "card_123456",
                "amount": "100.00",
                "id_user": "user_001",
                "location": "Bogotá, Colombia",
                "device_id": "device_abc123",
                "transaction_id": "txn_20260128_001",
                "description": "Transfer to savings account",
            }
        }


class TransferResponse(BaseModel):
    """Response model for transfer submission"""
    
    transaction_id: str = Field(..., description="Transaction ID")
    status: str = Field(..., description="Status: PENDING_EVALUATION")
    amount: Decimal = Field(..., description="Transfer amount")
    card_id: str = Field(..., description="Source card")
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., description="Status message")
    monto: Optional[Decimal] = Field(None, description="Amount (alias)")
    usuario: Optional[str] = Field(None, description="User ID (alias)")
    estado: Optional[str] = Field(None, description="State (alias)")
    risk_score: Optional[float] = Field(None, description="Fraud risk score (0-100)")


class BlockCardRequest(BaseModel):
    """Request model for blocking card"""
    
    reason: Optional[str] = Field(None, description="Reason for blocking")


class CardListResponse(BaseModel):
    """Response model for list of cards"""
    
    cards: List[CardResponse] = Field(..., description="List of cards")
    count: int = Field(..., description="Number of cards in list")
    limit: int = Field(default=3, description="Maximum cards returned")


class TransactionItem(BaseModel):
    """Model for individual transaction"""
    
    transaction_id: str = Field(..., description="Transaction ID")
    transaction_date: str = Field(..., description="Transaction date/time ISO 8601")
    description: str = Field(..., description="Transaction description")
    amount: Decimal = Field(..., description="Transaction amount")
    merchant: str = Field(..., description="Merchant name")
    status: str = Field(..., description="Transaction status: Completed, Pending")


class TransactionListResponse(BaseModel):
    """Response model for transaction history"""
    
    card_id: str = Field(..., description="Card ID")
    transactions: List[TransactionItem] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    skip: int = Field(default=0, description="Pagination offset")
    limit: int = Field(default=20, description="Pagination limit")


class ErrorResponse(BaseModel):
    """Standard error response"""
    
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


def create_card_routes() -> APIRouter:
    """
    Create card API routes
    
    Returns:
        APIRouter with all card endpoints configured
    """
    router = APIRouter(prefix="/api/v1", tags=["cards"])

    @router.get(
        "/cards",
        response_model=CardListResponse,
        status_code=status.HTTP_200_OK,
        summary="Get user's cards",
        description="Fetch up to 3 active cards for authenticated user",
    )
    async def get_user_cards(
        limit: int = Query(3, ge=1, le=10, description="Max cards to return")
    ) -> CardListResponse:
        """
        Get authenticated user's cards
        
        Returns up to 3 active cards with full details.
        
        Response: 200 OK with list of cards
        """
        logger.info(f"GET /cards with limit={limit}")
        
        # TODO: Extract user_id from JWT token in request context
        # This will be implemented in integration with auth middleware
        
        return CardListResponse(cards=[], count=0, limit=limit)

    @router.get(
        "/cards/{card_id}",
        response_model=CardResponse,
        status_code=status.HTTP_200_OK,
        summary="Get card details",
    )
    async def get_card_detail(card_id: str) -> CardResponse:
        """
        Get single card by ID
        
        Requires user to be card owner (verified in middleware).
        
        Response: 200 OK with card details
        Errors:
        - 404 Not Found: Card doesn't exist
        - 403 Forbidden: User not card owner
        """
        logger.info(f"GET /cards/{card_id}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not yet implemented",
        )

    @router.get(
        "/cards/{card_id}/transactions",
        response_model=TransactionListResponse,
        status_code=status.HTTP_200_OK,
        summary="Get card transaction history",
    )
    async def get_card_transactions(
        card_id: str,
        skip: int = Query(0, ge=0, description="Pagination offset"),
        limit: int = Query(20, ge=1, le=100, description="Page size"),
    ) -> TransactionListResponse:
        """
        Get transaction history for a card (paginated)
        
        Returns transactions sorted by date (newest first).
        
        Response: 200 OK with transactions
        """
        logger.info(f"GET /cards/{card_id}/transactions?skip={skip}&limit={limit}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not yet implemented",
        )

    @router.post(
        "/transfers",
        response_model=TransferResponse,
        status_code=status.HTTP_202_ACCEPTED,
        summary="Submit money transfer",
    )
    async def submit_transfer(transfer_request: TransferRequest) -> TransferResponse:
        """
        Submit money transfer (async-first pattern)
        
        Validates transfer request and submits to fraud evaluation queue.
        Returns 202 ACCEPTED while processing happens asynchronously.
        
        Response: 202 ACCEPTED with transaction_id
        Errors:
        - 400 Bad Request: Invalid transfer data
        - 422 Unprocessable Entity: Validation failed
        - 403 Forbidden: User not card owner
        - 409 Conflict: Card blocked or insufficient balance
        """
        logger.info(f"POST /transfers: {transfer_request.transaction_id}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not yet implemented",
        )

    @router.put(
        "/cards/{card_id}/block",
        response_model=CardResponse,
        status_code=status.HTTP_200_OK,
        summary="Block a card",
    )
    async def block_card(
        card_id: str,
        request: Optional[BlockCardRequest] = None,
    ) -> CardResponse:
        """
        Block a card (disable transfers)
        
        Updates card status to BLOCKED and publishes event.
        
        Response: 200 OK with updated card
        Errors:
        - 404 Not Found: Card doesn't exist
        - 403 Forbidden: User not card owner
        """
        logger.info(f"PUT /cards/{card_id}/block")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not yet implemented",
        )

    @router.put(
        "/cards/{card_id}/unblock",
        response_model=CardResponse,
        status_code=status.HTTP_200_OK,
        summary="Unblock a card",
    )
    async def unblock_card(card_id: str) -> CardResponse:
        """
        Unblock a card (enable transfers)
        
        Updates card status to ACTIVE.
        
        Response: 200 OK with updated card
        """
        logger.info(f"PUT /cards/{card_id}/unblock")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint not yet implemented",
        )

    return router
