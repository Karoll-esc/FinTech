"""
Card Repository Interface (Port)
TASK-022, TASK-023: Define repository interface following Dependency Inversion

This is a port in the Hexagonal Architecture - defines the contract that
infrastructure adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Card


class CardRepository(ABC):
    """
    Repository interface for Card persistence
    
    TASK-023: Define methods for card management
    - get_by_user_id: Retrieve all cards for a user
    - save: Persist a new card
    - get_by_id: Retrieve a single card by ID
    """
    
    @abstractmethod
    def get_by_user_id(self, user_id: str) -> List[Card]:
        """
        Retrieve all cards for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of Card objects (may be empty)
            Cards should be ordered by created_at DESC (most recent first)
        """
        pass
    
    @abstractmethod
    def save(self, card: Card) -> None:
        """
        Persist a card to storage
        
        Args:
            card: Card value object to persist
            
        Raises:
            ValueError: If card already exists or validation fails
        """
        pass
    
    @abstractmethod
    def get_by_id(self, card_id: str) -> Optional[Card]:
        """
        Retrieve a single card by ID
        
        Args:
            card_id: Card identifier
            
        Returns:
            Card object if found, None otherwise
        """
        pass
