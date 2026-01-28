---
goal: Implement Card Viewing and Transaction Management (HU-016 MVP)
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
owner: Development Team
status: 'Planned'
tags: [feature, card-view, transactions, mvp, backend, frontend]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan covers the **MVP development** of HU-016: View and Manage Multiple Cards. The feature enables bank customers to view their linked cards, see card-specific transaction history, and submit new transactions using a selected card.

**Key Deliverables (MVP Scope):**
- View all user cards (simple list, no pagination)
- Display card details with masked numbers
- Submit transactions from specific card
- View transaction history per card (basic list)
- Basic card status display (active/inactive)
- Integration with existing fraud detection system

**Deferred to Post-MVP:**
- Advanced filtering (date range, amount, status)
- Pagination for cards and transactions
- Real-time balance updates via WebSocket
- Card blocking/unblocking functionality
- Transaction cancellation

**TDD Approach:** All implementation follows RED-GREEN-REFACTOR cycle with approval gates between phases.

## 1. Requirements & Constraints

### Functional Requirements

- **REQ-001**: Users must authenticate before accessing card views
- **REQ-002**: Display all user cards in a simple list (no pagination in MVP)
- **REQ-003**: Each card shows: masked number (last 4), holder name, type, status, balance
- **REQ-004**: Users can view transaction history filtered by card_id
- **REQ-005**: Users can submit transactions from a specific card
- **REQ-006**: Transaction submission validates card balance before submission
- **REQ-007**: Transaction integrates with existing fraud detection queue (202 Accepted)
- **REQ-008**: Card-specific transactions are isolated (query by card_id)

### Security Requirements (MVP)

- **SEC-001**: Card numbers displayed as masked (XXXX-XXXX-XXXX-1234)
- **SEC-002**: Transaction submission requires user authentication
- **SEC-003**: Users can only view/transact with their own cards
- **SEC-004**: Transaction amounts validated server-side (cannot exceed balance)

### Data Requirements

- **DAT-001**: Card schema includes: card_id, user_id, last_four, holder_name, card_type, status, current_balance
- **DAT-002**: Transaction schema includes: transaction_id, card_id, user_id, amount, recipient_id, description, timestamp, status
- **DAT-003**: Card status: ACTIVE, INACTIVE (blocking deferred to post-MVP)
- **DAT-004**: Transaction status: PENDING, COMPLETED, FAILED

### Technical Constraints

- **CON-001**: Must use existing MongoDB for data persistence
- **CON-002**: Must integrate with existing fraud detection API (POST /api/v1/transactions)
- **CON-003**: Must use FastAPI for backend endpoints
- **CON-004**: Must use React + TypeScript for frontend
- **CON-005**: Must maintain Clean Architecture compliance
- **CON-006**: Test coverage must remain ≥70%

### Architectural Guidelines

- **GUD-001**: Follow hexagonal architecture pattern
- **GUD-002**: Use Repository Pattern for data access
- **GUD-003**: Implement Dependency Injection for testability
- **GUD-004**: Domain models independent of frameworks

### MVP Patterns

- **PAT-001**: Simple list rendering (no pagination, lazy loading)
- **PAT-002**: Basic form validation (required fields, numeric amounts)
- **PAT-003**: Async transaction submission (202 Accepted, fraud queue integration)

## 2. Implementation Steps

### Phase 1: Domain Layer - Card View Models (RED → GREEN → REFACTOR)

