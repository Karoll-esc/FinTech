/**
 * Card Store (Zustand)
 * HU-016: Add Card - Phase 5 State Management
 * 
 * Global state management for card operations
 * Handles card list, loading state, errors, and form submissions
 */

import { create } from 'zustand';
import { cardService, CardResponse, CardServiceError, CreateCardPayload } from '../services/cardService';

/**
 * Card Store State
 */
export interface CardStoreState {
  // Data
  cards: CardResponse[];
  selectedCard: CardResponse | null;

  // Loading states
  isLoadingCards: boolean;
  isCreatingCard: boolean;
  isUpdatingCard: boolean;
  isDeletingCard: boolean;

  // Error state
  error: {
    code?: string;
    message?: string;
    details?: any;
  } | null;

  // Actions
  fetchCards: () => Promise<void>;
  createCard: (payload: CreateCardPayload) => Promise<CardResponse>;
  selectCard: (card: CardResponse | null) => void;
  updateCardNickname: (cardId: string, nickname: string) => Promise<CardResponse>;
  setDefaultCard: (cardId: string) => Promise<CardResponse>;
  deleteCard: (cardId: string) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

/**
 * Zustand card store
 */
export const useCardStore = create<CardStoreState>((set, get) => ({
  // Initial state
  cards: [],
  selectedCard: null,
  isLoadingCards: false,
  isCreatingCard: false,
  isUpdatingCard: false,
  isDeletingCard: false,
  error: null,

  /**
   * Fetches user's cards from backend
   */
  fetchCards: async () => {
    set({ isLoadingCards: true, error: null });
    try {
      const cards = await cardService.getCards();
      set({ cards, isLoadingCards: false });
    } catch (error) {
      const err = error as CardServiceError;
      set({
        error: {
          code: err.code,
          message: err.message,
          details: err.details,
        },
        isLoadingCards: false,
      });
      throw error;
    }
  },

  /**
   * Creates a new card
   * @param payload Card data
   * @returns Created card
   */
  createCard: async (payload: CreateCardPayload) => {
    set({ isCreatingCard: true, error: null });
    try {
      const newCard = await cardService.createCard(payload);
      
      // Add to local cards list
      set((state) => ({
        cards: [...state.cards, newCard],
        isCreatingCard: false,
      }));

      return newCard;
    } catch (error) {
      const err = error as CardServiceError;
      set({
        error: {
          code: err.code,
          message: err.message,
          details: err.details,
        },
        isCreatingCard: false,
      });
      throw error;
    }
  },

  /**
   * Selects a card
   */
  selectCard: (card: CardResponse | null) => {
    set({ selectedCard: card });
  },

  /**
   * Updates card nickname
   */
  updateCardNickname: async (cardId: string, nickname: string) => {
    set({ isUpdatingCard: true, error: null });
    try {
      const updatedCard = await cardService.updateCardNickname(cardId, nickname);

      // Update in local list
      set((state) => ({
        cards: state.cards.map((card) =>
          card.id === cardId ? updatedCard : card
        ),
        selectedCard:
          state.selectedCard?.id === cardId ? updatedCard : state.selectedCard,
        isUpdatingCard: false,
      }));

      return updatedCard;
    } catch (error) {
      const err = error as CardServiceError;
      set({
        error: {
          code: err.code,
          message: err.message,
          details: err.details,
        },
        isUpdatingCard: false,
      });
      throw error;
    }
  },

  /**
   * Sets a card as default payment method
   */
  setDefaultCard: async (cardId: string) => {
    set({ isUpdatingCard: true, error: null });
    try {
      const updatedCard = await cardService.setDefaultCard(cardId);

      // Update all cards: only one should be default
      set((state) => ({
        cards: state.cards.map((card) => ({
          ...card,
          isDefault: card.id === cardId,
        })),
        selectedCard:
          state.selectedCard?.id === cardId
            ? updatedCard
            : state.selectedCard,
        isUpdatingCard: false,
      }));

      return updatedCard;
    } catch (error) {
      const err = error as CardServiceError;
      set({
        error: {
          code: err.code,
          message: err.message,
          details: err.details,
        },
        isUpdatingCard: false,
      });
      throw error;
    }
  },

  /**
   * Deletes a card
   */
  deleteCard: async (cardId: string) => {
    set({ isDeletingCard: true, error: null });
    try {
      await cardService.deleteCard(cardId);

      // Remove from local list
      set((state) => ({
        cards: state.cards.filter((card) => card.id !== cardId),
        selectedCard:
          state.selectedCard?.id === cardId ? null : state.selectedCard,
        isDeletingCard: false,
      }));
    } catch (error) {
      const err = error as CardServiceError;
      set({
        error: {
          code: err.code,
          message: err.message,
          details: err.details,
        },
        isDeletingCard: false,
      });
      throw error;
    }
  },

  /**
   * Clears error state
   */
  clearError: () => {
    set({ error: null });
  },

  /**
   * Resets store to initial state
   */
  reset: () => {
    set({
      cards: [],
      selectedCard: null,
      isLoadingCards: false,
      isCreatingCard: false,
      isUpdatingCard: false,
      isDeletingCard: false,
      error: null,
    });
  },
}));

export default useCardStore;
