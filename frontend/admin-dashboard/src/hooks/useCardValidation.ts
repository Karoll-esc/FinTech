/**
 * useCardValidation Hook
 * HU-016: Add Card - Phase 4 Frontend
 * 
 * Custom React hook for card field validation
 * Provides real-time validation for all card fields with error messages
 */

import { useState, useCallback } from 'react';
import {
  luhnChecksum,
  detectCardType,
  isCardExpired,
  CardType,
} from '../utils/cardUtils';

export interface ValidationResult {
  isValid: boolean;
  error?: string;
  cardType?: CardType;
}

export interface FormValidationResult {
  cardNumber: ValidationResult;
  expiry: ValidationResult;
  cvv: ValidationResult;
  holderName: ValidationResult;
  documentId: ValidationResult;
  nickname: ValidationResult;
  isFormValid: boolean;
}

export interface CardValidationState {
  cardNumber: ValidationResult;
  expiry: ValidationResult;
  cvv: ValidationResult;
  holderName: ValidationResult;
  documentId: ValidationResult;
  nickname: ValidationResult;
  isFormValid: boolean;
}

interface CardFormData {
  cardNumber: string;
  month: number;
  year: number;
  cvv: string;
  holderName: string;
  documentId: string;
  nickname?: string;
  cardType?: CardType;
}

const useCardValidation = () => {
  const [validationState, setValidationState] = useState<CardValidationState>({
    cardNumber: { isValid: false },
    expiry: { isValid: false },
    cvv: { isValid: false },
    holderName: { isValid: false },
    documentId: { isValid: false },
    nickname: { isValid: true }, // Optional field
    isFormValid: false,
  });

  /**
   * Validates card number using Luhn algorithm
   */
  const validateCardNumber = useCallback((cardNumber: string): ValidationResult => {
    if (!cardNumber || cardNumber.trim().length === 0) {
      return { isValid: false, error: 'Card number is required' };
    }

    const digitsOnly = cardNumber.replace(/\D/g, '');

    // Check length: 13-19 digits
    if (digitsOnly.length < 13 || digitsOnly.length > 19) {
      return { isValid: false, error: 'Card number must be 13-19 digits' };
    }

    // Validate Luhn
    if (!luhnChecksum(digitsOnly)) {
      return { isValid: false, error: 'Card number is invalid' };
    }

    const cardType = detectCardType(digitsOnly);

    return { isValid: true, cardType };
  }, []);

  /**
   * Validates expiry date
   */
  const validateExpiry = useCallback((month: number, year: number): ValidationResult => {
    // Month validation
    if (!month || month < 1 || month > 12) {
      return { isValid: false, error: 'Invalid month (1-12)' };
    }

    // Year validation
    if (!year) {
      return { isValid: false, error: 'Year is required' };
    }

    // Convert 2-digit year to 4-digit if needed
    let fullYear = year;
    if (year < 100) {
      fullYear = year < 30 ? 2000 + year : 1900 + year;
    }

    // Check if expired
    if (isCardExpired(month, fullYear)) {
      return { isValid: false, error: 'Card has expired' };
    }

    return { isValid: true };
  }, []);

  /**
   * Validates CVV
   */
  const validateCVV = useCallback((cvv: string, cardType: CardType = 'UNKNOWN'): ValidationResult => {
    if (!cvv || cvv.trim().length === 0) {
      return { isValid: false, error: 'CVV is required' };
    }

    const digitsOnly = cvv.replace(/\D/g, '');

    // AMEX requires 4 digits, others require 3
    const requiredLength = cardType === 'AMEX' ? 4 : 3;
    const minLength = 3;
    const maxLength = 4;

    if (digitsOnly.length < minLength || digitsOnly.length > maxLength) {
      return { isValid: false, error: `CVV must be ${minLength}-${maxLength} digits` };
    }

    // For specific card types, enforce exact length
    if (cardType !== 'UNKNOWN' && digitsOnly.length !== requiredLength) {
      return { isValid: false, error: `${cardType} requires ${requiredLength}-digit CVV` };
    }

    return { isValid: true };
  }, []);

  /**
   * Validates holder name
   */
  const validateHolderName = useCallback((holderName: string): ValidationResult => {
    if (!holderName || holderName.trim().length === 0) {
      return { isValid: false, error: 'Holder name is required' };
    }

    const trimmed = holderName.trim();

    if (trimmed.length < 2) {
      return { isValid: false, error: 'Holder name must be at least 2 characters' };
    }

    if (trimmed.length > 50) {
      return { isValid: false, error: 'Holder name must not exceed 50 characters' };
    }

    // Allow letters, spaces, and hyphens/apostrophes
    if (!/^[a-zA-Z\s\-']+$/.test(trimmed)) {
      return { isValid: false, error: 'Holder name can only contain letters and spaces' };
    }

    return { isValid: true };
  }, []);

  /**
   * Validates document ID
   */
  const validateDocumentId = useCallback((documentId: string): ValidationResult => {
    if (!documentId || documentId.trim().length === 0) {
      return { isValid: false, error: 'Document ID is required' };
    }

    const trimmed = documentId.trim();

    if (trimmed.length < 5) {
      return { isValid: false, error: 'Document ID must be at least 5 characters' };
    }

    if (trimmed.length > 20) {
      return { isValid: false, error: 'Document ID must not exceed 20 characters' };
    }

    return { isValid: true };
  }, []);

  /**
   * Validates nickname (optional field)
   */
  const validateNickname = useCallback((nickname: string): ValidationResult => {
    // Optional field - always valid if empty
    if (!nickname || nickname.trim().length === 0) {
      return { isValid: true };
    }

    const trimmed = nickname.trim();

    if (trimmed.length > 30) {
      return { isValid: false, error: 'Nickname must not exceed 30 characters' };
    }

    return { isValid: true };
  }, []);

  /**
   * Validates entire form
   */
  const validateForm = useCallback((formData: CardFormData): FormValidationResult => {
    const cardNumberValidation = validateCardNumber(formData.cardNumber);
    const expiryValidation = validateExpiry(formData.month, formData.year);
    const cvvValidation = validateCVV(formData.cvv, cardNumberValidation.cardType);
    const holderNameValidation = validateHolderName(formData.holderName);
    const documentIdValidation = validateDocumentId(formData.documentId);
    const nicknameValidation = validateNickname(formData.nickname || '');

    const isFormValid =
      cardNumberValidation.isValid &&
      expiryValidation.isValid &&
      cvvValidation.isValid &&
      holderNameValidation.isValid &&
      documentIdValidation.isValid &&
      nicknameValidation.isValid;

    return {
      cardNumber: cardNumberValidation,
      expiry: expiryValidation,
      cvv: cvvValidation,
      holderName: holderNameValidation,
      documentId: documentIdValidation,
      nickname: nicknameValidation,
      isFormValid,
    };
  }, [validateCardNumber, validateExpiry, validateCVV, validateHolderName, validateDocumentId, validateNickname]);

  /**
   * Detects card type from card number
   */
  const detectCard = useCallback((cardNumber: string): CardType => {
    const digitsOnly = cardNumber.replace(/\D/g, '');
    return detectCardType(digitsOnly);
  }, []);

  return {
    validationState,
    setValidationState,
    validateCardNumber,
    validateExpiry,
    validateCVV,
    validateHolderName,
    validateDocumentId,
    validateNickname,
    validateForm,
    detectCard,
  };
};

export default useCardValidation;
