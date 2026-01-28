---
goal: Implement HU-015 - View and Manage Multiple Cards with Full-Stack Integration
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
owner: Development Team
status: 'Planned'
tags: ['feature', 'cards', 'user-app', 'api', 'database']
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan enables bank customers to view up to 3 active cards with details (number, balance, expiry, status) and perform key actions (view transactions, transfer money, block card) from the user app dashboard. The feature follows Clean Architecture principles, implements TDD/BDD practices with 95%+ test coverage, and integrates with existing fraud detection and transaction processing systems.

## 1. Requirements & Constraints

### Functional Requirements
- **REQ-001**: Display up to 3 active cards on user dashboard (Inicio page)
- **REQ-002**: Show card details: masked number (XXXX-XXXX-XXXX-1234), cardholder name, balance, expiry date, status, type
- **REQ-003**: Implement 4 card action buttons: View Transactions, Transfer Money, Block Card, Card Details
- **REQ-004**: Display visual indicators for blocked cards (red badge, dimmed appearance, disabled transfer button)
- **REQ-005**: Modal/page to view card transactions sorted by date (most recent first)
- **REQ-006**: Transfer form with fields: source_card (pre-filled), amount, user_id, location, device_id, transaction_id, description
- **REQ-007**: Prevent transfers from blocked cards with tooltip message
- **REQ-008**: Pagination/View All link for accounts with >3 cards
- **REQ-009**: Empty state message "No cards found" with "Request a Card" button for no cards
- **REQ-010**: Return HTTP 403 Forbidden for users without card viewing permissions
- **REQ-011**: Handle insufficient balance error with available_balance in response

### Non-Functional Requirements
- **PER-001**: Card data loads within 2 seconds
- **ACC-001**: All buttons and text meet WCAG 2.1 AA accessibility standards
- **RES-001**: Responsive layout adapts to mobile (1 card), tablet (2 cards), desktop (3 cards)
- **SEC-001**: Card numbers masked (XXXX-XXXX-XXXX-1234), no full numbers in logs
- **INT-001**: Support multiple currencies and languages

### Constraints
- **CON-001**: Maximum 3 cards displayed by default
- **CON-002**: Card data cached in Redis for 5 minutes (TTL: 300s)
- **CON-003**: Must use existing fraud evaluation service for transfer validation
- **CON-004**: Transfer amounts must pass fraud detection before execution
- **CON-005**: All card operations logged to audit trail (MongoDB)

### Architecture Patterns
- **PAT-001**: Follow Clean Architecture (domain/application/infrastructure separation)
- **PAT-002**: Implement Repository Pattern for card data access
- **PAT-003**: Use Zustand for React state management (existing pattern)
- **PAT-004**: Use axios interceptors for API authentication
- **PAT-005**: E2E tests must use Playwright role-based locators (getByRole, getByLabel)

### Testing Standards
- **TST-001**: All domain logic tested in `tests/unit/` (pytest)
- **TST-002**: Backend API endpoints tested in `tests/integration/` (pytest)
- **TST-003**: Frontend components tested in `frontend/user-app/src/__tests__/` (Vitest)
- **TST-004**: E2E user workflows tested in `tests-e2e/tests/` (Playwright)
- **TST-005**: Minimum code coverage: 70%, target: 95%
- **TST-006**: All tests must pass locally before PR submission

## 2. Implementation Steps

### Phase 1: Backend Domain & Infrastructure Layer

**GOAL-001**: Implement card data models, repository interfaces, and MongoDB adapters for persistent card storage and retrieval.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create Card domain entity with immutable dataclass | | |
| TASK-002 | Create CardStatus enum (ACTIVE, BLOCKED, EXPIRED, PENDING) | | |
| TASK-003 | Create TransferRequest domain model with validation | | |
| TASK-004 | Create CardRepository abstract interface in application/ports/ | | |
| TASK-005 | Implement MongoDBCardAdapter in infrastructure/ | | |
| TASK-006 | Create Redis card cache adapter with TTL=300s | | |
| TASK-007 | Add card collections to MongoDB init script | | |
| TASK-008 | Write unit tests for Card models (95% coverage) | | |
| TASK-009 | Write integration tests for CardRepository implementations | | |

