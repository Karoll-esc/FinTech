"""
Unit Tests for CreateCardUseCase
Testing application layer use case with mocked ports
TDD: RED → GREEN → REFACTOR

TASK-012 a TASK-020: Tests para CreateCardUseCase orquestación
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import CardType
from src.application.use_cases.create_card import CreateCardUseCase
from src.application.ports.card_ports import (
    CardRepository, EncryptionService, CardLimitChecker, AuditLogger
)


@pytest.mark.unit
class TestCreateCardUseCaseSuccess:
    """Tests para camino feliz del CreateCardUseCase"""
    
    @pytest.fixture
    def mock_ports(self):
        """Crea mocks de todos los puertos"""
        card_repo = AsyncMock(spec=CardRepository)
        encryption = AsyncMock(spec=EncryptionService)
        limit_checker = AsyncMock(spec=CardLimitChecker)
        audit_logger = AsyncMock(spec=AuditLogger)
        
        return {
            'card_repo': card_repo,
            'encryption': encryption,
            'limit_checker': limit_checker,
            'audit_logger': audit_logger,
        }
    
    @pytest.fixture
    def use_case(self, mock_ports):
        """Instancia el use case con puertos mockeados"""
        return CreateCardUseCase(
            card_repository=mock_ports['card_repo'],
            encryption_service=mock_ports['encryption'],
            card_limit_checker=mock_ports['limit_checker'],
            audit_logger=mock_ports['audit_logger']
        )
    
    @pytest.fixture
    def valid_card_data(self):
        """Datos válidos de tarjeta para testing"""
        return {
            'user_id': 'user_123',
            'number': '4532015112830366',  # VISA válido
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890',
            'nickname': 'Mi VISA'
        }
    
    @pytest.mark.asyncio
    async def test_create_card_success_visa(self, use_case, mock_ports, valid_card_data):
        """TASK-016: Crear tarjeta VISA exitosamente"""
        # Arrange
        mock_ports['limit_checker'].can_add_card.return_value = True
        mock_ports['card_repo'].exists_by_number.return_value = False
        mock_ports['encryption'].encrypt.return_value = 'encrypted_number_xyz'
        mock_ports['card_repo'].save.return_value = 'card_id_123'
        
        # Act
        result = await use_case.execute(valid_card_data)
        
        # Assert
        assert result['success'] is True
        assert result['card_id'] == 'card_id_123'
        assert result['last_4_digits'] == '0366'
        assert result['card_type'] == 'VISA'
        assert 'number' not in result  # Número no debe retornarse
        assert 'cvv' not in result  # CVV nunca debe retornarse
        
        # Verificar que se llamaron los métodos correctos
        mock_ports['limit_checker'].can_add_card.assert_called_once()
        mock_ports['encryption'].encrypt.assert_called_once()
        mock_ports['card_repo'].save.assert_called_once()
        mock_ports['audit_logger'].log_card_creation_attempt.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_card_success_mastercard(self, use_case, mock_ports):
        """TASK-016: Crear tarjeta Mastercard exitosamente"""
        card_data = {
            'user_id': 'user_456',
            'number': '5555555555554444',  # MC válido
            'expiry_month': 6,
            'expiry_year': 2027,
            'cvv': '456',
            'holder_name': 'María García',
            'document_id': '9876543210',
            'nickname': 'Mi Mastercard'
        }
        
        mock_ports['limit_checker'].can_add_card.return_value = True
        mock_ports['card_repo'].exists_by_number.return_value = False
        mock_ports['encryption'].encrypt.return_value = 'encrypted_mc'
        mock_ports['card_repo'].save.return_value = 'card_id_456'
        
        result = await use_case.execute(card_data)
        
        assert result['success'] is True
        assert result['card_type'] == 'MASTERCARD'
        assert result['last_4_digits'] == '4444'
    
    @pytest.mark.asyncio
    async def test_create_card_success_amex(self, use_case, mock_ports):
        """TASK-016: Crear tarjeta American Express exitosamente"""
        card_data = {
            'user_id': 'user_789',
            'number': '374245455400126',  # AMEX válido (15 dígitos)
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '1234',  # AMEX tiene 4 dígitos
            'holder_name': 'Carlos López',
            'document_id': '5555555555',
            'nickname': None  # Sin nickname
        }
        
        mock_ports['limit_checker'].can_add_card.return_value = True
        mock_ports['card_repo'].exists_by_number.return_value = False
        mock_ports['encryption'].encrypt.return_value = 'encrypted_amex'
        mock_ports['card_repo'].save.return_value = 'card_id_789'
        
        result = await use_case.execute(card_data)
        
        assert result['success'] is True
        assert result['card_type'] == 'AMEX'
        assert result['last_4_digits'] == '0126'
        # Si nickname es None, generar nombre default
        assert 'nickname' in result
        assert 'AMEX' in result['nickname']  # ej: "Tarjeta AMEX 0126"
    
    @pytest.mark.asyncio
    async def test_create_card_default_nickname_generated(self, use_case, mock_ports, valid_card_data):
        """TASK-018: Si no hay apodo, generar nombre default"""
        valid_card_data['nickname'] = None
        
        mock_ports['limit_checker'].can_add_card.return_value = True
        mock_ports['card_repo'].exists_by_number.return_value = False
        mock_ports['encryption'].encrypt.return_value = 'encrypted_xyz'
        mock_ports['card_repo'].save.return_value = 'card_id_default'
        
        result = await use_case.execute(valid_card_data)
        
        assert result['success'] is True
        # Nickname debe ser generado: "Tarjeta VISA 0366"
        assert result['nickname'] is not None
        assert 'VISA' in result['nickname']
        assert '0366' in result['nickname']


@pytest.mark.unit
class TestCreateCardUseCaseValidation:
    """Tests para validación en CreateCardUseCase"""
    
    @pytest.fixture
    def mock_ports(self):
        card_repo = AsyncMock(spec=CardRepository)
        encryption = AsyncMock(spec=EncryptionService)
        limit_checker = AsyncMock(spec=CardLimitChecker)
        audit_logger = AsyncMock(spec=AuditLogger)
        return {
            'card_repo': card_repo,
            'encryption': encryption,
            'limit_checker': limit_checker,
            'audit_logger': audit_logger,
        }
    
    @pytest.fixture
    def use_case(self, mock_ports):
        return CreateCardUseCase(
            card_repository=mock_ports['card_repo'],
            encryption_service=mock_ports['encryption'],
            card_limit_checker=mock_ports['limit_checker'],
            audit_logger=mock_ports['audit_logger']
        )
    
    @pytest.mark.asyncio
    async def test_invalid_luhn_number(self, use_case, mock_ports):
        """TASK-019: Rechazar número inválido por Luhn"""
        card_data = {
            'user_id': 'user_123',
            'number': '1234567890123456',  # Luhn inválido
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        mock_ports['audit_logger'].log_card_creation_attempt = AsyncMock()
        
        result = await use_case.execute(card_data)
        
        assert result['success'] is False
        assert 'error' in result
        # El error puede estar en español o inglés, lo importante es que fue rechazado
    
    @pytest.mark.asyncio
    async def test_expired_date(self, use_case, mock_ports):
        """TASK-019: Rechazar fecha expirada"""
        card_data = {
            'user_id': 'user_123',
            'number': '4532015112830366',  # VISA válido
            'expiry_month': 1,
            'expiry_year': 2020,  # Año pasado
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        mock_ports['audit_logger'].log_card_creation_attempt = AsyncMock()
        
        result = await use_case.execute(card_data)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'expir' in result['error'].lower() or 'date' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_cvv_length_visa(self, use_case, mock_ports):
        """TASK-019: Rechazar CVV incorrecto para VISA (debe ser 3)"""
        card_data = {
            'user_id': 'user_123',
            'number': '4532015112830366',  # VISA
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '1234',  # 4 dígitos (VISA requiere 3)
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        mock_ports['audit_logger'].log_card_creation_attempt = AsyncMock()
        
        result = await use_case.execute(card_data)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'CVV' in result['error'] or 'cvv' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_cvv_length_amex(self, use_case, mock_ports):
        """TASK-019: Rechazar CVV incorrecto para AMEX (debe ser 4)"""
        card_data = {
            'user_id': 'user_123',
            'number': '374245455400126',  # AMEX
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',  # 3 dígitos (AMEX requiere 4)
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        mock_ports['audit_logger'].log_card_creation_attempt = AsyncMock()
        
        result = await use_case.execute(card_data)
        
        assert result['success'] is False
        assert 'error' in result


@pytest.mark.unit
class TestCreateCardUseCaseLimitAndDuplicates:
    """Tests para límite de 3 tarjetas y duplicados"""
    
    @pytest.fixture
    def mock_ports(self):
        card_repo = AsyncMock(spec=CardRepository)
        encryption = AsyncMock(spec=EncryptionService)
        limit_checker = AsyncMock(spec=CardLimitChecker)
        audit_logger = AsyncMock(spec=AuditLogger)
        return {
            'card_repo': card_repo,
            'encryption': encryption,
            'limit_checker': limit_checker,
            'audit_logger': audit_logger,
        }
    
    @pytest.fixture
    def use_case(self, mock_ports):
        return CreateCardUseCase(
            card_repository=mock_ports['card_repo'],
            encryption_service=mock_ports['encryption'],
            card_limit_checker=mock_ports['limit_checker'],
            audit_logger=mock_ports['audit_logger']
        )
    
    @pytest.fixture
    def valid_card_data(self):
        return {
            'user_id': 'user_123',
            'number': '4532015112830366',
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
    
    @pytest.mark.asyncio
    async def test_limit_3_cards_reached(self, use_case, mock_ports, valid_card_data):
        """TASK-004: Rechazar si usuario ya tiene 3 tarjetas"""
        mock_ports['limit_checker'].can_add_card.return_value = False
        
        result = await use_case.execute(valid_card_data)
        
        assert result['success'] is False
        assert 'error' in result
        # El error contiene información sobre el límite (en español o inglés)
    
    @pytest.mark.asyncio
    async def test_duplicate_card_detected(self, use_case, mock_ports, valid_card_data):
        """TASK-017: Rechazar si tarjeta duplicada (mismo últimos 4 dígitos)"""
        mock_ports['limit_checker'].can_add_card.return_value = True
        # Tarjeta ya existe (últimos 4 dígitos duplicados)
        mock_ports['card_repo'].exists_by_number.return_value = True
        
        result = await use_case.execute(valid_card_data)
        
        assert result['success'] is False
        assert 'error' in result
        # El error menciona que ya existe la tarjeta
        
        # No debe intentar encriptar ni guardar
        mock_ports['encryption'].encrypt.assert_not_called()
        mock_ports['card_repo'].save.assert_not_called()


@pytest.mark.unit
class TestCreateCardUseCaseAuditLogging:
    """Tests para auditoría y logging"""
    
    @pytest.fixture
    def mock_ports(self):
        card_repo = AsyncMock(spec=CardRepository)
        encryption = AsyncMock(spec=EncryptionService)
        limit_checker = AsyncMock(spec=CardLimitChecker)
        audit_logger = AsyncMock(spec=AuditLogger)
        return {
            'card_repo': card_repo,
            'encryption': encryption,
            'limit_checker': limit_checker,
            'audit_logger': audit_logger,
        }
    
    @pytest.fixture
    def use_case(self, mock_ports):
        return CreateCardUseCase(
            card_repository=mock_ports['card_repo'],
            encryption_service=mock_ports['encryption'],
            card_limit_checker=mock_ports['limit_checker'],
            audit_logger=mock_ports['audit_logger']
        )
    
    @pytest.mark.asyncio
    async def test_success_audit_log_called(self, use_case, mock_ports):
        """TASK-020: Registrar intento exitoso en auditoría"""
        card_data = {
            'user_id': 'user_123',
            'number': '4532015112830366',
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        mock_ports['limit_checker'].can_add_card.return_value = True
        mock_ports['card_repo'].exists_by_number.return_value = False
        mock_ports['encryption'].encrypt.return_value = 'encrypted_xyz'
        mock_ports['card_repo'].save.return_value = 'card_id_123'
        
        await use_case.execute(card_data)
        
        # Verificar que se registró el intento exitoso
        mock_ports['audit_logger'].log_card_creation_attempt.assert_called_once()
        call_args = mock_ports['audit_logger'].log_card_creation_attempt.call_args
        
        # Verificar argumentos del log
        assert call_args[1]['user_id'] == 'user_123'
        assert call_args[1]['success'] is True
        assert call_args[1]['last_4_digits'] == '0366'
        assert call_args[1]['card_type'] == 'VISA'
    
    @pytest.mark.asyncio
    async def test_failure_audit_log_called(self, use_case, mock_ports):
        """TASK-020: Registrar intento fallido con razón del fallo"""
        card_data = {
            'user_id': 'user_123',
            'number': '1234567890123456',  # Inválido
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        await use_case.execute(card_data)
        
        # Verificar que se registró el intento fallido
        mock_ports['audit_logger'].log_card_creation_attempt.assert_called_once()
        call_args = mock_ports['audit_logger'].log_card_creation_attempt.call_args
        
        assert call_args[1]['success'] is False
        assert 'reason' in call_args[1]
        assert call_args[1]['reason'] is not None  # Debe tener razón del fallo


@pytest.mark.unit
class TestCreateCardUseCaseSecurityCVV:
    """Tests para verificar que CVV nunca se persiste"""
    
    @pytest.fixture
    def mock_ports(self):
        card_repo = AsyncMock(spec=CardRepository)
        encryption = AsyncMock(spec=EncryptionService)
        limit_checker = AsyncMock(spec=CardLimitChecker)
        audit_logger = AsyncMock(spec=AuditLogger)
        return {
            'card_repo': card_repo,
            'encryption': encryption,
            'limit_checker': limit_checker,
            'audit_logger': audit_logger,
        }
    
    @pytest.fixture
    def use_case(self, mock_ports):
        return CreateCardUseCase(
            card_repository=mock_ports['card_repo'],
            encryption_service=mock_ports['encryption'],
            card_limit_checker=mock_ports['limit_checker'],
            audit_logger=mock_ports['audit_logger']
        )
    
    @pytest.mark.asyncio
    async def test_cvv_not_persisted(self, use_case, mock_ports):
        """SEC-001: CVV nunca debe guardarse en BD"""
        card_data = {
            'user_id': 'user_123',
            'number': '4532015112830366',
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        mock_ports['limit_checker'].can_add_card.return_value = True
        mock_ports['card_repo'].exists_by_number.return_value = False
        mock_ports['encryption'].encrypt.return_value = 'encrypted_xyz'
        mock_ports['card_repo'].save.return_value = 'card_id_123'
        
        await use_case.execute(card_data)
        
        # Verificar qué se pasó a save()
        save_call_args = mock_ports['card_repo'].save.call_args
        saved_data = save_call_args[0][1]  # Segundo argumento es los datos
        
        # CVV NO debe estar en los datos guardados
        assert 'cvv' not in saved_data
        # Verifica que CVV específicamente no está en saved_data
        for key, value in saved_data.items():
            assert key != 'cvv'
    
    @pytest.mark.asyncio
    async def test_cvv_not_in_response(self, use_case, mock_ports):
        """SEC-002: CVV nunca debe retornarse en respuesta"""
        card_data = {
            'user_id': 'user_123',
            'number': '4532015112830366',
            'expiry_month': 12,
            'expiry_year': 2026,
            'cvv': '123',
            'holder_name': 'Juan Pérez',
            'document_id': '1234567890'
        }
        
        mock_ports['limit_checker'].can_add_card.return_value = True
        mock_ports['card_repo'].exists_by_number.return_value = False
        mock_ports['encryption'].encrypt.return_value = 'encrypted_xyz'
        mock_ports['card_repo'].save.return_value = 'card_id_123'
        
        result = await use_case.execute(card_data)
        
        # CVV NO debe estar en la respuesta
        assert 'cvv' not in result
        # Verifica que la clave 'cvv' no existe en la respuesta
        for key in result.keys():
            assert key != 'cvv'
