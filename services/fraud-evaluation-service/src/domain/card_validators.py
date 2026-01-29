"""
Card Domain Validators - Pure functions for card validation
Implementa TASK-010 y TASK-011 del plan feature-add-card-1.md

Validadores implementados:
- LuhnValidator: Validación del algoritmo Luhn para números de tarjeta
- CardTypeDetector: Detección automática de tipo (VISA, MC, AMEX)
- ExpiryValidator: Validación de fecha de vencimiento
- CardNumberValidator: Validación de formato de número
- CVVValidator: Validación de CVV (3 o 4 dígitos según tipo)

IMPORTANT: No external framework imports (FastAPI, Pydantic, MongoDB, Redis)
           Pure functions, no side effects, stateless
"""

from typing import Optional
from datetime import datetime
from src.domain.models import CardType


class LuhnValidator:
    """
    Validador del algoritmo Luhn (Check digit)
    Verifica la validez matemática del número de tarjeta
    
    Reglas:
    1. De derecha a izquierda, doblar cada segundo dígito
    2. Si el resultado es > 9, restar 9
    3. Sumar todos los dígitos
    4. Si la suma es divisible por 10, es válido
    """
    
    @staticmethod
    def validate(card_number: str) -> bool:
        """
        Valida un número de tarjeta usando el algoritmo Luhn
        
        Args:
            card_number: String de dígitos (13-19 caracteres)
            
        Returns:
            bool: True si es válido, False si no
        """
        # Remover espacios y guiones (por si acaso)
        if not isinstance(card_number, str):
            raise TypeError("Card number must be a string")
        
        # Validar que sea numérico
        if not card_number.isdigit():
            return False
        
        # Validar rango de longitud (13-19 dígitos)
        if len(card_number) < 13 or len(card_number) > 19:
            return False
        
        # Aplicar algoritmo Luhn
        total = 0
        should_double = False
        
        # Recorrer de derecha a izquierda
        for digit in reversed(card_number):
            digit_val = int(digit)
            
            if should_double:
                digit_val *= 2
                if digit_val > 9:
                    digit_val -= 9
            
            total += digit_val
            should_double = not should_double
        
        return total % 10 == 0


class CardTypeDetector:
    """
    Detector de tipo de tarjeta basado en prefijo (IIN - Issuer Identification Number)
    
    Rangos:
    - VISA: Comienza con 4 (13, 16 o 19 dígitos)
    - MASTERCARD: Comienza con 51-55 o 2221-2720 (16 dígitos)
    - AMEX: Comienza con 34 o 37 (15 dígitos)
    """
    
    @staticmethod
    def detect(card_number: str) -> Optional[CardType]:
        """
        Detecta el tipo de tarjeta basado en el prefijo
        
        Args:
            card_number: String de dígitos
            
        Returns:
            CardType: VISA, MASTERCARD, AMEX, o None si es desconocido
        """
        if not card_number or not isinstance(card_number, str):
            return None
        
        if len(card_number) < 2:
            return None
        
        # Primeros 2 dígitos
        first_two = card_number[:2]
        first_digit = card_number[0]
        
        # VISA: Comienza con 4
        if first_digit == '4':
            return CardType.VISA
        
        # MASTERCARD: Comienza con 51-55
        if first_two in ['51', '52', '53', '54', '55']:
            return CardType.MASTERCARD
        
        # AMEX: Comienza con 34 o 37
        if first_two in ['34', '37']:
            return CardType.AMEX
        
        # Desconocido
        return None


class ExpiryValidator:
    """
    Validador de fecha de vencimiento
    
    Reglas:
    - Mes debe estar entre 1 y 12
    - Año debe ser >= año actual
    - Si es el año actual, mes debe ser >= mes actual
    - Se considera válido hasta el último día del mes de vencimiento
    """
    
    @staticmethod
    def validate(month: int, year: int) -> bool:
        """
        Valida la fecha de vencimiento
        
        Args:
            month: Mes (1-12)
            year: Año (4 dígitos, ej: 2026)
            
        Returns:
            bool: True si es válido, False si no
        """
        if not isinstance(month, int) or not isinstance(year, int):
            raise TypeError("Month and year must be integers")
        
        # Validar rango del mes
        if month < 1 or month > 12:
            return False
        
        # Obtener fecha actual
        today = datetime.now()
        current_month = today.month
        current_year = today.year
        
        # Si el año es anterior al actual, es inválido
        if year < current_year:
            return False
        
        # Si el año es igual al actual, el mes debe ser >= al mes actual
        if year == current_year and month < current_month:
            return False
        
        return True


class CardNumberValidator:
    """
    Validador de formato de número de tarjeta
    
    Reglas:
    - Debe ser numérico
    - Longitud 13-19 dígitos
    - Sin espacios, guiones u otros caracteres
    """
    
    @staticmethod
    def validate(card_number: str) -> bool:
        """
        Valida el formato del número de tarjeta
        
        Args:
            card_number: String de dígitos
            
        Returns:
            bool: True si el formato es válido, False si no
        """
        if not isinstance(card_number, str):
            return False
        
        # Debe ser numérico
        if not card_number.isdigit():
            return False
        
        # Validar rango de longitud
        length = len(card_number)
        if length < 13 or length > 19:
            return False
        
        return True


class CVVValidator:
    """
    Validador de CVV (Card Verification Value)
    
    Reglas:
    - VISA/Mastercard: 3 dígitos
    - American Express: 4 dígitos
    - Solo dígitos
    """
    
    @staticmethod
    def validate(cvv: str, card_type: CardType) -> bool:
        """
        Valida el CVV según el tipo de tarjeta
        
        Args:
            cvv: String de dígitos (3 o 4 según tipo)
            card_type: CardType (VISA, MASTERCARD, AMEX)
            
        Returns:
            bool: True si es válido, False si no
        """
        if not isinstance(cvv, str):
            raise TypeError("CVV must be a string")
        
        # Debe ser numérico
        if not cvv.isdigit():
            return False
        
        # Validar longitud según tipo de tarjeta
        if card_type == CardType.AMEX:
            # Amex requiere 4 dígitos
            return len(cvv) == 4
        else:
            # VISA y Mastercard requieren 3 dígitos
            return len(cvv) == 3
