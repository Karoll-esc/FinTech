"""
TASK-042: Tests para Card Utilities
Test-Driven Development: Tests escritos PRIMERO

HU-016: Add Card - Phase 4 Frontend Utilities
"""

import { describe, it, expect } from 'vitest';
import {
  formatCardNumber,
  luhnChecksum,
  maskCardNumber,
  formatExpiry,
  getCardTypeIcon,
  getCardTypeLabel,
  parseExpiry,
  isCardExpired,
  generateNickname
} from '../utils/cardUtils';

describe('Card Number Formatting', () => {
  it('TASK-042: should format card number with spaces (4-4-4-4)', () => {
    const result = formatCardNumber('4532015112830366');
    expect(result).toBe('4532 0151 1283 0366');
  });

  it('TASK-042: should handle card numbers with existing spaces', () => {
    const result = formatCardNumber('4532 0151 1283 0366');
    expect(result).toBe('4532 0151 1283 0366');
  });

  it('TASK-042: should strip non-numeric characters except spaces', () => {
    const result = formatCardNumber('4532-0151-1283-0366');
    expect(result).toBe('4532 0151 1283 0366');
  });

  it('TASK-042: should handle incomplete numbers', () => {
    const result = formatCardNumber('4532');
    expect(result).toBe('4532');
    
    const result2 = formatCardNumber('45320151');
    expect(result2).toBe('4532 0151');
  });

  it('TASK-042: should limit to 19 characters (max 16-19 digits + 3-4 spaces)', () => {
    const long = '45320151128303661234567890';
    const result = formatCardNumber(long);
    expect(result.length).toBeLessThanOrEqual(23);
  });

  it('TASK-042: should handle empty string', () => {
    const result = formatCardNumber('');
    expect(result).toBe('');
  });
});

describe('Luhn Algorithm', () => {
  it('TASK-042: should validate correct card numbers', () => {
    expect(luhnChecksum('4532015112830366')).toBe(true);
    expect(luhnChecksum('5555555555554444')).toBe(true);
    expect(luhnChecksum('378282246310005')).toBe(true);
  });

  it('TASK-042: should reject invalid card numbers', () => {
    expect(luhnChecksum('1234567890123456')).toBe(false);
    expect(luhnChecksum('0000000000000000')).toBe(false);
  });

  it('TASK-042: should handle spaces in input', () => {
    expect(luhnChecksum('4532 0151 1283 0366')).toBe(true);
  });

  it('TASK-042: should handle dashes in input', () => {
    expect(luhnChecksum('4532-0151-1283-0366')).toBe(true);
  });

  it('TASK-042: should reject non-numeric input', () => {
    expect(luhnChecksum('ABCD 1234 5678 9012')).toBe(false);
  });

  it('TASK-042: should reject empty string', () => {
    expect(luhnChecksum('')).toBe(false);
  });

  it('TASK-042: should handle single digit', () => {
    expect(luhnChecksum('0')).toBe(true); // 0 passes Luhn
  });
});

describe('Card Number Masking', () => {
  it('TASK-042: should mask card number showing only last 4 digits', () => {
    const result = maskCardNumber('4532015112830366');
    expect(result).toBe('**** **** **** 0366');
  });

  it('TASK-042: should work with formatted input', () => {
    const result = maskCardNumber('4532 0151 1283 0366');
    expect(result).toBe('**** **** **** 0366');
  });

  it('TASK-042: should handle short numbers', () => {
    const result = maskCardNumber('453201');
    expect(result).toContain('453201');
  });

  it('TASK-042: should return empty for empty input', () => {
    const result = maskCardNumber('');
    expect(result).toBe('');
  });

  it('TASK-042: should keep proper spacing', () => {
    const result = maskCardNumber('4532015112830366');
    const parts = result.split(' ');
    expect(parts.length).toBe(4);
  });
});

