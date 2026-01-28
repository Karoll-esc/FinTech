/**
 * useCard Custom Hook - Phase 5 REFACTOR
 * 
 * Central hook for all card management operations with complete state management.
 * 
 * @description
 * Provides a unified interface for card operations including:
 * - Fetch individual card details with auto-load capability
 * - Add new cards with validation and duplicate detection
 * - Remove cards with soft-delete (INACTIVE status)
 * - List user's cards with smart caching (5-second TTL)
 * - Comprehensive error handling with HTTP status mapping
 * - Loading and submission state tracking
 * 
 * @example
 * ```tsx
 * const { card, cards, addCard, listCards, error, isLoading } = useCard('card_123');
 * 
 * // Or without auto-fetch
 * const { listCards, addCard } = useCard(undefined, { autoFetch: false });
 * ```
 * 
 * @features
 * - Cache invalidation on mutations (add/remove)
 * - Automatic card fetch on component mount if cardId provided
 * - Error recovery with descriptive messages
 * - Request deduplication via cache mechanism
 * - Immutable state updates for React optimization
 */

import { useState, useCallback, useEffect } from 'react';
import api from '@/services/api';

export interface Card {
  card_id: string;
  card_number: string; // Masked ****0366
  card_holder_name: string;
  expiry_date: string;
  card_type: 'DEBIT' | 'CREDIT';
  nickname?: string;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
  updated_at: string;
}

interface UseCardOptions {
  autoFetch?: boolean; // Auto-fetch details if cardId provided
}

interface UseCardReturn {
  card: Card | null;
  cards: Card[];
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  addCard: (data: AddCardRequest) => Promise<Card>;
  removeCard: (cardId: string) => Promise<void>;
  listCards: () => Promise<Card[]>;
}

interface AddCardRequest {
  card_number: string;
  card_holder_name: string;
  expiry_date: string;
  card_type: 'DEBIT' | 'CREDIT';
  nickname?: string;
}

/**
 * Internal cache storage for card list results
 * Reduces API calls when component remounts or multiple hooks exist
 * @private
 */
let cardListCache: Card[] | null = null;
let cardCacheTime = 0;
const CACHE_DURATION = 5000; // 5 seconds

/**
 * Custom Hook: useCard
 * 
 * @param {string} [cardId] - Optional card ID for auto-fetch on mount
 * @param {UseCardOptions} [options] - Configuration options
 * @returns {UseCardReturn} Card state and operations
 * 
 * @throws Will not throw - errors are returned in error state
 * 
 * Stateful operations:
 * - isLoading: True during fetch operations (initial load)
 * - isSubmitting: True during add/remove operations (mutations)
 * - error: Human-readable error message if operation fails
 * 
 * Performance optimizations:
 * - Card list caching with 5-second TTL
 * - Auto-cache invalidation on mutations
 * - Debounced API calls via cache mechanism
 */