**Phase 1 Completion Criteria**:
- ✅ Card models immutable and serializable
- ✅ Repository interface defined with methods: get_user_cards(user_id, limit=3), get_card_by_id(card_id), update_card_status(card_id, status)
- ✅ MongoDB adapter implements repository with queries in <100ms
- ✅ Redis adapter returns cached cards or fetches from MongoDB on miss
- ✅ All unit/integration tests passing with 95%+ coverage
- ✅ No framework imports in domain layer

---

### Phase 2: Backend Application Layer & Use Cases

**GOAL-002**: Implement use cases that orchestrate card retrieval, transfer validation, and blocking operations.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Create GetUserCardsUseCase (query, limit enforcement, permission check) | | |
| TASK-011 | Create GetCardDetailUseCase with full transaction history | | |
| TASK-012 | Create TransferMoneyUseCase with fraud evaluation integration | | |
| TASK-013 | Create BlockCardUseCase with status update | | |
| TASK-014 | Create GetCardTransactionsUseCase with pagination | | |
| TASK-015 | Implement permission checking (403 Forbidden for unauthorized users) | | |
| TASK-016 | Implement balance validation (error if insufficient funds) | | |
| TASK-017 | Add EventPublisher dependency for card events (CARD_BLOCKED, TRANSFER_INITIATED) | | |
| TASK-018 | Write comprehensive use case tests with mocked repositories | | |

**Phase 2 Completion Criteria**:
- ✅ All use cases follow dependency injection pattern
- ✅ GetUserCardsUseCase enforces limit=3 and permission checks
- ✅ TransferMoneyUseCase calls fraud evaluation service and validates balance
- ✅ All use cases publish events to RabbitMQ for audit trail
- ✅ Error handling returns proper status codes (403, 400, 422)
- ✅ 95%+ test coverage with mocked dependencies

---

### Phase 3: Backend FastAPI Routes & Validation

**GOAL-003**: Create REST API endpoints with Pydantic validation, authentication, and error handling.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-019 | Create CardResponse Pydantic model (masked number, balance, expiry, status) | | |
| TASK-020 | Create TransferRequest Pydantic model with validation rules | | |
| TASK-021 | Add GET /api/v1/cards endpoint with limit query param | | |
| TASK-022 | Add GET /api/v1/cards/{card_id} endpoint | | |
| TASK-023 | Add GET /api/v1/cards/{card_id}/transactions endpoint with pagination | | |
| TASK-024 | Add POST /api/v1/transfers endpoint (triggers fraud evaluation) | | |
| TASK-025 | Add PUT /api/v1/cards/{card_id}/block endpoint | | |
| TASK-026 | Add authentication middleware (verify JWT token, extract user_id) | | |
| TASK-027 | Add error handlers for 403 Forbidden, 400 Bad Request, 422 Unprocessable Entity | | |
| TASK-028 | Write route integration tests with test client | | |

**Phase 3 Completion Criteria**:
- ✅ All endpoints return 202 Accepted for async operations (transfers)
- ✅ All endpoints return 200 OK for sync operations (get cards)
- ✅ Card numbers masked in responses (XXXX-XXXX-XXXX-1234)
- ✅ Authentication required for all endpoints (401 if missing token)
- ✅ Proper HTTP status codes: 200, 202, 400, 403, 422, 500
- ✅ Swagger UI docs auto-generated and correct
- ✅ Integration tests verify full request/response cycle

---

### Phase 4: Frontend Components & Pages

