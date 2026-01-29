/**
 * AddCardForm Component
 * HU-016: Add Card - Phase 4 Frontend
 * 
 * React component for adding a new card to user's wallet
 * Features: Auto-formatting, real-time validation, CVV masking, card type detection
 */

import React, { useState, useCallback, useEffect } from 'react';
import toast from 'react-hot-toast';
import useCardValidation, { FormValidationResult } from '../../hooks/useCardValidation';
import useCardStore from '../../store/cardStore';
import {
  formatCardNumber,
  formatExpiry,
  maskCardNumber,
  generateNickname,
  getCardTypeIcon,
  getCardTypeLabel,
} from '../../utils/cardUtils';

interface AddCardFormProps {
  onCardAdded: (cardData: CardFormData) => void;
  onCancel?: () => void;
  isLoading?: boolean;
}

export interface CardFormData {
  cardNumber: string;
  month: number;
  year: number;
  cvv: string;
  holderName: string;
  documentId: string;
  nickname: string;
}

interface FormErrors {
  cardNumber?: string;
  expiry?: string;
  cvv?: string;
  holderName?: string;
  documentId?: string;
  nickname?: string;
}

const AddCardForm: React.FC<AddCardFormProps> = ({ onCardAdded, onCancel, isLoading = false }) => {
  // Zustand store
  const { createCard, isCreatingCard, error: storeError, clearError } = useCardStore();

  // Form state
  const [formData, setFormData] = useState<CardFormData>({
    cardNumber: '',
    month: 0,
    year: 0,
    cvv: '',
    holderName: '',
    documentId: '',
    nickname: '',
  });

  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [touchedFields, setTouchedFields] = useState<Set<keyof CardFormData>>(new Set());
  const [localError, setLocalError] = useState<string>('');

  // Combine isLoading props with store loading state
  const isSubmitting = isLoading || isCreatingCard;

  // Validation hook
  const {
    validateCardNumber,
    validateExpiry,
    validateCVV,
    validateHolderName,
    validateDocumentId,
    validateNickname,
    validateForm,
    detectCard,
  } = useCardValidation();

  const [detectedCardType, setDetectedCardType] = useState('UNKNOWN');

  /**
   * Validates a single field and updates error state
   */
  const validateField = useCallback((field: keyof CardFormData) => {
    const errors: FormErrors = { ...formErrors };

    switch (field) {
      case 'cardNumber': {
        const validation = validateCardNumber(formData.cardNumber);
        if (validation.error) {
          errors.cardNumber = validation.error;
          setDetectedCardType('UNKNOWN');
        } else {
          delete errors.cardNumber;
          setDetectedCardType(validation.cardType || 'UNKNOWN');
        }
        break;
      }
      case 'month':
      case 'year': {
        const validation = validateExpiry(formData.month, formData.year);
        if (validation.error) {
          errors.expiry = validation.error;
        } else {
          delete errors.expiry;
        }
        break;
      }
      case 'cvv': {
        const validation = validateCVV(formData.cvv, detectedCardType as any);
        if (validation.error) {
          errors.cvv = validation.error;
        } else {
          delete errors.cvv;
        }
        break;
      }
      case 'holderName': {
        const validation = validateHolderName(formData.holderName);
        if (validation.error) {
          errors.holderName = validation.error;
        } else {
          delete errors.holderName;
        }
        break;
      }
      case 'documentId': {
        const validation = validateDocumentId(formData.documentId);
        if (validation.error) {
          errors.documentId = validation.error;
        } else {
          delete errors.documentId;
        }
        break;
      }
      case 'nickname': {
        const validation = validateNickname(formData.nickname);
        if (validation.error) {
          errors.nickname = validation.error;
        } else {
          delete errors.nickname;
        }
        break;
      }
    }

    setFormErrors(errors);
  }, [formData, formErrors, validateCardNumber, validateExpiry, validateCVV, validateHolderName, validateDocumentId, validateNickname, detectedCardType]);

  /**
   * Handle card number input with auto-formatting
   */
  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    const formatted = formatCardNumber(value);
    setFormData({ ...formData, cardNumber: formatted });
    
    // Mark field as touched
    setTouchedFields(new Set(touchedFields).add('cardNumber'));
  };

  /**
   * Handle card number blur for validation
   */
  const handleCardNumberBlur = () => {
    setTouchedFields(new Set(touchedFields).add('cardNumber'));
    validateField('cardNumber');
  };

  /**
   * Handle expiry month change
   */
  const handleExpiryMonthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 2);
    const month = value ? parseInt(value, 10) : 0;
    setFormData({ ...formData, month });
    
    // Validate if both month and year are set
    if (month && formData.year) {
      setTouchedFields(new Set(touchedFields).add('month').add('year'));
    }
  };

  /**
   * Handle expiry year change
   */
  const handleExpiryYearChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4);
    const year = value ? parseInt(value, 10) : 0;
    setFormData({ ...formData, year });
    
    // Validate if both month and year are set
    if (formData.month && year) {
      setTouchedFields(new Set(touchedFields).add('month').add('year'));
    }
  };

  /**
   * Handle expiry blur for validation
   */
  const handleExpiryBlur = () => {
    setTouchedFields(new Set(touchedFields).add('month').add('year'));
    validateField('month');
  };

  /**
   * Handle CVV input with masking display
   */
  const handleCVVChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    const digitsOnly = value.replace(/\D/g, '').slice(0, 4);
    setFormData({ ...formData, cvv: digitsOnly });
    
    // Mark field as touched
    setTouchedFields(new Set(touchedFields).add('cvv'));
  };

  /**
   * Handle CVV blur for validation
   */
  const handleCVVBlur = () => {
    setTouchedFields(new Set(touchedFields).add('cvv'));
    validateField('cvv');
  };

  /**
   * Handle holder name input
   */
  const handleHolderNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setFormData({ ...formData, holderName: value });
    
    // Mark field as touched
    setTouchedFields(new Set(touchedFields).add('holderName'));
  };

  /**
   * Handle holder name blur for validation
   */
  const handleHolderNameBlur = () => {
    setTouchedFields(new Set(touchedFields).add('holderName'));
    validateField('holderName');
  };

  /**
   * Handle document ID input
   */
  const handleDocumentIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setFormData({ ...formData, documentId: value });
    
    // Mark field as touched
    setTouchedFields(new Set(touchedFields).add('documentId'));
  };

  /**
   * Handle document ID blur for validation
   */
  const handleDocumentIdBlur = () => {
    setTouchedFields(new Set(touchedFields).add('documentId'));
    validateField('documentId');
  };

  /**
   * Handle nickname input
   */
  const handleNicknameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setFormData({ ...formData, nickname: value });
    
    // Mark field as touched
    setTouchedFields(new Set(touchedFields).add('nickname'));
  };

  /**
   * Handle nickname blur for validation
   */
  const handleNicknameBlur = () => {
    setTouchedFields(new Set(touchedFields).add('nickname'));
    validateField('nickname');
  };

  /**
   * Auto-generate nickname when card type is detected
   */
  useEffect(() => {
    if (detectedCardType !== 'UNKNOWN' && !formData.nickname) {
      const last4 = formData.cardNumber.replace(/\D/g, '').slice(-4);
      const autoNickname = generateNickname(detectedCardType as any, last4);
      setFormData(prev => ({ ...prev, nickname: autoNickname }));
    }
  }, [detectedCardType, formData.cardNumber]);

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Clear previous errors
    setLocalError('');
    clearError();

    // Mark all fields as touched
    const allFields: (keyof CardFormData)[] = [
      'cardNumber',
      'month',
      'year',
      'cvv',
      'holderName',
      'documentId',
      'nickname',
    ];
    setTouchedFields(new Set(allFields));

    // Validate entire form
    const validation = validateForm({
      ...formData,
      year: formData.year || new Date().getFullYear(),
    });

    if (validation.isFormValid) {
      // Submit to backend via store
      createCard({
        cardNumber: formData.cardNumber.replace(/\s/g, ''), // Remove spaces
        month: formData.month,
        year: formData.year,
        cvv: formData.cvv,
        holderName: formData.holderName,
        documentId: formData.documentId,
        nickname: formData.nickname,
      })
        .then((newCard) => {
          // Show success toast
          toast.success(`Card added successfully! (${newCard.last4Digits})`);
          
          // Call parent callback
          onCardAdded(formData);
          
          // Reset form
          setFormData({
            cardNumber: '',
            month: 0,
            year: 0,
            cvv: '',
            holderName: '',
            documentId: '',
            nickname: '',
          });
          setFormErrors({});
          setTouchedFields(new Set());
        })
        .catch((error) => {
          // Show error toast
          toast.error(error.message);
          setLocalError(error.message);
        });
    } else {
      // Update form errors from validation
      const newErrors: FormErrors = {};
      if (validation.cardNumber.error) newErrors.cardNumber = validation.cardNumber.error;
      if (validation.expiry.error) newErrors.expiry = validation.expiry.error;
      if (validation.cvv.error) newErrors.cvv = validation.cvv.error;
      if (validation.holderName.error) newErrors.holderName = validation.holderName.error;
      if (validation.documentId.error) newErrors.documentId = validation.documentId.error;
      if (validation.nickname.error) newErrors.nickname = validation.nickname.error;
      setFormErrors(newErrors);
      
      setLocalError('Please fix the errors below and try again.');
    }
  };

  /**
   * Handle cancel button
   */
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="add-card-form" aria-label="Add new card">
      {/* Error Alert */}
      {(localError || storeError) && (
        <div className="error-alert" role="alert" aria-live="polite">
          <span className="error-icon">⚠️</span>
          <div>
            <p className="error-title">Error adding card</p>
            <p className="error-message">{localError || storeError?.message}</p>
          </div>
          <button
            type="button"
            className="error-close"
            onClick={() => {
              setLocalError('');
              clearError();
            }}
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}

      {/* Card Number */}
      <div className="form-group">
        <label htmlFor="cardNumber">Card Number</label>
        <div className="card-input-wrapper">
          <input
            id="cardNumber"
            type="text"
            inputMode="numeric"
            placeholder="0000 0000 0000 0000"
            value={formData.cardNumber}
            onChange={handleCardNumberChange}
            onBlur={handleCardNumberBlur}
            disabled={isSubmitting}
            aria-invalid={!!formErrors.cardNumber}
            aria-describedby={formErrors.cardNumber ? 'cardNumber-error' : undefined}
            maxLength={23}
          />
          {detectedCardType !== 'UNKNOWN' && (
            <div className="card-type-icon" title={getCardTypeLabel(detectedCardType as any)}>
              <span className={`icon icon-${getCardTypeIcon(detectedCardType as any)}`} />
            </div>
          )}
        </div>
        {formErrors.cardNumber && touchedFields.has('cardNumber') && (
          <span id="cardNumber-error" className="error-message" role="alert">
            {formErrors.cardNumber}
          </span>
        )}
      </div>

      {/* Expiry Date */}
      <div className="form-group">
        <label htmlFor="expiryMonth">Expiry Date</label>
        <div className="expiry-inputs">
          <input
            id="expiryMonth"
            type="text"
            inputMode="numeric"
            placeholder="MM"
            value={formData.month ? String(formData.month).padStart(2, '0') : ''}
            onChange={handleExpiryMonthChange}
            onBlur={handleExpiryBlur}
            disabled={isSubmitting}
            maxLength={2}
            aria-invalid={!!formErrors.expiry}
            aria-describedby={formErrors.expiry ? 'expiry-error' : undefined}
          />
          <span className="expiry-separator">/</span>
          <input
            id="expiryYear"
            type="text"
            inputMode="numeric"
            placeholder="YY"
            value={formData.year ? String(formData.year).slice(-2) : ''}
            onChange={handleExpiryYearChange}
            onBlur={handleExpiryBlur}
            disabled={isSubmitting}
            maxLength={2}
            aria-invalid={!!formErrors.expiry}
            aria-describedby={formErrors.expiry ? 'expiry-error' : undefined}
          />
        </div>
        {formErrors.expiry && touchedFields.has('month') && (
          <span id="expiry-error" className="error-message" role="alert">
            {formErrors.expiry}
          </span>
        )}
      </div>

      {/* CVV */}
      <div className="form-group">
        <label htmlFor="cvv">CVV</label>
        <input
          id="cvv"
          type="password"
          inputMode="numeric"
          placeholder="•••"
          value={formData.cvv ? '●'.repeat(formData.cvv.length) : ''}
          onChange={handleCVVChange}
          onBlur={handleCVVBlur}
          disabled={isSubmitting}
          aria-invalid={!!formErrors.cvv}
          aria-describedby={formErrors.cvv ? 'cvv-error' : undefined}
          maxLength={4}
        />
        {formErrors.cvv && touchedFields.has('cvv') && (
          <span id="cvv-error" className="error-message" role="alert">
            {formErrors.cvv}
          </span>
        )}
      </div>

      {/* Holder Name */}
      <div className="form-group">
        <label htmlFor="holderName">Cardholder Name</label>
        <input
          id="holderName"
          type="text"
          placeholder="Full name"
          value={formData.holderName}
          onChange={handleHolderNameChange}
          onBlur={handleHolderNameBlur}
          disabled={isSubmitting}
          aria-invalid={!!formErrors.holderName}
          aria-describedby={formErrors.holderName ? 'holderName-error' : undefined}
          maxLength={50}
        />
        {formErrors.holderName && touchedFields.has('holderName') && (
          <span id="holderName-error" className="error-message" role="alert">
            {formErrors.holderName}
          </span>
        )}
      </div>

      {/* Document ID */}
      <div className="form-group">
        <label htmlFor="documentId">Document ID</label>
        <input
          id="documentId"
          type="text"
          placeholder="DNI/ID number"
          value={formData.documentId}
          onChange={handleDocumentIdChange}
          onBlur={handleDocumentIdBlur}
          disabled={isSubmitting}
          aria-invalid={!!formErrors.documentId}
          aria-describedby={formErrors.documentId ? 'documentId-error' : undefined}
          maxLength={20}
        />
        {formErrors.documentId && touchedFields.has('documentId') && (
          <span id="documentId-error" className="error-message" role="alert">
            {formErrors.documentId}
          </span>
        )}
      </div>

      {/* Nickname */}
      <div className="form-group">
        <label htmlFor="nickname">Card Nickname (Optional)</label>
        <input
          id="nickname"
          type="text"
          placeholder="e.g., My VISA"
          value={formData.nickname}
          onChange={handleNicknameChange}
          onBlur={handleNicknameBlur}
          disabled={isSubmitting}
          aria-invalid={!!formErrors.nickname}
          aria-describedby={formErrors.nickname ? 'nickname-error' : undefined}
          maxLength={30}
        />
        {formErrors.nickname && touchedFields.has('nickname') && (
          <span id="nickname-error" className="error-message" role="alert">
            {formErrors.nickname}
          </span>
        )}
      </div>

      {/* Form Actions */}
      <div className="form-actions">
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn btn-primary"
          aria-label="Add card"
        >
          {isSubmitting ? 'Adding...' : 'Add Card'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="btn btn-secondary"
            aria-label="Cancel"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

export default AddCardForm;
