# Card Management API Documentation

## Overview

The Card Management API provides endpoints for users to manage their payment cards within the FinTech fraud detection system. Features include:
- Add and manage multiple cards (up to 10 per user)
- Soft-delete with audit trail
- Real-time validation
- Duplicate detection
- Card number masking in API responses
- Event publishing for audit compliance

**Base URL:** `http://localhost:8000` (development)

---

## Authentication

All card management endpoints require authentication via the `X-User-ID` header:

```
X-User-ID: user_123
```

**Note:** In production, use JWT Bearer tokens:
```
Authorization: Bearer <jwt_token>
```

---

## Data Models

### Card Object

```json
{
  "card_id": "card_550e8400-e29b-41d4-a716-446655440000",
  "card_number": "****0366",
  "card_holder_name": "John Doe",
  "expiry_date": "12/25",
  "card_type": "DEBIT",
  "nickname": "Main Card",
  "status": "ACTIVE",
  "created_at": "2026-01-28T10:30:00Z",
  "updated_at": "2026-01-28T10:30:00Z"
}
```

**Field Details:**
- `card_id` (UUID): Unique identifier, auto-generated
- `card_number` (string): Always masked as `****XXXX` in responses (last 4 digits only)
- `card_holder_name` (string): 3-50 characters, name as it appears on card
- `expiry_date` (string): MM/YY format, must be future date
- `card_type` (enum): `DEBIT` or `CREDIT`
- `nickname` (string, optional): Custom label, max 20 characters
- `status` (enum): `ACTIVE` or `INACTIVE` (soft-delete)
- `created_at` (ISO-8601): UTC timestamp of creation
- `updated_at` (ISO-8601): UTC timestamp of last update

### Card Request Body

```json
{
  "card_number": "4532015112830366",
  "card_holder_name": "John Doe",
  "expiry_date": "12/25",
  "card_type": "DEBIT",
  "nickname": "Main Card"
}
```

**Validation Rules:**
- `card_number`: Exactly 16 digits, numeric only
- `card_holder_name`: 3-50 characters, letters/spaces
- `expiry_date`: MM/YY format (01-12/00-99), must be future date
- `card_type`: Must be `DEBIT` or `CREDIT`
- `nickname`: Optional, max 20 characters

---

## Endpoints

### 1. POST /cards - Add New Card

**Description:** Create a new card for the authenticated user.

**Request:**
```bash
curl -X POST http://localhost:8000/cards \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{
    "card_number": "4532015112830366",
    "card_holder_name": "John Doe",
    "expiry_date": "12/25",
    "card_type": "DEBIT",
    "nickname": "Main Card"
  }'
```

**Response (201 Created):**
```json
{
  "card_id": "card_550e8400-e29b-41d4-a716-446655440000",
  "card_number": "****0366",
  "card_holder_name": "John Doe",
  "expiry_date": "12/25",
  "card_type": "DEBIT",
  "nickname": "Main Card",
  "status": "ACTIVE",
  "created_at": "2026-01-28T10:30:00Z",
  "updated_at": "2026-01-28T10:30:00Z"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Validation Error | Invalid card details (wrong format, expired date) |
| 400 | Max Cards Exceeded | User has reached 10 card limit |
| 409 | Duplicate Card | Card with same last 4 digits already exists |
| 422 | Unprocessable Entity | Missing required fields |
| 500 | Internal Server Error | Database or service error |

**Example Error (400 - Max Limit):**
```json
{
  "status_code": 400,
  "error_code": "MAX_CARDS_EXCEEDED",
  "message": "User has reached the maximum of 10 cards",
  "timestamp": "2026-01-28T10:30:00Z"
}
```

**Example Error (409 - Duplicate):**
```json
{
  "status_code": 409,
  "error_code": "DUPLICATE_CARD",
  "message": "Card with last 4 digits 0366 already linked to this account",
  "timestamp": "2026-01-28T10:30:00Z"
}
```

**Business Rules:**
- User can have maximum 10 active cards
- Cards with same last 4 digits are treated as duplicates
- Card number is never returned in plain text
- Duplicate check is case-insensitive
- Audit event `CARD_ADDED` is published

---

### 2. GET /cards - List User's Cards

**Description:** Retrieve all active cards for the authenticated user.

**Request:**
```bash
curl -X GET http://localhost:8000/cards \
  -H "X-User-ID: user_123"