**GOAL-004**: Build React components for card display, transfer form, transaction history, and responsive layouts.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-029 | Create CardCard component (displays single card with details) | | |
| TASK-030 | Create CardStatus badge component (ACTIVE green, BLOCKED red) | | |
| TASK-031 | Create CardActions component (4 action buttons: View Txns, Transfer, Block, Details) | | |
| TASK-032 | Create CardsList component (displays up to 3 cards, handles empty state) | | |
| TASK-033 | Create TransactionHistory component (modal/page with transaction list) | | |
| TASK-034 | Create TransferForm component (7 input fields, validation, submit) | | |
| TASK-035 | Create TransferConfirmation component (success message with details) | | |
| TASK-036 | Create CardsPage component (main Inicio page with cards list) | | |
| TASK-037 | Implement loading states (skeleton loaders or spinners) | | |
| TASK-038 | Implement error boundaries and error messages | | |
| TASK-039 | Implement responsive CSS (Tailwind: mobile 1 card, tablet 2 cards, desktop 3) | | |
| TASK-040 | Add accessibility attributes (aria-labels, aria-roles) | | |

**Phase 4 Completion Criteria**:
- ✅ All components use React.FC with TypeScript types
- ✅ All components styled with Tailwind CSS (no inline styles)
- ✅ Loading states display while fetching (2s target)
- ✅ Responsive layout tested on mobile/tablet/desktop
- ✅ Error messages display with retry button
- ✅ Card numbers masked in all components
- ✅ All ARIA attributes present and correct

---

### Phase 5: Frontend State Management & API Integration

**GOAL-005**: Implement Zustand store for card data, fetch from API, handle errors, and update UI.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-041 | Create cardStore.ts with Zustand (state: cards, loading, error, transfers) | | |
| TASK-042 | Implement fetchUserCards action (calls GET /api/v1/cards with limit=3) | | |
| TASK-043 | Implement fetchCardTransactions action (calls GET /api/v1/cards/{card_id}/transactions) | | |
| TASK-044 | Implement transferMoney action (POST /api/v1/transfers, polls for fraud evaluation) | | |
| TASK-045 | Implement blockCard action (PUT /api/v1/cards/{card_id}/block) | | |
| TASK-046 | Add error handling middleware (retry on network errors, display messages) | | |
| TASK-047 | Add axios interceptor for authentication header injection | | |
| TASK-048 | Implement polling for transfer status (check fraud evaluation result) | | |
| TASK-049 | Create custom hooks: useCards(), useCardTransactions(), useTransfer() | | |
| TASK-050 | Write Vitest unit tests for store actions and selectors | | |

**Phase 5 Completion Criteria**:
- ✅ Zustand store centralized, no prop drilling
- ✅ All API calls include Authorization header
- ✅ Error states display user-friendly messages
- ✅ Loading states show spinners (max 2s)
- ✅ Polling for transfer result works (max 10s, check every 1s)
- ✅ Store mutations are immutable (no direct state modification)
- ✅ 85%+ test coverage for store actions

---

### Phase 6: Frontend Forms & Validation

**GOAL-006**: Implement form validation, submission handling, and error feedback for transfer and card management.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-051 | Create TransferForm with React Hook Form validation | | |
| TASK-052 | Implement 7 form fields with required/optional rules | | |
| TASK-053 | Add real-time validation feedback (error messages under fields) | | |
| TASK-054 | Disable submit button until all required fields valid | | |
| TASK-055 | Add error handling for insufficient balance (display available_balance) | | |
| TASK-056 | Add error handling for blocked card (disable transfer button, show tooltip) | | |
| TASK-057 | Implement form submission with fraud evaluation API call | | |
| TASK-058 | Show confirmation modal with transfer details + success message | | |
| TASK-059 | Add back navigation to return to cards list | | |
| TASK-060 | Write Vitest tests for form validation and submission | | |

**Phase 6 Completion Criteria**:
- ✅ Form validates all required fields before submit
- ✅ Form shows inline error messages (red text under inputs)
- ✅ Submit button disabled while loading
- ✅ Success confirmation shows Monto, Usuario, Estado, Risk Score
- ✅ Error message for insufficient balance includes available amount
- ✅ Blocked card shows disabled transfer button with tooltip
- ✅ Form clears after successful submission

---

### Phase 7: Database Initialization & Migrations

