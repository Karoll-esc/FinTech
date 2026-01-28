/**
 * TransferForm Component - Phase 6 (TASK-051-060)
 * 
 * Form for initiating money transfers with:
 * - React Hook Form validation
 * - Real-time error feedback
 * - Balance checking
 * - Blocked card detection
 * - Submit handling with fraud evaluation
 */

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';

interface TransferFormData {
  source_card_id: string;
  amount: string;
  id_user: string;
  location: string;
  device_id: string;
  transaction_id: string;
  description?: string;
}

interface TransferFormProps {
  cardId: string;
  cardBalance: number;
  isBlocked: boolean;
  onSubmit: (data: TransferFormData) => Promise<void>;
  onCancel: () => void;
}

const TransferForm: React.FC<TransferFormProps> = ({
  cardId,
  cardBalance,
  isBlocked,
  onSubmit,
  onCancel,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    reset,
  } = useForm<TransferFormData>({
    mode: 'onChange',
    defaultValues: {
      source_card_id: cardId,
      amount: '',
      id_user: '',
      location: '',
      device_id: '',
      transaction_id: '',
      description: '',
    },
  });

  const amount = watch('amount');
  const transferAmount = parseFloat(amount) || 0;
  const hasInsufficientBalance = transferAmount > cardBalance;

  const onFormSubmit = async (data: TransferFormData) => {
    try {
      setSubmitting(true);
      setSubmitError(null);

      // Check for blocked card
      if (isBlocked) {
        setSubmitError('Cannot transfer from blocked card');
        setSubmitting(false);
        return;
      }

      // Check for insufficient balance
      if (hasInsufficientBalance) {
        setSubmitError(
          `Insufficient balance. Available: $${cardBalance.toFixed(2)}, Required: $${transferAmount.toFixed(2)}`
        );
        setSubmitting(false);
        return;
      }

      await onSubmit(data);
      setSubmitSuccess('Transfer initiated successfully! Processing...');
      reset();

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSubmitSuccess(null);
      }, 3000);
    } catch (error) {
      setSubmitError(
        error instanceof Error ? error.message : 'Transfer failed. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-slate-800 rounded-lg border border-slate-700">
      <h2 className="text-2xl font-bold text-white mb-6">💸 Transfer Money</h2>

      {/* Alert Messages */}
      {submitError && (
        <div className="mb-4 p-4 bg-red-900 bg-opacity-30 border border-red-700 rounded-lg">
          <p className="text-red-300 text-sm">❌ {submitError}</p>
        </div>
      )}

      {submitSuccess && (
        <div className="mb-4 p-4 bg-green-900 bg-opacity-30 border border-green-700 rounded-lg">
          <p className="text-green-300 text-sm">✅ {submitSuccess}</p>
        </div>
      )}

      {isBlocked && (
        <div className="mb-4 p-4 bg-yellow-900 bg-opacity-30 border border-yellow-700 rounded-lg">
          <p className="text-yellow-300 text-sm">
            ⚠️ This card is blocked. You cannot transfer funds.
          </p>
        </div>
      )}

      {/* Balance Display */}
      <div className="mb-6 p-4 bg-slate-700 rounded-lg">
        <p className="text-slate-400 text-sm">Available Balance</p>
        <p className="text-white text-2xl font-bold mt-1">
          ${cardBalance.toFixed(2)}
        </p>
      </div>

      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
        {/* Amount */}
        <div>
          <label className="block text-white font-semibold mb-2">
            Amount (Required) *
          </label>
          <div className="relative">
            <span className="absolute left-3 top-3 text-slate-400">$</span>
            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              {...register('amount', {
                required: 'Amount is required',
                validate: {
                  positive: (value: string) =>
                    parseFloat(value) > 0 || 'Amount must be greater than 0',
                  sufficient: (value: string) =>
                    parseFloat(value) <= cardBalance ||
                    `Insufficient balance. Available: $${cardBalance.toFixed(2)}`,
                },
              })}
              className={`w-full pl-8 pr-4 py-2 bg-slate-700 text-white rounded border transition ${
                errors.amount
                  ? 'border-red-500 focus:border-red-600'
                  : 'border-slate-600 focus:border-blue-500'
              } focus:outline-none`}
            />
          </div>
          {errors.amount && (
            <p className="text-red-400 text-sm mt-1">⚠️ {errors.amount.message}</p>
          )}
        </div>

        {/* User ID */}
        <div>
          <label className="block text-white font-semibold mb-2">
            User ID (Required) *
          </label>
          <input
            type="text"
            {...register('id_user', {
              required: 'User ID is required',
            })}
            className={`w-full px-4 py-2 bg-slate-700 text-white rounded border transition ${
              errors.id_user
                ? 'border-red-500 focus:border-red-600'
                : 'border-slate-600 focus:border-blue-500'
            } focus:outline-none`}
            placeholder="e.g., user_001"
          />
          {errors.id_user && (
            <p className="text-red-400 text-sm mt-1">⚠️ {errors.id_user.message}</p>
          )}
        </div>

        {/* Location */}
        <div>
          <label className="block text-white font-semibold mb-2">
            Location (Required) *
          </label>
          <input
            type="text"
            {...register('location', {
              required: 'Location is required',
            })}
            className={`w-full px-4 py-2 bg-slate-700 text-white rounded border transition ${
              errors.location
                ? 'border-red-500 focus:border-red-600'
                : 'border-slate-600 focus:border-blue-500'
            } focus:outline-none`}
            placeholder="e.g., Bogotá, Colombia"
          />
          {errors.location && (
            <p className="text-red-400 text-sm mt-1">⚠️ {errors.location.message}</p>
          )}
        </div>

        {/* Device ID */}
        <div>
          <label className="block text-white font-semibold mb-2">
            Device ID (Required) *
          </label>
          <input
            type="text"
            {...register('device_id', {
              required: 'Device ID is required',
            })}
            className={`w-full px-4 py-2 bg-slate-700 text-white rounded border transition ${
              errors.device_id
                ? 'border-red-500 focus:border-red-600'
                : 'border-slate-600 focus:border-blue-500'
            } focus:outline-none`}
            placeholder="e.g., device_abc123"
          />
          {errors.device_id && (
            <p className="text-red-400 text-sm mt-1">⚠️ {errors.device_id.message}</p>
          )}
        </div>

        {/* Transaction ID */}
        <div>
          <label className="block text-white font-semibold mb-2">
            Transaction ID (Required) *
          </label>
          <input
            type="text"
            {...register('transaction_id', {
              required: 'Transaction ID is required',
            })}
            className={`w-full px-4 py-2 bg-slate-700 text-white rounded border transition ${
              errors.transaction_id
                ? 'border-red-500 focus:border-red-600'
                : 'border-slate-600 focus:border-blue-500'
            } focus:outline-none`}
            placeholder="e.g., txn_20260128_001"
          />
          {errors.transaction_id && (
            <p className="text-red-400 text-sm mt-1">
              ⚠️ {errors.transaction_id.message}
            </p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-white font-semibold mb-2">
            Description (Optional)
          </label>
          <textarea
            {...register('description')}
            className="w-full px-4 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-blue-500 focus:outline-none resize-none"
            rows={3}
            placeholder="e.g., Savings transfer"
          />
        </div>

        {/* Form Actions */}
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={submitting || !isValid || isBlocked || hasInsufficientBalance}
            className={`flex-1 py-2 font-semibold rounded transition ${
              submitting || !isValid || isBlocked || hasInsufficientBalance
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {submitting ? '⏳ Processing...' : '✓ Confirm Transfer'}
          </button>

          <button
            type="button"
            onClick={onCancel}
            disabled={submitting}
            className="flex-1 py-2 font-semibold text-white bg-slate-700 hover:bg-slate-600 rounded transition disabled:bg-gray-600"
          >
            ✕ Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default TransferForm;
