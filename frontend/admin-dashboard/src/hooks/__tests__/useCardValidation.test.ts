"""
TASK-041: Tests para useCardValidation Hook
Test-Driven Development: Tests escritos PRIMERO

HU-016: Add Card - Phase 4 Frontend Hooks
"""

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useCardValidation from '../hooks/useCardValidation';

describe('useCardValidation Hook', () => {
  describe('Card Number Validation', () => {
    it('TASK-041: should validate card number with Luhn algorithm', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('4532015112830366');
        expect(validation.isValid).toBe(true);
        expect(validation.error).toBeUndefined();
      });
    });

    it('TASK-041: should reject invalid card number (Luhn)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('1234567890123456');
        expect(validation.isValid).toBe(false);
        expect(validation.error).toContain('invalid');
      });
    });

    it('TASK-041: should detect card type (VISA)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('4532015112830366');
        expect(validation.cardType).toBe('VISA');
      });
    });

    it('TASK-041: should detect card type (Mastercard)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('5555555555554444');
        expect(validation.cardType).toBe('MASTERCARD');
      });
    });

    it('TASK-041: should detect card type (AMEX)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('378282246310005');
        expect(validation.cardType).toBe('AMEX');
      });
    });

    it('TASK-041: should require 13-19 digit card number', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const tooShort = result.current.validateCardNumber('453201511');
        expect(tooShort.isValid).toBe(false);
        
        const tooLong = result.current.validateCardNumber('45320151128303661234567890');
        expect(tooLong.isValid).toBe(false);
      });
    });

    it('TASK-041: should strip spaces/formatting when validating', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('4532 0151 1283 0366');
        expect(validation.isValid).toBe(true);
      });
    });
  });

  describe('Expiry Date Validation', () => {
    it('TASK-041: should validate future expiry date', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateExpiry(12, 2026);
        expect(validation.isValid).toBe(true);
        expect(validation.error).toBeUndefined();
      });
    });

    it('TASK-041: should reject expired date', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateExpiry(1, 2020);
        expect(validation.isValid).toBe(false);
        expect(validation.error).toContain('expired');
      });
    });

    it('TASK-041: should reject invalid month (13)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateExpiry(13, 2026);
        expect(validation.isValid).toBe(false);
        expect(validation.error).toContain('month');
      });
    });

    it('TASK-041: should reject invalid month (0)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateExpiry(0, 2026);
        expect(validation.isValid).toBe(false);
      });
    });

    it('TASK-041: should accept current month/year', () => {
      const { result } = renderHook(() => useCardValidation());
      
      const now = new Date();
      const currentMonth = now.getMonth() + 1;
      const currentYear = now.getFullYear();
      
      act(() => {
        const validation = result.current.validateExpiry(currentMonth, currentYear);
        expect(validation.isValid).toBe(true);
      });
    });
  });

  describe('CVV Validation', () => {
    it('TASK-041: should validate 3-digit CVV for VISA', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCVV('123', 'VISA');
        expect(validation.isValid).toBe(true);
      });
    });

    it('TASK-041: should validate 4-digit CVV for AMEX', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCVV('1234', 'AMEX');
        expect(validation.isValid).toBe(true);
      });
    });

    it('TASK-041: should reject 4-digit CVV for VISA', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCVV('1234', 'VISA');
        expect(validation.isValid).toBe(false);
      });
    });

    it('TASK-041: should reject 2-digit CVV', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCVV('12', 'VISA');
        expect(validation.isValid).toBe(false);
      });
    });

    it('TASK-041: should only accept digits in CVV', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCVV('1A3', 'VISA');
        expect(validation.isValid).toBe(false);
      });
    });
  });

  describe('Holder Name Validation', () => {
    it('TASK-041: should accept valid holder name', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateHolderName('Juan Pérez');
        expect(validation.isValid).toBe(true);
      });
    });

    it('TASK-041: should reject empty holder name', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateHolderName('');
        expect(validation.isValid).toBe(false);
      });
    });

    it('TASK-041: should accept special characters (apostrophe, hyphen)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateHolderName("O'Brien-Smith");
        expect(validation.isValid).toBe(true);
      });
    });

    it('TASK-041: should reject names that are too long (>50 chars)', () => {
      const { result } = renderHook(() => useCardValidation());
      
      const longName = 'a'.repeat(51);
      act(() => {
        const validation = result.current.validateHolderName(longName);
        expect(validation.isValid).toBe(false);
      });
    });
  });

  describe('Document ID Validation', () => {
    it('TASK-041: should accept valid document ID', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateDocumentId('1234567890');
        expect(validation.isValid).toBe(true);
      });
    });

    it('TASK-041: should reject empty document ID', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateDocumentId('');
        expect(validation.isValid).toBe(false);
      });
    });

    it('TASK-041: should accept alphanumeric document IDs', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateDocumentId('ABC123XYZ');
        expect(validation.isValid).toBe(true);
      });
    });
  });

  describe('Nickname Validation', () => {
    it('TASK-041: should accept valid nickname', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateNickname('Mi VISA');
        expect(validation.isValid).toBe(true);
      });
    });

    it('TASK-041: should allow empty nickname', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateNickname('');
        expect(validation.isValid).toBe(true);
      });
    });

    it('TASK-041: should validate nickname max length', () => {
      const { result } = renderHook(() => useCardValidation());
      
      const longNickname = 'a'.repeat(51);
      act(() => {
        const validation = result.current.validateNickname(longNickname);
        expect(validation.isValid).toBe(false);
      });
    });
  });

  describe('Full Form Validation', () => {
    it('TASK-041: should validate complete form data', () => {
      const { result } = renderHook(() => useCardValidation());
      
      const formData = {
        cardNumber: '4532015112830366',
        expiryMonth: 12,
        expiryYear: 2026,
        cvv: '123',
        holderName: 'Juan Pérez',
        documentId: '1234567890',
        nickname: 'Mi VISA'
      };
      
      act(() => {
        const validation = result.current.validateForm(formData);
        expect(validation.isValid).toBe(true);
        expect(validation.errors).toEqual({});
      });
    });

    it('TASK-041: should return all field errors', () => {
      const { result } = renderHook(() => useCardValidation());
      
      const invalidFormData = {
        cardNumber: '1234567890123456', // Invalid Luhn
        expiryMonth: 13, // Invalid month
        expiryYear: 2020, // Expired
        cvv: 'ABC', // Not digits
        holderName: '', // Empty
        documentId: '', // Empty
        nickname: ''
      };
      
      act(() => {
        const validation = result.current.validateForm(invalidFormData);
        expect(validation.isValid).toBe(false);
        expect(Object.keys(validation.errors).length).toBeGreaterThan(0);
        expect(validation.errors.cardNumber).toBeDefined();
        expect(validation.errors.expiry).toBeDefined();
        expect(validation.errors.cvv).toBeDefined();
        expect(validation.errors.holderName).toBeDefined();
        expect(validation.errors.documentId).toBeDefined();
      });
    });

    it('TASK-041: should suggest correct CVV length for card type', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const visaValidation = result.current.validateCVV('', 'VISA');
        expect(visaValidation.expectedLength).toBe(3);
        
        const amexValidation = result.current.validateCVV('', 'AMEX');
        expect(amexValidation.expectedLength).toBe(4);
      });
    });
  });

  describe('Real-time Validation', () => {
    it('TASK-041: should provide real-time validation results', () => {
      const { result, rerender } = renderHook(() => useCardValidation());
      
      // Test validation as user types
      act(() => {
        const validation1 = result.current.validateCardNumber('4');
        expect(validation1.isIncomplete).toBe(true);
        
        const validation2 = result.current.validateCardNumber('45320151128303');
        expect(validation2.isIncomplete).toBe(true);
        
        const validation3 = result.current.validateCardNumber('4532015112830366');
        expect(validation3.isValid).toBe(true);
      });
    });

    it('TASK-041: should provide isIncomplete flag', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('453201');
        expect(validation.isIncomplete).toBe(true);
      });
    });

    it('TASK-041: should provide card type suggestion before full number', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('4532');
        expect(validation.cardType).toBe('VISA');
        expect(validation.isIncomplete).toBe(true);
      });
    });
  });

  describe('Error Messages', () => {
    it('TASK-041: should provide user-friendly error messages', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateCardNumber('1234567890123456');
        expect(validation.error).toMatch(/invalid|check|luhn/i);
      });
    });

    it('TASK-041: should provide actionable error messages', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.validateExpiry(1, 2020);
        expect(validation.error).toMatch(/expired|past|renewal|update/i);
      });
    });
  });

  describe('Card Type Detection', () => {
    it('TASK-041: should detect VISA from prefix', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.detectCardType('4532015112830366');
        expect(validation).toBe('VISA');
      });
    });

    it('TASK-041: should detect Mastercard from prefix', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.detectCardType('5555555555554444');
        expect(validation).toBe('MASTERCARD');
      });
    });

    it('TASK-041: should detect AMEX from prefix', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.detectCardType('378282246310005');
        expect(validation).toBe('AMEX');
      });
    });

    it('TASK-041: should return undefined for unknown card type', () => {
      const { result } = renderHook(() => useCardValidation());
      
      act(() => {
        const validation = result.current.detectCardType('6011111111111117');
        expect(['DISCOVER', 'UNKNOWN']).toContain(validation);
      });
    });
  });
});
