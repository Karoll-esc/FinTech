"""
CreateCardUseCase - Application Layer Use Case
Implementa TASK-012 a TASK-020 del plan feature-add-card-1.md

Responsabilidades:
1. Orquestar validadores del dominio (Luhn, Expiry, etc.)
2. Verificar límite de 3 tarjetas
3. Detectar duplicados
4. Encriptar número de tarjeta
5. Persistir datos
6. Registrar en auditoría (sin CVV)

NOTA: Este use case NO depende de FastAPI, Pydantic, MongoDB, etc.
Solo depende de puertos (interfaces abstractas).
"""

from typing import Dict, Any, Optional
from src.domain.models import CardType
from src.domain.card_validators import (
    LuhnValidator,
    CardTypeDetector,
    ExpiryValidator,
    CardNumberValidator,
    CVVValidator,
)
from src.application.ports.card_ports import (
    CardRepository,
    EncryptionService,
    CardLimitChecker,
    AuditLogger,
)


class CreateCardUseCase:
    """
    Use Case para crear una nueva tarjeta
    
    Patrón: Dependency Injection para los puertos
    Beneficio: Fácil de testear con mocks
    """
    
    def __init__(
        self,
        card_repository: CardRepository,
        encryption_service: EncryptionService,
        card_limit_checker: CardLimitChecker,
        audit_logger: AuditLogger,
        max_cards: int = 3,
    ):
        """
        Inicializa el use case con sus dependencias (puertos)
        
        Args:
            card_repository: Puerto para persistencia
            encryption_service: Puerto para encriptación AES-256
            card_limit_checker: Puerto para verificar límite de tarjetas
            audit_logger: Puerto para logging de auditoría
            max_cards: Máximo de tarjetas por usuario (por defecto 3)
        """
        self.card_repository = card_repository
        self.encryption_service = encryption_service
        self.card_limit_checker = card_limit_checker
        self.audit_logger = audit_logger
        self.max_cards = max_cards
    
    async def execute(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el use case de creación de tarjeta
        
        Args:
            card_data: {
                'user_id': str,
                'number': str (16 dígitos sin formatos),
                'expiry_month': int (1-12),
                'expiry_year': int (YYYY),
                'cvv': str (3 o 4 dígitos),
                'holder_name': str,
                'document_id': str,
                'nickname': Optional[str]
            }
        
        Returns:
            {
                'success': bool,
                'card_id': str (si exitoso),
                'last_4_digits': str,
                'card_type': str (VISA, MASTERCARD, AMEX),
                'holder_name': str,
                'nickname': str,
                'error': str (si falló),
                'reason': str (si falló)
            }
        """
        try:
            user_id = card_data.get('user_id')
            card_number = card_data.get('number')
            expiry_month = card_data.get('expiry_month')
            expiry_year = card_data.get('expiry_year')
            cvv = card_data.get('cvv')
            holder_name = card_data.get('holder_name')
            document_id = card_data.get('document_id')
            nickname = card_data.get('nickname')
            
            # ===== VALIDACIÓN 1: Validar número con Luhn =====
            if not LuhnValidator.validate(card_number):
                reason = "Número de tarjeta inválido (Luhn check failed)"
                await self.audit_logger.log_card_creation_attempt(
                    user_id=user_id,
                    card_type="UNKNOWN",
                    last_4_digits=card_number[-4:] if len(card_number) >= 4 else "????",
                    success=False,
                    reason=reason
                )
                return {
                    'success': False,
                    'error': 'El número de tarjeta es inválido',
                    'reason': reason
                }
            
            # ===== VALIDACIÓN 2: Detectar tipo de tarjeta =====
            card_type = CardTypeDetector.detect(card_number)
            if card_type is None:
                reason = "Tipo de tarjeta no soportado"
                last_4 = card_number[-4:] if len(card_number) >= 4 else "????"
                await self.audit_logger.log_card_creation_attempt(
                    user_id=user_id,
                    card_type="UNKNOWN",
                    last_4_digits=last_4,
                    success=False,
                    reason=reason
                )
                return {
                    'success': False,
                    'error': 'El tipo de tarjeta no es soportado',
                    'reason': reason
                }
            
            # ===== VALIDACIÓN 3: Validar fecha de vencimiento =====
            if not ExpiryValidator.validate(expiry_month, expiry_year):
                reason = f"Fecha de vencimiento inválida ({expiry_month}/{expiry_year})"
                last_4 = card_number[-4:]
                await self.audit_logger.log_card_creation_attempt(
                    user_id=user_id,
                    card_type=card_type.name,
                    last_4_digits=last_4,
                    success=False,
                    reason=reason
                )
                return {
                    'success': False,
                    'error': 'La fecha de vencimiento es inválida o está expirada',
                    'reason': reason
                }
            
            # ===== VALIDACIÓN 4: Validar CVV =====
            if not CVVValidator.validate(cvv, card_type):
                reason = f"CVV inválido para {card_type.name}"
                last_4 = card_number[-4:]
                await self.audit_logger.log_card_creation_attempt(
                    user_id=user_id,
                    card_type=card_type.name,
                    last_4_digits=last_4,
                    success=False,
                    reason=reason
                )
                return {
                    'success': False,
                    'error': 'El código de seguridad (CVV) es inválido',
                    'reason': reason
                }
            
            # ===== VALIDACIÓN 5: Verificar límite de tarjetas (máx 3) =====
            can_add = await self.card_limit_checker.can_add_card(user_id, self.max_cards)
            if not can_add:
                reason = f"Usuario ya tiene {self.max_cards} tarjetas (límite alcanzado)"
                last_4 = card_number[-4:]
                await self.audit_logger.log_card_creation_attempt(
                    user_id=user_id,
                    card_type=card_type.name,
                    last_4_digits=last_4,
                    success=False,
                    reason=reason
                )
                return {
                    'success': False,
                    'error': f'Has alcanzado el límite de {self.max_cards} tarjetas',
                    'reason': reason
                }
            
            # ===== Extraer últimos 4 dígitos =====
            last_4_digits = card_number[-4:]
            
            # ===== VALIDACIÓN 6: Verificar duplicados =====
            exists = await self.card_repository.exists_by_number(user_id, last_4_digits)
            if exists:
                reason = f"Tarjeta duplicada (últimos 4 dígitos: {last_4_digits})"
                await self.audit_logger.log_card_creation_attempt(
                    user_id=user_id,
                    card_type=card_type.name,
                    last_4_digits=last_4_digits,
                    success=False,
                    reason=reason
                )
                return {
                    'success': False,
                    'error': 'Ya tienes esta tarjeta registrada',
                    'reason': reason
                }
            
            # ===== SEGURIDAD: Encriptar número de tarjeta =====
            encrypted_number = await self.encryption_service.encrypt(card_number)
            
            # ===== Generar nickname si no se proporcionó =====
            if not nickname:
                nickname = f"Tarjeta {card_type.name} {last_4_digits}"
            
            # ===== PERSISTENCIA: Guardar en BD =====
            # IMPORTANTE: NO incluir CVV en los datos guardados
            card_data_to_save = {
                'user_id': user_id,
                'encrypted_number': encrypted_number,
                'last_4_digits': last_4_digits,
                'card_type': card_type.name,
                'expiry_month': expiry_month,
                'expiry_year': expiry_year,
                'holder_name': holder_name,
                'document_id': document_id,
                'nickname': nickname,
                # CVV NO se guarda (security requirement)
            }
            
            card_id = await self.card_repository.save(user_id, card_data_to_save)
            
            # ===== AUDITORÍA: Registrar intento exitoso =====
            await self.audit_logger.log_card_creation_attempt(
                user_id=user_id,
                card_type=card_type.name,
                last_4_digits=last_4_digits,
                success=True
            )
            
            # ===== RESPUESTA: Retornar solo datos no sensibles =====
            # IMPORTANTE: NO retornar número completo ni CVV
            return {
                'success': True,
                'card_id': card_id,
                'last_4_digits': last_4_digits,
                'card_type': card_type.name,
                'holder_name': holder_name,
                'nickname': nickname,
                # No incluir: number, cvv, encrypted_number, document_id
            }
        
        except Exception as e:
            # Error inesperado
            reason = f"Error interno: {str(e)}"
            try:
                user_id = card_data.get('user_id')
                card_number = card_data.get('number')
                if user_id and card_number:
                    last_4 = card_number[-4:] if len(card_number) >= 4 else "????"
                    await self.audit_logger.log_card_creation_attempt(
                        user_id=user_id,
                        card_type="UNKNOWN",
                        last_4_digits=last_4,
                        success=False,
                        reason=reason
                    )
            except:
                pass  # Si falla el log de auditoría, no fallar completamente
            
            return {
                'success': False,
                'error': 'Ocurrió un error al procesar tu solicitud',
                'reason': reason
            }
