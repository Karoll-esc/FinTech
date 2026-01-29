"""
MongoDB Card Adapter - Infrastructure Layer
TASK-025 a TASK-029: Implementación de CardRepository para MongoDB

Cumple con:
- Hexagonal Architecture: Adaptador que implementa port (CardRepository)
- Dependency Inversion: Infraestructura depende de dominio, no al revés
- Clean Architecture: Capa de infraestructura adapta tecnología externa
"""
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Card, CardStatus, CardType
from src.application.ports.card_repository import CardRepository


class MongoDBCardAdapter(CardRepository):
    """
    Adaptador MongoDB para CardRepository
    
    TASK-025: Implementar adaptador que persiste tarjetas en MongoDB
    TASK-026: Implementar get_by_user_id con ordenamiento
    TASK-027: Implementar save con validación de duplicados
    TASK-028: Implementar get_by_id
    TASK-029: Crear índices para optimización
    
    Notas de seguridad (PCI-DSS):
    - Solo almacena últimos 4 dígitos del número de tarjeta
    - No almacena CVV ni información sensible
    - Cifrado en tránsito (TLS) manejado por MongoDB
    """
    
    def __init__(self, collection):
        """
        TASK-025: Inicializar adaptador con colección MongoDB
        
        Args:
            collection: pymongo.collection.Collection o mongomock collection
        """
        self._collection = collection
    
    def save(self, card: Card) -> None:
        """
        TASK-027: Guardar tarjeta en MongoDB
        
        Args:
            card: Tarjeta a persistir
            
        Raises:
            ValueError: Si la tarjeta ya existe (ID duplicado)
        """
        # Verificar que no exista tarjeta con el mismo ID
        existing = self._collection.find_one({"_id": card.id})
        if existing:
            raise ValueError(f"Card with id {card.id} already exists")
        
        # Preparar documento MongoDB
        document = {
            "_id": card.id,  # Usar card.id como _id de MongoDB
            "user_id": card.user_id,
            "card_number": card.card_number,  # Solo últimos 4 dígitos (ya enmascarado)
            "card_type": card.card_type.value,  # Guardar valor numérico del enum
            "balance": str(card.balance),  # Convertir Decimal a string para preservar precisión
            "status": card.status.value,  # Guardar valor numérico del enum
            "nickname": card.nickname,
            "created_at": card.created_at
        }
        
        # Insertar en MongoDB
        self._collection.insert_one(document)
    
    def get_by_user_id(self, user_id: str) -> List[Card]:
        """
        TASK-026: Obtener todas las tarjetas de un usuario
        
        Args:
            user_id: Identificador del usuario
            
        Returns:
            Lista de tarjetas ordenadas por created_at DESC
            Lista vacía si el usuario no tiene tarjetas
        """
        # Buscar todas las tarjetas del usuario
        cursor = self._collection.find({"user_id": user_id})
        
        # Ordenar por created_at descendente (más nueva primero)
        cursor = cursor.sort("created_at", -1)  # -1 = DESC
        
        # Convertir documentos a objetos Card
        cards = []
        for doc in cursor:
            cards.append(self._document_to_card(doc))
        
        return cards
    
    def get_by_id(self, card_id: str) -> Optional[Card]:
        """
        TASK-028: Obtener tarjeta por ID
        
        Args:
            card_id: Identificador de la tarjeta
            
        Returns:
            Card si existe, None si no se encuentra
        """
        document = self._collection.find_one({"_id": card_id})
        
        if document is None:
            return None
        
        return self._document_to_card(document)
    
    def ensure_indexes(self) -> None:
        """
        TASK-029: Crear índices para optimización
        
        Índices creados:
        - user_id: Para búsquedas rápidas por usuario
        - user_id + created_at: Para ordenamiento eficiente
        
        Note: Este método debe llamarse al inicializar la aplicación
        """
        # Índice en user_id para get_by_user_id()
        self._collection.create_index("user_id")
        
        # Índice compuesto para ordenamiento eficiente
        self._collection.create_index([
            ("user_id", 1),      # Ascendente
            ("created_at", -1)   # Descendente
        ])
    
    def _document_to_card(self, document: dict) -> Card:
        """
        Convertir documento MongoDB a objeto Card del dominio
        
        Args:
            document: Documento de MongoDB
            
        Returns:
            Objeto Card del dominio
        """
        return Card(
            id=document["_id"],
            user_id=document["user_id"],
            card_number=document["card_number"],
            card_type=CardType(document["card_type"]),  # Convertir int a enum
            balance=Decimal(document["balance"]),  # Convertir string a Decimal
            status=CardStatus(document["status"]),  # Convertir int a enum
            nickname=document.get("nickname"),  # Puede ser None
            created_at=document["created_at"]
        )
