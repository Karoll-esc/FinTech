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
