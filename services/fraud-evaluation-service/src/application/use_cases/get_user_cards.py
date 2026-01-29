"""
GetUserCardsUseCase - Caso de uso para obtener tarjetas de usuario
TASK-017 a TASK-020: Implementación del caso de uso

Cumple con:
- Clean Architecture: Orquesta dominio + puertos
- DIP: Depende de CardRepository (abstracción), no de implementación
- SRP: Solo una responsabilidad - obtener y ordenar tarjetas
"""
import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "services" / "fraud-evaluation-service"))

from src.domain.models import Card
from src.application.ports.card_repository import CardRepository


class GetUserCardsUseCase:
    """
    Caso de Uso: Obtener tarjetas de un usuario
    
    TASK-017: Inyección de dependencias (CardRepository)
    TASK-018: Ordenamiento descendente por created_at
    TASK-019: Retornar máximo 3 tarjetas
    TASK-020: Validación y manejo de edge cases
    
    Reglas de negocio:
    - Máximo 3 tarjetas por usuario (HU-015)
    - Ordenadas por fecha de creación DESC (más nueva primero)
    - Sin filtros por estado (retorna todas: ACTIVE, BLOCKED, SUSPENDED)
    """
    
    def __init__(self, card_repository: CardRepository):
        """
        TASK-017: Constructor con inyección de dependencias
        
        Args:
            card_repository: Implementación de CardRepository (port)
        """
        self._card_repository = card_repository
    
    def execute(self, user_id: str) -> List[Card]:
        """
        Ejecutar caso de uso: obtener tarjetas del usuario
        
        Args:
            user_id: Identificador del usuario
            
        Returns:
            Lista de hasta 3 tarjetas ordenadas por created_at DESC
            Lista vacía si el usuario no tiene tarjetas
            
        TASK-018: Ordenamiento garantizado por created_at DESC
        TASK-019: Limitado a máximo 3 tarjetas
        TASK-020: Manejo de casos edge (vacío, saldos cero, diferentes estados)
        """
        # TASK-017: Delegar recuperación al repositorio
        cards = self._card_repository.get_by_user_id(user_id)
        
        # TASK-018: Ordenar por created_at descendente (más nueva primero)
        # Nota: Asumimos que el repositorio puede retornar sin orden garantizado,
        # por lo que el caso de uso debe garantizar el ordenamiento
        sorted_cards = sorted(cards, key=lambda card: card.created_at, reverse=True)
        
        # TASK-019: Limitar a 3 tarjetas máximo (requisito de negocio HU-015)
        return sorted_cards[:3]