**GOAL-007**: Set up MongoDB collections for cards, transactions, and audit logs.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-061 | Create MongoDB migration script (init-db.js or Python equivalent) | | |
| TASK-062 | Create collections: cards, card_transactions, card_audits | | |
| TASK-063 | Define indexes: cards(user_id), card_transactions(card_id, timestamp), card_audits(card_id) | | |
| TASK-064 | Insert sample data: 5 test users with 1-3 cards each | | |
| TASK-065 | Verify indexes are created (use db.collection.getIndexes()) | | |

**Phase 7 Completion Criteria**:
- ✅ Collections created with proper schema validation
- ✅ Indexes created for fast queries (<100ms)
- ✅ Sample data inserted for testing
- ✅ Migration script idempotent (safe to run multiple times)

---

### Phase 8: E2E Testing with Playwright

**GOAL-008**: Write full user workflow tests verifying card display, transactions, transfers, and error scenarios.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-066 | Create tests-e2e/tests/cards.spec.ts file | | |
| TASK-067 | Test: View cards on dashboard (3 cards display with details) | | |
| TASK-068 | Test: Card with blocked status shows red badge + disabled transfer | | |
| TASK-069 | Test: Click View Transactions opens modal with sorted transactions | | |
| TASK-070 | Test: Click Transfer Money opens transfer form | | |
| TASK-071 | Test: Complete transfer with valid data shows confirmation | | |
| TASK-072 | Test: Cannot transfer from blocked card (button disabled) | | |
| TASK-073 | Test: More than 3 cards shows pagination/View All link | | |
| TASK-074 | Test: No cards shows "No cards found" with request button | | |
| TASK-075 | Test: Insufficient balance shows error message with available amount | | |
| TASK-076 | Test: Load time <2 seconds (measure with navigation.timing) | | |
| TASK-077 | Test: Responsive layout (mobile 1 card, tablet 2, desktop 3) | | |
| TASK-078 | Test: Accessibility (ARIA labels, keyboard navigation, screen reader) | | |

**Phase 8 Completion Criteria**:
- ✅ All tests use role-based locators (getByRole, getByLabel, getByText)
- ✅ Tests use test.step() for readability
- ✅ Tests use auto-retrying assertions (toHaveText, toBeVisible)
- ✅ All tests pass in chromium, firefox, webkit
- ✅ No hard-coded waits (rely on Playwright auto-waiting)
- ✅ Screenshots captured on failure for debugging
- ✅ Tests complete in <5 minutes total

---

### Phase 9: Integration Testing & Fraud Evaluation

**GOAL-009**: Test full integration of card transfers with fraud detection pipeline.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-079 | Write integration test: Transfer triggers fraud evaluation | | |
| TASK-080 | Verify fraud result blocks high-risk transfers | | |
| TASK-081 | Verify low-risk transfers auto-approved | | |
| TASK-082 | Verify medium-risk transfers queued for human review | | |
| TASK-083 | Test transfer with GPS location triggers location strategy | | |
| TASK-084 | Test transfer with unrecognized device triggers device strategy | | |
| TASK-085 | Verify audit trail records transfer with timestamp + actor | | |

**Phase 9 Completion Criteria**:
- ✅ All integration tests pass with docker-compose running
- ✅ Fraud evaluation service correctly evaluates transfers
- ✅ RabbitMQ events published for each transfer
- ✅ MongoDB audit trail records all operations
- ✅ Redis cache populated with card data

---

### Phase 10: Documentation & Code Review

**GOAL-010**: Document API endpoints, component architecture, and deployment instructions.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-086 | Update API Swagger docs with new card endpoints | | |
| TASK-087 | Create frontend component documentation (Storybook optional) | | |
| TASK-088 | Write README for card feature in frontend/user-app/README.md | | |
| TASK-089 | Add curl examples for card API endpoints in docs/API.md | | |
| TASK-090 | Create PR template checklist items for card feature | | |
| TASK-091 | Code review: Ensure Clean Architecture principles followed | | |
| TASK-092 | Code review: Verify test coverage 95%+ | | |
| TASK-093 | Code review: Check accessibility compliance | | |

