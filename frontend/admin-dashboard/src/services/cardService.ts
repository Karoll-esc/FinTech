/**
 * Card Service
 * HU-016: Add Card - Phase 5 API Integration
 * 
 * API client for card operations
 * Communicates with backend POST /api/v1/cards endpoint
 */

import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Card request payload sent to backend
 */
export interface CreateCardPayload {
  cardNumber: string;
  month: number;
  year: number;
  cvv: string;
  holderName: string;
  documentId: string;
  nickname: string;
}

/**
 * Card response from backend
 */
export interface CardResponse {
  id: string;
  userId: string;
  cardType: string;
  last4Digits: string;
  holderName: string;
  expiryMonth: number;
  expiryYear: number;
  nickname: string;
  isDefault: boolean;
  createdAt: string;
  status: 'ACTIVE' | 'INACTIVE' | 'BLOCKED';
}

/**
 * Error response from API
 */
export interface ApiErrorResponse {
  detail: string | {
    msg: string;
    type?: string;
    loc?: string[];
  }[];
  status: number;
}

/**
 * Typed API error
 */
export class CardServiceError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message);
    this.name = 'CardServiceError';
  }
}

/**
 * Card Service API client
 */
class CardService {
  private axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    // Add request interceptor to include auth token
    this.axiosInstance.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor to handle errors
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorResponse>) => {
        if (error.response?.status === 401) {
          // Token expired or invalid - redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Creates a new card
   * @param payload Card data (card number, expiry, CVV, holder name, etc.)
   * @returns Card response with masked card number (last 4 digits only)
   * @throws CardServiceError on validation error, rate limit, duplicate card, or server error
   */
  async createCard(payload: CreateCardPayload): Promise<CardResponse> {
    try {
      const response = await this.axiosInstance.post<CardResponse>(
        '/api/v1/cards',
        payload
      );

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Gets list of user's cards
   * @returns Array of cards (with last 4 digits masked)
   * @throws CardServiceError on authentication or server error
   */
  async getCards(): Promise<CardResponse[]> {
    try {
      const response = await this.axiosInstance.get<CardResponse[]>(
        '/api/v1/cards'
      );

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Gets a single card by ID
   * @param cardId Card ID
   * @returns Card data with masked number
   * @throws CardServiceError if card not found
   */
  async getCard(cardId: string): Promise<CardResponse> {
    try {
      const response = await this.axiosInstance.get<CardResponse>(
        `/api/v1/cards/${cardId}`
      );

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Updates card nickname
   * @param cardId Card ID
   * @param nickname New nickname
   * @returns Updated card
   * @throws CardServiceError if card not found
   */
  async updateCardNickname(cardId: string, nickname: string): Promise<CardResponse> {
    try {
      const response = await this.axiosInstance.put<CardResponse>(
        `/api/v1/cards/${cardId}`,
        { nickname }
      );

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Sets card as default payment method
   * @param cardId Card ID
   * @returns Updated card with isDefault=true
   * @throws CardServiceError if card not found
   */
  async setDefaultCard(cardId: string): Promise<CardResponse> {
    try {
      const response = await this.axiosInstance.put<CardResponse>(
        `/api/v1/cards/${cardId}/default`,
        {}
      );

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Deletes a card
   * @param cardId Card ID
   * @throws CardServiceError if card not found or is default card
   */
  async deleteCard(cardId: string): Promise<void> {
    try {
      await this.axiosInstance.delete(`/api/v1/cards/${cardId}`);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Handles API errors and converts them to CardServiceError
   */
  private handleError(error: any): CardServiceError {
    // Network error or no response
    if (!axios.isAxiosError(error)) {
      return new CardServiceError(
        'NETWORK_ERROR',
        'Network error. Please check your connection.',
        0,
        error
      );
    }

    const status = error.response?.status || 0;
    const data = error.response?.data;

    // Handle specific error codes
    switch (status) {
      case 400:
        return new CardServiceError(
          'VALIDATION_ERROR',
          this.extractErrorMessage(data) || 'Invalid card data. Please check your input.',
          400,
          data
        );

      case 401:
        return new CardServiceError(
          'UNAUTHORIZED',
          'Your session has expired. Please login again.',
          401
        );

      case 403:
        return new CardServiceError(
          'FORBIDDEN',
          'You do not have permission to perform this action.',
          403
        );

      case 404:
        return new CardServiceError(
          'NOT_FOUND',
          'Card not found.',
          404
        );

      case 409:
        return new CardServiceError(
          'CONFLICT',
          'This card is already in your wallet.',
          409,
          data
        );

      case 429:
        return new CardServiceError(
          'RATE_LIMITED',
          'Too many requests. Please wait a moment and try again.',
          429,
          {
            retryAfter: error.response?.headers['retry-after'],
            rateLimit: {
              limit: error.response?.headers['x-ratelimit-limit'],
              remaining: error.response?.headers['x-ratelimit-remaining'],
              reset: error.response?.headers['x-ratelimit-reset'],
            },
          }
        );

      case 500:
        return new CardServiceError(
          'SERVER_ERROR',
          'Server error. Please try again later.',
          500
        );

      default:
        return new CardServiceError(
          'UNKNOWN_ERROR',
          error.message || 'An unexpected error occurred.',
          status,
          data
        );
    }
  }

  /**
   * Extracts error message from API response
   */
  private extractErrorMessage(data: any): string | null {
    if (!data) return null;

    // Handle string detail
    if (typeof data.detail === 'string') {
      return data.detail;
    }

    // Handle array of validation errors
    if (Array.isArray(data.detail)) {
      const messages = data.detail
        .map((error: any) => error.msg || error)
        .filter(Boolean);
      return messages.length > 0 ? messages.join(', ') : null;
    }

    return null;
  }
}

/**
 * Singleton instance of CardService
 */
export const cardService = new CardService();

export default cardService;
