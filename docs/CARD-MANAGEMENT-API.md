# HU-015: Card Management API Documentation

## Overview

The Card Management feature (HU-015) provides a complete system for users to manage debit/credit cards, view transactions, and initiate transfers with integrated fraud evaluation. This document describes the API endpoints, data models, and integration patterns.

## API Endpoints

All endpoints require `Authorization: Bearer <user_id>` header.

### Card Operations

#### 1. List User Cards
```
GET /api/v1/cards
Authorization: Bearer <user_id>
```

**Response (200 OK):**
```json
{
  "cards": [
    {
      "card_id": "card_uuid_001",
      "last_four": "4242",
      "card_type": "VISA",
      "balance": 5000.00,
      "currency": "USD",
      "status": "ACTIVE",
      "expires_at": "2026-12-31T23:59:59Z",
      "created_at": "2025-01-28T10:30:00Z"
    }
  ],
  "total": 1,
  "timestamp": "2025-01-28T14:30:00Z"
}
```

**Query Parameters:**
- `limit` (int, default: 10): Maximum cards to return
- `offset` (int, default: 0): Pagination offset
- `status` (string, optional): Filter by status (ACTIVE, BLOCKED, EXPIRED)

**Status Codes:**
- `200 OK`: Cards retrieved successfully
- `401 Unauthorized`: Missing or invalid authorization
- `500 Server Error`: Database connection failure

---

#### 2. Get Card Details
```
GET /api/v1/cards/{card_id}
Authorization: Bearer <user_id>
```

**Response (200 OK):**
```json
{
  "card_id": "card_uuid_001",
  "user_id": "user_001",
  "last_four": "4242",
  "card_type": "VISA",
  "balance": 5000.00,
  "currency": "USD",
  "status": "ACTIVE",
  "expires_at": "2026-12-31T23:59:59Z",
  "created_at": "2025-01-28T10:30:00Z",
  "blocked_at": null,
  "block_reason": null
}
```

**Status Codes:**
- `200 OK`: Card found
- `404 Not Found`: Card does not exist
- `403 Forbidden`: Card belongs to different user

---

#### 3. Block Card
```
PUT /api/v1/cards/{card_id}/block
Authorization: Bearer <user_id>

{
  "reason": "Card lost or stolen"
}
```

**Response (202 Accepted):**
```json
{
  "card_id": "card_uuid_001",
  "status": "BLOCKED",
  "blocked_at": "2025-01-28T14:35:00Z",
  "reason": "Card lost or stolen"
}
```

**Status Codes:**
- `202 Accepted`: Block request accepted (async processing)
- `400 Bad Request`: Card already blocked
- `404 Not Found`: Card not found
- `403 Forbidden`: Unauthorized

---

#### 4. Unblock Card
```
PUT /api/v1/cards/{card_id}/unblock
Authorization: Bearer <user_id>
```

**Response (202 Accepted):**
```json
{
  "card_id": "card_uuid_001",
  "status": "ACTIVE",
  "unblocked_at": "2025-01-28T14:40:00Z"
}
```

---

#### 5. Transfer Money (With Fraud Evaluation)
```
POST /api/v1/cards/{card_id}/transfer
Authorization: Bearer <user_id>
Content-Type: application/json

{
  "amount": 500.00,
  "recipient_user_id": "user_002",
  "description": "Payment for invoice #INV-2025-001",
  "location": {
    "lat": 4.7110,
    "lng": -74.0721,
    "city": "Bogotá",
    "country": "Colombia"
  },
  "device_id": "device_uuid_abc123",
  "metadata": {
    "invoice_id": "INV-2025-001",
    "reference": "Monthly subscription"
  }
}
```

**Response (202 Accepted):**
```json
{
  "transaction_id": "txn_uuid_2025_001",
  "card_id": "card_uuid_001",
  "amount": 500.00,
  "status": "PENDING_FRAUD_EVALUATION",
  "initiated_at": "2025-01-28T14:45:00Z",
  "estimated_completion": "2025-01-28T14:46:00Z"
}
```

**Status Codes:**
- `202 Accepted`: Transfer initiated (async processing with fraud evaluation)
- `400 Bad Request`: Insufficient balance, invalid amount, validation error
- `403 Forbidden`: Card blocked or expired
- `404 Not Found`: Card not found
- `409 Conflict`: Card status not compatible (e.g., card pending fraud review)

**Request Validation:**
- `amount`: Must be > 0 and ≤ card balance
- `amount`: Must not exceed daily limit (configured per user)
- `location`: Must include lat, lng
- `device_id`: Must be non-empty string

---

#### 6. Get Transfer Status
```
GET /api/v1/transfers/{transaction_id}/status
Authorization: Bearer <user_id>
```

**Response (200 OK):**
```json
{
  "transaction_id": "txn_uuid_2025_001",
  "card_id": "card_uuid_001",
  "status": "APPROVED",
  "fraud_evaluation": {
    "risk_level": "LOW_RISK",
    "strategies_triggered": [],
    "confidence": 0.98,
    "evaluated_at": "2025-01-28T14:45:15Z"
  },
  "initiated_at": "2025-01-28T14:45:00Z",
  "completed_at": "2025-01-28T14:45:30Z"
}
```