**Phase 10 Completion Criteria**:
- ✅ All endpoints documented in Swagger with examples
- ✅ Frontend component architecture documented
- ✅ README includes setup, usage, and troubleshooting
- ✅ API examples show all scenarios (success, errors, edge cases)
- ✅ PR ready for merge with all approvals

---

## 3. Alternatives

- **ALT-001**: Store card data in Redis only (rejected: persistence required for audit trail, MongoDB provides immutability)
- **ALT-002**: Fetch all user cards without limit (rejected: REQ-001 specifies max 3, pagination on backend provides better performance)
- **ALT-003**: Use GraphQL for card queries (rejected: existing project uses REST API, REST simpler for this feature)
- **ALT-004**: Implement transfer as synchronous call (rejected: follows async-first pattern already in fraud evaluation service, 202 Accepted required)
- **ALT-005**: Store full card numbers (rejected: SEC-001 requires masking, PCI DSS compliance violation)

## 4. Dependencies

- **DEP-001**: Existing fraud evaluation service (services/fraud-evaluation-service) must be running for transfer validation
- **DEP-002**: MongoDB 7.0+ for card data persistence
- **DEP-003**: Redis 7.2+ for card data caching
- **DEP-004**: RabbitMQ 3.12+ for event publishing
- **DEP-005**: FastAPI 0.104+ already installed in project
- **DEP-006**: React 18.3+ with TypeScript already in frontend
- **DEP-007**: Zustand state management already in use
- **DEP-008**: Playwright already configured for E2E tests
- **DEP-009**: pytest with coverage already configured
- **DEP-010**: Docker & docker-compose for running services

## 5. Files

### Backend Files to Create/Modify

**Domain Layer (Pure Business Logic - No Framework Imports)**
- **FILE-001**: `services/fraud-evaluation-service/src/domain/card_models.py` - Card, CardStatus enums, TransferRequest dataclasses
- **FILE-002**: `services/fraud-evaluation-service/src/domain/card_strategies.py` - CardBlockingStrategy, CardBalanceValidation (if needed)

**Application Layer (Use Cases & Ports)**
- **FILE-003**: `services/fraud-evaluation-service/src/application/ports/card_repository.py` - CardRepository interface
- **FILE-004**: `services/fraud-evaluation-service/src/application/ports/card_cache.py` - CardCacheService interface
- **FILE-005**: `services/fraud-evaluation-service/src/application/use_cases/get_user_cards.py` - GetUserCardsUseCase
- **FILE-006**: `services/fraud-evaluation-service/src/application/use_cases/get_card_transactions.py` - GetCardTransactionsUseCase
- **FILE-007**: `services/fraud-evaluation-service/src/application/use_cases/transfer_money.py` - TransferMoneyUseCase
- **FILE-008**: `services/fraud-evaluation-service/src/application/use_cases/block_card.py` - BlockCardUseCase

**Infrastructure Layer (Adapters)**
- **FILE-009**: `services/fraud-evaluation-service/src/adapters/card_mongodb_adapter.py` - MongoDBCardRepository
- **FILE-010**: `services/fraud-evaluation-service/src/adapters/card_redis_adapter.py` - RedisCardCache

**API Gateway (FastAPI Routes)**
- **FILE-011**: `services/api-gateway/src/routes/cards.py` - Card endpoints (GET, POST, PUT)
- **FILE-012**: `services/api-gateway/src/models/card_models.py` - Pydantic models (CardResponse, TransferRequest)

**Testing**
- **FILE-013**: `tests/unit/test_card_models.py` - Domain model tests
- **FILE-014**: `tests/unit/test_get_user_cards_usecase.py` - Use case tests
- **FILE-015**: `tests/unit/test_transfer_money_usecase.py` - Transfer use case tests
- **FILE-016**: `tests/integration/test_card_endpoints.py` - API endpoint tests
- **FILE-017**: `tests/fixtures/cards_sample_data.json` - Test card data

### Frontend Files to Create/Modify