```

**Response (200 OK):**
```json
{
  "cards": [
    {
      "card_id": "card_550e8400-e29b-41d4-a716-446655440000",
      "card_number": "****0366",
      "card_holder_name": "John Doe",
      "expiry_date": "12/25",
      "card_type": "DEBIT",
      "nickname": "Main Card",
      "status": "ACTIVE",
      "created_at": "2026-01-28T10:30:00Z",
      "updated_at": "2026-01-28T10:30:00Z"
    },
    {
      "card_id": "card_660e8400-e29b-41d4-a716-446655440001",
      "card_number": "****3442",
      "card_holder_name": "Jane Smith",
      "expiry_date": "03/27",
      "card_type": "CREDIT",
      "nickname": "Work Card",
      "status": "ACTIVE",
      "created_at": "2026-01-25T14:22:00Z",
      "updated_at": "2026-01-25T14:22:00Z"
    }
  ],
  "total": 2
}
```

**Empty Response (200 OK):**
```json
{
  "cards": [],
  "total": 0
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Unauthorized | Missing/invalid authentication |
| 500 | Internal Server Error | Database error |

**Filtering & Pagination:**
- Currently returns all active cards
- Future: Add pagination with `page`, `limit` parameters
- Inactive (deleted) cards are excluded
- Results sorted by `created_at` descending

---

### 3. GET /cards/{card_id} - Get Card Details

**Description:** Retrieve details of a specific card.

**Request:**
```bash
curl -X GET http://localhost:8000/cards/card_550e8400-e29b-41d4-a716-446655440000 \
  -H "X-User-ID: user_123"
```

**Response (200 OK):**
```json
{
  "card_id": "card_550e8400-e29b-41d4-a716-446655440000",
  "card_number": "****0366",
  "card_holder_name": "John Doe",
  "expiry_date": "12/25",
  "card_type": "DEBIT",
  "nickname": "Main Card",
  "status": "ACTIVE",
  "created_at": "2026-01-28T10:30:00Z",
  "updated_at": "2026-01-28T10:30:00Z"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 403 | Forbidden | User doesn't own this card |
| 404 | Not Found | Card doesn't exist or is deleted |
| 401 | Unauthorized | Missing authentication |
| 500 | Internal Server Error | Database error |

**Example Error (404):**
```json
{
  "status_code": 404,
  "error_code": "CARD_NOT_FOUND",
  "message": "Card with ID card_invalid not found",
  "timestamp": "2026-01-28T10:30:00Z"
}
```

**Example Error (403):**
```json
{
  "status_code": 403,
  "error_code": "FORBIDDEN",
  "message": "You do not have permission to access this card",
  "timestamp": "2026-01-28T10:30:00Z"
}
```

**Security Notes:**
- Only card owner can view details
- Card number is always masked
- No sensitive data in error messages

---

### 4. PUT /cards/{card_id} - Update Card Nickname

**Description:** Update the nickname of a card.

**Request:**
```bash
curl -X PUT http://localhost:8000/cards/card_550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{
    "nickname": "Updated Nickname"
  }'
```

**Response (200 OK):**
```json
{
  "card_id": "card_550e8400-e29b-41d4-a716-446655440000",
  "card_number": "****0366",
  "card_holder_name": "John Doe",
  "expiry_date": "12/25",
  "card_type": "DEBIT",
  "nickname": "Updated Nickname",
  "status": "ACTIVE",
  "created_at": "2026-01-28T10:30:00Z",
  "updated_at": "2026-01-28T10:31:00Z"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Validation Error | Nickname too long (max 20 chars) |
| 403 | Forbidden | User doesn't own this card |
| 404 | Not Found | Card doesn't exist |
| 422 | Unprocessable Entity | Invalid request body |
| 500 | Internal Server Error | Database error |

**Validation Rules:**
- Nickname: max 20 characters
- Can be empty string to clear nickname
- Updates `updated_at` timestamp
- Audit event `CARD_UPDATED` is published

---

### 5. DELETE /cards/{card_id} - Delete Card

**Description:** Soft-delete a card (marks as INACTIVE, audit trail preserved).

**Request:**
```bash
curl -X DELETE http://localhost:8000/cards/card_550e8400-e29b-41d4-a716-446655440000 \
  -H "X-User-ID: user_123"
```

**Response (204 No Content):**
```
(empty body)
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 403 | Forbidden | User doesn't own this card |
| 404 | Not Found | Card doesn't exist or already deleted |
| 401 | Unauthorized | Missing authentication |
| 500 | Internal Server Error | Database error |

**Example Error (404):**
```json
{
  "status_code": 404,
  "error_code": "CARD_NOT_FOUND",
  "message": "Card with ID card_invalid not found",
  "timestamp": "2026-01-28T10:30:00Z"
}
```

**Business Rules:**
- Soft-delete: Card is marked `INACTIVE`, not permanently deleted
- Audit trail is preserved for compliance
- Card won't appear in list queries
- Deleted card details can still be viewed by owner (for audit purposes)
- Audit event `CARD_REMOVED` is published to RabbitMQ

---

## HTTP Status Codes

| Code | Meaning | Common Cause |
|------|---------|-------------|
| 200 | OK | Successful GET/PUT request |
| 201 | Created | Card successfully created |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Validation error, max cards, duplicate |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Card doesn't exist |
| 409 | Conflict | Duplicate card detected |
| 422 | Unprocessable Entity | Invalid JSON/schema |
| 500 | Server Error | Internal error |

---

## Audit Events

All card operations trigger audit events published to RabbitMQ (`fraud.audit.events` queue):

**Event Structure:**
```json
{
  "action": "CARD_ADDED",
  "entity_type": "CARD",
  "entity_id": "card_550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123",
  "timestamp": "2026-01-28T10:30:00Z",
  "details": {
    "card_number_last_four": "0366",
    "card_type": "DEBIT",
    "nickname": "Main Card"
  }
}
```

**Event Types:**
- `CARD_ADDED` - User added new card
- `CARD_UPDATED` - User updated card nickname
- `CARD_REMOVED` - User deleted card

---

## Rate Limiting

Currently not enforced, but recommended for production:
- Add card: 5 requests per hour
- List cards: 60 requests per hour
- Get card: 100 requests per hour
- Update card: 10 requests per hour
- Delete card: 5 requests per hour

---

## Security Best Practices

1. **Card Number Masking**
   - API never returns full card number
   - Only last 4 digits exposed in UI
   - Full number used only in validation

2. **Authorization**
   - All endpoints check user ownership
   - User can only access own cards
   - No cross-user access possible

3. **Input Validation**
   - Server-side validation on all inputs
   - Card number not stored as-is
   - Expiry date validated for future dates

4. **Soft Delete**
   - Cards marked INACTIVE, not deleted
   - Audit trail preserved
   - Can be reviewed for compliance

5. **Audit Trail**
   - All operations logged to MongoDB
   - Events published to RabbitMQ
   - Timestamps in UTC

---

## Example Workflows

### Workflow 1: Add and List Cards

```bash
# 1. Add first card
curl -X POST http://localhost:8000/cards \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{
    "card_number": "4532015112830366",
    "card_holder_name": "John Doe",
    "expiry_date": "12/25",
    "card_type": "DEBIT",
    "nickname": "Main"
  }'

