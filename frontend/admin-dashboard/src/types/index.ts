/**
 * HUMAN REVIEW (Maria Paula Gutierrez):
 * La IA usó 'any' en todas partes.
 * Definí tipos específicos para evitar errores y
 * que el código sea más claro.
 */
export interface Rule {
  id: string;
  name: string;
  type: string;
  parameters: Record<string, any>;
  enabled: boolean;
  order: number;
}

export interface Transaction {
  id: string;
  amount: number;
  userId: string;
  date: string;
  status: 'APPROVED' | 'SUSPICIOUS' | 'REJECTED';
  violations: string[];
  riskLevel: string;
  location?: string;
  userAuthenticated?: boolean | null;
  reviewedBy?: string | null;
  reviewedAt?: string | null;
}

export interface Metrics {
  totalTransactions: number;
  blockedRate: number;
  suspiciousRate: number;
  avgRiskScore: number;
}

export interface TrendData {
  time: string;
  approved: number;
  suspicious: number;
  rejected: number;
}

// Card Management Types (HU-015, HU-016)
export interface Card {
  card_id: string;
  card_number: string; // Masked: ****0366
  card_holder_name: string;
  expiry_date: string; // MM/YY format
  card_type: 'DEBIT' | 'CREDIT';
  nickname?: string;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
  updated_at: string;
}

export interface CardListResponse {
  cards: Card[];
  total: number;
}

export interface AddCardRequest {
  card_number: string; // 16 digits
  card_holder_name: string; // 3-50 characters
  expiry_date: string; // MM/YY format
  card_type: 'DEBIT' | 'CREDIT';
  nickname?: string; // Optional, max 20 chars
}
