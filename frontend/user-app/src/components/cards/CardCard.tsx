/**
 * Card Component - Phase 4 (TASK-029)
 * 
 * Displays a single card with:
 * - Masked card number
 * - Cardholder name
 * - Balance and expiry
 * - Status badge
 * - Action buttons
 * 
 * Props:
 * - card: Card entity with all details
 * - onViewTransactions: Callback to view transactions
 * - onTransfer: Callback to initiate transfer
 * - onBlock: Callback to block card
 */

import React from 'react';

export interface CardData {
  card_id: string;
  card_number: string;
  cardholder_name: string;
  current_balance: number;
  expiry_month: number;
  expiry_year: number;
  status: 'ACTIVE' | 'BLOCKED' | 'EXPIRED' | 'PENDING';
  card_type: 'DEBIT' | 'CREDIT';
  created_at: string;
  updated_at?: string;
}

interface CardCardProps {
  card: CardData;
  onViewTransactions: (cardId: string) => void;
  onTransfer: (cardId: string) => void;
  onBlock: (cardId: string) => void;
  onDetails: (cardId: string) => void;
}

const CardCard: React.FC<CardCardProps> = ({
  card,
  onViewTransactions,
  onTransfer,
  onBlock,
  onDetails,
}) => {
  // Determine if card is blocked
  const isBlocked = card.status === 'BLOCKED';
  const isExpired = card.status === 'EXPIRED';
  const canTransfer = card.status === 'ACTIVE' && !isExpired;

  // Get status color
  const getStatusColor = () => {
    switch (card.status) {
      case 'ACTIVE':
        return 'bg-green-100 text-green-800';
      case 'BLOCKED':
        return 'bg-red-100 text-red-800';
      case 'EXPIRED':
        return 'bg-yellow-100 text-yellow-800';
      case 'PENDING':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div
      className={`relative w-full max-w-sm p-6 bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl shadow-lg transition-transform hover:scale-105 ${
        isBlocked ? 'opacity-60 grayscale' : ''
      }`}
    >
      {/* Card Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-slate-400 text-xs font-semibold">CARD NUMBER</p>
          <p className="text-white text-lg font-mono tracking-wider mt-1">
            {card.card_number}
          </p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor()}`}>
          {card.status}
        </div>
      </div>

      {/* Card Details */}
      <div className="mb-6">
        <p className="text-slate-400 text-xs font-semibold">CARDHOLDER</p>
        <p className="text-white text-sm font-semibold mt-1">{card.cardholder_name}</p>

        <div className="grid grid-cols-2 gap-4 mt-4">
          <div>
            <p className="text-slate-400 text-xs font-semibold">BALANCE</p>
            <p className="text-white text-lg font-bold mt-1">
              ${card.current_balance.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-slate-400 text-xs font-semibold">EXPIRES</p>
            <p className="text-white text-lg font-bold mt-1">
              {String(card.expiry_month).padStart(2, '0')}/{card.expiry_year}
            </p>
          </div>
        </div>

        <div className="mt-4">
          <p className="text-slate-400 text-xs font-semibold">TYPE</p>
          <p className="text-white text-sm font-semibold mt-1">{card.card_type}</p>
        </div>
      </div>

      {/* Blocked Card Banner */}
      {isBlocked && (
        <div className="mb-4 p-3 bg-red-500 bg-opacity-20 border border-red-500 rounded-lg">
          <p className="text-red-400 text-xs font-semibold">
            ⚠️ This card is blocked. Transfers are disabled.
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => onViewTransactions(card.card_id)}
          className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded transition"
          aria-label="View transactions"
        >
          📊 Transactions
        </button>

        <button
          onClick={() => onTransfer(card.card_id)}
          disabled={!canTransfer}
          className={`px-3 py-2 text-xs font-semibold rounded transition ${
            canTransfer
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-gray-400 text-gray-200 cursor-not-allowed'
          }`}
          title={
            isBlocked ? 'Cannot transfer from blocked card' : 'Transfer money'
          }
          aria-label="Transfer money"
        >
          💸 Transfer
        </button>

        <button
          onClick={() => onBlock(card.card_id)}
          className="px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white text-xs font-semibold rounded transition"
          aria-label="Block card"
        >
          🔒 Block
        </button>

        <button
          onClick={() => onDetails(card.card_id)}
          className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold rounded transition"
          aria-label="View full details"
        >
          ℹ️ Details
        </button>
      </div>
    </div>
  );
};

export default CardCard;
