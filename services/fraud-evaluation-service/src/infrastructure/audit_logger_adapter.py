"""
AuditLoggerAdapter - Audit Trail Implementation
Implementa el puerto AuditLogger para logging de intentos de crear tarjetas

Importante: NO loguea CVV, número completo, o información sensible
Solo loguea: user_id, timestamp, resultado, razón de fallo
"""

from datetime import datetime
from typing import Optional
from src.application.ports.card_ports import AuditLogger


class AuditLoggerAdapter(AuditLogger):
    """
    Adaptador que registra intentos de crear tarjetas en MongoDB
    
    Cumplimiento PCI DSS: NO almacena datos sensibles en logs
    """
    
    def __init__(self, collection):
        """
        Inicializa el adaptador con una colección MongoDB
        
        Args:
            collection: Colección MongoDB para audit logs
        """
        self.collection = collection
    
    async def log_card_creation_attempt(
        self,
        user_id: str,
        card_type: str,
        last_4_digits: str,
        success: bool,
        reason: Optional[str] = None
    ) -> None:
        """
        Registra un intento de crear tarjeta en auditoría
        
        Args:
            user_id: ID del usuario
            card_type: Tipo de tarjeta (VISA, MC, AMEX)
            last_4_digits: Últimos 4 dígitos (sin número completo)
            success: ¿Fue exitoso?
            reason: Razón de fallo si aplica (no incluye datos sensibles)
        """
        # Crear documento de auditoría
        audit_log = {
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'card_type': card_type,
            'last_4_digits': last_4_digits,
            'success': success,
        }
        
        # Agregar razón si aplica
        if reason:
            audit_log['reason'] = reason
        
        # Insertar en MongoDB
        await self.collection.insert_one(audit_log)