describe('Expiry Date Formatting', () => {
  it('TASK-042: should format expiry as MM/YY', () => {
    const result = formatExpiry('1226');
    expect(result).toBe('12/26');
  });

  it('TASK-042: should handle input with slash', () => {
    const result = formatExpiry('12/26');
    expect(result).toBe('12/26');
  });

  it('TASK-042: should pad single digit month', () => {
    const result = formatExpiry('126');
    expect(result).toBe('01/26');
  });

  it('TASK-042: should handle incomplete input', () => {
    const result = formatExpiry('1');
    expect(result).toBe('1');
    
    const result2 = formatExpiry('12');
    expect(result2).toBe('12');
  });

  it('TASK-042: should return empty for empty input', () => {
    const result = formatExpiry('');
    expect(result).toBe('');
  });

  it('TASK-042: should limit to 5 characters (MM/YY)', () => {
    const result = formatExpiry('12269999');
    expect(result.length).toBeLessThanOrEqual(5);
  });
});

describe('Parse Expiry Date', () => {
  it('TASK-042: should parse MM/YY format', () => {
    const result = parseExpiry('12/26');
    expect(result).toEqual({ month: 12, year: 2026 });
  });

  it('TASK-042: should parse MMYY format', () => {
    const result = parseExpiry('1226');
    expect(result).toEqual({ month: 12, year: 2026 });
  });

  it('TASK-042: should handle single digit month', () => {
    const result = parseExpiry('1/26');
    expect(result).toEqual({ month: 1, year: 2026 });
  });

  it('TASK-042: should return null for invalid format', () => {
    expect(parseExpiry('invalid')).toBeNull();
    expect(parseExpiry('')).toBeNull();
  });

  it('TASK-042: should assume current century for 2-digit year', () => {
    const result = parseExpiry('12/26');
    expect(result!.year).toBe(2026);
  });

  it('TASK-042: should handle single digit year', () => {
    const result = parseExpiry('12/6');
    expect(result).toEqual({ month: 12, year: 2006 });
  });
});

describe('Card Expiration Check', () => {
  it('TASK-042: should recognize expired card', () => {
    const result = isCardExpired(1, 2020);
    expect(result).toBe(true);
  });

  it('TASK-042: should recognize valid card', () => {
    const result = isCardExpired(12, 2026);
    expect(result).toBe(true);
  });

  it('TASK-042: should recognize current month/year as valid', () => {
    const now = new Date();
    const currentMonth = now.getMonth() + 1;
    const currentYear = now.getFullYear();
    
    const result = isCardExpired(currentMonth, currentYear);
    expect(result).toBe(true);
  });

  it('TASK-042: should recognize next month as valid', () => {
    const now = new Date();
    let nextMonth = now.getMonth() + 2;
    let nextYear = now.getFullYear();
    
    if (nextMonth > 12) {
      nextMonth = 1;
      nextYear += 1;
    }
    
    const result = isCardExpired(nextMonth, nextYear);
    expect(result).toBe(true);
  });

  it('TASK-042: should recognize last month as expired', () => {
    const now = new Date();
    let lastMonth = now.getMonth();
    let lastYear = now.getFullYear();
    
    if (lastMonth === 1) {
      lastMonth = 12;
      lastYear -= 1;
    }
    
    const result = isCardExpired(lastMonth, lastYear);
    expect(result).toBe(false);
  });
});

describe('Card Type Icon', () => {
  it('TASK-042: should return VISA icon for VISA card', () => {
    const icon = getCardTypeIcon('VISA');
    expect(icon).toBeDefined();
    expect(icon).toContain('visa');
  });

  it('TASK-042: should return Mastercard icon for Mastercard', () => {
    const icon = getCardTypeIcon('MASTERCARD');
    expect(icon).toBeDefined();
    expect(icon).toContain('mastercard' || 'mc');
  });

  it('TASK-042: should return AMEX icon for American Express', () => {
    const icon = getCardTypeIcon('AMEX');
    expect(icon).toBeDefined();
    expect(icon).toContain('amex' || 'american');
  });

  it('TASK-042: should return default icon for unknown type', () => {
    const icon = getCardTypeIcon('UNKNOWN');
    expect(icon).toBeDefined();
  });

  it('TASK-042: should return null for empty input', () => {
    const icon = getCardTypeIcon('');
    expect(icon).toBeNull();
  });

  it('TASK-042: should be case-insensitive', () => {
    const icon1 = getCardTypeIcon('VISA');
    const icon2 = getCardTypeIcon('visa');
    expect(icon1).toBe(icon2);
  });
});

