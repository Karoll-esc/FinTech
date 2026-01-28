# Card Management Components - Frontend Documentation

## Overview

The Card Management feature provides a complete UI for users to:
- View their debit/credit cards
- Manage card status (block/unblock)
- View transaction history
- Initiate transfers with fraud evaluation
- Handle responsive layouts and accessibility

## Architecture

### State Management (Zustand Store)

The `cardStore.ts` centralized state management:

```typescript
// src/stores/cardStore.ts
interface CardStoreState {
  // State
  cards: Card[];
  selectedCard: Card | null;
  transactions: Transaction[];
  transferStatus: TransferStatus | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchUserCards: () => Promise<Card[]>;
  fetchCardTransactions: (cardId: string, limit?: number) => Promise<Transaction[]>;
  blockCard: (cardId: string, reason: string) => Promise<void>;
  unblockCard: (cardId: string) => Promise<void>;
  submitTransfer: (request: TransferRequest) => Promise<{ transaction_id: string }>;
  pollTransferStatus: (transactionId: string) => Promise<TransferStatus>;
  clearError: () => void;
}
```

### Component Hierarchy

```
Dashboard (Page)
├── CardsList (Container)
│   ├── CardCard (Component) × 3
│   │   ├── StatusBadge
│   │   └── ActionButtons
│   │       ├── ViewTransactions
│   │       ├── Transfer
│   │       ├── Block
│   │       └── Details
│   ├── SkeletonCard (Loading)
│   └── EmptyState
└── TransferForm (Modal)
    ├── AmountInput
    ├── RecipientInput
    ├── LocationInput
    ├── DeviceInput
    └── SubmitButton
```

## Components

### 1. CardCard Component

**File:** `src/components/cards/CardCard.tsx`

Single card display with actions.

**Props:**
```typescript
interface CardCardProps {
  card: Card;
  onViewTransactions: (cardId: string) => void;
  onTransfer: (cardId: string) => void;
  onBlock: (cardId: string) => void;
  onDetails: (cardId: string) => void;
}
```

**Features:**
- Displays masked card number (XXXX-XXXX-XXXX-1234)
- Shows balance, expiry date, cardholder name
- Color-coded status badge (green ACTIVE, red BLOCKED, yellow EXPIRED)
- 4 action buttons with icons
- Disabled transfer for blocked cards
- Responsive gradient background

**Example:**
```typescript
<CardCard
  card={card}
  onViewTransactions={() => handleViewTransactions(card.card_id)}
  onTransfer={() => setSelectedCard(card)}
  onBlock={() => handleBlock(card.card_id)}
  onDetails={() => setShowDetails(card)}
/>
```

### 2. CardsList Component

**File:** `src/components/cards/CardsList.tsx`

Container displaying user's cards with pagination.

**Props:**
```typescript
interface CardsListProps {
  onTransfer: (card: Card) => void;
  onViewTransactions: (cardId: string) => void;
}
```

**Features:**
- Displays up to 3 cards by default
- Skeleton loader during fetch
- Empty state with "Request Card" button
- Error state with retry button
- "View All Cards" pagination for >3 cards
- Responsive grid (1 mobile, 2 tablet, 3 desktop)

**States:**
```
LOADING: Shows 3 skeleton cards
SUCCESS: Displays cards with actions
EMPTY: No cards found
ERROR: Retry button with error message
```

**Example:**
```typescript
<CardsList
  onTransfer={(card) => setShowTransferForm(card)}
  onViewTransactions={(cardId) => loadTransactions(cardId)}
/>
```

### 3. TransferForm Component

**File:** `src/components/cards/TransferForm.tsx`

React Hook Form-based transfer form with validation.

**Props:**
```typescript
interface TransferFormProps {
  card: Card;
  onSubmit: (request: TransferRequest) => Promise<{ transaction_id: string }>;
  onCancel: () => void;
}
```

**Form Fields:**
1. **Amount** (required)
   - Validation: > 0, ≤ balance, decimal 2 places
   - Real-time available balance check
   - Error: "Insufficient balance"

2. **Recipient User ID** (required)
   - Validation: Non-empty, valid format
   - Hint: "user_001, user_name_123"

3. **Location** (required)
   - Format: "City, Country" or "Lat, Lng"
   - Validation: Required for fraud evaluation