**GOAL-001**: Create domain models for card viewing and transactions

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | **[RED]** Write failing tests for CardView entity (read-only card representation) | | |
| TASK-002 | **[RED]** Write failing tests for TransactionSubmission value object | | |
| TASK-003 | **[RED]** Write failing tests for balance validation logic | | |
| TASK-004 | **[RED]** Write failing tests for card masking utility | | |
| TASK-005 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-006 | **[GREEN]** Implement CardView entity (frozen dataclass) | | |
| TASK-007 | **[GREEN]** Implement TransactionSubmission value object | | |
| TASK-008 | **[GREEN]** Implement balance validator (amount <= balance) | | |
| TASK-009 | **[GREEN]** Implement card number masking function | | |
| TASK-010 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-011 | **[REFACTOR]** Add comprehensive docstrings | | |
| TASK-012 | **[REFACTOR]** Extract validation into separate module | | |
| TASK-013 | **[REFACTOR]** Add error messages for validation failures | | |
| TASK-014 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/fraud-evaluation-service/src/domain/models/card_view.py` - CardView entity
- `services/fraud-evaluation-service/src/domain/models/transaction_submission.py` - Transaction VO
- `services/fraud-evaluation-service/src/domain/validation/balance_validator.py` - Balance checks
- `services/fraud-evaluation-service/src/domain/utils/card_masking.py` - Masking utility
- `tests/unit/test_domain_card_view.py` - Domain tests (8+ tests)

---

### Phase 2: Application Layer - Card & Transaction Use Cases (RED → GREEN → REFACTOR)

**GOAL-002**: Implement use cases for viewing cards and submitting transactions

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-015 | **[RED]** Write failing tests for GetUserCardsUseCase | | |
| TASK-016 | **[RED]** Write failing tests for GetCardTransactionsUseCase | | |
| TASK-017 | **[RED]** Write failing tests for SubmitTransactionUseCase (with balance check) | | |
| TASK-018 | **[RED]** Write failing tests for authorization (user owns card) | | |
| TASK-019 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-020 | **[GREEN]** Define CardRepository port (find_by_user_id, find_by_id) | | |
| TASK-021 | **[GREEN]** Define TransactionRepository port (find_by_card_id, create) | | |
| TASK-022 | **[GREEN]** Implement GetUserCardsUseCase | | |
| TASK-023 | **[GREEN]** Implement GetCardTransactionsUseCase | | |
| TASK-024 | **[GREEN]** Implement SubmitTransactionUseCase (balance validation + fraud queue) | | |
| TASK-025 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-026 | **[REFACTOR]** Add detailed error messages | | |
| TASK-027 | **[REFACTOR]** Add docstrings with usage examples | | |
| TASK-028 | **[REFACTOR]** Extract authorization check into separate method | | |
| TASK-029 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/fraud-evaluation-service/src/application/use_cases/get_user_cards.py` - Get cards
- `services/fraud-evaluation-service/src/application/use_cases/get_card_transactions.py` - Get transactions
- `services/fraud-evaluation-service/src/application/use_cases/submit_transaction.py` - Submit transaction
- `tests/unit/test_use_cases_card_view.py` - Use case tests (12+ tests)

---

### Phase 3: Infrastructure Layer - Adapters (RED → GREEN → REFACTOR)

**GOAL-003**: Implement MongoDB adapters and fraud queue integration

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-030 | **[RED]** Write failing integration tests for MongoCardRepository (read operations) | | |
| TASK-031 | **[RED]** Write failing integration tests for MongoTransactionRepository | | |
| TASK-032 | **[RED]** Write failing tests for FraudQueuePublisher (RabbitMQ integration) | | |
| TASK-033 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-034 | **[GREEN]** Implement MongoCardRepository (find_by_user_id, find_by_id) | | |
| TASK-035 | **[GREEN]** Implement MongoTransactionRepository (find_by_card_id, create) | | |
| TASK-036 | **[GREEN]** Implement FraudQueuePublisher (publish to fraud.queue) | | |
| TASK-037 | **[GREEN]** Add MongoDB indexes: card_id, user_id, created_at | | |
| TASK-038 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-039 | **[REFACTOR]** Add connection error handling | | |
| TASK-040 | **[REFACTOR]** Add query optimization | | |
| TASK-041 | **[REFACTOR]** Add logging (mask sensitive data) | | |
| TASK-042 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/fraud-evaluation-service/src/infrastructure/adapters/mongo_transaction_repository.py` - Transaction adapter
- `services/fraud-evaluation-service/src/infrastructure/adapters/fraud_queue_publisher.py` - RabbitMQ publisher
- `tests/integration/test_transaction_repository.py` - Integration tests (6+ tests)

---

### Phase 4: API Gateway - REST Endpoints (RED → GREEN → REFACTOR)

**GOAL-004**: Create FastAPI endpoints for card viewing and transactions

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-043 | **[RED]** Write failing API tests for GET /api/v1/cards (user cards) | | |
| TASK-044 | **[RED]** Write failing API tests for GET /api/v1/cards/{id}/transactions | | |
| TASK-045 | **[RED]** Write failing API tests for POST /api/v1/transactions (from card) | | |
| TASK-046 | **[RED]** Write failing tests for insufficient balance error (400) | | |
| TASK-047 | **[RED]** Write failing tests for unauthorized access (403) | | |
| TASK-048 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-049 | **[GREEN]** Create Pydantic schemas: CardViewResponse, TransactionListResponse, TransactionSubmitRequest | | |
| TASK-050 | **[GREEN]** Implement GET /api/v1/cards endpoint | | |
| TASK-051 | **[GREEN]** Implement GET /api/v1/cards/{id}/transactions endpoint | | |
| TASK-052 | **[GREEN]** Implement POST /api/v1/transactions endpoint (202 Accepted) | | |
| TASK-053 | **[GREEN]** Add authentication dependency | | |
| TASK-054 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-055 | **[REFACTOR]** Add OpenAPI documentation | | |
| TASK-056 | **[REFACTOR]** Add request/response examples | | |
| TASK-057 | **[REFACTOR]** Add proper HTTP status codes (200, 202, 400, 403) | | |
| TASK-058 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/api-gateway/src/routes/card_views.py` - Card viewing endpoints
- `services/api-gateway/src/routes/transactions.py` [MODIFIED] - Add card-based transaction
- `services/api-gateway/src/schemas/card_view_schemas.py` - Pydantic models
- `tests/integration/test_api_card_views.py` - API tests (10+ tests)

