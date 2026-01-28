"""
FastAPI routes for Card Management API.

Endpoints:
- POST /cards - Add new card
- GET /cards - List user's cards
- GET /cards/{card_id} - Get card details
- DELETE /cards/{card_id} - Remove card

CLEAN ARCHITECTURE:
- Routes are thin wrappers around use cases
- Dependency injection: use cases and repositories provided
- Request/response validation via Pydantic schemas
- Error handling with proper HTTP status codes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from datetime import datetime

from src.schemas.card_schemas import (
    AddCardRequest, CardResponse, CardListResponse, ErrorResponse
)


# Dependency placeholder - will be injected from container
# In real implementation, these come from dependency_injector or FastAPI Depends
async def get_add_card_use_case():
    """Dependency: AddCardUseCase. Will be provided by dependency container."""
    raise NotImplementedError("Use case dependency not configured")


async def get_remove_card_use_case():
    """Dependency: RemoveCardUseCase. Will be provided by dependency container."""
    raise NotImplementedError("Use case dependency not configured")


async def get_list_user_cards_use_case():
    """Dependency: ListUserCardsUseCase. Will be provided by dependency container."""
    raise NotImplementedError("Use case dependency not configured")


async def get_card_details_use_case():
    """Dependency: GetCardDetailsUseCase. Will be provided by dependency container."""
    raise NotImplementedError("Use case dependency not configured")


async def get_current_user_id() -> str:
    """
    Dependency: Extract authenticated user ID from JWT token.
    
    In real implementation:
    - Verify JWT token from Authorization header
    - Extract user_id from token claims
    - Return user_id for authorization checks
    
    For now: Returns placeholder. Framework like FastAPI-JWT or similar needed.
    """
    raise NotImplementedError("Authentication not configured")


router = APIRouter(
    prefix="/cards",
    tags=["cards"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad request or validation error"},
        401: {"model": ErrorResponse, "description": "Unauthorized - missing or invalid token"},
        403: {"model": ErrorResponse, "description": "Forbidden - access denied"},
        404: {"model": ErrorResponse, "description": "Not found"},
        409: {"model": ErrorResponse, "description": "Conflict - duplicate card"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)


@router.post(
    "",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add new card",
    description="Add a new payment card to user account. Card number is validated and masked in response.",
)
async def add_card(
    request: AddCardRequest,
    user_id: Annotated[str, Depends(get_current_user_id)],
    add_card_use_case = Depends(get_add_card_use_case),
) -> CardResponse:
    """
    Add new card to user account.
    
    Request body:
    - card_number: 16 digits
    - card_holder_name: 3-50 chars
    - expiry_date: MM/YY format
    - card_type: DEBIT or CREDIT
    - nickname: Optional, max 20 chars
    
    Response:
    - 201 Created with card details (number masked)
    - 400 Bad Request: Invalid card data
    - 409 Conflict: Duplicate card (same last 4 digits)
    - 400 Bad Request: Max 10 cards per user limit exceeded
    
    Implementation Notes:
    - Calls AddCardUseCase with validated request data
    - Returns card with masked card_number
    - Publishes CARD_ADDED audit event (async, non-blocking)
    """
    try:
        # Call use case with request data
        card_domain = await add_card_use_case.execute({
            'card_number': request.card_number,
            'card_holder_name': request.card_holder_name,
            'expiry_date': request.expiry_date,
            'card_type': request.card_type,
            'user_id': user_id,
            'nickname': request.nickname,
        })
        
        # Convert domain model to response (with masked number)
        return CardResponse(
            card_id=card_domain.card_id,
            card_number=card_domain.mask_card_number(),
            card_holder_name=card_domain.card_holder_name,
            expiry_date=card_domain.expiry_date,
            card_type=card_domain.card_type,
            nickname=card_domain.nickname,
            status=card_domain.status,
            created_at=card_domain.created_at,
            updated_at=card_domain.updated_at,
        )
    
    except ValueError as e:
        error_msg = str(e)
        
        # Duplicate card error (409)
        if "already linked" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "DUPLICATE_CARD",
                    "message": error_msg,
                }
            )
        
        # Max cards limit error (400)
        if "maximum of 10" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "MAX_CARDS_EXCEEDED",
                    "message": error_msg,
                }
            )
        
        # Generic validation error (400)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": error_msg,
            }
        )


@router.get(
    "",
    response_model=CardListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user cards",
    description="Get all active payment cards for the authenticated user.",
)
async def list_cards(
    user_id: Annotated[str, Depends(get_current_user_id)],
    list_use_case = Depends(get_list_user_cards_use_case),
) -> CardListResponse:
    """
    List all active cards for authenticated user.
    
    Response:
    - 200 OK with list of CardResponse objects
    - Card numbers are masked for security
    - Empty list if user has no cards
    
    Implementation Notes:
    - Calls ListUserCardsUseCase
    - Filters by user_id automatically (from authentication)
    - Masks all card numbers in response
    """
    try:
        cards = await list_use_case.execute(user_id=user_id)
        
        return CardListResponse(
            cards=[
                CardResponse(
                    card_id=card.card_id,
                    card_number=card.mask_card_number(),
                    card_holder_name=card.card_holder_name,
                    expiry_date=card.expiry_date,
                    card_type=card.card_type,
                    nickname=card.nickname,
                    status=card.status,
                    created_at=card.created_at,
                    updated_at=card.updated_at,
                )
                for card in cards
            ],
            total=len(cards),
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to retrieve cards",
            }
        )


@router.get(
    "/{card_id}",
    response_model=CardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get card details",
    description="Retrieve details for a specific card. User must own the card.",
)
async def get_card_details(
    card_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    details_use_case = Depends(get_card_details_use_case),
) -> CardResponse:
    """
    Get details for a single card.
    
    Response:
    - 200 OK with CardResponse
    - 404 Not Found: Card doesn't exist
    - 403 Forbidden: User doesn't own the card
    
    Implementation Notes:
    - Calls GetCardDetailsUseCase
    - Validates user owns the card (authorization check in use case)
    - Returns card with masked number
    """
    try:
        card = await details_use_case.execute(user_id=user_id, card_id=card_id)
        
        return CardResponse(
            card_id=card.card_id,
            card_number=card.mask_card_number(),
            card_holder_name=card.card_holder_name,
            expiry_date=card.expiry_date,
            card_type=card.card_type,
            nickname=card.nickname,
            status=card.status,
            created_at=card.created_at,
            updated_at=card.updated_at,
        )
    
    except ValueError as e:
        error_msg = str(e)
        
        # Not found error (404)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "CARD_NOT_FOUND",
                    "message": error_msg,
                }
            )
        
        # Unauthorized error (403)
        if "unauthorized" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Access denied to this card",
                }
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ERROR",
                "message": error_msg,
            }
        )


@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove card",
    description="Remove a payment card from user account. User must own the card.",
)
async def remove_card(
    card_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    remove_use_case = Depends(get_remove_card_use_case),
) -> None:
    """
    Remove (soft-delete) a card.
    
    Response:
    - 204 No Content: Success (no response body)
    - 404 Not Found: Card doesn't exist
    - 403 Forbidden: User doesn't own the card
    
    Implementation Notes:
    - Calls RemoveCardUseCase
    - Performs soft-delete (marks as INACTIVE, preserves audit trail)
    - Publishes CARD_REMOVED audit event (async, non-blocking)
    - Validates user owns the card (authorization check in use case)
    """
    try:
        await remove_use_case.execute(user_id=user_id, card_id=card_id)
        # 204 No Content - return None
        return None
    
    except ValueError as e:
        error_msg = str(e)
        
        # Not found error (404)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "CARD_NOT_FOUND",
                    "message": error_msg,
                }
            )
        
        # Unauthorized error (403)
        if "unauthorized" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FORBIDDEN",
                    "message": "Access denied to this card",
                }
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ERROR",
                "message": error_msg,
            }
        )
