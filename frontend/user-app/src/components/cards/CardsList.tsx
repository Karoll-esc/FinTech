/**
 * CardsList Component - Phase 4 (TASK-032)
 * 
 * Displays up to 3 user cards with:
 * - Loading state (skeleton loaders)
 * - Empty state (no cards)
 * - Error state with retry button
 * - Pagination link if > 3 cards
 */

import React, { useState } from 'react';
import CardCard, { CardData } from './CardCard';

interface CardsListProps {
  cards: CardData[];
  loading: boolean;
  error?: string;
  onViewTransactions: (cardId: string) => void;
  onTransfer: (cardId: string) => void;
  onBlock: (cardId: string) => void;
  onDetails: (cardId: string) => void;
  onRetry: () => void;
  onViewAll?: () => void;
  totalCardsCount?: number;
}

const SkeletonCard: React.FC = () => (
  <div className="w-full max-w-sm p-6 bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl shadow-lg animate-pulse">
    <div className="h-6 bg-slate-600 rounded w-3/4 mb-4"></div>
    <div className="h-8 bg-slate-600 rounded w-full mb-2"></div>
    <div className="h-4 bg-slate-600 rounded w-1/2 mb-6"></div>
    <div className="grid grid-cols-2 gap-4 mb-6">
      <div className="h-4 bg-slate-600 rounded"></div>
      <div className="h-4 bg-slate-600 rounded"></div>
    </div>
    <div className="grid grid-cols-2 gap-2">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-8 bg-slate-600 rounded"></div>
      ))}
    </div>
  </div>
);

const CardsList: React.FC<CardsListProps> = ({
  cards,
  loading,
  error,
  onViewTransactions,
  onTransfer,
  onBlock,
  onDetails,
  onRetry,
  onViewAll,
  totalCardsCount,
}) => {
  const [showAllCards, setShowAllCards] = useState(false);

  // Empty state
  if (!loading && cards.length === 0 && !error) {
    return (
      <div className="w-full p-8 text-center bg-slate-800 rounded-lg border border-slate-700">
        <div className="text-4xl mb-4">💳</div>
        <h3 className="text-xl font-bold text-white mb-2">No Cards Found</h3>
        <p className="text-slate-400 mb-6">
          You don't have any cards yet. Request a card to get started.
        </p>
        <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded transition">
          📝 Request a Card
        </button>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="w-full p-8 bg-red-900 bg-opacity-20 border border-red-700 rounded-lg">
        <h3 className="text-lg font-bold text-red-400 mb-2">⚠️ Error Loading Cards</h3>
        <p className="text-red-300 mb-4">{error}</p>
        <button
          onClick={onRetry}
          className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded transition"
        >
          🔄 Retry
        </button>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
        {[1, 2, 3].map((i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  // Cards grid
  const displayCards = cards.slice(0, 3);
  const hasMoreCards = totalCardsCount ? totalCardsCount > 3 : false;

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {displayCards.map((card) => (
          <CardCard
            key={card.card_id}
            card={card}
            onViewTransactions={onViewTransactions}
            onTransfer={onTransfer}
            onBlock={onBlock}
            onDetails={onDetails}
          />
        ))}
      </div>

      {/* View All Cards Link */}
      {hasMoreCards && (
        <div className="flex justify-center">
          <button
            onClick={() => {
              setShowAllCards(!showAllCards);
              onViewAll?.();
            }}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded transition border border-slate-600"
          >
            {showAllCards ? '▲ Show Less' : '▼ View All Cards'} ({totalCardsCount} total)
          </button>
        </div>
      )}

      {/* Cards Count */}
      <div className="text-center text-slate-400 text-sm mt-4">
        Showing {displayCards.length} of {totalCardsCount || displayCards.length} card(s)
      </div>
    </div>
  );
};

export default CardsList;