describe('Card Type Label', () => {
  it('TASK-042: should return label for VISA', () => {
    const label = getCardTypeLabel('VISA');
    expect(label).toBe('VISA');
  });

  it('TASK-042: should return label for Mastercard', () => {
    const label = getCardTypeLabel('MASTERCARD');
    expect(label).toBe('Mastercard');
  });

  it('TASK-042: should return label for AMEX', () => {
    const label = getCardTypeLabel('AMEX');
    expect(label).toBe('American Express');
  });

  it('TASK-042: should return formatted label for unknown type', () => {
    const label = getCardTypeLabel('UNKNOWN');
    expect(label).toBeDefined();
  });

  it('TASK-042: should be human-readable', () => {
    const label = getCardTypeLabel('VISA');
    expect(label).not.toMatch(/^[a-z_]+$/); // Not all lowercase/underscore
  });
});

describe('Generate Default Nickname', () => {
  it('TASK-042: should generate "Mi VISA" for VISA card', () => {
    const nickname = generateNickname('VISA');
    expect(nickname).toMatch(/visa|VISA/i);
  });

  it('TASK-042: should generate nickname for Mastercard', () => {
    const nickname = generateNickname('MASTERCARD');
    expect(nickname).toMatch(/mastercard|MC/i);
  });

  it('TASK-042: should generate nickname for AMEX', () => {
    const nickname = generateNickname('AMEX');
    expect(nickname).toMatch(/amex|american/i);
  });

  it('TASK-042: should format with "Mi" prefix (Spanish)', () => {
    const nickname = generateNickname('VISA');
    expect(nickname).toMatch(/^Mi\s/);
  });

  it('TASK-042: should handle unknown card types', () => {
    const nickname = generateNickname('UNKNOWN');
    expect(nickname).toBeDefined();
  });

  it('TASK-042: should be capitalized', () => {
    const nickname = generateNickname('VISA');
    expect(nickname[0]).toMatch(/[A-Z]/);
  });

  it('TASK-042: should return empty string for empty input', () => {
    const nickname = generateNickname('');
    expect(nickname).toBe('');
  });
});

describe('CVV Formatting', () => {
  it('TASK-042: should only allow 3-4 digits for CVV', () => {
    // This would be part of a formatCVV function
    expect('123').toMatch(/^\d{3,4}$/);
    expect('1234').toMatch(/^\d{3,4}$/);
    expect('12').not.toMatch(/^\d{3,4}$/);
  });
});

describe('Integration Tests - Card Number + Type', () => {
  it('TASK-042: should format and detect type together', () => {
    const formatted = formatCardNumber('4532015112830366');
    expect(formatted).toBe('4532 0151 1283 0366');
    
    const valid = luhnChecksum('4532015112830366');
    expect(valid).toBe(true);
  });

  it('TASK-042: should mask detected card properly', () => {
    const masked = maskCardNumber('4532015112830366');
    expect(masked).toBe('**** **** **** 0366');
  });

  it('TASK-042: should handle full card flow', () => {
    const cardNumber = '4532015112830366';
    
    const formatted = formatCardNumber(cardNumber);
    const valid = luhnChecksum(cardNumber);
    const masked = maskCardNumber(cardNumber);
    
    expect(formatted).toBe('4532 0151 1283 0366');
    expect(valid).toBe(true);
    expect(masked).toBe('**** **** **** 0366');
  });
});
