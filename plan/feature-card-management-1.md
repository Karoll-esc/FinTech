---
goal: Implement Card Management System with Add/Link/Remove Capabilities (HU-015)
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
owner: Development Team
status: 'Planned'
tags: [feature, card-management, pci-dss, tdd, backend, frontend]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan covers the **MVP development** of HU-015: Add and Link Cards to Account. The feature enables bank customers to manage multiple payment cards (debit/credit) with basic CRUD operations and audit trail integration.

**Key Deliverables (MVP Scope):**
- Backend API endpoints for card CRUD operations
- Basic input validation (format, required fields)
- Frontend card management UI (user-app)
- Integration with existing audit trail system
- Comprehensive test coverage (unit, integration, E2E)

**Deferred to Post-MVP:**
- Advanced card validation (Luhn algorithm, issuer detection)
- PCI-DSS compliance (tokenization, encryption)
- Payment processor integration

**TDD Approach:** All implementation follows RED-GREEN-REFACTOR cycle with approval gates between phases.

## 1. Requirements & Constraints

### Functional Requirements

- **REQ-001**: Users must authenticate before accessing card management features
- **REQ-002**: Card number must be 16 digits (basic format validation)
- **REQ-003**: Maximum 10 cards per user account (business constraint)
- **REQ-004**: Duplicate card prevention - same last 4 digits cannot be added twice to same account
- **REQ-005**: Card removal must be soft-delete (preserve audit trail)
- **REQ-006**: All card operations must be logged to audit trail (HU-002 integration)
- **REQ-007**: Card operations must complete in <1000ms (MVP performance target)

### Security Requirements (MVP)

- **SEC-001**: CVV is NOT stored (input validation only, discarded after form submission)
- **SEC-002**: Card numbers stored as plain text in MongoDB (encrypted database volume)
- **SEC-003**: Only last 4 digits of card shown in UI (masked display)
- **SEC-004**: Card data access requires user authentication + authorization
- **SEC-005**: Basic rate limiting on card operations (10 requests/minute per user)

**Post-MVP Security Enhancements:**
- PCI-DSS tokenization
- Field-level encryption
- Advanced rate limiting and fraud detection

### Data Requirements

- **DAT-001**: Card schema: card_number (plain text, 16 digits), card_holder_name, expiry_date, card_type, nickname (optional), status, user_id, created_at, updated_at
- **DAT-002**: Card status enum: ACTIVE, INACTIVE
- **DAT-003**: Card type enum: DEBIT, CREDIT
- **DAT-004**: Expiry date format: MM/YY (basic format validation, no future date check in MVP)
- **DAT-005**: Card holder name: 3-50 characters (alphanumeric + spaces allowed)

### Technical Constraints

- **CON-001**: Must use existing MongoDB for card persistence
- **CON-002**: Must integrate with Redis cache for user card lists
- **CON-003**: Must use FastAPI for backend endpoints
- **CON-004**: Must use React + TypeScript for frontend
- **CON-005**: Must maintain Clean Architecture (domain → application → infrastructure)
- **CON-006**: Domain layer must have zero framework dependencies
- **CON-007**: Test coverage must remain ≥70% (current: 95%)

### Architectural Guidelines

- **GUD-001**: Follow hexagonal architecture - domain models independent of FastAPI/MongoDB
- **GUD-002**: Apply Strategy Pattern for card validation rules
- **GUD-003**: Use Repository Pattern for data access abstraction
- **GUD-004**: Implement Dependency Injection for testability
- **GUD-005**: All business logic in domain layer, orchestration in application layer
- **GUD-006**: Infrastructure adapters implement ports defined in application layer

### MVP Patterns

- **PAT-001**: Audit logging - all card operations emit events to audit_logs collection
- **PAT-002**: Soft delete pattern - card removal sets status to INACTIVE, preserves data
- **PAT-003**: Simple duplicate detection - compare last 4 digits + user_id

