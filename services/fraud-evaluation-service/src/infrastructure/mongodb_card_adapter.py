"""
MongoDB Card Adapter - Infrastructure Layer
Implementa el puerto CardRepository con MongoDB

Cumple con:
- Hexagonal Architecture: Adaptador que implementa port
- Dependency Inversion: Infraestructura depende de abstracción
- Clean Architecture: Capa que adapta tecnología externa
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from src.application.ports.card_ports import CardRepository


class MongoDBCardAdapter(CardRepository):
    """
    Adaptador MongoDB para CardRepository
    
    Persiste datos de tarjetas con seguridad PCI DSS:
    - Solo almacena últimos 4 dígitos
    - Número encriptado almacenado
    - No almacena CVV
    """
    
    def __init__(self, collection):
        """
        Inicializa el adaptador con colección MongoDB
        
        Args:
            collection: pymongo collection para tarjetas
        """
        self.collection = collection
        self._create_indexes()
    
    def _create_indexes(self):
        """Crea índices para optimización de queries"""
        try:
            # Índice en user_id para búsquedas por usuario
            self.collection.create_index("user_id")
            # Índice compuesto para búsquedas de duplicados
            self.collection.create_index([("user_id", 1), ("last_4_digits", 1)])
        except:
            pass  # Si los índices ya existen o mongomock, ignorar
    
    async def save(self, user_id: str, card_data: dict) -> str:
        """
        Guarda una tarjeta y retorna su ID
        
        Args:
            user_id: ID del usuario propietario
            card_data: Datos de la tarjeta (número encriptado, últimos 4, tipo, etc.)
            
        Returns:
            str: ID de la tarjeta guardada
        """
        # Preparar documento para MongoDB
        document = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            **card_data  # Desempaquetacar datos de tarjeta
        }
        
        # Insertar documento
        result = self.collection.insert_one(document)
        
        # Retornar ID del documento insertado
        return str(result.inserted_id)
    
    async def find_by_user_id(self, user_id: str) -> List[dict]:
        """
        Obtiene todas las tarjetas de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            List[dict]: Lista de tarjetas (sin números sensibles)
        """
        # Buscar todas las tarjetas del usuario
        cards = self.collection.find(
            {'user_id': user_id},
            {
                'encrypted_number': 0,  # No retornar número encriptado
                'document_id': 0  # No retornar documento de identidad
            }
        ).sort('created_at', -1)  # Ordenar por más reciente primero
        
        # Convertir cursor a lista
        return list(cards)
    
    async def exists_by_number(self, user_id: str, last_4_digits: str) -> bool:
        """
        Verifica si una tarjeta ya existe para este usuario
        
        Args:
            user_id: ID del usuario
            last_4_digits: Últimos 4 dígitos
            
        Returns:
            bool: True si ya existe, False si no
        """
        # Buscar tarjeta con estos últimos 4 dígitos
        card = self.collection.find_one({
            'user_id': user_id,
            'last_4_digits': last_4_digits
        })
        
        return card is not None
    
    async def count_by_user_id(self, user_id: str) -> int:
        """
        Cuenta cuántas tarjetas tiene un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            int: Cantidad de tarjetas
        """
        # Contar documentos con este user_id
        count = self.collection.count_documents({'user_id': user_id})
        return count
