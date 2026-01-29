/**
 * CardErrorBoundary Component
 * 
 * Displays user-friendly error messages for card operations.
 * Features:
 * - Error context detection (404, 403, 409, 400, 500, network)
 * - Helpful recovery suggestions
 * - Dismissable alerts
 * - Accessible error messaging
 * - Icon indicators for error types
 */

import React from 'react';

export interface CardErrorProps {
  error: string;
  errorCode?: number;
  onDismiss?: () => void;
  onRetry?: () => void;
  context?: 'form' | 'list' | 'details' | 'delete';
}

/**
 * Maps HTTP error codes to user-friendly messages and suggestions
 */
const getErrorContext = (code?: number, message?: string) => {
  if (!code) {
    return {
      title: 'Error',
      icon: '⚠️',
      suggestion: 'Please try again or contact support.',
    };
  }

  switch (code) {
    case 400:
      if (message?.includes('maximum')) {
        return {
          title: 'Card Limit Reached',
          icon: '📋',
          suggestion: 'You can have a maximum of 10 cards. Delete one to add another.',
        };
      }
      return {
        title: 'Invalid Information',
        icon: '❌',
        suggestion: 'Please check your card details and try again.',
      };
    case 403:
      return {
        title: 'Access Denied',
        icon: '🔒',
        suggestion: 'You do not have permission to perform this action.',
      };
    case 404:
      return {
        title: 'Card Not Found',
        icon: '🔍',
        suggestion: 'The card may have been deleted. Please refresh and try again.',
      };
    case 409:
      return {
        title: 'Card Already Exists',
        icon: '⏸️',
        suggestion: 'A card with this last 4 digits is already linked. Use a different card.',
      };
    case 500:
      return {
        title: 'Server Error',
        icon: '⚙️',
        suggestion: 'Something went wrong on our end. Please try again later.',
      };
    default:
      return {
        title: 'Network Error',
        icon: '🌐',
        suggestion: 'Check your connection and try again.',
      };
  }
};

export const CardErrorBoundary: React.FC<CardErrorProps> = ({
  error,
  errorCode,
  onDismiss,
  onRetry,
  context: _context = 'form',
}) => {
  const errorInfo = getErrorContext(errorCode, error);

  return (
    <div
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      className="bg-red-50 border-l-4 border-red-600 rounded-r-lg p-4 mb-4 shadow-sm"
    >
      <div className="flex gap-4 items-start">
        <span className="text-2xl flex-shrink-0" aria-hidden="true">
          {errorInfo.icon}
        </span>
        <div className="flex-1">
          <h3 className="font-semibold text-red-800 text-lg mb-1">
            {errorInfo.title}
          </h3>
          <p className="text-red-700 text-sm mb-3">{error}</p>
          <p className="text-red-600 text-xs mb-3 italic">
            💡 {errorInfo.suggestion}
          </p>
          <div className="flex gap-2">
            {onRetry && (
              <button
                onClick={onRetry}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded transition-colors"
                aria-label="Retry the previous action"
              >
                Try Again
              </button>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-4 py-2 text-red-700 hover:bg-red-100 text-sm font-medium rounded transition-colors"
                aria-label="Dismiss this error message"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CardErrorBoundary;