---

### Phase 5: Frontend - Card List & Transaction UI (RED → GREEN → REFACTOR)

**GOAL-005**: Build React components for card viewing and transaction submission

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-059 | **[RED]** Write failing Vitest tests for CardListView component | | |
| TASK-060 | **[RED]** Write failing tests for CardDetailsView component | | |
| TASK-061 | **[RED]** Write failing tests for TransactionHistoryList component | | |
| TASK-062 | **[RED]** Write failing tests for TransactionForm component | | |
| TASK-063 | **[RED]** Write failing tests for balance validation in form | | |
| TASK-064 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-065 | **[GREEN]** Create CardListView (fetch and display cards) | | |
| TASK-066 | **[GREEN]** Create CardDetailsView (single card with masked number) | | |
| TASK-067 | **[GREEN]** Create TransactionHistoryList (simple list, no filters) | | |
| TASK-068 | **[GREEN]** Create TransactionForm (amount, recipient, description) | | |
| TASK-069 | **[GREEN]** Implement cardViewService API client | | |
| TASK-070 | **[GREEN]** Add Cards view page route | | |
| TASK-071 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-072 | **[REFACTOR]** Add form validation feedback | | |
| TASK-073 | **[REFACTOR]** Add loading states | | |
| TASK-074 | **[REFACTOR]** Add success/error notifications | | |
| TASK-075 | **[REFACTOR]** Add empty state for no cards/transactions | | |
| TASK-076 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `frontend/user-app/src/pages/CardsView.tsx` - Cards overview page
- `frontend/user-app/src/components/cards/CardListView.tsx` - Card list
- `frontend/user-app/src/components/cards/CardDetailsView.tsx` - Card detail card
- `frontend/user-app/src/components/transactions/TransactionHistoryList.tsx` - Transaction list
- `frontend/user-app/src/components/transactions/TransactionForm.tsx` - Submit transaction form
- `frontend/user-app/src/services/cardViewService.ts` - API client
- `frontend/user-app/src/components/cards/__tests__/` - Component tests (10+ tests)

---

### Phase 6: E2E Tests (RED → GREEN → REFACTOR)

**GOAL-006**: Create end-to-end tests for complete user flows

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-077 | **[RED]** Write failing E2E test for viewing cards list | | |
| TASK-078 | **[RED]** Write failing E2E test for viewing card transactions | | |
| TASK-079 | **[RED]** Write failing E2E test for submitting transaction from card | | |
| TASK-080 | **[RED]** Write failing E2E test for insufficient balance error | | |
| TASK-081 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-082 | **[GREEN]** Implement E2E test for view cards flow | | |
| TASK-083 | **[GREEN]** Implement E2E test for view transactions flow | | |
| TASK-084 | **[GREEN]** Implement E2E test for submit transaction flow | | |
| TASK-085 | **[GREEN]** Implement E2E test for balance validation | | |
| TASK-086 | **[GREEN]** Add test fixtures for cards and transactions | | |
| TASK-087 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-088 | **[REFACTOR]** Extract Page Object Models | | |
| TASK-089 | **[REFACTOR]** Add reusable task helpers | | |
| TASK-090 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `tests-e2e/tests/card-view.spec.ts` - E2E test suite
- `tests-e2e/pages/CardViewPage.ts` - Page Object Model
- `tests-e2e/tasks/transactionTasks.ts` - Reusable operations
- `tests-e2e/fixtures/cardViewData.json` - Test data