# Response: 201 Created with card details

# 2. Add second card
curl -X POST http://localhost:8000/cards \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{
    "card_number": "5425233010103442",
    "card_holder_name": "John Doe",
    "expiry_date": "03/27",
    "card_type": "CREDIT",
    "nickname": "Work"
  }'

# Response: 201 Created

# 3. List all cards
curl -X GET http://localhost:8000/cards \
  -H "X-User-ID: user_123"

# Response: 200 OK with array of 2 cards
```

### Workflow 2: View and Update Card

```bash
# 1. Get card details
curl -X GET http://localhost:8000/cards/card_550e8400-e29b-41d4-a716-446655440000 \
  -H "X-User-ID: user_123"

# Response: 200 OK with card details

# 2. Update nickname
curl -X PUT http://localhost:8000/cards/card_550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{"nickname": "Primary Card"}'

# Response: 200 OK with updated card
```

### Workflow 3: Delete Card

```bash
# 1. Delete card
curl -X DELETE http://localhost:8000/cards/card_550e8400-e29b-41d4-a716-446655440000 \
  -H "X-User-ID: user_123"

# Response: 204 No Content

# 2. Verify deleted (should return empty or 404)
curl -X GET http://localhost:8000/cards/card_550e8400-e29b-41d4-a716-446655440000 \
  -H "X-User-ID: user_123"

# Response: 404 Not Found
```

---

## Implementation Details

### Database Schema

**MongoDB Collection: `cards`**

```javascript
{
  _id: ObjectId("..."),
  card_id: UUID,
  user_id: String,
  card_number_hash: String,
  card_number_last_four: String,
  card_holder_name: String,
  expiry_date: String,
  card_type: String,
  nickname: String,
  status: String,
  created_at: Date,
  updated_at: Date,
  
  // Indexes
  card_id: { unique: true },
  user_id: { sparse: true },
  status: { sparse: true },
  created_at: { sparse: true }
}
```

### Cache (Redis)

Card list cached with 5-second TTL:
- Key: `user:{user_id}:cards`
- Cache invalidated on add/update/delete

---

## Testing

### Unit Tests
- 37 domain model tests
- 19 use case tests

### Integration Tests
- 13 MongoDB repository tests
- RabbitMQ event publishing tests

### API Tests
- 21 endpoint tests
- Error scenario coverage

### E2E Tests
- 11 Playwright tests
- Complete user workflows

Run tests:
```bash
# Backend unit + integration
pytest tests/unit/ tests/integration/ -v --cov=services

# Frontend E2E
cd tests-e2e && npm test
```

---

## Changelog

### Version 1.0 (2026-01-28)
- Initial release
- Add/List/Get/Update/Delete cards
- Soft-delete with audit trail
- Card number masking
- Duplicate detection
- Max 10 cards per user
- Event publishing to RabbitMQ