**Components**
- **FILE-018**: `frontend/user-app/src/components/CardCard.tsx` - Single card display component
- **FILE-019**: `frontend/user-app/src/components/CardStatus.tsx` - Status badge component
- **FILE-020**: `frontend/user-app/src/components/CardActions.tsx` - Action buttons component
- **FILE-021**: `frontend/user-app/src/components/CardsList.tsx` - Cards list container
- **FILE-022**: `frontend/user-app/src/components/TransactionHistory.tsx` - Transaction modal/page
- **FILE-023**: `frontend/user-app/src/components/TransferForm.tsx` - Transfer form with React Hook Form
- **FILE-024**: `frontend/user-app/src/components/TransferConfirmation.tsx` - Success confirmation component

**Pages**
- **FILE-025**: `frontend/user-app/src/pages/CardsPage.tsx` - Main cards page (Inicio)

**State Management**
- **FILE-026**: `frontend/user-app/src/store/cardStore.ts` - Zustand store for card data
- **FILE-027**: `frontend/user-app/src/hooks/useCards.ts` - Custom hook for card operations
- **FILE-028**: `frontend/user-app/src/hooks/useCardTransactions.ts` - Custom hook for transactions
- **FILE-029**: `frontend/user-app/src/hooks/useTransfer.ts` - Custom hook for transfers

**Services**
- **FILE-030**: `frontend/user-app/src/services/cardService.ts` - Axios API client for cards

**Testing**
- **FILE-031**: `frontend/user-app/src/__tests__/CardCard.test.tsx` - Component tests
- **FILE-032**: `frontend/user-app/src/__tests__/CardsList.test.tsx` - Cards list tests
- **FILE-033**: `frontend/user-app/src/__tests__/TransferForm.test.tsx` - Form validation tests

**E2E Testing**
- **FILE-034**: `tests-e2e/tests/cards.spec.ts` - Playwright E2E tests for card feature
- **FILE-035**: `tests-e2e/pages/CardsPage.ts` - Page Object Model for cards

### Database & Configuration
- **FILE-036**: `docker-compose.yml` - Update with MongoDB collections initialization
- **FILE-037**: `scripts/init-cards-db.js` - MongoDB migration script for card schema

## 6. Testing

### Unit Tests (pytest)
- **TEST-001**: `tests/unit/test_card_models.py` - Card entity immutability, validation
- **TEST-002**: `tests/unit/test_card_status_enum.py` - Status enum values and transitions
- **TEST-003**: `tests/unit/test_get_user_cards_usecase.py` - Query logic, limit enforcement, permission checks
- **TEST-004**: `tests/unit/test_transfer_money_usecase.py` - Amount validation, balance check, fraud call
- **TEST-005**: `tests/unit/test_block_card_usecase.py` - Status update, event publishing
- **TEST-006**: `tests/unit/test_card_mongodb_adapter.py` - CRUD operations, query performance
- **TEST-007**: `tests/unit/test_card_redis_adapter.py` - Cache hit/miss, TTL expiration
- **TEST-008**: `tests/unit/test_card_routes.py` - Endpoint validation, authentication, error handling
- **TEST-009**: `tests/unit/test_cardstore_zustand.ts` (Vitest) - Store selectors, actions
- **TEST-010**: `tests/unit/test_useCards_hook.ts` (Vitest) - Custom hook behavior

### Integration Tests (pytest)
- **TEST-011**: `tests/integration/test_card_endpoints_full.py` - Full request/response cycle
- **TEST-012**: `tests/integration/test_transfer_with_fraud.py` - Transfer triggers fraud evaluation
- **TEST-013**: `tests/integration/test_card_audit_trail.py` - Operations recorded in MongoDB

