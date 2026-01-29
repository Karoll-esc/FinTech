"""
CardLimitCheckerAdapter - Card Limit Implementation
Implementa el puerto CardLimitChecker

Regla: Máximo 3 tarjetas por usuario
"""

from src.application.ports.card_ports import CardLimitChecker, CardRepository


class CardLimitCheckerAdapter(CardLimitChecker):
    """
    Adaptador que verifica el límite de tarjetas por usuario
    
    Depende del puerto CardRepository para contar tarjetas existentes.
    """
    
    def __init__(self, card_repository: CardRepository):
        """
        Inicializa el adaptador con una dependencia al repositorio
        
        Args:
            card_repository: Puerto CardRepository para acceder a datos
        """
        self.card_repository = card_repository
    
    async def can_add_card(self, user_id: str, max_cards: int = 3) -> bool:
        """
        Verifica si el usuario puede agregar una tarjeta más
        
        Args:
            user_id: ID del usuario
            max_cards: Máximo permitido (por defecto 3)
            
        Returns:
            bool: True si puede agregar, False si ya tiene el máximo
        """
        # Contar tarjetas existentes
        count = await self.card_repository.count_by_user_id(user_id)
        
        # Permitir agregar si está por debajo del límite
        return count < max_cards