**Possible Statuses:**
- `PENDING_FRAUD_EVALUATION`: Awaiting fraud service evaluation
- `APPROVED`: Passed fraud checks, transfer approved
- `FLAGGED_FOR_REVIEW`: High risk, pending manual review
- `REJECTED`: Fraud evaluation rejected transfer
- `COMPLETED`: Transfer successfully completed
- `FAILED`: Transfer failed (insufficient funds, card error, etc.)

---

#### 7. List Card Transactions
```
GET /api/v1/cards/{card_id}/transactions
Authorization: Bearer <user_id>

Query Parameters:
- limit: 20 (default)
- offset: 0 (default)
- status: COMPLETED (optional filter)
- date_from: ISO-8601 (optional)
- date_to: ISO-8601 (optional)
```

**Response (200 OK):**
```json
{
  "transactions": [
    {
      "transaction_id": "txn_uuid_2025_001",
      "type": "TRANSFER",
      "amount": 500.00,
      "recipient_id": "user_002",
      "status": "COMPLETED",
      "initiated_at": "2025-01-28T14:45:00Z",
      "completed_at": "2025-01-28T14:45:30Z",
      "description": "Payment for invoice #INV-2025-001"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

---

## Data Models

### Card
```python
@dataclass(frozen=True)
class Card:
    card_id: str              # UUID
    user_id: str              # Card owner
    last_four: str            # Last 4 digits
    card_type: CardType       # VISA, MASTERCARD, etc.
    balance: Decimal          # Current balance
    currency: str = "USD"
    status: CardStatus        # ACTIVE, BLOCKED, EXPIRED
    expires_at: datetime      # Expiration date
    created_at: datetime
    blocked_at: Optional[datetime] = None
    block_reason: Optional[str] = None
```

### CardStatus (Enum)
```python
class CardStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"
```

### CardType (Enum)
```python
class CardType(str, Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"
    DISCOVER = "DISCOVER"
```

### TransferRequest
```python
@dataclass(frozen=True)
class TransferRequest:
    card_id: str
    amount: Decimal
    recipient_user_id: str
    location: Location           # {lat, lng, city, country}
    device_id: str
    description: Optional[str] = None
    metadata: Optional[dict] = None
    initiated_at: datetime = field(default_factory=datetime.utcnow)
```

### TransactionRecord
```python
@dataclass
class TransactionRecord:
    transaction_id: str
    card_id: str
    type: str                    # TRANSFER, WITHDRAWAL, etc.
    amount: Decimal
    status: str                  # PENDING, COMPLETED, FAILED
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    fraud_evaluation: Optional[dict] = None
```

---

## Integration Patterns

### 1. Async Transfer Processing (202 Pattern)

All transfer requests follow the async-first pattern:

```
Client → API (validate) → Queue → 202 Accepted
                                      ↓
                         Worker (fraud evaluation)
                                      ↓
                         MongoDB (record status)
                                      ↓
                         Client polls /transfer/{id}/status
```

**Benefits:**
- Immediate response to client
- Non-blocking fraud evaluation
- Decoupled from external fraud service latency

### 2. Fraud Evaluation Integration

When a transfer is initiated:

1. **API Gateway** validates request and publishes to `fraud.queue`
2. **Worker Service** consumes from RabbitMQ
3. **Fraud Service** evaluates against 7 strategies:
   - Amount threshold check
   - Location impossibility (geolocation velocity)
   - Device validation
   - Rapid successive transactions
   - Unusual time of day
   - Timezone shift detection
   - Whitelist/blacklist check
4. **Result** stored in MongoDB `evaluations` collection
5. **Status** updated in `transactions` collection

### 3. Caching Strategy (Cache-Aside)

```
GET /api/v1/cards
├─ Check Redis: user:{user_id}:cards
├─ If HIT: Return cached response (TTL: 5 min)
└─ If MISS:
    ├─ Query MongoDB
    ├─ Cache result in Redis
    └─ Return response
```

**Cache Invalidation:**
- On card creation/deletion: Delete `user:{user_id}:cards`
- On transfer/balance change: Delete `user:{user_id}:cards` and `user:{user_id}:transactions`
- TTL: 5 minutes (automatic)

### 4. Audit Trail

All card operations logged to `audit_logs` collection:

```json
{
  "audit_id": "audit_uuid",
  "action": "TRANSFER_INITIATED",
  "entity_type": "CARD",
  "entity_id": "card_uuid_001",
  "user_id": "user_001",
  "timestamp": "2025-01-28T14:45:00Z",
  "request_id": "req_uuid",
  "details": {
    "amount": 500.00,
    "status_before": "ACTIVE",
    "status_after": "ACTIVE"
  }
}
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request - Validation Error
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "amount",
      "message": "Amount must be greater than 0"
    }
  ]
}
```

#### 403 Forbidden - Card Blocked
```json
{
  "detail": "Cannot transfer from blocked card. Reason: Card lost or stolen"
}
```

#### 404 Not Found
```json
{
  "detail": "Card card_uuid_001 not found"
}
```

#### 409 Conflict - Status Incompatible
```json
{
  "detail": "Cannot perform operation. Card status is BLOCKED"
}
```

#### 429 Too Many Requests - Rate Limit
```json
{
  "detail": "Rate limit exceeded. Max 10 transfers per minute"
}
```

---

## Curl Examples

### List Cards
```bash
curl -X GET http://localhost:8000/api/v1/cards \
  -H "Authorization: Bearer user_001" \
  -H "Content-Type: application/json"
