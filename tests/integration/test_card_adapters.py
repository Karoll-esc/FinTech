"""
Integration Tests for Card Infrastructure Adapters (TDD: RED phase)
Testing Encryption, Limit Checker, and Audit Logger adapters

TASK-021 a TASK-030: Tests para adapters de infraestructura
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.application.ports.card_ports import (
    EncryptionService, CardLimitChecker, AuditLogger
)


@pytest.mark.integration
class TestEncryptionAdapter:
    """Tests para adaptador de encriptación AES-256"""
    
    @pytest.fixture
    def encryption_adapter(self):
        """Crea adaptador de encriptación"""
        from src.infrastructure.encryption_adapter import EncryptionAdapter
        return EncryptionAdapter()
    
    @pytest.mark.asyncio
    async def test_encrypt_decrypt_roundtrip(self, encryption_adapter: EncryptionService):
        """TASK-021: Encriptar y desencriptar debe retornar el valor original"""
        original = "4532015112830366"
        
        # Encriptar
        encrypted = await encryption_adapter.encrypt(original)
        
        # Encriptado debe ser diferente del original
        assert encrypted != original
        assert len(encrypted) > 0
        
        # Desencriptar
        decrypted = await encryption_adapter.decrypt(encrypted)
        
        # Debe retornar el original
        assert decrypted == original
    
    @pytest.mark.asyncio
    async def test_encrypt_different_numbers_different_ciphertext(self, encryption_adapter: EncryptionService):
        """TASK-021: Números diferentes deben producir ciphertexts diferentes"""
        card1 = "4532015112830366"
        card2 = "5555555555554444"
        
        encrypted1 = await encryption_adapter.encrypt(card1)
        encrypted2 = await encryption_adapter.encrypt(card2)
        
        # Ciphertexts diferentes (probablemente)
        assert encrypted1 != encrypted2
    
    @pytest.mark.asyncio
    async def test_encrypt_empty_string(self, encryption_adapter: EncryptionService):
        """TASK-021: Encriptar string vacío"""
        encrypted = await encryption_adapter.encrypt("")
        assert len(encrypted) > 0
        decrypted = await encryption_adapter.decrypt(encrypted)
        assert decrypted == ""
    
    @pytest.mark.asyncio
    async def test_encrypt_long_string(self, encryption_adapter: EncryptionService):
        """TASK-021: Encriptar strings largos"""
        long_string = "a" * 1000
        encrypted = await encryption_adapter.encrypt(long_string)
        decrypted = await encryption_adapter.decrypt(encrypted)
        assert decrypted == long_string


@pytest.mark.integration
class TestCardLimitCheckerAdapter:
    """Tests para adaptador de límite de tarjetas"""
    
    @pytest.fixture
    def limit_checker_adapter(self):
        """Crea adaptador de límite"""
        from src.infrastructure.card_limit_checker_adapter import CardLimitCheckerAdapter
        from unittest.mock import AsyncMock
        
        # Mock del repositorio
        mock_repo = AsyncMock()
        return CardLimitCheckerAdapter(card_repository=mock_repo)
    
    @pytest.mark.asyncio
    async def test_can_add_card_when_below_limit(self, limit_checker_adapter: CardLimitChecker):
        """TASK-021: Permitir agregar si está por debajo del límite"""
        # Mock: usuario tiene 2 tarjetas
        limit_checker_adapter.card_repository.count_by_user_id.return_value = 2
        
        can_add = await limit_checker_adapter.can_add_card("user_123", max_cards=3)
        
        assert can_add is True
    
    @pytest.mark.asyncio
    async def test_cannot_add_card_at_limit(self, limit_checker_adapter: CardLimitChecker):
        """TASK-021: Rechazar si está en el límite"""
        # Mock: usuario tiene 3 tarjetas (límite)
        limit_checker_adapter.card_repository.count_by_user_id.return_value = 3
        
        can_add = await limit_checker_adapter.can_add_card("user_123", max_cards=3)
        
        assert can_add is False
    
    @pytest.mark.asyncio
    async def test_cannot_add_card_above_limit(self, limit_checker_adapter: CardLimitChecker):
        """TASK-021: Rechazar si está arriba del límite"""
        # Mock: usuario tiene 5 tarjetas (arriba del límite)
        limit_checker_adapter.card_repository.count_by_user_id.return_value = 5
        
        can_add = await limit_checker_adapter.can_add_card("user_123", max_cards=3)
        
        assert can_add is False
    
    @pytest.mark.asyncio
    async def test_can_add_first_card(self, limit_checker_adapter: CardLimitChecker):
        """TASK-021: Permitir agregar primera tarjeta (0 existentes)"""
        # Mock: usuario no tiene tarjetas
        limit_checker_adapter.card_repository.count_by_user_id.return_value = 0
        
        can_add = await limit_checker_adapter.can_add_card("user_123", max_cards=3)
        
        assert can_add is True


@pytest.mark.integration
class TestAuditLoggerAdapter:
    """Tests para adaptador de audit logging"""
    
    @pytest.fixture
    def audit_logger_adapter(self):
        """Crea adaptador de auditoría"""
        from src.infrastructure.audit_logger_adapter import AuditLoggerAdapter
        from unittest.mock import AsyncMock
        
        # Mock de la colección de MongoDB
        mock_collection = AsyncMock()
        return AuditLoggerAdapter(collection=mock_collection)
    
    @pytest.mark.asyncio
    async def test_log_success_attempt(self, audit_logger_adapter: AuditLogger):
        """TASK-021: Registrar intento exitoso"""
        await audit_logger_adapter.log_card_creation_attempt(
            user_id="user_123",
            card_type="VISA",
            last_4_digits="0366",
            success=True
        )
        
        # Verificar que se llamó insert_one
        audit_logger_adapter.collection.insert_one.assert_called_once()
        
        # Obtener los datos insertados
        call_args = audit_logger_adapter.collection.insert_one.call_args
        inserted_data = call_args[0][0]
        
        assert inserted_data['user_id'] == "user_123"
        assert inserted_data['card_type'] == "VISA"
        assert inserted_data['last_4_digits'] == "0366"
        assert inserted_data['success'] is True
        assert 'timestamp' in inserted_data
    
    @pytest.mark.asyncio
    async def test_log_failure_attempt_with_reason(self, audit_logger_adapter: AuditLogger):
        """TASK-021: Registrar intento fallido con razón"""
        await audit_logger_adapter.log_card_creation_attempt(
            user_id="user_456",
            card_type="MASTERCARD",
            last_4_digits="4444",
            success=False,
            reason="Tarjeta duplicada"
        )
        
        # Verificar que se llamó insert_one
        audit_logger_adapter.collection.insert_one.assert_called_once()
        
        # Obtener los datos insertados
        call_args = audit_logger_adapter.collection.insert_one.call_args
        inserted_data = call_args[0][0]
        
        assert inserted_data['user_id'] == "user_456"
        assert inserted_data['success'] is False
        assert inserted_data['reason'] == "Tarjeta duplicada"
    
    @pytest.mark.asyncio
    async def test_log_no_cvv_in_audit(self, audit_logger_adapter: AuditLogger):
        """TASK-021: Verificar que CVV nunca está en logs de auditoría"""
        await audit_logger_adapter.log_card_creation_attempt(
            user_id="user_123",
            card_type="VISA",
            last_4_digits="0366",
            success=True
        )
        
        call_args = audit_logger_adapter.collection.insert_one.call_args
        inserted_data = call_args[0][0]
        
        # CVV no debe estar en ninguna parte
        assert 'cvv' not in inserted_data
        assert 'CVV' not in str(inserted_data)