4. **Device ID** (required)
   - Validation: Non-empty string
   - Hint: "device_uuid or device_name"

5. **Transaction ID** (optional)
   - Auto-generated if not provided
   - Format: "txn_YYYYMMDD_XXXXX"

6. **Description** (optional)
   - Max 200 characters
   - Hint: "Payment for services"

7. **Metadata** (optional)
   - JSON object for additional context

**Features:**
- Real-time validation with inline errors
- Balance checking with available amount display
- Disabled transfer button for blocked/expired cards
- Submit and cancel buttons
- Loading state during submission
- Success confirmation with transaction ID
- Error recovery with retry

**Example:**
```typescript
<TransferForm
  card={selectedCard}
  onSubmit={async (request) => {
    return await cardStore.getState().submitTransfer(request);
  }}
  onCancel={() => setShowTransferForm(false)}
/>
```

## Store Actions (Zustand)

### fetchUserCards()
```typescript
// Fetch all cards for authenticated user
const cards = await cardStore.getState().fetchUserCards();

// Cached for 5 minutes
// Fallback to cache on network error
// Returns [] if no cards found
```

**Response:**
```json
{
  "cards": [
    {
      "card_id": "uuid",
      "user_id": "user_001",
      "last_four": "4242",
      "card_type": "VISA",
      "balance": 5000.00,
      "currency": "USD",
      "status": "ACTIVE",
      "expires_at": "2026-12-31"
    }
  ]
}
```

### fetchCardTransactions(cardId, limit)
```typescript
// Fetch transactions for specific card
const transactions = await cardStore
  .getState()
  .fetchCardTransactions('card_uuid', 20);

// Returns paginated transactions
// Limit: 1-100, default 20
```

**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "txn_uuid",
      "type": "TRANSFER",
      "amount": 500.00,
      "status": "COMPLETED",
      "initiated_at": "2025-01-28T14:45:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "has_more": true
}
```

### submitTransfer(request)
```typescript
// Initiate transfer with fraud evaluation
const result = await cardStore.getState().submitTransfer({
  card_id: 'card_uuid',
  amount: 500,
  recipient_user_id: 'user_002',
  location: { lat: 4.7110, lng: -74.0721 },
  device_id: 'device_abc123',
  description: 'Payment for invoice'
});

// Returns transaction_id
// Status: PENDING_FRAUD_EVALUATION
// Use pollTransferStatus() to check fraud evaluation
```

### pollTransferStatus(transactionId)
```typescript
// Poll fraud evaluation result
// Polls every 1 second, max 10 polls (10 seconds)
const status = await cardStore
  .getState()
  .pollTransferStatus('txn_uuid');

// Returns: { status: 'APPROVED' | 'FLAGGED_FOR_REVIEW' | 'REJECTED', risk_level: 'LOW_RISK' | 'HIGH_RISK' }
```

### blockCard(cardId)
```typescript
// Block card (async)
await cardStore.getState().blockCard('card_uuid');

// Updates card status to BLOCKED
// Invalidates cache
// Shows in UI immediately
```

## Type Definitions

```typescript
// Card
interface Card {
  card_id: string;
  user_id: string;
  last_four: string;
  card_type: 'VISA' | 'MASTERCARD' | 'AMEX' | 'DISCOVER';
  balance: number;
  currency: string;
  status: 'ACTIVE' | 'BLOCKED' | 'EXPIRED' | 'PENDING_ACTIVATION';
  expires_at: string; // ISO-8601
  created_at: string; // ISO-8601
  blocked_at?: string;
  block_reason?: string;
}

// TransferRequest
interface TransferRequest {
  card_id: string;
  amount: number;
  recipient_user_id: string;
  location: {
    lat: number;
    lng: number;
    city?: string;
    country?: string;
  };
  device_id: string;
  description?: string;
  transaction_id?: string;
  metadata?: Record<string, any>;
}

// TransferStatus
interface TransferStatus {
  transaction_id: string;
  status: 'PENDING_FRAUD_EVALUATION' | 'APPROVED' | 'FLAGGED_FOR_REVIEW' | 'REJECTED' | 'COMPLETED';
  fraud_evaluation?: {
    risk_level: 'LOW_RISK' | 'MEDIUM_RISK' | 'HIGH_RISK';
    strategies_triggered: string[];
    confidence: number;
  };
  initiated_at: string;
  completed_at?: string;
}

