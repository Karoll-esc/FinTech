"""
Audit Publisher Port - Interface for audit trail publishing
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class AuditEventPublisher(ABC):
    """
    Abstract interface for publishing audit events
    
    Used by use cases to emit events for audit logging
    """

    @abstractmethod
    async def publish_event(self, event: Dict[str, Any]) -> None:
        """
        Publish an audit event
        
        Args:
            event: Event dictionary with action, user_id, timestamp, etc.
        """
        pass