---

### Phase 7: Documentation & Integration

**GOAL-007**: Complete documentation and final integration

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-091 | Update API documentation (Swagger) | | |
| TASK-092 | Create user guide for card viewing and transactions | | |
| TASK-093 | Update README.md with HU-016 features | | |
| TASK-094 | Final integration test - full flow UI to DB | | |

**Files Created:**
- `docs/CARD_VIEW_TRANSACTIONS.md` - Feature documentation

---

## 3. Alternatives

### Alternative Approaches Considered

- **ALT-001**: **Implement pagination in MVP** - Deferred to post-MVP for simplicity. Most users have <10 cards, so full list is acceptable.

- **ALT-002**: **Real-time balance updates** - Deferred to post-MVP. Simple page refresh is sufficient for MVP.

- **ALT-003**: **Advanced transaction filtering** - Deferred to post-MVP. Basic chronological list meets core needs.

- **ALT-004**: **Card blocking UI** - Deferred to post-MVP. Status display only for now.

## 4. Dependencies

### External Dependencies (MVP)

- **DEP-001**: None - uses existing infrastructure

### Internal Dependencies

- **DEP-002**: **HU-015 Card Management** - Cards must exist before viewing
- **DEP-003**: **HU-001 Transaction API** - Transaction submission uses existing fraud detection
- **DEP-004**: **HU-002 Audit Trail** - Transaction history relies on audit logs
- **DEP-005**: **Authentication System** - User identification required

### Library Dependencies

- **DEP-006**: None - use existing frontend/backend libraries

## 5. Files

### Backend Files (New/Modified)

**Domain Layer**
- **FILE-001**: `services/fraud-evaluation-service/src/domain/models/card_view.py` - CardView entity
- **FILE-002**: `services/fraud-evaluation-service/src/domain/models/transaction_submission.py` - Transaction VO
- **FILE-003**: `services/fraud-evaluation-service/src/domain/validation/balance_validator.py` - Balance validation
- **FILE-004**: `services/fraud-evaluation-service/src/domain/utils/card_masking.py` - Card masking utility

**Application Layer**
- **FILE-005**: `services/fraud-evaluation-service/src/application/use_cases/get_user_cards.py` - Get cards use case
- **FILE-006**: `services/fraud-evaluation-service/src/application/use_cases/get_card_transactions.py` - Get transactions
- **FILE-007**: `services/fraud-evaluation-service/src/application/use_cases/submit_transaction.py` - Submit transaction

**Infrastructure Layer**
- **FILE-008**: `services/fraud-evaluation-service/src/infrastructure/adapters/mongo_transaction_repository.py` - Transaction repo
- **FILE-009**: `services/fraud-evaluation-service/src/infrastructure/adapters/fraud_queue_publisher.py` - RabbitMQ publisher

**API Gateway**
- **FILE-010**: `services/api-gateway/src/routes/card_views.py` - Card view endpoints
- **FILE-011**: `services/api-gateway/src/routes/transactions.py` [MODIFIED] - Add card-based transaction endpoint
- **FILE-012**: `services/api-gateway/src/schemas/card_view_schemas.py` - Pydantic schemas

### Frontend Files (New/Modified)

**React Components**
- **FILE-013**: `frontend/user-app/src/pages/CardsView.tsx` - Main cards view page
- **FILE-014**: `frontend/user-app/src/components/cards/CardListView.tsx` - Card list component
- **FILE-015**: `frontend/user-app/src/components/cards/CardDetailsView.tsx` - Card detail component
- **FILE-016**: `frontend/user-app/src/components/transactions/TransactionHistoryList.tsx` - Transaction list
- **FILE-017**: `frontend/user-app/src/components/transactions/TransactionForm.tsx` - Transaction form
- **FILE-018**: `frontend/user-app/src/services/cardViewService.ts` - API client

### Test Files (New)