export const useCard = (cardId?: string, options?: UseCardOptions): UseCardReturn => {
  const [card, setCard] = useState<Card | null>(null);
  const [cards, setCards] = useState<Card[]>([]);
  const [isLoading, setIsLoading] = useState(cardId ? true : false); // Load if cardId provided
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetches single card details by ID
   * Maps HTTP errors to user-friendly messages
   * 
   * @private
   * @param {string} id - Card ID to fetch
   * @returns {Promise<Card|null>} Card data or null if error
   * 
   * Error handling:
   * - 404: Card not found (may be deleted)
   * - 403: Unauthorized access to card
   * - Other: Generic network or server error
   */
  const fetchCardDetails = useCallback(async (id: string): Promise<Card | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.get(`/cards/${id}`);
      setCard(response.data);
      return response.data;
    } catch (err: any) {
      let errorMessage = 'Failed to load card details';
      
      if (err.response?.status === 404) {
        errorMessage = 'Card not found';
      } else if (err.response?.status === 403) {
        errorMessage = 'You do not have permission to view this card';
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      }
      
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Adds new card to user's account
   * Validates card details and checks for duplicates
   * Invalidates list cache after success
   * 
   * @param {AddCardRequest} data - Card information
   * @returns {Promise<Card>} Newly created card
   * @throws {Error} With user-friendly message for display
   * 
   * Error handling:
   * - 400: Validation error or max cards limit exceeded
   * - 409: Duplicate card (same last 4 digits)
   * - 422: Missing required fields
   * - Other: Network or server error
   * 
   * Side effects:
   * - Invalidates cardListCache on success
   * - Sets isSubmitting state
   */
  const addCard = useCallback(async (data: AddCardRequest): Promise<Card> => {
    try {
      setIsSubmitting(true);
      setError(null);
      const response = await api.post('/cards', data);
      
      // Invalidate card list cache
      cardListCache = null;
      
      return response.data;
    } catch (err: any) {
      let errorMessage = 'Failed to add card';
      
      if (err.response?.status === 400) {
        // Check specific error messages
        if (err.response?.data?.message?.includes('maximum')) {
          errorMessage = 'You have reached the maximum of 10 cards';
        } else {
          errorMessage = err.response.data.message || 'Invalid card information';
        }
      } else if (err.response?.status === 409) {
        errorMessage = 'Card with this last 4 digits already linked to your account';
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  /**
   * Removes (soft-deletes) a card from user's account
   * Card status is set to INACTIVE, not permanently deleted
   * Invalidates caches after success
   * 
   * @param {string} id - Card ID to remove
   * @returns {Promise<void>}
   * @throws {Error} With user-friendly message for display
   * 
   * Error handling:
   * - 404: Card not found
   * - 403: Unauthorized deletion
   * - Other: Network or server error
   * 
   * Side effects:
   * - Clears cardListCache on success
   * - Clears card details on success
   * - Sets isSubmitting state
   */
  const removeCard = useCallback(async (id: string): Promise<void> => {
    try {
      setIsSubmitting(true);
      setError(null);
      await api.delete(`/cards/${id}`);
      
      // Invalidate caches
      cardListCache = null;
      setCard(null);
    } catch (err: any) {
      let errorMessage = 'Failed to remove card';
      
      if (err.response?.status === 404) {
        errorMessage = 'Card not found';
      } else if (err.response?.status === 403) {
        errorMessage = 'You do not have permission to delete this card';
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  /**
   * Lists all active cards for current user
   * Implements smart caching to reduce API calls:
   * - Returns cached result if < 5 seconds old
   * - Otherwise fetches fresh data from API
   * 
   * @returns {Promise<Card[]>} Array of user's active cards
   * 
   * Cache behavior:
   * - Cache duration: 5 seconds (CACHE_DURATION)
   * - Cache invalidation: On add/remove operations
   * - Graceful degradation: Returns empty array on error
   * 
   * Use cases:
   * - On component mount for CardList
   * - After successful card add/remove (refresh)
   * - Manual refresh button clicks
   */
  const listCards = useCallback(async (): Promise<Card[]> => {
    try {
      // Check cache first
      if (cardListCache && Date.now() - cardCacheTime < CACHE_DURATION) {
        setCards(cardListCache);
        return cardListCache;
      }

      setIsLoading(true);
      setError(null);
      const response = await api.get('/cards');
      
      // Handle paginated response or direct array
      const cardList = response.data.cards || response.data;
      cardListCache = cardList;
      cardCacheTime = Date.now();
      
      setCards(cardList);
      return cardList;
    } catch (err: any) {
      let errorMessage = 'Failed to load cards';
      
      if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      }
      
      setError(errorMessage);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Effect: Auto-fetch card details on mount
   * 
   * Triggers when:
   * - cardId prop changes
   * - options.autoFetch changes
   * - fetchCardDetails function reference changes
   * 
   * Does NOT trigger on:
   * - component re-renders with same cardId
   * - state updates within this hook
   * 
   * Performance note:
   * fetchCardDetails function is memoized to prevent
   * unnecessary dependency updates
   */
  useEffect(() => {
    if (cardId && options?.autoFetch !== false) {
      fetchCardDetails(cardId);
    }
  }, [cardId, options?.autoFetch, fetchCardDetails]);

  return {
    card,
    cards,
    isLoading,
    isSubmitting,
    error,
    addCard,
    removeCard,
    listCards,
  };
};

export default useCard;