## 2. Implementation Steps

### Phase 1: Domain Layer - Card Models & Basic Validation (RED → GREEN → REFACTOR)

**GOAL-001**: Create pure domain models with basic validation for card management

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | **[RED]** Write failing tests for Card entity (frozen dataclass with immutability) | | |
| TASK-002 | **[RED]** Write failing tests for card number format validation (16 digits) | | |
| TASK-003 | **[RED]** Write failing tests for expiry date format validation (MM/YY) | | |
| TASK-004 | **[RED]** Write failing tests for card holder name validation (3-50 chars) | | |
| TASK-005 | **[RED]** Write failing tests for card type enum (DEBIT/CREDIT) | | |
| TASK-006 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-007 | **[GREEN]** Implement Card entity as frozen dataclass with all fields | | |
| TASK-008 | **[GREEN]** Implement basic card number validator (16 digits, numeric) | | |
| TASK-009 | **[GREEN]** Implement expiry date validator (MM/YY format) | | |
| TASK-010 | **[GREEN]** Implement card holder name validator (length check) | | |
| TASK-011 | **[GREEN]** Implement CardType and CardStatus enums | | |
| TASK-012 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-013 | **[REFACTOR]** Add comprehensive docstrings to all domain models | | |
| TASK-014 | **[REFACTOR]** Extract validation logic into separate validator functions | | |
| TASK-015 | **[REFACTOR]** Add null checks and error messages | | |
| TASK-016 | **[REFACTOR]** Ensure all methods <20 lines, apply SRP | | |
| TASK-017 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/fraud-evaluation-service/src/domain/models/card.py` - Card entity
- `services/fraud-evaluation-service/src/domain/validation/card_validators.py` - Basic validation functions
- `services/fraud-evaluation-service/src/domain/enums.py` [MODIFIED] - Add CardType, CardStatus enums
- `tests/unit/test_domain_card.py` - Domain model tests (10+ tests expected)

---

### Phase 2: Application Layer - Card Use Cases (RED → GREEN → REFACTOR)

**GOAL-002**: Implement use cases for card CRUD operations with ports/interfaces

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-018 | **[RED]** Write failing tests for AddCardUseCase (happy path + validation failures) | | |
| TASK-019 | **[RED]** Write failing tests for RemoveCardUseCase (soft delete) | | |
| TASK-020 | **[RED]** Write failing tests for ListUserCardsUseCase (basic list) | | |
| TASK-021 | **[RED]** Write failing tests for GetCardDetailsUseCase (by card_id) | | |
| TASK-022 | **[RED]** Write failing tests for duplicate prevention (last 4 digits) | | |
| TASK-023 | **[RED]** Write failing tests for max cards limit (10 cards) | | |
| TASK-024 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-025 | **[GREEN]** Define CardRepository port with: save, find_by_id, find_by_user_id, soft_delete | | |
| TASK-026 | **[GREEN]** Implement AddCardUseCase with validation, duplicate check, limit enforcement | | |
| TASK-027 | **[GREEN]** Implement RemoveCardUseCase with soft delete | | |
| TASK-028 | **[GREEN]** Implement ListUserCardsUseCase | | |
| TASK-029 | **[GREEN]** Implement GetCardDetailsUseCase | | |
| TASK-030 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-031 | **[REFACTOR]** Add detailed error messages for validation failures | | |
| TASK-032 | **[REFACTOR]** Add comprehensive docstrings with usage examples | | |
| TASK-033 | **[REFACTOR]** Add audit event emission for all operations | | |
| TASK-034 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/fraud-evaluation-service/src/application/ports/card_repository.py` - Repository interface
- `services/fraud-evaluation-service/src/application/use_cases/add_card.py` - AddCardUseCase
- `services/fraud-evaluation-service/src/application/use_cases/remove_card.py` - RemoveCardUseCase
- `services/fraud-evaluation-service/src/application/use_cases/list_user_cards.py` - ListUserCardsUseCase
- `services/fraud-evaluation-service/src/application/use_cases/get_card_details.py` - GetCardDetailsUseCase
- `tests/unit/test_use_cases_card.py` - Use case tests (15+ tests expected)