**Backend Tests**
- **FILE-019**: `tests/unit/test_domain_card_view.py` - Domain tests (8+ tests)
- **FILE-020**: `tests/unit/test_use_cases_card_view.py` - Use case tests (12+ tests)
- **FILE-021**: `tests/integration/test_transaction_repository.py` - Integration tests (6+ tests)
- **FILE-022**: `tests/integration/test_api_card_views.py` - API tests (10+ tests)

**Frontend Tests**
- **FILE-023**: `frontend/user-app/src/components/cards/__tests__/CardListView.test.tsx`
- **FILE-024**: `frontend/user-app/src/components/transactions/__tests__/TransactionForm.test.tsx`

**E2E Tests**
- **FILE-025**: `tests-e2e/tests/card-view.spec.ts` - E2E tests
- **FILE-026**: `tests-e2e/pages/CardViewPage.ts` - Page Object Model
- **FILE-027**: `tests-e2e/fixtures/cardViewData.json` - Test data

### Documentation

- **FILE-028**: `docs/CARD_VIEW_TRANSACTIONS.md` - Feature documentation

## 6. Testing

### Unit Tests (Backend)

**Domain Layer Tests** (tests/unit/test_domain_card_view.py)
- **TEST-001**: CardView entity creation with valid data
- **TEST-002**: CardView is immutable (frozen dataclass)
- **TEST-003**: Card number masking shows only last 4 digits
- **TEST-004**: Card number masking format: XXXX-XXXX-XXXX-1234
- **TEST-005**: Balance validator accepts valid amount
- **TEST-006**: Balance validator rejects amount > balance
- **TEST-007**: Balance validator rejects negative amounts
- **TEST-008**: TransactionSubmission value object validates required fields

**Application Layer Tests** (tests/unit/test_use_cases_card_view.py)
- **TEST-009**: GetUserCardsUseCase returns all user cards
- **TEST-010**: GetUserCardsUseCase returns empty list for user with no cards
- **TEST-011**: GetUserCardsUseCase masks card numbers in response
- **TEST-012**: GetCardTransactionsUseCase returns card-specific transactions
- **TEST-013**: GetCardTransactionsUseCase filters by card_id correctly
- **TEST-014**: GetCardTransactionsUseCase validates user owns card (403 if not)
- **TEST-015**: SubmitTransactionUseCase creates transaction with valid data
- **TEST-016**: SubmitTransactionUseCase validates balance before submission
- **TEST-017**: SubmitTransactionUseCase returns 400 for insufficient balance
- **TEST-018**: SubmitTransactionUseCase publishes to fraud queue
- **TEST-019**: SubmitTransactionUseCase returns 202 Accepted with transaction_id
- **TEST-020**: SubmitTransactionUseCase validates user owns source card

### Integration Tests (Backend)

**Repository Tests** (tests/integration/test_transaction_repository.py)
- **TEST-021**: MongoTransactionRepository finds transactions by card_id
- **TEST-022**: MongoTransactionRepository creates transaction record
- **TEST-023**: MongoTransactionRepository sorts by timestamp DESC
- **TEST-024**: FraudQueuePublisher publishes message to fraud.queue
- **TEST-025**: FraudQueuePublisher includes all required fields
- **TEST-026**: MongoCardRepository finds cards by user_id

**API Tests** (tests/integration/test_api_card_views.py)
- **TEST-027**: GET /api/v1/cards returns user cards with masked numbers
- **TEST-028**: GET /api/v1/cards returns 200 with empty array for new user
- **TEST-029**: GET /api/v1/cards/{id}/transactions returns card transactions
- **TEST-030**: GET /api/v1/cards/{id}/transactions returns 403 if user doesn't own card
- **TEST-031**: POST /api/v1/transactions returns 202 Accepted
- **TEST-032**: POST /api/v1/transactions returns 400 for insufficient balance
- **TEST-033**: POST /api/v1/transactions returns 403 if user doesn't own card
- **TEST-034**: POST /api/v1/transactions validates required fields
- **TEST-035**: POST /api/v1/transactions returns transaction_id in response
- **TEST-036**: API masks card numbers in all responses

### Frontend Tests (Vitest)

