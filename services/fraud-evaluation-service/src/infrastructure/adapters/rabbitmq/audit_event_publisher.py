"""
RabbitMQ adapter for AuditEventPublisher port.

CLEAN ARCHITECTURE:
- This is an INFRASTRUCTURE adapter implementing the PORTS interface
- Depends on: Application port (AuditEventPublisher), aio-pika (async RabbitMQ)
- Does NOT import: FastAPI, Pydantic, MongoDB, or other frameworks
- Pure message publishing logic with RabbitMQ-specific operations

Pattern: Publish-Subscribe with persistent message queue
Queue: fraud.audit.events (configured in docker-compose)
Delivery: Persistent (survives broker restart), async non-blocking
"""

import json
from datetime import datetime
from typing import Dict, Any
import aio_pika
from aio_pika import DeliveryMode

from src.application.ports.audit_publisher import AuditEventPublisher


class RabbitMQAuditEventPublisher(AuditEventPublisher):
    """
    RabbitMQ implementation of AuditEventPublisher.
    
    Handles async publishing of audit events to RabbitMQ for:
    - Compliance and regulatory audit trail
    - Event-driven architecture (worker service consumes events)
    - Fraud monitoring and alerting systems
    - Analytics and reporting
    
    Queue Configuration:
    - Name: fraud.audit.events
    - Durable: True (survives broker restart)
    - Auto-delete: False (explicit deletion required)
    
    Message Properties:
    - content_type: application/json
    - delivery_mode: PERSISTENT (2)
    - timestamp: Included in all messages
    
    HUMAN REVIEW (Developer Name):
    RabbitMQ ensures guaranteed delivery with acknowledgments.
    Dead-letter queue (fraud.audit.events.dlq) handles failed publishes.
    See ARCHITECTURE.md for event flow details.
    """
    
    QUEUE_NAME = 'fraud.audit.events'
    EXCHANGE_NAME = 'fraud.events'
    ROUTING_KEY = 'audit.event'
    DLQ_NAME = 'fraud.audit.events.dlq'
    
    def __init__(self, channel: aio_pika.Channel):
        """
        Initialize RabbitMQ AuditEventPublisher.
        
        Args:
            channel: aio_pika async channel connected to RabbitMQ
        
        Setup:
        - Declares exchange and queue with durable settings
        - Configures dead-letter queue for failed messages
        """
        self.channel = channel
        self.queue = None
        self.exchange = None
    
    async def initialize(self) -> None:
        """
        Initialize RabbitMQ exchange and queues.
        
        Should be called once during application startup.
        
        Implementation Notes:
        - Declares exchange and main queue as durable
        - Declares DLQ for message processing failures
        - Idempotent: Safe to call multiple times
        """
        # Declare exchange
        self.exchange = await self.channel.declare_exchange(
            self.EXCHANGE_NAME,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
            auto_delete=False
        )
        
        # Declare dead-letter queue
        dlq = await self.channel.declare_queue(
            self.DLQ_NAME,
            durable=True,
            auto_delete=False
        )
        
        # Declare main queue with DLQ routing
        self.queue = await self.channel.declare_queue(
            self.QUEUE_NAME,
            durable=True,
            auto_delete=False,
            arguments={
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': self.DLQ_NAME
            }
        )
        
        # Bind queue to exchange
        await self.queue.bind(self.exchange, routing_key=self.ROUTING_KEY)
    
    async def publish_event(self, event: Dict[str, Any]) -> None:
        """
        Publish audit event to RabbitMQ.
        
        Args:
            event: Audit event dict with keys:
                - action: Event type (e.g., 'CARD_ADDED', 'CARD_REMOVED')
                - card_id: Card identifier
                - user_id: User identifier
                - timestamp: ISO-8601 timestamp
                - Additional metadata (card_type, last_four, etc.)
        
        Raises:
            ValueError: If event is invalid or missing required fields
            Exception: On RabbitMQ connection errors
        
        Implementation Notes:
        - Serializes event to JSON
        - Sets persistent delivery mode (survives broker restart)
        - Includes content-type and timestamp in message properties
        - Non-blocking: Returns immediately after publish
        """
        # Validate event
        if not event or not isinstance(event, dict):
            raise ValueError(f"Event must be a non-empty dict, got {type(event)}")
        
        # Require action field
        if 'action' not in event:
            raise ValueError("Event must include 'action' field")
        
        # Serialize to JSON
        try:
            message_body = json.dumps(event)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Event must be JSON serializable: {e}")
        
        # Create message with persistent properties
        message = aio_pika.Message(
            body=message_body.encode('utf-8'),
            content_type='application/json',
            delivery_mode=DeliveryMode.PERSISTENT,
            timestamp=datetime.utcnow(),
            app_id='fraud-evaluation-service',
            headers={
                'event_type': event.get('action'),
                'user_id': event.get('user_id'),
            }
        )
        
        # Publish to exchange
        await self.exchange.publish(
            message,
            routing_key=self.ROUTING_KEY,
            mandatory=False  # Don't fail if no consumers
        )