---

### Phase 3: Infrastructure Layer - Adapters (RED → GREEN → REFACTOR)

**GOAL-003**: Implement concrete adapters for MongoDB and audit logging

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-035 | **[RED]** Write failing integration tests for MongoCardRepository (CRUD operations) | | |
| TASK-036 | **[RED]** Write failing tests for audit event emission on card operations | | |
| TASK-037 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-038 | **[GREEN]** Implement MongoCardRepository with cards collection schema | | |
| TASK-039 | **[GREEN]** Implement AuditEventPublisher for card operations | | |
| TASK-040 | **[GREEN]** Add MongoDB indexes: user_id, last_four_digits + user_id (unique), created_at | | |
| TASK-041 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-042 | **[REFACTOR]** Add connection pooling and retry logic for MongoDB | | |
| TASK-043 | **[REFACTOR]** Add comprehensive logging (mask card numbers in logs) | | |
| TASK-044 | **[REFACTOR]** Add error handling for database failures | | |
| TASK-045 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/fraud-evaluation-service/src/infrastructure/adapters/mongo_card_repository.py` - MongoDB adapter
- `services/fraud-evaluation-service/src/infrastructure/adapters/audit_publisher.py` - Audit event publisher
- `tests/integration/test_card_repository.py` - Integration tests (8+ tests)

---

### Phase 4: API Gateway - REST Endpoints (RED → GREEN → REFACTOR)

**GOAL-004**: Create FastAPI endpoints for card management with validation and error handling

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-046 | **[RED]** Write failing API tests for POST /api/v1/cards (add card) | | |
| TASK-047 | **[RED]** Write failing API tests for DELETE /api/v1/cards/{id} (remove card) | | |
| TASK-048 | **[RED]** Write failing API tests for GET /api/v1/cards (list user cards) | | |
| TASK-049 | **[RED]** Write failing API tests for GET /api/v1/cards/{id} (card details) | | |
| TASK-050 | **[RED]** Write failing tests for validation error responses (400, 409) | | |
| TASK-051 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-052 | **[GREEN]** Create Pydantic schemas: AddCardRequest, CardResponse, CardListResponse | | |
| TASK-053 | **[GREEN]** Implement POST /api/v1/cards endpoint with validation | | |
| TASK-054 | **[GREEN]** Implement DELETE /api/v1/cards/{id} endpoint | | |
| TASK-055 | **[GREEN]** Implement GET /api/v1/cards endpoint | | |
| TASK-056 | **[GREEN]** Implement GET /api/v1/cards/{id} endpoint | | |
| TASK-057 | **[GREEN]** Add authentication dependency (verify user_id from JWT) | | |
| TASK-058 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-059 | **[REFACTOR]** Add detailed OpenAPI documentation for all endpoints | | |
| TASK-060 | **[REFACTOR]** Add request/response examples in Swagger | | |
| TASK-061 | **[REFACTOR]** Implement proper HTTP status codes (201, 204, 409) | | |
| TASK-062 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `services/api-gateway/src/routes/cards.py` - Card endpoints
- `services/api-gateway/src/schemas/card_schemas.py` - Pydantic models
- `services/api-gateway/src/dependencies/auth.py` - Authentication dependency
- `tests/integration/test_api_cards.py` - API integration tests (15+ tests)

---

### Phase 5: Frontend - Card Management UI (RED → GREEN → REFACTOR)

**GOAL-005**: Build basic React components for card management in user-app

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-063 | **[RED]** Write failing Vitest tests for AddCardForm component | | |
| TASK-064 | **[RED]** Write failing tests for CardList component | | |
| TASK-065 | **[RED]** Write failing tests for CardItem component | | |
| TASK-066 | **[RED]** Write failing tests for RemoveCardModal component | | |
| TASK-067 | **[RED]** Write failing tests for card API service (fetch, create, delete) | | |
| TASK-068 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-069 | **[GREEN]** Create AddCardForm with basic validation | | |
| TASK-070 | **[GREEN]** Create CardList component (simple list, no pagination) | | |
| TASK-071 | **[GREEN]** Create CardItem component with masked card number (last 4 digits) | | |
| TASK-072 | **[GREEN]** Create RemoveCardModal with confirmation | | |
| TASK-073 | **[GREEN]** Implement cardService API client (fetch API) | | |
| TASK-074 | **[GREEN]** Add Cards page route to user-app | | |
| TASK-075 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-076 | **[REFACTOR]** Add form validation feedback (error messages) | | |
| TASK-077 | **[REFACTOR]** Add loading states | | |
| TASK-078 | **[REFACTOR]** Add success/error toast notifications | | |
| TASK-079 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `frontend/user-app/src/pages/Cards.tsx` - Main cards page
- `frontend/user-app/src/components/cards/AddCardForm.tsx` - Add card form
- `frontend/user-app/src/components/cards/CardList.tsx` - Card list
- `frontend/user-app/src/components/cards/CardItem.tsx` - Individual card display
- `frontend/user-app/src/components/cards/RemoveCardModal.tsx` - Removal confirmation
- `frontend/user-app/src/services/cardService.ts` - API client
- `frontend/user-app/src/components/cards/__tests__/` - Component tests (10+ tests)

---

### Phase 6: E2E Tests & Integration (RED → GREEN → REFACTOR)

**GOAL-006**: Create basic end-to-end tests with Playwright

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-080 | **[RED]** Write failing E2E test for add card happy path | | |
| TASK-081 | **[RED]** Write failing E2E test for add card validation failure | | |
| TASK-082 | **[RED]** Write failing E2E test for remove card flow | | |
| TASK-083 | ⏸️ **APPROVAL GATE**: Present RED phase results, await user approval | | |
| TASK-084 | **[GREEN]** Implement E2E test for complete add card flow | | |
| TASK-085 | **[GREEN]** Implement E2E test for validation errors | | |
| TASK-086 | **[GREEN]** Implement E2E test for card removal | | |
| TASK-087 | **[GREEN]** Add test fixtures for card data | | |
| TASK-088 | ⏸️ **APPROVAL GATE**: Present GREEN phase results, await user approval | | |
| TASK-089 | **[REFACTOR]** Extract Page Object Models for card pages | | |
| TASK-090 | **[REFACTOR]** Add reusable tasks for common card operations | | |
| TASK-091 | ⏸️ **APPROVAL GATE**: Present REFACTOR phase results, await user approval | | |

**Files Created:**
- `tests-e2e/tests/cards.spec.ts` - E2E test suite
- `tests-e2e/pages/CardsPage.ts` - Page Object Model
- `tests-e2e/tasks/cardTasks.ts` - Reusable card operations
- `tests-e2e/fixtures/cardData.json` - Test fixtures

---

### Phase 7: Documentation & Deployment Preparation

**GOAL-007**: Complete documentation and deployment preparation

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-092 | Create MongoDB migration script for cards collection | | |
| TASK-093 | Update API documentation (Swagger/OpenAPI) | | |
| TASK-094 | Update README.md with card management section | | |
| TASK-095 | Create basic user guide for card management feature | | |
| TASK-096 | Final integration test - full flow from UI to DB | | |

**Files Created:**
- `docs/CARD_MANAGEMENT.md` - Feature documentation
- `scripts/migrations/001_create_cards_collection.py` - MongoDB migration
- `docs/PCI_DSS_CHECKLIST.md` - Compliance documentation
- `docs/DEPLOYMENT_RUNBOOK_HU015.md` - Deployment guide

---

## 3. Alternatives

### Alternative Approaches Considered

- **ALT-001**: **Synchronous card validation** - Rejected in favor of async approach for better UX and scalability. Backend validation happens in <500ms, so async not needed initially.

- **ALT-002**: **Client-side only validation** - Rejected due to security concerns. All validation must occur server-side; client validation is only for UX improvement.

- **ALT-003**: **Implement PCI-DSS compliance in MVP** - Deferred to post-MVP to accelerate delivery. Database-level encryption provides baseline security.

- **ALT-004**: **Use third-party card management SaaS** - Rejected to maintain control over data and reduce external dependencies. Tokenization service is acceptable limited dependency.

- **ALT-005**: **Hard delete cards** - Rejected in favor of soft delete to maintain audit trail and comply with HU-002 requirements.

- **ALT-006**: **Unlimited cards per user** - Rejected to prevent abuse and maintain reasonable system load. 10-card limit is industry standard.

## 4. Dependencies

### External Dependencies (MVP)

- **DEP-001**: None for MVP - all dependencies deferred to post-MVP phase

### Internal Dependencies

- **DEP-004**: **HU-002 Audit Trail** - Card operations must emit events to existing audit logging system.

- **DEP-005**: **HU-016 Card List View** - Frontend dependency mentioned in HU-015, but appears to be part of same feature (list is needed for add/remove).

- **DEP-006**: **Authentication System** - Existing JWT authentication must be functional for user identification.

- **DEP-007**: **MongoDB Setup** - Database must be configured with encryption at rest before storing card data.

### Library Dependencies (New)

- **DEP-008**: None - use built-in HTML5 form validation and basic JavaScript validation in MVP

## 5. Files

### Backend Files (New/Modified)

**Domain Layer**
- **FILE-001**: `services/fraud-evaluation-service/src/domain/models/card.py` - Card entity model
- **FILE-002**: `services/fraud-evaluation-service/src/domain/validation/card_validators.py` - Basic validation functions
- **FILE-003**: `services/fraud-evaluation-service/src/domain/enums.py` [MODIFIED] - Add CardType, CardStatus enums

**Application Layer**
- **FILE-004**: `services/fraud-evaluation-service/src/application/ports/card_repository.py` - Repository interface
- **FILE-005**: `services/fraud-evaluation-service/src/application/use_cases/add_card.py` - Add card use case
- **FILE-006**: `services/fraud-evaluation-service/src/application/use_cases/remove_card.py` - Remove card use case
- **FILE-007**: `services/fraud-evaluation-service/src/application/use_cases/list_user_cards.py` - List cards use case
- **FILE-008**: `services/fraud-evaluation-service/src/application/use_cases/get_card_details.py` - Get card use case

**Infrastructure Layer**
- **FILE-009**: `services/fraud-evaluation-service/src/infrastructure/adapters/mongo_card_repository.py` - MongoDB adapter
- **FILE-010**: `services/fraud-evaluation-service/src/infrastructure/adapters/audit_publisher.py` - Audit event publisher

**API Gateway**
- **FILE-011**: `services/api-gateway/src/routes/cards.py` - Card API endpoints
- **FILE-012**: `services/api-gateway/src/schemas/card_schemas.py` - Pydantic request/response schemas
- **FILE-013**: `services/api-gateway/src/dependencies/auth.py` [MODIFIED] - Add card-specific auth checks
- **FILE-014**: `services/api-gateway/src/main.py` [MODIFIED] - Mount card routes

### Frontend Files (New/Modified)

**React Components**
- **FILE-015**: `frontend/user-app/src/pages/Cards.tsx` - Main cards management page
- **FILE-016**: `frontend/user-app/src/components/cards/AddCardForm.tsx` - Add card form component
- **FILE-017**: `frontend/user-app/src/components/cards/CardList.tsx` - Card list component
- **FILE-018**: `frontend/user-app/src/components/cards/CardItem.tsx` - Individual card display
- **FILE-019**: `frontend/user-app/src/components/cards/RemoveCardModal.tsx` - Card removal confirmation
- **FILE-020**: `frontend/user-app/src/services/cardService.ts` - Card API client service
- **FILE-021**: `frontend/user-app/src/App.tsx` [MODIFIED] - Add Cards route

### Test Files (New)

**Backend Tests**
- **FILE-022**: `tests/unit/test_domain_card.py` - Domain model tests (10+ tests)
- **FILE-023**: `tests/unit/test_use_cases_card.py` - Use case tests (15+ tests)
- **FILE-024**: `tests/integration/test_card_repository.py` - Repository integration tests (8+ tests)
- **FILE-025**: `tests/integration/test_api_cards.py` - API endpoint tests (12+ tests)

**Frontend Tests**
- **FILE-026**: `frontend/user-app/src/components/cards/__tests__/AddCardForm.test.tsx` - Add card form tests
- **FILE-027**: `frontend/user-app/src/components/cards/__tests__/CardList.test.tsx` - Card list tests
- **FILE-028**: `frontend/user-app/src/components/cards/__tests__/CardItem.test.tsx` - Card item tests
- **FILE-029**: `frontend/user-app/src/components/cards/__tests__/RemoveCardModal.test.tsx` - Modal tests

**E2E Tests**
- **FILE-030**: `tests-e2e/tests/cards.spec.ts` - End-to-end card management tests
- **FILE-031**: `tests-e2e/pages/CardsPage.ts` - Cards page object model
- **FILE-032**: `tests-e2e/tasks/cardTasks.ts` - Reusable card operation tasks
- **FILE-033**: `tests-e2e/fixtures/cardData.json` - Test fixtures

### Configuration & Documentation Files

- **FILE-034**: `docs/CARD_MANAGEMENT.md` - Feature documentation
- **FILE-035**: `scripts/migrations/001_create_cards_collection.py` - MongoDB migration script

## 6. Testing

### Unit Tests (Backend)

**Domain Layer Tests** (tests/unit/test_domain_card.py)
- **TEST-001**: Card entity creation with valid data should succeed
- **TEST-002**: Card entity is immutable (frozen dataclass)
- **TEST-003**: Card number validation accepts 16 digits
- **TEST-004**: Card number validation rejects non-16 digit input
- **TEST-005**: Card number validation rejects non-numeric input
- **TEST-006**: Expiry date validation accepts MM/YY format
- **TEST-007**: Expiry date validation rejects invalid format
- **TEST-008**: Card holder name validation rejects names <3 chars
- **TEST-009**: Card holder name validation rejects names >50 chars
- **TEST-010**: CardType enum has DEBIT and CREDIT values
- **TEST-011**: CardStatus enum has ACTIVE and INACTIVE values

**Application Layer Tests** (tests/unit/test_use_cases_card.py)
- **TEST-012**: AddCardUseCase creates card with valid data
- **TEST-013**: AddCardUseCase rejects duplicate card (same last 4 digits, 409 Conflict)
- **TEST-014**: AddCardUseCase rejects when user has 10 cards (429 Too Many Requests)
- **TEST-015**: AddCardUseCase validates card number format (16 digits)
- **TEST-016**: AddCardUseCase emits audit event on success
- **TEST-017**: RemoveCardUseCase performs soft delete (sets status to INACTIVE)
- **TEST-018**: RemoveCardUseCase preserves card data for audit
- **TEST-019**: RemoveCardUseCase emits audit event on removal
- **TEST-020**: ListUserCardsUseCase returns only active cards
- **TEST-021**: GetCardDetailsUseCase returns full card details
- **TEST-022**: GetCardDetailsUseCase returns 404 for non-existent card
- **TEST-023**: GetCardDetailsUseCase validates user owns card (authorization)
- **TEST-024**: AddCardUseCase handles repository failures gracefully

### Integration Tests (Backend)

**Repository Tests** (tests/integration/test_card_repository.py)
- **TEST-025**: MongoCardRepository saves card to database
- **TEST-026**: MongoCardRepository retrieves card by ID
- **TEST-027**: MongoCardRepository retrieves cards by user_id
- **TEST-028**: MongoCardRepository enforces unique constraint on last_four + user_id
- **TEST-029**: MongoCardRepository soft deletes card (updates status)
- **TEST-030**: AuditEventPublisher emits card_added event
- **TEST-031**: AuditEventPublisher emits card_removed event

**API Tests** (tests/integration/test_api_cards.py)
- **TEST-032**: POST /api/v1/cards returns 201 with valid data
- **TEST-033**: POST /api/v1/cards returns 400 with invalid card number format
- **TEST-034**: POST /api/v1/cards returns 409 when card already exists
- **TEST-035**: POST /api/v1/cards returns 401 without authentication
- **TEST-036**: DELETE /api/v1/cards/{id} returns 204 on success
- **TEST-037**: DELETE /api/v1/cards/{id} returns 404 for non-existent card
- **TEST-038**: DELETE /api/v1/cards/{id} returns 403 when user doesn't own card
- **TEST-039**: GET /api/v1/cards returns user's card list
- **TEST-040**: GET /api/v1/cards returns 200 with empty array for new user
- **TEST-041**: GET /api/v1/cards/{id} returns card details
- **TEST-042**: GET /api/v1/cards masks card number (shows last 4 digits)
- **TEST-043**: API returns proper OpenAPI schema in /docs

### Frontend Tests (Vitest)

**Component Tests**
- **TEST-044**: AddCardForm renders all input fields
- **TEST-045**: AddCardForm validates card number (16 digits)
- **TEST-046**: AddCardForm shows error for invalid card number
- **TEST-047**: AddCardForm validates expiry date format (MM/YY)
- **TEST-048**: AddCardForm validates card holder name length
- **TEST-049**: AddCardForm submits valid form data
- **TEST-050**: AddCardForm disables submit during API call
- **TEST-051**: CardList renders list of cards
- **TEST-052**: CardList displays masked card numbers
- **TEST-053**: CardItem triggers remove action
- **TEST-054**: RemoveCardModal shows confirmation message
- **TEST-055**: RemoveCardModal calls delete API on confirm
- **TEST-056**: RemoveCardModal closes without action on cancel
- **TEST-057**: cardService makes correct API calls with auth headers

### E2E Tests (Playwright)

**User Workflows**
- **TEST-058**: User can add a new card with valid data
- **TEST-059**: User sees validation error for invalid card number format
- **TEST-060**: User can remove a card with confirmation
- **TEST-061**: User can cancel card removal
- **TEST-062**: User sees updated card list after add/remove
- **TEST-063**: User sees masked card number (last 4 digits only)

### Test Coverage Goals (MVP)

- **Minimum Overall Coverage**: 70% (enforced by pytest)
- **Target Coverage**: 80% (reduced from 95% for MVP scope)
- **Critical Path Coverage**: 100% (card CRUD operations, audit logging)
- **Domain Layer Coverage**: 100% (pure business logic must be fully tested)

## 7. Risks & Assumptions

### Technical Risks (MVP)

- **RISK-001**: **Data Security Without Tokenization**
  - *Impact*: Medium - Card numbers stored as plain text (encrypted DB volume only)
  - *Mitigation*: Use MongoDB encrypted storage engine, limit access via RBAC, plan tokenization for post-MVP

- **RISK-002**: **Basic Validation May Allow Invalid Cards**
  - *Impact*: Low - Format validation only, no Luhn check
  - *Mitigation*: Accept risk for MVP, add Luhn validation in post-MVP phase

- **RISK-003**: **Race Condition on Max Cards Check**
  - *Impact*: Low - User might add 11th card if two requests concurrent
  - *Mitigation*: Use database unique constraint + atomic counter

### Business Risks (MVP)

- **RISK-004**: **Production Use Without PCI-DSS**
  - *Impact*: High - Cannot process real payments until compliant
  - *Mitigation*: Clearly document MVP limitations, add prominent "Demo Mode" disclaimer, implement PCI-DSS before public launch

- **RISK-005**: **Duplicate Detection Limited to Last 4 Digits**
  - *Impact*: Low - Different cards with same last 4 digits cannot be added
  - *Mitigation*: Acceptable for MVP, improve with full card hashing in post-MVP

### Operational Risks (MVP)

- **RISK-006**: **Performance with Many Cards**
  - *Impact*: Low - User with 10 cards experiences slow load times without caching
  - *Mitigation*: Add MongoDB indexes, optimize queries, add Redis caching in post-MVP if needed

### Assumptions (MVP)

- **ASSUMPTION-001**: This is a demonstration/MVP system, NOT production-ready for real payment processing
- **ASSUMPTION-002**: JWT authentication is already implemented and secure
- **ASSUMPTION-003**: MongoDB has encrypted storage volumes in production environment
- **ASSUMPTION-004**: Card data is NOT synced with external banking systems (internal records only)
- **ASSUMPTION-005**: CVV is NOT stored (validation only, discarded after submission)
- **ASSUMPTION-006**: Users cannot edit card details after creation (must remove and re-add)
- **ASSUMPTION-007**: Card balance tracking is out of scope (separate feature)
- **ASSUMPTION-008**: Post-MVP will implement full PCI-DSS compliance before production use

## 8. Related Specifications / Further Reading

### Internal Documentation

- [HU-015: Add and Link Cards to Account](../docs/user-stories/HU-015-add-cards-to-account.md) - Original user story
- [HU-016: View and Manage Multiple Cards](../docs/user-stories/HU-016-view-manage-multiple-cards.md) - Related card list view feature
- [HU-002: Immutable Audit Trail](../docs/user-stories/HU-002-immutable-audit-trail.md) - Audit logging requirements
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture and Clean Architecture patterns
- [CONTEXT.md](../docs/CONTEXT.md) - Development setup and TDD workflow
- [TDD-GUIDE.md](../TDD-GUIDE.md) - Detailed TDD practices for this project

### External Resources (Post-MVP)

- [PCI DSS Quick Reference Guide](https://www.pcisecuritystandards.org/documents/PCI_DSS_v3-2-1_QRG.pdf) - For future compliance implementation
- [Luhn Algorithm Wikipedia](https://en.wikipedia.org/wiki/Luhn_algorithm) - For post-MVP validation enhancement

---

**Implementation Plan Version**: 1.0 (MVP Scope)  
**Last Updated**: 2026-01-28  
**Estimated Effort**: 8 Story Points (~2 sprints for 2-person team)  
**Prerequisites**: MongoDB with encrypted storage, JWT authentication, audit trail system (HU-002)

**MVP Scope Summary:**
- ✅ Basic card CRUD operations
- ✅ Format validation (16 digits, MM/YY expiry)
- ✅ Soft delete with audit trail
- ✅ 10-card limit per user
- ✅ Duplicate prevention (last 4 digits)
- ❌ Luhn algorithm validation (post-MVP)
- ❌ Card issuer detection (post-MVP)
- ❌ PCI-DSS tokenization (post-MVP)
- ❌ CVV encryption (CVV not stored in MVP)

**Total Tasks**: 96 (reduced from 119)

**Next Steps**:
1. Review simplified MVP plan with team
2. Confirm acceptable security level for demo/internal use
3. Begin Phase 1 (Domain Layer) with RED tests
4. Schedule approval gate meetings for each phase
5. Plan post-MVP security enhancements
