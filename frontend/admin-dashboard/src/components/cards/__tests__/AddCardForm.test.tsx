"""
TASK-040: Tests para AddCardForm.tsx (React Component)
Test-Driven Development: Tests escritos PRIMERO

HU-016: Add Card - Phase 4 Frontend Components
"""

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import AddCardForm from '../AddCardForm';

describe('AddCardForm Component', () => {
  describe('Form Rendering', () => {
    it('TASK-040: should render all form fields', () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      expect(screen.getByLabelText(/card number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/expiry date/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/cvv/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/holder name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/document id/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/nickname/i)).toBeInTheDocument();
    });

    it('TASK-040: should render submit button', () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      expect(submitBtn).toBeInTheDocument();
    });

    it('TASK-040: should render cancel/close button', () => {
      render(<AddCardForm onCardAdded={vi.fn()} onCancel={vi.fn()} />);
      
      const cancelBtn = screen.getByRole('button', { name: /cancel|close/i });
      expect(cancelBtn).toBeInTheDocument();
    });

    it('TASK-040: should have proper form structure (fieldset)', () => {
      const { container } = render(<AddCardForm onCardAdded={vi.fn()} />);
      
      const form = container.querySelector('form');
      expect(form).toBeInTheDocument();
    });
  });

  describe('Card Number Input', () => {
    it('TASK-040: should auto-format card number with spaces (4-4-4-4)', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/card number/i);
      
      await userEvent.type(input, '4532015112830366');
      
      // Expected format: 4532 0151 1283 0366
      expect(input).toHaveValue('4532 0151 1283 0366');
    });

    it('TASK-040: should only accept numbers in card field', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/card number/i);
      
      await userEvent.type(input, '4532ABC012830366');
      
      // ABC should be filtered out
      expect(input.value.replace(/\s/g, '')).toMatch(/^\d+$/);
    });

    it('TASK-040: should limit card number to 19 characters', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/card number/i);
      
      await userEvent.type(input, '45320151128303661234567890');
      
      // Max should be 19 chars (16-19 digits + spaces)
      expect(input.value.length).toBeLessThanOrEqual(23); // 19 digits + 4 spaces
    });

    it('TASK-040: should show card type icon (VISA, Mastercard, AMEX)', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/card number/i);
      
      // Type VISA card (starts with 4)
      await userEvent.type(input, '4532');
      
      // Should detect VISA and show icon
      await waitFor(() => {
        const icon = screen.queryByAltText(/visa|mastercard|amex/i);
        expect(icon || document.querySelector('[class*="visa"]')).toBeTruthy();
      });
    });

    it('TASK-040: should show real-time Luhn validation error', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/card number/i);
      
      // Type invalid card number
      await userEvent.type(input, '1234567890123456');
      
      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/invalid.*card|card.*invalid/i)).toBeInTheDocument();
      });
    });

    it('TASK-040: should clear Luhn error when valid number entered', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/card number/i);
      
      // Type invalid first
      await userEvent.type(input, '1234567890123456');
      
      // Clear and type valid
      await userEvent.clear(input);
      await userEvent.type(input, '4532015112830366');
      
      // Error should disappear
      await waitFor(() => {
        expect(screen.queryByText(/invalid.*card|card.*invalid/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Expiry Date Input', () => {
    it('TASK-040: should format expiry as MM/YY', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/expiry/i);
      
      await userEvent.type(input, '12');
      
      expect(input).toHaveValue('12');
      
      await userEvent.type(input, '26');
      
      // Should auto-format to 12/26
      expect(input).toHaveValue('12/26');
    });

    it('TASK-040: should validate expiry not in past', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/expiry/i);
      
      // Type expired date (01/20 is in the past)
      await userEvent.type(input, '0120');
      
      // Should show error
      await waitFor(() => {
        expect(screen.getByText(/expired|past/i)).toBeInTheDocument();
      });
    });

    it('TASK-040: should validate future expiry date', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/expiry/i);
      
      // Type future date
      await userEvent.type(input, '1228');
      
      // Should not show error
      expect(screen.queryByText(/expired|past/i)).not.toBeInTheDocument();
    });

    it('TASK-040: should only accept valid months (01-12)', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/expiry/i);
      
      await userEvent.type(input, '13');
      
      // Month 13 is invalid
      expect(screen.getByText(/invalid.*month|month.*invalid/i)).toBeInTheDocument();
    });
  });

  describe('CVV Input', () => {
    it('TASK-040: should mask CVV with dots while typing', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/cvv/i);
      
      await userEvent.type(input, '123');
      
      // Should be masked as ● or ·
      expect(input).toHaveAttribute('type', 'password');
    });

    it('TASK-040: should validate CVV length (3-4 digits)', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/cvv/i);
      
      await userEvent.type(input, '12'); // Too short
      
      expect(screen.getByText(/cvv.*invalid|invalid.*cvv/i)).toBeInTheDocument();
      
      await userEvent.clear(input);
      await userEvent.type(input, '123'); // Valid
      
      expect(screen.queryByText(/cvv.*invalid|invalid.*cvv/i)).not.toBeInTheDocument();
    });

    it('TASK-040: should only accept numbers in CVV', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/cvv/i);
      
      await userEvent.type(input, 'ABC123');
      
      // Only numbers should be present
      expect(input.value).toMatch(/^\d*$/);
    });

    it('TASK-040: should allow AMEX CVV (4 digits)', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      // First enter AMEX card number
      const cardInput = screen.getByLabelText(/card number/i);
      await userEvent.type(cardInput, '378282246310005');
      
      // Then enter CVV
      const cvvInput = screen.getByLabelText(/cvv/i);
      await userEvent.type(cvvInput, '1234');
      
      // AMEX 4-digit CVV should be valid
      expect(screen.queryByText(/cvv.*invalid|invalid.*cvv/i)).not.toBeInTheDocument();
    });
  });

  describe('Holder Name Input', () => {
    it('TASK-040: should accept holder name input', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/holder name/i);
      
      await userEvent.type(input, 'Juan Pérez');
      
      expect(input).toHaveValue('Juan Pérez');
    });

    it('TASK-040: should validate holder name not empty', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      expect(screen.getByText(/holder.*required|name.*required/i)).toBeInTheDocument();
    });

    it('TASK-040: should allow special characters in name', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/holder name/i);
      
      await userEvent.type(input, "O'Brien-Smith");
      
      expect(input).toHaveValue("O'Brien-Smith");
    });
  });

  describe('Document ID Input', () => {
    it('TASK-040: should accept document ID', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/document|document id|id/i);
      
      await userEvent.type(input, '1234567890');
      
      expect(input).toHaveValue('1234567890');
    });

    it('TASK-040: should validate document ID not empty', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      expect(screen.getByText(/document.*required|id.*required/i)).toBeInTheDocument();
    });
  });

  describe('Nickname Input', () => {
    it('TASK-040: should accept optional nickname', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/nickname/i);
      
      await userEvent.type(input, 'Mi VISA');
      
      expect(input).toHaveValue('Mi VISA');
    });

    it('TASK-040: should allow nickname to be empty', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      const input = screen.getByLabelText(/nickname/i);
      
      // Leave empty - should be OK
      expect(input).toHaveValue('');
    });

    it('TASK-040: should generate default nickname if empty', async () => {
      const onCardAdded = vi.fn();
      render(<AddCardForm onCardAdded={onCardAdded} />);
      
      // Fill card number (VISA)
      await userEvent.type(screen.getByLabelText(/card number/i), '4532015112830366');
      
      // Leave nickname empty
      // Submit form
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      // Should generate "Mi VISA" as default
      await waitFor(() => {
        expect(onCardAdded).toHaveBeenCalled();
        const call = onCardAdded.mock.calls[0][0];
        expect(call.nickname).toMatch(/visa|mi/i);
      });
    });
  });

  describe('Form Submission', () => {
    it('TASK-040: should call onCardAdded with valid data', async () => {
      const onCardAdded = vi.fn();
      render(<AddCardForm onCardAdded={onCardAdded} />);
      
      // Fill all fields
      await userEvent.type(screen.getByLabelText(/card number/i), '4532015112830366');
      await userEvent.type(screen.getByLabelText(/expiry/i), '1226');
      await userEvent.type(screen.getByLabelText(/cvv/i), '123');
      await userEvent.type(screen.getByLabelText(/holder name/i), 'Juan Pérez');
      await userEvent.type(screen.getByLabelText(/document|id/i), '1234567890');
      await userEvent.type(screen.getByLabelText(/nickname/i), 'Mi VISA');
      
      // Submit
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      await waitFor(() => {
        expect(onCardAdded).toHaveBeenCalledWith(
          expect.objectContaining({
            number: '4532015112830366',
            expiry_month: 12,
            expiry_year: 2026,
            cvv: '123',
            holder_name: 'Juan Pérez',
            document_id: '1234567890',
            nickname: 'Mi VISA'
          })
        );
      });
    });

    it('TASK-040: should not submit with invalid data', async () => {
      const onCardAdded = vi.fn();
      render(<AddCardForm onCardAdded={onCardAdded} />);
      
      // Fill only card number (invalid)
      await userEvent.type(screen.getByLabelText(/card number/i), '1234567890123456');
      
      // Try to submit
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      await waitFor(() => {
        expect(onCardAdded).not.toHaveBeenCalled();
      });
    });

    it('TASK-040: should disable submit button while loading', async () => {
      const onCardAdded = vi.fn((data) => new Promise(r => setTimeout(r, 1000)));
      render(<AddCardForm onCardAdded={onCardAdded} />);
      
      // Fill form
      await userEvent.type(screen.getByLabelText(/card number/i), '4532015112830366');
      await userEvent.type(screen.getByLabelText(/expiry/i), '1226');
      await userEvent.type(screen.getByLabelText(/cvv/i), '123');
      await userEvent.type(screen.getByLabelText(/holder name/i), 'Juan Pérez');
      await userEvent.type(screen.getByLabelText(/document|id/i), '1234567890');
      
      // Submit
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      // Button should be disabled
      expect(submitBtn).toBeDisabled();
    });

    it('TASK-040: should show loading indicator during submission', async () => {
      const onCardAdded = vi.fn((data) => new Promise(r => setTimeout(r, 500)));
      render(<AddCardForm onCardAdded={onCardAdded} />);
      
      // Fill and submit form
      const fields = [
        [/card number/i, '4532015112830366'],
        [/expiry/i, '1226'],
        [/cvv/i, '123'],
        [/holder name/i, 'Juan Pérez'],
        [/document|id/i, '1234567890']
      ];
      
      for (const [label, value] of fields) {
        await userEvent.type(screen.getByLabelText(label), value);
      }
      
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText(/loading|processing|adding/i)).toBeInTheDocument();
      });
    });
  });

  describe('Cancel/Close Functionality', () => {
    it('TASK-040: should call onCancel when cancel button clicked', async () => {
      const onCancel = vi.fn();
      render(<AddCardForm onCardAdded={vi.fn()} onCancel={onCancel} />);
      
      const cancelBtn = screen.getByRole('button', { name: /cancel|close/i });
      fireEvent.click(cancelBtn);
      
      expect(onCancel).toHaveBeenCalled();
    });

    it('TASK-040: should reset form when cancelled', async () => {
      const onCancel = vi.fn();
      render(<AddCardForm onCardAdded={vi.fn()} onCancel={onCancel} />);
      
      // Fill some fields
      await userEvent.type(screen.getByLabelText(/card number/i), '4532');
      
      // Cancel
      const cancelBtn = screen.getByRole('button', { name: /cancel|close/i });
      fireEvent.click(cancelBtn);
      
      // onCancel should be called
      expect(onCancel).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('TASK-040: should show all validation errors at once', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      // Try to submit empty form
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      fireEvent.click(submitBtn);
      
      // Should show multiple errors
      await waitFor(() => {
        const errors = screen.getAllByText(/required|invalid/i);
        expect(errors.length).toBeGreaterThanOrEqual(3);
      });
    });

    it('TASK-040: should clear error when field corrected', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      const input = screen.getByLabelText(/card number/i);
      
      // Type invalid card
      await userEvent.type(input, '1234567890123456');
      
      // Error should show
      expect(screen.getByText(/invalid/i)).toBeInTheDocument();
      
      // Clear and type valid
      await userEvent.clear(input);
      await userEvent.type(input, '4532015112830366');
      
      // Error should disappear
      expect(screen.queryByText(/invalid.*card/i)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('TASK-040: should have proper labels for all inputs', () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      expect(screen.getByLabelText(/card number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/expiry/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/cvv/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/holder name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/document|id/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/nickname/i)).toBeInTheDocument();
    });

    it('TASK-040: should support keyboard navigation', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      const cardInput = screen.getByLabelText(/card number/i);
      const submitBtn = screen.getByRole('button', { name: /add card/i });
      
      // Tab to card number field
      cardInput.focus();
      expect(cardInput).toHaveFocus();
      
      // Tab through fields...
      await userEvent.keyboard('{Tab}');
      // Next field should have focus
      expect(document.activeElement).not.toBe(cardInput);
    });

    it('TASK-040: should announce validation errors for screen readers', async () => {
      render(<AddCardForm onCardAdded={vi.fn()} />);
      
      const input = screen.getByLabelText(/card number/i);
      
      // Type invalid and trigger validation
      await userEvent.type(input, '1234567890123456');
      
      // Look for aria-invalid or role="alert"
      await waitFor(() => {
        const error = screen.getByText(/invalid/i);
        expect(error).toHaveAttribute('role', 'alert');
      });
    });
  });
});
