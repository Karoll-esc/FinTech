# Copilot Instructions - Fraud Detection Engine

## Quick Reference

**Stack**: Python 3.11 (FastAPI) + TypeScript (React/Vite) | **Architecture**: Clean Architecture + Microservices | **Tests**: pytest (unit/integration) + Vitest/Playwright (E2E)

---

## System Architecture

### Three-Service Microservice Architecture

1. **API Gateway** (`services/api-gateway/`) - FastAPI REST layer
   - Fast Pydantic validation, dependency injection
   - Endpoints: `POST /transaction` (202 Accepted), `GET /audit/*`, `PUT /config/*`
   - All responses must maintain 202 pattern for transaction submissions (async-first)

2. **Fraud Evaluation Service** (`services/fraud-evaluation-service/`) - Domain logic (Clean Architecture)
   - Folder structure: `domain/` (models + 7 strategies), `application/` (use cases), `infrastructure/` (adapters)
   - **No external framework imports in domain/** - pure Python business logic only
   - 7 fraud strategies: amount threshold, location check, device validation, rapid succession, unusual time, timezone shift, traveling velocity
   - All strategies implement `FraudStrategy` interface in `domain/strategies/base.py`

3. **Worker Service** (`services/worker-service/`) - Async processing
   - Consumes `fraud.queue` from RabbitMQ
   - Fetches user context from Redis, evaluates fraud, persists to MongoDB + Redis

### Key Data Flow Pattern

```
Client → API (validate, publish to queue) → 202 Accepted
         ↓
      RabbitMQ ← Worker (consume) → Domain Logic → MongoDB + Redis
```

---

## Development Setup

### Prerequisites
- Docker Desktop running (`docker --version`)
- Python 3.11+ (for local testing)
- Node.js 18+ (for frontend)

### Start All Services
```bash
docker-compose up -d
# Verify: docker-compose ps
# API Swagger UI: http://localhost:8000/docs
```

### Run Backend Tests
```powershell
# Windows: ./scripts/run-tests.ps1 -TestType backend
# Or directly: pytest tests/unit/ -v --cov=services
```

### Run Frontend Tests
```bash
cd frontend/admin-dashboard && npm test
cd frontend/user-app && npm test
```

### Run E2E Tests
```bash
cd tests-e2e && npm test
# Or with UI: npx playwright test --ui
```

---

## Critical Patterns & Conventions

### Domain Layer (Inviolable Rules)
- **No imports of FastAPI, MongoDB, Redis, RabbitMQ, or any framework**
- All models are immutable: use `@dataclass(frozen=True)` for Value Objects
- Strategies inherit from `FraudStrategy` (abstract base in `domain/strategies/base.py`)
- Use `RiskLevel` enum (LOW_RISK=1, MEDIUM_RISK=2, HIGH_RISK=3) - numeric values allow comparisons
- Reference: [models.py](services/fraud-evaluation-service/src/domain/models.py#L1-L50)

### Clean Architecture Folder Structure
```
services/fraud-evaluation-service/src/
├── domain/              # Pure business logic - NO external imports
│   ├── models.py        # Entities & Value Objects (Transaction, RiskLevel, Location, etc.)
│   └── strategies/      # 7 pluggable fraud strategies
├── application/         # Use cases - orchestrate domain + depend on ports (interfaces)
│   ├── use_cases/       # EvaluateTransactionUseCase, ReviewTransactionUseCase, etc.
│   └── ports/           # Interfaces: TransactionRepository, CacheService, EventPublisher
├── infrastructure/      # Adapters - implement ports (MongoDB, Redis, RabbitMQ)
└── adapters.py          # Dependency injection setup
```

### Test-Driven Development (TDD) Workflow

**Always write tests BEFORE code:**

1. Create test file in `tests/unit/test_[feature].py`
2. Write failing test for domain model or strategy
3. Implement domain logic to pass test
4. Refactor if needed (Red → Green → Refactor cycle)
5. Verify coverage remains ≥70% (`pytest --cov=services --cov-fail-under=70`)

**Test organization:**
- `tests/unit/` - Domain logic, strategies, models (fastest, isolated)
- `tests/integration/` - API endpoints, use case orchestration
- `tests-e2e/` - Full user workflows (Playwright, slowest)

### Testing Requirements

**Backend (pytest):**
- Mark tests: `@pytest.mark.unit` or `@pytest.mark.integration`
- Use fixtures from `tests/conftest.py`
- Mock RabbitMQ, Redis, MongoDB - never run real services in tests
- Minimum coverage: 70%, current: 95%

**Frontend (Vitest + Playwright):**
- Prioritize role-based locators: `getByRole()`, `getByLabel()`, `getByText()`
- Use `test.step()` for readable test reporting
- Playwright tests in `tests-e2e/tests/` (e.g., `tests-e2e/tests/search.spec.ts`)
- Use auto-retrying assertions: `await expect(locator).toHaveText()`

### Git Workflow
- Branch naming: `feature/HU-XXX-description` or `fix/issue-description`
- PR template enforces: tests written first, ≥2 approvals required
- PR checklist items: tests pass locally, Clean Architecture followed, HUMAN REVIEW comments where needed

### HUMAN REVIEW Convention

When suggesting AI assistance or refactoring, add comment:
```python
# HUMAN REVIEW (Developer Name):
# AI suggested X. I chose Y because [reason]. See docs/ARCHITECTURE.md for rationale.
```

This documents non-obvious decisions for future maintainers.

---

## Strategy Pattern (7 Fraud Rules)

Each strategy in `domain/strategies/[strategy_name].py`:
- Inherits from `FraudStrategy` abstract base
- Implements `evaluate(transaction: Transaction, context: UserContext) → RiskLevel`
- Strategies are **stateless and pure functions** - no side effects
- All 7 evaluated in parallel for each transaction

**Examples:**
- `amount_threshold.py` - HIGH_RISK if amount > configured threshold
- `location_check.py` - Compare distance from last known location (uses `geopy`)
- `device_validation.py` - Check if device_id exists in user's device history
- `rapid_transaction.py` - Time delta < threshold between consecutive transactions
- `unusual_time.py` - Transaction outside user's typical time window
- (2 more timezone/velocity rules)

---

## Key Integration Points

### RabbitMQ Message Format
```python
# API publishes to fraud.queue:
{
    "transaction_id": "uuid",
    "user_id": "string",
    "amount": float,
    "location": {"lat": float, "lng": float},
    "device_id": "string",
    "timestamp": "ISO-8601"
}
```

### MongoDB Collections
- `transactions` (append-only audit trail)
- `evaluations` (fraud evaluation results)
- `users` (user profiles)
- `audit_logs` (compliance tracking)

### Redis Keys (cache)
- `user:{user_id}:profile` → user context (TTL: 24h)
- `user:{user_id}:locations` → location history
- `user:{user_id}:devices` → known devices

### Dynamic Rule Configuration
- Thresholds stored in MongoDB collection `fraud_config`
- Updated via `PUT /config/{rule_name}` endpoint
- **Zero-downtime**: Worker reads from Redis cache with fallback to MongoDB
- No restart required

---

## Common Pitfalls & Solutions

| Issue | Solution |
|-------|----------|
| Test fails with "ModuleNotFoundError" | Set `PYTHONPATH=.` or run from project root |
| MongoDB/RabbitMQ connection timeout | Verify `docker-compose ps` shows all services running |
| Domain layer imports FastAPI/Pydantic | Move to infrastructure/ - domain must be framework-agnostic |
| Strategy returns `None` instead of `RiskLevel` | Ensure all code paths return a RiskLevel enum value |
| E2E test times out | Check `docker-compose logs worker` for async job completion |
| Coverage drops below 70% | Add tests to `tests/unit/` before merging (TDD) |

---

## File Reference Guide

| File | Purpose |
|------|---------|
| [README.md](README.md) | Project overview, quick start, user stories |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, layers, data flows (source of truth for architecture) |
| [docs/CONTEXT.md](docs/CONTEXT.md) | Development workflows, Git, CI/CD, known issues |
| [docs/PRODUCT.md](docs/PRODUCT.md) | Business requirements, fraud rules, metrics |
| [docs/user-stories/](docs/user-stories/) | HU-001 through HU-014 (user requirements + acceptance criteria) |
| [pytest.ini](pytest.ini) | Test markers, coverage config (min 70%) |
| [pyproject.toml](pyproject.toml) | Dependencies (FastAPI, pymongo, redis, pika), Poetry config |
| [services/fraud-evaluation-service/src/domain/](services/fraud-evaluation-service/src/domain/) | **START HERE for domain logic** |
| [tests/unit/](tests/unit/) | Unit tests (strategies, models, use cases) |
| [tests-e2e/README.md](tests-e2e/README.md) | Playwright E2E test setup |

---

## Debugging Checklist

1. **Test fails locally but passes in CI?** → Check `PYTHONPATH`, env vars, Docker services
2. **Strategy not evaluating correctly?** → Add debug print in `domain/strategies/`, verify test isolation
3. **API returns 500 instead of 202?** → Check validation in `api-gateway/src/routes/` (Pydantic)
4. **Worker hangs?** → Monitor `docker-compose logs worker`, verify RabbitMQ queue
5. **Coverage drops?** → Run `pytest --cov=services --cov-report=term-missing` to identify untested lines

---

## Updated 2026-01-28 | TDD/BDD enforced | 95% coverage | 14 user stories
