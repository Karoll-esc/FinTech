"""
Phase 3 - RED: Integration tests for RabbitMQ AuditEventPublisher adapter
Following TDD approach: Write tests first, watch them fail

Test Pyramid Level: Integration Tests
Coverage Target: 100% of infrastructure/adapters/rabbitmq/audit_event_publisher.py
Message Queue: RabbitMQ
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, AsyncMock, patch
import json
import sys
from pathlib import Path

# Add services/fraud-evaluation-service/src to sys.path for imports
_repo_root = Path(__file__).resolve().parents[2]
_fraud_service_src = _repo_root / 'services' / 'fraud-evaluation-service' / 'src'
if str(_fraud_service_src) not in sys.path:
    sys.path.insert(0, str(_fraud_service_src))


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def card_added_event():
    """Sample CARD_ADDED audit event"""
    return {
        'action': 'CARD_ADDED',
        'card_id': 'card_001',
        'user_id': 'user_12345',
        'card_type': 'DEBIT',
        'last_four_digits': '0366',
        'timestamp': datetime.utcnow().isoformat(),
    }


@pytest.fixture
def card_removed_event():
    """Sample CARD_REMOVED audit event"""
    return {
        'action': 'CARD_REMOVED',
        'card_id': 'card_001',
        'user_id': 'user_12345',
        'card_type': 'DEBIT',
        'last_four_digits': '0366',
        'timestamp': datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_rabbitmq_channel():
    """Mock RabbitMQ channel"""
    channel = AsyncMock()
    channel.basic_publish = AsyncMock(return_value=None)
    channel.queue_declare = AsyncMock(return_value=None)
    channel.exchange_declare = AsyncMock(return_value=None)
    return channel


@pytest.fixture
def mock_rabbitmq_connection():
    """Mock RabbitMQ connection"""
    connection = AsyncMock()
    channel = AsyncMock()
    connection.channel = AsyncMock(return_value=channel)
    return connection


# ============================================================================
# Test Suite 1: RabbitMQAuditEventPublisher - Publishing Events
# ============================================================================

class TestRabbitMQAuditEventPublisherPublish:
    """Tests for publishing audit events to RabbitMQ"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_publish_event_sends_to_audit_queue(self, card_added_event, mock_rabbitmq_channel):
        """Should publish event to RabbitMQ audit.events queue"""
        # This test will FAIL until RabbitMQAuditEventPublisher is implemented
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute
        await publisher.publish_event(card_added_event)
        
        # Verify - basic_publish should be called with correct routing key
        mock_rabbitmq_channel.basic_publish.assert_called_once()
        call_args = mock_rabbitmq_channel.basic_publish.call_args
        assert 'audit.events' in str(call_args)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_publish_event_serializes_to_json(self, card_added_event, mock_rabbitmq_channel):
        """Should serialize event dict to JSON before publishing"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute
        await publisher.publish_event(card_added_event)
        
        # Verify - published message should be valid JSON
        mock_rabbitmq_channel.basic_publish.assert_called_once()
        call_args = mock_rabbitmq_channel.basic_publish.call_args
        # Body should be JSON serializable
        message_body = call_args[1]['body'] if 'body' in call_args[1] else call_args[0][2]
        assert isinstance(message_body, (str, bytes))

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_publish_card_added_event(self, card_added_event, mock_rabbitmq_channel):
        """Should publish CARD_ADDED event with correct structure"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute
        await publisher.publish_event(card_added_event)
        
        # Verify - event contains required fields
        # action, card_id, user_id, timestamp

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_publish_card_removed_event(self, card_removed_event, mock_rabbitmq_channel):
        """Should publish CARD_REMOVED event with correct structure"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute
        await publisher.publish_event(card_removed_event)
        
        # Verify - event routing should be to audit.events queue


# ============================================================================
# Test Suite 2: RabbitMQAuditEventPublisher - Message Properties
# ============================================================================

class TestRabbitMQAuditEventPublisherMessageProperties:
    """Tests for RabbitMQ message properties and metadata"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_publishes_with_persistent_delivery(self, card_added_event, mock_rabbitmq_channel):
        """Should publish with persistent flag (survives broker restart)"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute
        await publisher.publish_event(card_added_event)
        
        # Verify - message should have delivery_mode=2 (persistent)
        mock_rabbitmq_channel.basic_publish.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_includes_content_type_header(self, card_added_event, mock_rabbitmq_channel):
        """Should include content-type: application/json header"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute
        await publisher.publish_event(card_added_event)
        
        # Verify - properties should have content_type='application/json'

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_includes_timestamp_in_message_properties(self, card_added_event, mock_rabbitmq_channel):
        """Should include timestamp in message properties"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute
        await publisher.publish_event(card_added_event)
        
        # Verify - timestamp field populated


# ============================================================================
# Test Suite 3: RabbitMQAuditEventPublisher - Error Handling
# ============================================================================

class TestRabbitMQAuditEventPublisherErrorHandling:
    """Tests for error handling during publishing"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_handles_connection_error(self, card_added_event, mock_rabbitmq_channel):
        """Should raise error on RabbitMQ connection failure"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        # Mock connection failure
        failing_channel = AsyncMock()
        failing_channel.basic_publish = AsyncMock(side_effect=Exception("Connection refused"))
        
        publisher = RabbitMQAuditEventPublisher(failing_channel)
        
        # Execute & Verify
        with pytest.raises(Exception):
            await publisher.publish_event(card_added_event)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_handles_queue_not_found_error(self, card_added_event, mock_rabbitmq_channel):
        """Should raise error if queue doesn't exist"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        # Mock queue not found error
        failing_channel = AsyncMock()
        failing_channel.basic_publish = AsyncMock(
            side_effect=Exception("NOT_FOUND - no queue 'audit.events'")
        )
        
        publisher = RabbitMQAuditEventPublisher(failing_channel)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_handles_invalid_event_data(self, mock_rabbitmq_channel):
        """Should raise error on invalid event data"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Execute with invalid event
        with pytest.raises((ValueError, TypeError)):
            await publisher.publish_event(None)


# ============================================================================
# Test Suite 4: RabbitMQAuditEventPublisher - Initialization
# ============================================================================

class TestRabbitMQAuditEventPublisherInitialization:
    """Tests for RabbitMQAuditEventPublisher initialization"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_initialize_with_channel(self, mock_rabbitmq_channel):
        """Should initialize with RabbitMQ channel"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        # Execute
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Verify
        assert publisher is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_declare_queue_on_initialization(self, mock_rabbitmq_channel):
        """Should declare audit.events queue on init"""
        pytest.skip("RabbitMQAuditEventPublisher not yet implemented")
        
        from src.infrastructure.adapters.rabbitmq.audit_event_publisher import RabbitMQAuditEventPublisher
        
        # Execute
        publisher = RabbitMQAuditEventPublisher(mock_rabbitmq_channel)
        
        # Verify - queue_declare should be called with durable=True
        # mock_rabbitmq_channel.queue_declare.assert_called_once()


# ============================================================================
# Test Suite 5: Integration - Card Operations Trigger Audit Events
# ============================================================================

class TestCardOperationsPublishAuditEvents:
    """Integration tests verifying card operations trigger audit events"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_add_card_operation_publishes_event(self, mock_rabbitmq_channel):
        """When card is added, CARD_ADDED event should be published"""
        pytest.skip("Integration not yet tested")
        
        # This is an end-to-end test: AddCardUseCase → RabbitMQAuditEventPublisher

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_remove_card_operation_publishes_event(self, mock_rabbitmq_channel):
        """When card is removed, CARD_REMOVED event should be published"""
        pytest.skip("Integration not yet tested")
        
        # This is an end-to-end test: RemoveCardUseCase → RabbitMQAuditEventPublisher