// Transaction
interface Transaction {
  transaction_id: string;
  type: 'TRANSFER' | 'WITHDRAWAL' | 'DEPOSIT';
  amount: number;
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
  initiated_at: string;
  completed_at?: string;
  description?: string;
  recipient_id?: string;
}
```

## API Integration

### Authorization Header
All API calls automatically include Bearer token:
```typescript
// Extracted from localStorage
const token = localStorage.getItem('auth_token') || 'user_001';
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

### Error Handling
```typescript
try {
  const result = await cardStore.getState().submitTransfer(request);
} catch (error) {
  if (error.response?.status === 403) {
    // Card blocked or expired
  } else if (error.response?.status === 400) {
    // Validation error (insufficient balance, invalid amount)
  } else if (error.response?.status === 404) {
    // Card not found
  }
}
```

## Usage Examples

### Basic Card List
```typescript
import { CardsList } from '@/components/cards/CardsList';

export function Dashboard() {
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [showTransfer, setShowTransfer] = useState(false);

  return (
    <div>
      <CardsList
        onTransfer={(card) => {
          setSelectedCard(card);
          setShowTransfer(true);
        }}
        onViewTransactions={(cardId) => {
          // Handle view transactions
        }}
      />

      {showTransfer && selectedCard && (
        <TransferForm
          card={selectedCard}
          onSubmit={async (request) => {
            const { transaction_id } = await cardStore
              .getState()
              .submitTransfer(request);
            
            // Poll for fraud evaluation result
            const status = await cardStore
              .getState()
              .pollTransferStatus(transaction_id);
            
            if (status.status === 'APPROVED') {
              // Show success
            } else if (status.status === 'FLAGGED_FOR_REVIEW') {
              // Show pending review message
            } else {
              // Show rejection
            }
          }}
          onCancel={() => setShowTransfer(false)}
        />
      )}
    </div>
  );
}
```

### Transaction History Modal
```typescript
import { TransactionsList } from '@/components/cards/TransactionsList';

function TransactionsModal({ cardId, onClose }: { cardId: string; onClose: () => void }) {
  const transactions = cardStore((s) => s.transactions);
  const fetchTransactions = cardStore((s) => s.fetchCardTransactions);

  useEffect(() => {
    fetchTransactions(cardId, 20);
  }, [cardId]);

  return (
    <Modal isOpen onClose={onClose}>
      <Modal.Header>Transaction History</Modal.Header>
      <Modal.Body>
        {transactions.map((txn) => (
          <TransactionItem key={txn.transaction_id} transaction={txn} />
        ))}
      </Modal.Body>
    </Modal>
  );
}
```

## Testing

### Unit Tests (Components)
```bash
cd frontend/user-app
npm test -- CardCard.test.tsx
npm test -- TransferForm.test.tsx
npm test -- CardsList.test.tsx
```

### E2E Tests (Playwright)
```bash
cd tests-e2e
npm test -- tests/cards.spec.ts
```

## Styling

Components use Tailwind CSS with dark mode:
- **Background**: `bg-slate-900` (dark)
- **Text**: `text-white`, `text-gray-300`
- **Buttons**: `bg-blue-600 hover:bg-blue-700`
- **Status Colors**:
  - ACTIVE: `bg-green-900` text-green-200`
  - BLOCKED: `bg-red-900 text-red-200`
  - EXPIRED: `bg-yellow-900 text-yellow-200`

## Performance

- **Card List Load**: < 100ms (cached)
- **Transfer Submission**: < 200ms
- **Fraud Evaluation**: 1-10 seconds (polled)
- **Responsive**: Mobile-first, tested on 375px-2560px widths

## Accessibility

- ARIA labels on all buttons
- Semantic HTML (buttons, forms, status roles)
- Keyboard navigation (Tab, Enter, Escape)
- Color not only indicator (status badges have text + color)
- Form validation feedback inline

## Known Issues

- None currently

## Future Enhancements

- [ ] Card creation/request flow
- [ ] Multi-currency support
- [ ] Transaction search and filters
- [ ] Card analytics dashboard
- [ ] Biometric authentication for transfers
- [ ] Scheduled transfers
- [ ] Recurring payments

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-28  
**Maintainer:** FinTech Frontend Team
