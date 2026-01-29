/**
 * Card Utility Functions
 * HU-016: Add Card - Phase 4 Frontend
 * 
 * Pure utility functions for card formatting, validation, and detection
 * No React dependencies - can be used in any context
 */

export type CardType = 'VISA' | 'MASTERCARD' | 'AMEX' | 'UNKNOWN';

/**
 * Formats card number into 4-4-4-4 spacing
 * @param cardNumber - Raw card number (with or without spaces/dashes)
 * @returns Formatted card number with spaces
 */
export function formatCardNumber(cardNumber: string): string {
  if (!cardNumber) return '';
  
  // Remove all non-digit characters
  const digitsOnly = cardNumber.replace(/\D/g, '');
  
  // Limit to 19 digits max
  const truncated = digitsOnly.slice(0, 19);
  
  // Format as 4-4-4-4-4 (up to 19 digits)
  return truncated.replace(/(\d{4})(?=\d)/g, '$1 ');
}

/**
 * Validates card number using Luhn algorithm
 * @param cardNumber - Card number (with or without formatting)
 * @returns true if valid, false otherwise
 */
export function luhnChecksum(cardNumber: string): boolean {
  if (!cardNumber) return false;
  
  // Remove all non-digit characters
  const digitsOnly = cardNumber.replace(/\D/g, '');
  
  // Luhn algorithm
  let sum = 0;
  let isEven = false;
  
  for (let i = digitsOnly.length - 1; i >= 0; i--) {
    let digit = parseInt(digitsOnly[i], 10);
    
    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    
    sum += digit;
    isEven = !isEven;
  }
  
  return sum % 10 === 0;
}

/**
 * Masks card number showing only last 4 digits
 * @param cardNumber - Card number (with or without formatting)
 * @returns Masked card number (**** **** **** 0366)
 */
export function maskCardNumber(cardNumber: string): string {
  if (!cardNumber) return '';
  
  // Remove non-digit characters
  const digitsOnly = cardNumber.replace(/\D/g, '');
  
  if (digitsOnly.length < 4) return '*'.repeat(digitsOnly.length);
  
  const last4 = digitsOnly.slice(-4);
  const stars = '*'.repeat(digitsOnly.length - 4);
  
  // Format as **** **** **** 0366
  return (stars + last4).replace(/(\*{4})(?=[\*\d])/g, '$1 ').trim();
}

/**
 * Formats expiry date input to MM/YY format
 * @param input - Raw input (e.g., "1225" or "12/25")
 * @returns Formatted expiry (MM/YY)
 */
export function formatExpiry(input: string): string {
  if (!input) return '';
  
  // Remove all non-digit characters
  const digitsOnly = input.replace(/\D/g, '');
  
  // Limit to 4 digits
  const truncated = digitsOnly.slice(0, 4);
  
  // Format as MM/YY
  if (truncated.length >= 2) {
    return truncated.slice(0, 2) + '/' + truncated.slice(2, 4);
  }
  
  return truncated;
}

/**
 * Parses expiry date string into month and year
 * @param expiryStr - Formatted expiry string (MM/YY or MMYY)
 * @returns Object with month (1-12) and year (2-digit or 4-digit)
 */
export function parseExpiry(expiryStr: string): { month: number; year: number } | null {
  if (!expiryStr) return null;
  
  // Handle both MM/YY and MMYY formats
  const parts = expiryStr.replace(/\D/g, '');
  
  if (parts.length !== 4) return null;
  
  const month = parseInt(parts.slice(0, 2), 10);
  let year = parseInt(parts.slice(2, 4), 10);
  
  // Convert 2-digit year to 4-digit
  if (year < 100) {
    year += year < 30 ? 2000 : 2000; // Assume 20xx for all 2-digit years
    year = year > 2100 ? year - 100 : year;
  }
  
  return { month, year };
}

/**
 * Checks if card is expired
 * @param month - Expiry month (1-12)
 * @param year - Expiry year (4-digit)
 * @returns true if expired, false if valid
 */
export function isCardExpired(month: number, year: number): boolean {
  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth() + 1; // getMonth returns 0-11
  
  // Card is valid until end of expiry month
  if (year < currentYear) return true;
  if (year === currentYear && month < currentMonth) return true;
  
  return false;
}

/**
 * Detects card type from card number
 * @param cardNumber - Card number (digits only)
 * @returns Card type (VISA, MASTERCARD, AMEX, or UNKNOWN)
 */
export function detectCardType(cardNumber: string): CardType {
  if (!cardNumber) return 'UNKNOWN';
  
  const digitsOnly = cardNumber.replace(/\D/g, '');
  const firstDigit = digitsOnly[0];
  const firstTwoDigits = digitsOnly.slice(0, 2);
  
  // VISA: starts with 4
  if (firstDigit === '4') return 'VISA';
  
  // MASTERCARD: starts with 51-55 or 2221-2720
  if (/^(51|52|53|54|55)/.test(digitsOnly)) return 'MASTERCARD';
  if (/^(222[1-9]|22[3-9]\d|2[3-6]\d{2}|27[01]\d|2720)/.test(digitsOnly)) return 'MASTERCARD';
  
  // AMEX: starts with 34 or 37
  if (/^(34|37)/.test(firstTwoDigits)) return 'AMEX';
  
  return 'UNKNOWN';
}

/**
 * Gets card type icon identifier
 * @param cardType - Card type
 * @returns Icon identifier (for use in UI)
 */
export function getCardTypeIcon(cardType: CardType): string {
  const iconMap: Record<CardType, string> = {
    VISA: 'visa',
    MASTERCARD: 'mastercard',
    AMEX: 'amex',
    UNKNOWN: 'card',
  };
  
  return iconMap[cardType];
}

/**
 * Gets human-readable card type label
 * @param cardType - Card type
 * @returns Human-readable label
 */
export function getCardTypeLabel(cardType: CardType): string {
  const labelMap: Record<CardType, string> = {
    VISA: 'Visa',
    MASTERCARD: 'Mastercard',
    AMEX: 'American Express',
    UNKNOWN: 'Card',
  };
  
  return labelMap[cardType];
}

/**
 * Generates default nickname for card
 * @param cardType - Card type
 * @param last4Digits - Last 4 digits of card (optional)
 * @returns Generated nickname (e.g., "Mi VISA" or "Mi VISA ...0366")
 */
export function generateNickname(cardType: CardType, last4Digits?: string): string {
  const label = getCardTypeLabel(cardType);
  
  if (last4Digits && last4Digits.length === 4) {
    return `Mi ${label} ...${last4Digits}`;
  }
  
  return `Mi ${label}`;
}
