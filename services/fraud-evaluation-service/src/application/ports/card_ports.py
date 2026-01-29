"""
Port Interfaces (Abstractions) for Card Management Use Cases
Following Dependency Inversion Principle (SOLID)

Nota: Los puertos son interfaces que definen contratos entre capas.
Application layer depende de estos puertos abstractos,
Infrastructure layer implementa estos puertos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal


class CardRepository(ABC):
    """
    Puerto (interface) para persistencia de tarjetas
    
    El use case depende de este puerto (abstracción).
    Infrastructure implementará este puerto con MongoDB, etc.
    """
    
    @abstractmethod
    async def save(self, user_id: str, card_data: dict) -> str:
        """
        Guarda una tarjeta y retorna su ID
        
        Args:
            user_id: ID del usuario propietario
            card_data: Datos de la tarjeta (número encriptado, últimos 4, tipo, etc.)
            
        Returns:
            str: ID de la tarjeta guardada
            
        Raises:
            ValueError: Si los datos son inválidos
            Exception: Si hay error de persistencia
        """
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[dict]:
        """
        Obtiene todas las tarjetas de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            List[dict]: Lista de tarjetas (sin números sensibles)
        """
        pass
    
    @abstractmethod
    async def exists_by_number(self, user_id: str, last_4_digits: str) -> bool:
        """
        Verifica si una tarjeta ya existe para este usuario
        (por últimos 4 dígitos)
        
        Args:
            user_id: ID del usuario
            last_4_digits: Últimos 4 dígitos de la tarjeta
            
        Returns:
            bool: True si ya existe, False si no
        """
        pass
    
    @abstractmethod
    async def count_by_user_id(self, user_id: str) -> int:
        """
        Cuenta cuántas tarjetas tiene un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            int: Cantidad de tarjetas
        """
        pass


class EncryptionService(ABC):
    """
    Puerto para servicio de encriptación AES-256
    
    El use case depende de este puerto.
    Infrastructure implementará con la librería cryptography.
    """
    
    @abstractmethod
    async def encrypt(self, plaintext: str) -> str:
        """
        Encripta un string con AES-256
        
        Args:
            plaintext: Texto a encriptar (ej: número de tarjeta)
            
        Returns:
            str: Texto encriptado (puede incluir IV + ciphertext)
        """
        pass
    
    @abstractmethod
    async def decrypt(self, ciphertext: str) -> str:
        """
        Desencripta un string
        
        Args:
            ciphertext: Texto encriptado
            
        Returns:
            str: Texto desencriptado
        """
        pass


class CardLimitChecker(ABC):
    """
    Puerto para verificar límites de tarjetas por usuario
    
    El use case depende de este puerto.
    Infrastructure implementará con lógica de negocio.
    """
    
    @abstractmethod
    async def can_add_card(self, user_id: str, max_cards: int = 3) -> bool:
        """
        Verifica si el usuario puede agregar una tarjeta más
        (máximo 3 tarjetas por usuario)
        
        Args:
            user_id: ID del usuario
            max_cards: Máximo permitido (por defecto 3)
            
        Returns:
            bool: True si puede agregar, False si ya tiene el máximo
        """
        pass


class AuditLogger(ABC):
    """
    Puerto para logging de auditoría de intentos de agregar tarjetas
    
    Importante: No loguear CVV, número completo, etc.
    Solo loguear: user_id, timestamp, resultado (success/failure), razón de fallo
    """
    
    @abstractmethod
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
            reason: Razón de fallo si aplica
        """
        pass