### E2E Tests (Playwright)
- **TEST-014**: `tests-e2e/tests/cards.spec.ts` - View 3 cards on dashboard
- **TEST-015**: `tests-e2e/tests/cards.spec.ts` - Block card visual indicators
- **TEST-016**: `tests-e2e/tests/cards.spec.ts` - View transactions in modal
- **TEST-017**: `tests-e2e/tests/cards.spec.ts` - Complete transfer workflow
- **TEST-018**: `tests-e2e/tests/cards.spec.ts` - Cannot transfer from blocked card
- **TEST-019**: `tests-e2e/tests/cards.spec.ts` - Pagination for >3 cards
- **TEST-020**: `tests-e2e/tests/cards.spec.ts` - Empty state handling
- **TEST-021**: `tests-e2e/tests/cards.spec.ts` - Insufficient balance error
- **TEST-022**: `tests-e2e/tests/cards.spec.ts` - Load time <2 seconds
- **TEST-023**: `tests-e2e/tests/cards.spec.ts` - Responsive layouts (mobile/tablet/desktop)
- **TEST-024**: `tests-e2e/tests/cards.spec.ts` - WCAG 2.1 AA accessibility

### Test Coverage Target
- **MIN-COV**: 70% (minimum required)
- **TARGET-COV**: 95% (project standard)
- **BACKEND**: pytest with coverage.py, `pytest --cov=services/fraud-evaluation-service --cov=services/api-gateway --cov-fail-under=95`
- **FRONTEND**: Vitest with c8, `npm test -- --coverage`

## 7. Risks & Assumptions

### Risks
- **RISK-001**: Card data consistency if MongoDB and Redis get out of sync (Mitigation: Implement cache invalidation on write, set TTL=300s for eventual consistency)
- **RISK-002**: Performance degradation if fetching cards for user with 100+ cards (Mitigation: Pagination on backend, limit=3 in query)
- **RISK-003**: Fraud evaluation service unavailable during transfer (Mitigation: Retry logic with exponential backoff, queue transfer to RabbitMQ for retry)
- **RISK-004**: Card number exposure in logs (Mitigation: Mask numbers before logging, use secrets masking in CI/CD)
- **RISK-005**: Accessibility issues missed in testing (Mitigation: Use axe-core in E2E tests, manual WCAG review before release)
- **RISK-006**: Race condition: concurrent block + transfer (Mitigation: Use MongoDB transactions or version fields, implement optimistic locking)

### Assumptions
- **ASSUMPTION-001**: Existing fraud evaluation service API remains stable (no breaking changes)
- **ASSUMPTION-002**: Card data schema provided by backend team (migrations prepared)
- **ASSUMPTION-003**: User authentication (JWT tokens) already implemented and working
- **ASSUMPTION-004**: RabbitMQ available for event publishing (already running in docker-compose)
- **ASSUMPTION-005**: Geolocation data available in transfer requests (device_id → location lookup)
- **ASSUMPTION-006**: Test database separate from production (safe to use fixtures)
- **ASSUMPTION-007**: React version 18.3+ with hooks support available
- **ASSUMPTION-008**: TypeScript types available for all dependencies

## 8. Related Specifications / Further Reading

- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture, Clean Architecture patterns
- [docs/CONTEXT.md](../docs/CONTEXT.md) - Development workflows, TDD/BDD practices
- [docs/PRODUCT.md](../docs/PRODUCT.md) - Product requirements, user stories
- [docs/user-stories/HU-001-receive-transactions-api.md](../docs/user-stories/HU-001-receive-transactions-api.md) - Transaction API foundation
- [docs/user-stories/HU-002-immutable-audit-trail.md](../docs/user-stories/HU-002-immutable-audit-trail.md) - Audit trail for card operations
- [docs/user-stories/HU-003-detect-high-amount.md](../docs/user-stories/HU-003-detect-high-amount.md) - Fraud detection (transfer validation)
- Playwright Documentation: https://playwright.dev
- FastAPI Documentation: https://fastapi.tiangolo.com
- MongoDB Documentation: https://docs.mongodb.com
- Zustand Documentation: https://github.com/pmndrs/zustand
- React Hook Form: https://react-hook-form.com
- TailwindCSS: https://tailwindcss.com
- WCAG 2.1 AA Standards: https://www.w3.org/WAI/WCAG21/quickref

---

**Implementation Plan Version: 1.0** | **Created: 2026-01-28** | **Owner: Development Team** | **Status: Ready for Implementation**

