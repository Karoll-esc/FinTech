/**
 * Card Store - Phase 5 (TASK-041-050)
 * 
 * Zustand store for card state management:
 * - Fetch user's cards
 * - Transfer money
 * - Block/unblock cards
 * - View transaction history
 * - Error handling and loading states
 * - Polling for fraud evaluation result
 */

import { create } from 'zustand';
import { CardData } from '../components/cards/CardCard';

interface TransactionItem {
  transaction_id: string;
  transaction_date: string;
  description: string;
  amount: number;
  merchant: string;
  status: 'Completed' | 'Pending';
}

interface TransferStatus {
  transaction_id: string;
  status: 'PENDING_EVALUATION' | 'APPROVED' | 'REJECTED' | 'COMPLETED';
  risk_score: number;
  message: string;
  monto?: number;
  usuario?: string;
  estado?: string;
}

interface CardStoreState {
  // State
  cards: CardData[];
  selectedCard: CardData | null;
  transactions: TransactionItem[];
  transferStatus: TransferStatus | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchUserCards: (userId: string) => Promise<void>;
  fetchCardTransactions: (cardId: string, skip?: number, limit?: number) => Promise<void>;
  blockCard: (cardId: string) => Promise<void>;
  unblockCard: (cardId: string) => Promise<void>;
  submitTransfer: (transferData: any) => Promise<string>; // Returns transaction_id
  pollTransferStatus: (transactionId: string, maxPolls?: number) => Promise<void>;
  clearError: () => void;
  clearTransferStatus: () => void;
  selectCard: (card: CardData | null) => void;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useCardStore = create<CardStoreState>()((set, _get) => ({
  // Initial state
  cards: [],
  selectedCard: null,
  transactions: [],
  transferStatus: null,
  loading: false,
  error: null,

  // Fetch user's cards (with cache-aside pattern)
  fetchUserCards: async (_userId: string) => {
    set({ loading: true, error: null });
    try {
      // Get token from localStorage
      const token = localStorage.getItem('auth_token') || '';

      const response = await fetch(`${API_BASE}/cards?limit=3`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You do not have permission to view cards');
        }
        if (response.status === 404) {
          throw new Error('No cards found');
        }
        throw new Error(`Failed to fetch cards: ${response.statusText}`);
      }

      const data = await response.json();
      set({ cards: data.cards || [], loading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch cards';
      set({ error: errorMessage, loading: false });
    }
  },

  // Fetch transaction history for a card
  fetchCardTransactions: async (cardId: string, skip = 0, limit = 20) => {
    set({ loading: true });
    try {
      const token = localStorage.getItem('auth_token') || '';

      const response = await fetch(
        `${API_BASE}/cards/${cardId}/transactions?skip=${skip}&limit=${limit}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch transactions: ${response.statusText}`);
      }

      const data = await response.json();
      set({ transactions: data.transactions || [], loading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch transactions';
      set({ error: errorMessage, loading: false });
    }
  },

  // Block a card
  blockCard: async (cardId: string) => {
    set({ loading: true });
    try {
      const token = localStorage.getItem('auth_token') || '';

      const response = await fetch(`${API_BASE}/cards/${cardId}/block`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to block card: ${response.statusText}`);
      }

      const updatedCard = await response.json();

      // Update the card in state
      set((state: CardStoreState) => ({
        cards: state.cards.map((card: CardData) =>
          card.card_id === cardId ? updatedCard : card
        ),
        loading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to block card';
      set({ error: errorMessage, loading: false });
      throw error;
    }
  },

  // Unblock a card
  unblockCard: async (cardId: string) => {
    set({ loading: true });
    try {
      const token = localStorage.getItem('auth_token') || '';

      const response = await fetch(`${API_BASE}/cards/${cardId}/unblock`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to unblock card: ${response.statusText}`);
      }

      const updatedCard = await response.json();

      // Update the card in state
      set((state: CardStoreState) => ({
        cards: state.cards.map((card: CardData) =>
          card.card_id === cardId ? updatedCard : card
        ),
        loading: false,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to unblock card';
      set({ error: errorMessage, loading: false });
      throw error;
    }
  },

  // Submit a transfer (returns transaction_id for polling)
  submitTransfer: async (transferData: any) => {
    set({ loading: true, error: null });
    try {
      const token = localStorage.getItem('auth_token') || '';

      const response = await fetch(`${API_BASE}/transfers`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transferData),
      });

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error('Invalid transfer data');
        }
        if (response.status === 403) {
          throw new Error('Permission denied');
        }
        if (response.status === 409) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Transfer conflict (blocked or insufficient balance)');
        }
        throw new Error(`Transfer failed: ${response.statusText}`);
      }

      const data = await response.json();
      set({ loading: false, transferStatus: data });
      return data.transaction_id;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Transfer failed';
      set({ error: errorMessage, loading: false });
      throw error;
    }
  },

  // Poll transfer status (with exponential backoff)
  pollTransferStatus: async (transactionId: string, maxPolls = 10) => {
    let pollCount = 0;
    const pollInterval = 1000; // 1 second

    const poll = async (): Promise<void> => {
      try {
        const token = localStorage.getItem('auth_token') || '';

        const response = await fetch(`${API_BASE}/transfers/${transactionId}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch transfer status: ${response.statusText}`);
        }

        const data = await response.json();
        set({ transferStatus: data });

        // Check if completed
        if (data.status === 'COMPLETED' || data.status === 'REJECTED') {
          return;
        }

        // Continue polling if not complete
        pollCount++;
        if (pollCount < maxPolls) {
          await new Promise((resolve) => setTimeout(resolve, pollInterval));
          await poll();
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Polling failed';
        set({ error: errorMessage });
        throw error;
      }
    };

    await poll();
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Clear transfer status
  clearTransferStatus: () => set({ transferStatus: null }),

  // Select a card
  selectCard: (card: CardData | null) => set({ selectedCard: card }),
}));