```

### Transfer Money
```bash
curl -X POST http://localhost:8000/api/v1/cards/card_uuid_001/transfer \
  -H "Authorization: Bearer user_001" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "recipient_user_id": "user_002",
    "description": "Payment for services",
    "location": {
      "lat": 4.7110,
      "lng": -74.0721,
      "city": "Bogotá",
      "country": "Colombia"
    },
    "device_id": "device_abc123"
  }'
```

**Response:**
```json
{
  "transaction_id": "txn_uuid_2025_001",
  "status": "PENDING_FRAUD_EVALUATION",
  "initiated_at": "2025-01-28T14:45:00Z"
}
```

### Check Transfer Status
```bash
curl -X GET http://localhost:8000/api/v1/transfers/txn_uuid_2025_001/status \
  -H "Authorization: Bearer user_001"
```

### Block Card
```bash
curl -X PUT http://localhost:8000/api/v1/cards/card_uuid_001/block \
  -H "Authorization: Bearer user_001" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Card lost"
  }'
```

---

## Performance Requirements

| Operation | Target | SLA |
|-----------|--------|-----|
| List cards | < 100ms | 99.9% |
| Get card details | < 50ms | 99.9% |
| Transfer initiation | < 200ms | 99% |
| Transfer status check | < 100ms | 99.9% |
| List transactions | < 150ms | 99.9% |

**Notes:**
- Cached responses (cache hit) should be < 50ms
- Database queries optimized with indexes on `user_id`, `card_id`, `status`, `created_at`

---

## Security Considerations

1. **Authorization**: All endpoints require valid Bearer token (user_id)
2. **Rate Limiting**: 10 transfers per minute per user
3. **Amount Limits**: Configurable daily/monthly limits per card
4. **Device Binding**: Optional device_id for device verification
5. **Audit Trail**: All operations logged for compliance

---

## SDK Usage Examples

### TypeScript/React
```typescript
import { cardStore } from '@/stores/cardStore';

// Fetch cards
const { cards, loading, error } = await cardStore.getState().fetchUserCards();

// Initiate transfer
const { transaction_id } = await cardStore.getState().submitTransfer({
  amount: 500,
  recipient_user_id: 'user_002',
  location: { lat: 4.7110, lng: -74.0721 },
  device_id: 'device_001',
  description: 'Payment'
});

// Poll status
const status = await cardStore.getState().pollTransferStatus(transaction_id);
```

### Python
```python
from services.fraud_evaluation_service.src.application.card_use_cases import GetUserCardsUseCase

use_case = GetUserCardsUseCase(card_repo, cache_service)
cards = await use_case.execute(user_id='user_001')

for card in cards:
    print(f"Card: {card.last_four}, Balance: {card.balance}")
```

---

## Testing

### Unit Tests (Phase 1-2)
```bash
pytest tests/unit/test_card_models.py -v
pytest tests/unit/test_card_use_cases.py -v
```

### Integration Tests (Phase 9)
```bash
pytest tests/integration/test_card_fraud_integration.py -v
```

### E2E Tests (Phase 8)
```bash
npx playwright test tests-e2e/tests/cards.spec.ts
```

---

## Deployment Checklist

- [ ] All unit tests passing (95% coverage)
- [ ] Integration tests passing
- [ ] E2E tests passing (main flows)
- [ ] Load testing completed (1000 TPS)
- [ ] Security audit passed
- [ ] API documentation reviewed
- [ ] Fraud rules configured in MongoDB
- [ ] Redis cache configured (5 min TTL)
- [ ] RabbitMQ queues created (`fraud.queue`)
- [ ] Monitoring alerts configured
- [ ] Runbooks created for common issues

---

## Troubleshooting

### Transfer stuck in PENDING_FRAUD_EVALUATION

**Symptoms:** Transfer status never updates

**Solution:**
1. Check Worker service logs: `docker-compose logs worker`
2. Verify RabbitMQ queue: `docker-compose exec rabbitmq rabbitmqctl list_queues`
3. Restart worker: `docker-compose restart worker`

### Cache inconsistency

**Symptoms:** Old card balance shown after transfer

**Solution:**
```bash
# Clear user cache
redis-cli DEL user:user_001:cards

# Next request will refresh from MongoDB
```

### High fraud false positives

**Solution:**
1. Review fraud strategy triggers in `PUT /config/{rule_name}`
2. Adjust thresholds
3. Monitor metrics: `GET /metrics/fraud-accuracy`

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-28  
**Maintainer:** FinTech Team