**Component Tests**
- **TEST-037**: CardListView renders list of cards
- **TEST-038**: CardListView displays masked card numbers
- **TEST-039**: CardListView shows card type and balance
- **TEST-040**: CardDetailsView renders card information
- **TEST-041**: TransactionHistoryList renders transactions
- **TEST-042**: TransactionHistoryList shows empty state for no transactions
- **TEST-043**: TransactionForm renders all input fields
- **TEST-044**: TransactionForm validates amount > 0
- **TEST-045**: TransactionForm validates amount <= balance
- **TEST-046**: TransactionForm shows error for insufficient balance
- **TEST-047**: TransactionForm submits valid data
- **TEST-048**: TransactionForm disables submit during API call

### E2E Tests (Playwright)

**User Workflows**
- **TEST-049**: User can view their cards list
- **TEST-050**: User sees masked card numbers
- **TEST-051**: User can view transactions for specific card
- **TEST-052**: User can submit transaction from card
- **TEST-053**: User sees error for insufficient balance
- **TEST-054**: User receives 202 Accepted response after submission

### Test Coverage Goals (MVP)

- **Minimum Overall Coverage**: 70% (enforced)
- **Target Coverage**: 80% (MVP reduced from 95%)
- **Critical Path Coverage**: 100% (transaction submission, balance validation)
- **Domain Layer Coverage**: 100%

## 7. Risks & Assumptions

### Technical Risks (MVP)

- **RISK-001**: **Transaction Consistency Without Locking**
  - *Impact*: Medium - Concurrent transactions might exceed balance
  - *Mitigation*: Validate balance at fraud evaluation time, implement optimistic locking post-MVP

- **RISK-002**: **Card Balance Sync Issues**
  - *Impact*: Low - Balance might be stale
  - *Mitigation*: Accept eventual consistency for MVP, add real-time updates post-MVP

- **RISK-003**: **Performance with Many Transactions**
  - *Impact*: Low - Slow queries for cards with hundreds of transactions
  - *Mitigation*: Add MongoDB indexes, implement pagination post-MVP

### Business Risks (MVP)

- **RISK-004**: **User Experience Without Filtering**
  - *Impact*: Medium - Hard to find specific transactions
  - *Mitigation*: Acceptable for MVP, add filters in post-MVP

- **RISK-005**: **No Transaction Cancellation**
  - *Impact*: Low - Users cannot cancel pending transactions
  - *Mitigation*: Deferred to post-MVP, most transactions complete quickly

### Assumptions (MVP)

- **ASSUMPTION-001**: Users have <50 transactions per card (no pagination needed)
- **ASSUMPTION-002**: Card balances are updated by external system (not managed here)
- **ASSUMPTION-003**: Fraud evaluation system is already functional (HU-001)
- **ASSUMPTION-004**: Users trust eventual consistency for balance updates
- **ASSUMPTION-005**: No concurrent transaction limit enforcement (post-MVP)

## 8. Related Specifications / Further Reading

### Internal Documentation

- [HU-016: View and Manage Multiple Cards](../docs/user-stories/HU-016-view-manage-multiple-cards.md) - Original user story
- [HU-015: Add and Link Cards](../docs/user-stories/HU-015-add-cards-to-account.md) - Card management dependency
- [HU-001: Receive Transactions API](../docs/user-stories/HU-001-receive-transactions-api.md) - Transaction submission
- [HU-002: Immutable Audit Trail](../docs/user-stories/HU-002-immutable-audit-trail.md) - Transaction history
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture
- [CONTEXT.md](../docs/CONTEXT.md) - Development setup and TDD workflow

---

**Implementation Plan Version**: 1.0 (MVP Scope)  
**Last Updated**: 2026-01-28  
**Estimated Effort**: 8 Story Points (~2 sprints for 2-person team)  
**Prerequisites**: HU-015 (cards exist), HU-001 (fraud API), Authentication system

**MVP Scope Summary:**
- ✅ View all user cards (simple list)
- ✅ View card-specific transactions (basic list)
- ✅ Submit transaction from card (with balance check)
- ✅ Card number masking
- ✅ Integration with fraud detection queue
- ❌ Pagination (post-MVP)
- ❌ Advanced filtering (post-MVP)
- ❌ Real-time balance updates (post-MVP)
- ❌ Card blocking/unblocking (post-MVP)

**Total Tasks**: 94

**Next Steps**:
1. Review simplified MVP plan
2. Confirm integration points with HU-015
3. Begin Phase 1 (Domain Layer) with RED tests
4. Schedule approval gate meetings
