---
title: "CONTEXT - Fraud Detection Engine"
description: "Development environment setup, TDD/BDD workflows, testing standards, git workflow, CI/CD pipeline, and developer guidance"
category: "developer"
audience: ["developers", "qa-engineers", "devops", "technical-writers"]
keywords: ["development-setup", "tdd", "bdd", "testing", "git-workflow", "ci-cd", "docker"]
last_updated: "2026-01-28"
version: "1.0"
source_of_truth: true
ai_friendly: true
---

# 💻 CONTEXT - Fraud Detection Engine

**Single Source of Truth for Development Environment, Workflows, and Developer Guidance**

---

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [TDD/BDD Workflow](#tddbdd-workflow)
- [Creating New User Stories](#creating-new-user-stories)
- [Testing Standards](#testing-standards)
- [Git Workflow](#git-workflow)
- [CI/CD Pipeline](#cicd-pipeline)
- [Common Tasks & Commands](#common-tasks--commands)
- [Technical Decisions Log](#technical-decisions-log)
- [Known Issues & Workarounds](#known-issues--workarounds)

---

## Development Environment Setup

### Prerequisites

- **Python**: 3.11 or later
- **Docker**: 24.0+ with Docker Compose 2.20+
- **Git**: 2.30+
- **Node.js**: 18+ (for frontend development)
- **IDE**: VS Code recommended (with Python, Docker, Git Graph extensions)

### Initial Setup (First Time)

#### 1. Clone & Navigate

```bash
git clone <repository-url>
cd fraud-detection-engine
```

#### 2. Set Up Environment Variables

```bash
# Copy the example to create your local env file
cp .env.local.example .env

# Edit .env if needed (default values work for local development)
cat .env
```

The `.env` file contains:

```env
# MongoDB (development defaults)
MONGODB_USERNAME=admin
MONGODB_PASSWORD=fraud2026dev
MONGODB_URL=mongodb://admin:fraud2026dev@mongodb:27017

# RabbitMQ (development defaults)
RABBITMQ_USERNAME=fraud
RABBITMQ_PASSWORD=fraud2026dev
RABBITMQ_URL=amqp://fraud:fraud2026dev@rabbitmq:5672

# Redis
REDIS_URL=redis://redis:6379

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

#### 3. Start All Services

```bash
# Build and start all containers (first time may take 2-3 minutes)
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs if any service fails
docker-compose logs -f api
```

#### 4. Verify Installation

```bash
# Test API is responsive
curl http://localhost:8000/docs

# Check if MongoDB is running
docker-compose logs mongodb | grep "waiting for connections"

# Test RabbitMQ UI
# Open browser: http://localhost:15672 (user: fraud, pass: fraud2026dev)
```

Expected Services:

| Service | URL | Status Check |
|---------|-----|-------------|
| API Documentation | `http://localhost:8000/docs` | Swagger UI loads |
| MongoDB | `mongodb://localhost:27017` | `docker-compose logs mongodb` |
| Redis | `redis://localhost:6379` | `docker-compose logs redis` |
| RabbitMQ Management | `http://localhost:15672` | Admin UI loads |
| User App | `http://localhost:3000` | React app loads |
| Admin Dashboard | `http://localhost:3001` | React dashboard loads |

### Python Virtual Environment (Alternative Local Setup)

If you want to run API/Worker locally without Docker:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Create virtual environment
poetry env use python3.11
poetry install

# Activate virtual environment
poetry shell

# Run tests locally
pytest tests/unit/ -v

# Start API locally (requires services via Docker)
python services/api-gateway/src/main.py
```

---

## Project Structure

### Directory Hierarchy

```
fraud-detection-engine/
│
├── 📁 services/                          # Backend Python services
│   ├── api-gateway/                      # FastAPI REST API
│   │   ├── src/
│   │   │   ├── main.py                   # FastAPI app initialization
│   │   │   ├── routes.py                 # HTTP endpoint handlers
│   │   │   ├── config.py                 # Environment config loading
│   │   │   └── dependencies.py           # Dependency injection setup
│   │   ├── Dockerfile                    # Container definition
│   │   └── README.md
│   │
│   ├── fraud-evaluation-service/         # Business logic (Core Domain)
│   │   ├── src/
│   │   │   ├── domain/                   # Domain models (pure business logic)
│   │   │   │   ├── models.py             # Transaction, FraudEvaluation entities
│   │   │   │   ├── enums.py              # RiskLevel, Status enums
│   │   │   │   └── strategies/           # Fraud detection strategies
│   │   │   │       ├── __init__.py
│   │   │   │       ├── base.py           # FraudStrategy ABC
│   │   │   │       ├── amount_threshold.py
│   │   │   │       ├── location_check.py
│   │   │   │       ├── device_validation.py
│   │   │   │       ├── rapid_transaction.py
│   │   │   │       ├── unusual_time.py
│   │   │   │       ├── timezone_shift.py
│   │   │   │       └── traveling_velocity.py
│   │   │   │
│   │   │   ├── application/              # Use cases (orchestration)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── evaluate_transaction.py
│   │   │   │   ├── review_transaction.py
│   │   │   │   └── configure_rules.py
│   │   │   │
│   │   │   ├── adapters.py               # Infrastructure adapters
│   │   │   │   ├── MongoDBAdapter
│   │   │   │   ├── RedisAdapter
│   │   │   │   └── RabbitMQAdapter
│   │   │   │
│   │   │   └── config.py                 # Service configuration
│   │   │
│   │   └── README.md
│   │
│   └── worker-service/                   # Background message processor
│       ├── src/
│       │   ├── worker.py                 # Main worker loop
│       │   ├── config.py
│       │   └── handlers.py               # Message handlers
│       ├── Dockerfile
│       └── README.md
│
├── 📁 frontend/                          # React applications
│   ├── user-app/                         # End-user transaction app
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   └── Dockerfile
│   │
│   └── admin-dashboard/                  # Admin fraud review dashboard
│       ├── src/
│       │   ├── App.tsx
│       │   ├── pages/
│       │   │   ├── Dashboard.tsx         # Metrics & trends
│       │   │   ├── Queue.tsx             # Pending reviews
│       │   │   ├── ReviewDetail.tsx      # Manual review UI
│       │   │   ├── Config.tsx            # Rule configuration
│       │   │   └── Analytics.tsx         # Fraud patterns & reports
│       │   ├── components/
│       │   ├── hooks/
│       │   └── services/
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── Dockerfile
│
├── 📁 tests/                             # Backend test suite
│   ├── __init__.py
│   ├── conftest.py                       # pytest fixtures
│   │
│   ├── unit/                             # Unit tests (162 tests)
│   │   ├── test_domain_models.py         # Entity & value object tests
│   │   ├── test_fraud_strategies.py      # Strategy pattern tests
│   │   ├── test_location_strategy.py     # Geographic distance tests
│   │   ├── test_location_edge_cases.py   # Haversine formula edge cases
│   │   ├── test_rapid_transaction_strategy.py
│   │   ├── test_unusual_time_strategy.py
│   │   ├── test_device_validation_strategy.py
│   │   ├── test_use_cases.py             # Use case orchestration tests
│   │   ├── test_routes.py                # HTTP endpoint tests
│   │   ├── test_worker.py                # Worker service tests
│   │   └── test_adapters.py              # MongoDB/Redis/RabbitMQ adapter tests
│   │
│   ├── integration/                      # Integration tests
│   │   ├── test_api_endpoints.py         # Full API flow tests
│   │   └── test_api_live.py              # Live API tests (manual)
│   │
│   └── fixtures/                         # Test data
│       ├── test_transaction_simple.json
│       └── test_low_risk.json
│
├── 📁 tests-e2e/                         # End-to-end tests (Playwright)
│   ├── tests/
│   │   ├── dashboard.spec.ts
│   │   ├── review-flow.spec.ts
│   │   └── configuration.spec.ts
│   ├── pages/
│   │   └── [Page Object Models]
│   ├── tasks/
│   │   └── [Reusable task definitions]
│   ├── playwright.config.ts
│   └── README.md
│
├── 📁 docs/                              # Documentation (this folder)
│   ├── ARCHITECTURE.md                   # ⭐ Technical backbone
│   ├── PRODUCT.md                        # ⭐ Business & user stories
│   ├── CONTEXT.md                        # ⭐ Developer guide (YOU ARE HERE)
│   ├── [Legacy docs consolidated above]
│   └── README.md
│
├── 📁 scripts/                           # Automation scripts
│   ├── run-tests.ps1                     # Run all tests
│   ├── run-tests-docker.ps1              # Tests in Docker
│   ├── run-tests-unified.ps1             # Unified test runner
│   ├── start-all-services.ps1            # Start Docker services
│   ├── test-auth-flow.ps1                # Test specific features
│   └── validate_architecture.py          # Architecture validation script
│
├── 📁 .github/                           # GitHub configuration
│   └── workflows/
│       ├── ci.yml                        # CI pipeline (test, build, scan)
│       ├── deploy.yml                    # CD pipeline (deployment)
│       └── security.yml                  # Security scanning
│
├── docker-compose.yml                    # Single unified compose file
├── pyproject.toml                        # Python project config (Poetry)
├── pytest.ini                            # pytest configuration
├── requirements-test.txt                 # Test dependencies
├── sonar-project.properties              # SonarQube configuration
├── .env.local.example                    # Example environment file
├── .gitignore
├── README.md                             # Project overview
│
└── coverage.xml                          # Generated code coverage report
```

### Key File Purposes

#### Backend Core

- **`services/fraud-evaluation-service/src/domain/`**: Pure business logic (no imports of FastAPI, MongoDB, etc.)
- **`services/fraud-evaluation-service/src/application/`**: Use cases that orchestrate domain logic
- **`services/fraud-evaluation-service/src/adapters.py`**: Implementations of ports (MongoDB, Redis, RabbitMQ)
- **`services/api-gateway/src/main.py`**: FastAPI app setup and route mounting
- **`services/api-gateway/src/routes.py`**: HTTP endpoint definitions and validation

#### Testing

- **`tests/conftest.py`**: Global pytest fixtures, mocks, and setup
- **`tests/unit/`**: Tests that run in isolation (no external services)
- **`tests/integration/`**: Tests that require running services (Docker)

#### Documentation

- **`docs/ARCHITECTURE.md`**: Technical design, layers, patterns (See ARCHITECTURE.md)
- **`docs/PRODUCT.md`**: User stories, business rules, personas (See PRODUCT.md)
- **`docs/CONTEXT.md`**: Development workflows, setup, git (You are reading this!)

---

## TDD/BDD Workflow

This project follows **Test-Driven Development (TDD)** and **Behavior-Driven Development (BDD)** strictly. Every feature is implemented with tests first.

### The TDD Cycle

```
┌─────────────────────────────────────────────┐
│  1. READ User Story (from PRODUCT.md)       │
│     └─ Understand acceptance criteria       │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  2. RED: Write failing test                 │
│     └─ Test fails (code doesn't exist yet)  │
│     └─ Commit: "test: add test for HU-003"  │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  3. GREEN: Write minimal code to pass test  │
│     └─ Test passes                          │
│     └─ Commit: "feat: implement HU-003"     │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  4. REFACTOR: Improve code quality          │
│     └─ Tests still pass                     │
│     └─ Extract functions, remove duplication│
│     └─ Commit: "refactor: simplify strategy"│
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  5. REPEAT: Add edge cases, boundary tests  │
│     └─ Coverage increases to 95%+           │
└─────────────────────────────────────────────┘
```

### Example: Implementing HU-003 (Amount Threshold)

#### Step 1: Read User Story

From [PRODUCT.md](PRODUCT.md#hu-003-detect-high-amount-transactions):

```gherkin
Feature: Detect high-amount transactions

Scenario: Flag transaction exceeding threshold
  Given the amount threshold is configured at $1,500
  When a transaction arrives with amount = $2,000
  Then the risk_level is HIGH_RISK
  And the reason includes "Amount $2,000 exceeds threshold $1,500"
```

#### Step 2: Write Failing Test (RED)

Create `tests/unit/test_amount_threshold_strategy.py`:

```python
import pytest
from services.fraud_evaluation_service.src.domain.strategies.amount_threshold import AmountThresholdStrategy
from services.fraud_evaluation_service.src.domain.models import Transaction, RiskLevel

class TestAmountThresholdStrategy:
    """Tests for amount threshold fraud detection strategy."""
    
    def test_flags_transaction_exceeding_threshold(self):
        """Scenario: Transaction amount exceeds threshold → HIGH_RISK"""
        # Arrange
        strategy = AmountThresholdStrategy(threshold=1500.0)
        transaction = Transaction(
            user_id="user_123",
            amount=2000.0,
            location="4.7110,-74.0721",
            device_id="device_abc",
            timestamp="2026-01-28T10:30:00Z"
        )
        
        # Act
        result = strategy.evaluate(transaction)
        
        # Assert
        assert result.risk_level == RiskLevel.HIGH_RISK
        assert "exceeds threshold" in result.reasons[0].lower()
        assert result.risk_increment == 30
    
    def test_approves_transaction_within_threshold(self):
        """Scenario: Transaction amount within threshold → LOW_RISK"""
        strategy = AmountThresholdStrategy(threshold=1500.0)
        transaction = Transaction(
            user_id="user_123",
            amount=1200.0,
            location="4.7110,-74.0721",
            device_id="device_abc",
            timestamp="2026-01-28T10:30:00Z"
        )
        
        result = strategy.evaluate(transaction)
        
        assert result.risk_level == RiskLevel.LOW_RISK
        assert result.risk_increment == 0
    
    def test_exact_threshold_is_acceptable(self):
        """Scenario: Transaction at exact threshold → LOW_RISK"""
        strategy = AmountThresholdStrategy(threshold=1500.0)
        transaction = Transaction(
            user_id="user_123",
            amount=1500.0,
            location="4.7110,-74.0721",
            device_id="device_abc",
            timestamp="2026-01-28T10:30:00Z"
        )
        
        result = strategy.evaluate(transaction)
        
        assert result.risk_level == RiskLevel.LOW_RISK
```

Run tests:

```bash
pytest tests/unit/test_amount_threshold_strategy.py -v
# Result: ❌ FAILED - AmountThresholdStrategy doesn't exist
```

#### Step 3: Write Minimal Code (GREEN)

Create `services/fraud-evaluation-service/src/domain/strategies/amount_threshold.py`:

```python
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

class RiskLevel(Enum):
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"

@dataclass
class EvaluationResult:
    risk_level: RiskLevel
    reasons: list[str]
    risk_increment: int

class FraudStrategy(ABC):
    @abstractmethod
    def evaluate(self, transaction) -> EvaluationResult:
        pass

class AmountThresholdStrategy(FraudStrategy):
    def __init__(self, threshold: float):
        self.threshold = threshold
    
    def evaluate(self, transaction) -> EvaluationResult:
        if transaction.amount > self.threshold:
            return EvaluationResult(
                risk_level=RiskLevel.HIGH_RISK,
                reasons=[f"Amount ${transaction.amount} exceeds threshold ${self.threshold}"],
                risk_increment=30
            )
        return EvaluationResult(
            risk_level=RiskLevel.LOW_RISK,
            reasons=[],
            risk_increment=0
        )
```

Run tests again:

```bash
pytest tests/unit/test_amount_threshold_strategy.py -v
# Result: ✅ PASSED (3/3 tests)
```

#### Step 4: Refactor (if needed)

In this case, the code is already simple and clear. No refactoring needed.

#### Step 5: Add Edge Cases

```python
def test_negative_amount_rejected(self):
    """Edge case: Negative amounts should be rejected at model level"""
    with pytest.raises(ValueError):
        Transaction(
            user_id="user_123",
            amount=-500.0,  # Invalid
            location="4.7110,-74.0721",
            device_id="device_abc",
            timestamp="2026-01-28T10:30:00Z"
        )

def test_zero_amount_allowed(self):
    """Edge case: Zero amount (refund) is allowed"""
    strategy = AmountThresholdStrategy(threshold=1500.0)
    transaction = Transaction(
        user_id="user_123",
        amount=0.0,
        location="4.7110,-74.0721",
        device_id="device_abc",
        timestamp="2026-01-28T10:30:00Z"
    )
    result = strategy.evaluate(transaction)
    assert result.risk_level == RiskLevel.LOW_RISK
```

### BDD: Gherkin Syntax

For integration/E2E tests, use Gherkin syntax that matches acceptance criteria:

```gherkin
# tests-e2e/tests/fraud-detection.spec.ts (Playwright)

import { test, expect } from '@playwright/test';

test.describe('Amount Threshold Rule', () => {
  test('should flag transactions exceeding $1,500 threshold', async ({ page }) => {
    // Navigate to API docs
    await page.goto('http://localhost:8000/docs');
    
    // Execute API request (via Swagger UI or direct fetch)
    const response = await page.request.post('http://localhost:8000/api/v1/transactions/evaluate', {
      data: {
        user_id: 'user_123',
        amount: 2000.0,
        location: '4.7110,-74.0721',
        device_id: 'device_abc'
      }
    });
    
    const result = await response.json();
    expect(result.status).toBe('processing');
    
    // Wait for background evaluation
    await page.waitForTimeout(2000);
    
    // Query audit trail
    const auditResponse = await page.request.get(
      `http://localhost:8000/api/v1/audit/transaction/${result.transaction_id}`
    );
    
    const evaluation = await auditResponse.json();
    expect(evaluation.risk_level).toBe('HIGH_RISK');
    expect(evaluation.reasons).toContainEqual(
      expect.stringContaining('exceeds threshold')
    );
  });
});
```

---

## Creating New User Stories

When implementing a new user story, follow this process:

### 1. Add to PRODUCT.md

Document the user story in [PRODUCT.md](PRODUCT.md#user-stories--acceptance-criteria) with:

```markdown
#### HU-015: [New Feature Title]

**As a** [user type]
**I want** [capability]
**So that** [business value]

**Acceptance Criteria:**

\`\`\`gherkin
Scenario: [First scenario]
  Given [precondition]
  When [action]
  Then [expected outcome]
\`\`\`

**Estimation**: [X story points]
**Priority**: [CRITICAL/HIGH/MEDIUM/LOW]
**Dependency**: [Other HU IDs if applicable]
```

### 2. Create Test File

In `tests/unit/`, create `test_hu_015.py`:

```python
import pytest
from [service_path] import [ClassUnderTest]

class TestHU015:
    """Tests for HU-015: [Feature Title]"""
    
    def test_acceptance_criterion_1(self):
        """Scenario: [First scenario]"""
        # Arrange, Act, Assert
        pass
    
    def test_acceptance_criterion_2(self):
        """Scenario: [Second scenario]"""
        pass
```

### 3. Write Red Tests

Run tests—they should fail:

```bash
pytest tests/unit/test_hu_015.py -v
# ❌ FAILED: [Class] not found or not implemented
```

### 4. Implement Feature

Add implementation in appropriate service:

- **Domain logic** → `services/fraud-evaluation-service/src/domain/`
- **API endpoint** → `services/api-gateway/src/routes.py`
- **Background processing** → `services/worker-service/src/worker.py`

### 5. Run Tests Again

```bash
pytest tests/unit/test_hu_015.py -v
# ✅ PASSED (all tests)
```

### 6. Commit with Clear Message

```bash
git add tests/unit/test_hu_015.py services/...
git commit -m "test(hu-015): Write tests for [feature]"

git add services/...
git commit -m "feat(hu-015): Implement [feature]"

git add tests/
git commit -m "test(hu-015): Add edge cases and coverage"
```

### 7. Create Pull Request

Push to feature branch and create PR with:

```markdown
## HU-015: [Feature Title]

### Changes
- Added `[ClassName]` to handle [responsibility]
- Added [N] tests for acceptance criteria
- Coverage: 95%

### Related
- [PRODUCT.md](../docs/PRODUCT.md#hu-015)
- Fixes #[issue-number]

### Testing
- `pytest tests/unit/test_hu_015.py -v` ✅ Passing
- Manual testing: [Describe any manual steps]
```

---

## Testing Standards

### Test Organization

```
tests/unit/
├── test_domain_models.py          # Domain entities & value objects
├── test_fraud_strategies.py       # Strategy pattern tests (all rules)
├── test_location_strategy.py      # Geographic distance calculation
├── test_location_edge_cases.py    # Boundary conditions for Haversine
├── test_rapid_transaction_strategy.py
├── test_unusual_time_strategy.py
├── test_device_validation_strategy.py
├── test_use_cases.py              # EvaluateTransactionUseCase, etc.
├── test_routes.py                 # FastAPI endpoint tests
├── test_worker.py                 # Background worker tests
└── test_adapters.py               # MongoDB, Redis, RabbitMQ adapter tests
```

### Test Quality Checklist

Before marking a PR as ready, ensure:

- [ ] **All tests pass**: `pytest tests/ -v` returns 100%
- [ ] **Coverage ≥ 95%**: `pytest tests/ --cov=services --cov-report=term-missing`
- [ ] **No skipped tests**: Use `@pytest.mark.skip` only with issue reference
- [ ] **No hardcoded secrets**: Use fixtures or environment variables
- [ ] **Docstrings present**: Each test describes what it validates
- [ ] **Isolated tests**: No test depends on another test's side effects
- [ ] **Async tests marked**: Use `@pytest.mark.asyncio` for async functions

### Running Tests

#### All Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=services --cov-report=html

# Coverage report opens in htmlcov/index.html
```

#### Specific Test File

```bash
pytest tests/unit/test_fraud_strategies.py -v
```

#### Single Test

```bash
pytest tests/unit/test_fraud_strategies.py::TestAmountThreshold::test_flags_high_amount -v
```

#### Tests by Pattern

```bash
# All tests for location rule
pytest tests/ -k location -v

# All HU-003 related tests
pytest tests/ -k "hu_003 or amount_threshold" -v
```

#### With Coverage Report

```bash
pytest tests/ --cov=services --cov-report=term-missing --cov-report=html
open htmlcov/index.html
```

### Fixture Management

In `tests/conftest.py`, define reusable fixtures:

```python
import pytest
from services.fraud_evaluation_service.src.domain.models import Transaction

@pytest.fixture
def sample_transaction():
    """A valid low-risk transaction for testing."""
    return Transaction(
        user_id="user_123",
        amount=500.0,
        location="4.7110,-74.0721",
        device_id="device_abc",
        timestamp="2026-01-28T10:30:00Z"
    )

@pytest.fixture
def high_risk_transaction():
    """A transaction that should trigger HIGH_RISK."""
    return Transaction(
        user_id="user_123",
        amount=2500.0,  # Exceeds threshold
        location="25.7617,-80.1918",  # Far from base
        device_id="device_unknown",  # Unknown device
        timestamp="2026-01-28T03:00:00Z"  # Unusual time
    )

@pytest.fixture
def mongodb_mock(mocker):
    """Mock MongoDB adapter."""
    return mocker.MagicMock()
```

Use in tests:

```python
def test_evaluate_transaction(sample_transaction, mongodb_mock):
    # sample_transaction and mongodb_mock are injected
    evaluator = FraudEvaluator(strategies=[...], repository=mongodb_mock)
    result = evaluator.evaluate(sample_transaction)
    assert result.risk_level == RiskLevel.LOW_RISK
```

---

## Git Workflow

### Branch Naming Convention

```
feature/[service]-[feature-name]      # New feature
  └─ feature/api-gateway-rate-limiting
  └─ feature/fraud-eval-ml-integration

bugfix/[service]-[issue-name]         # Bug fix
  └─ bugfix/worker-rabbitmq-reconnect

hotfix/[critical-issue]               # Critical production fix
  └─ hotfix/security-sql-injection

refactor/[scope]                      # Code refactoring
  └─ refactor/strategy-pattern-simplify

docs/[topic]                          # Documentation updates
  └─ docs/add-deployment-guide
```

### Commit Message Format

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`  
**Scope**: Service or area (`api-gateway`, `fraud-eval`, `worker`, `frontend-admin`)  
**Subject**: Imperative mood, lowercase, no period

**Examples**:

```bash
git commit -m "feat(api-gateway): Add rate limiting middleware"

git commit -m "fix(worker): Handle RabbitMQ reconnection gracefully

When the worker loses connection to RabbitMQ, it would crash.
Now it implements exponential backoff and reconnection logic.

Fixes #452"

git commit -m "test(fraud-eval): Add edge cases for Haversine distance

Added tests for:
- Antipodal points (opposite ends of Earth)
- Zero distance (same location)
- Crossing dateline"

git commit -m "docs(context): Update TDD workflow section"
```

### Pull Request Process

#### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/api-gateway-rate-limiting
```

#### 2. Make Changes & Commit

```bash
# Create test file
touch tests/unit/test_rate_limiting.py
# ... write tests ...
git add tests/
git commit -m "test(api-gateway): Add rate limiting tests"

# Implement feature
# ... write implementation ...
git add services/api-gateway/src/
git commit -m "feat(api-gateway): Implement rate limiting middleware"
```

#### 3. Push & Open PR

```bash
git push origin feature/api-gateway-rate-limiting
# Click GitHub link to open PR
```

#### 4. PR Description Template

```markdown
## Description
Brief explanation of what this PR accomplishes.

## Related Issue
Fixes #[issue-number]
Related to HU-[user-story-number]

## Changes
- [ ] Feature A
- [ ] Feature B
- [ ] Updated documentation

## Testing
- [x] Unit tests written (N new tests)
- [x] Coverage: 95%+
- [ ] Manual testing: [describe steps]
- [ ] E2E tests added

## Checklist
- [x] Code follows style guide
- [x] Self-reviewed my own code
- [x] Comments added for complex logic
- [x] Documentation updated (PRODUCT.md, CONTEXT.md, etc.)
- [x] No new warnings generated
- [x] Tests pass locally

## Screenshots (if UI changes)
[Attach before/after if relevant]
```

#### 5. Code Review & Approval

- At least 1 reviewer required
- CI/CD pipeline must pass
- Coverage must maintain 95%+

#### 6. Merge to Develop

```bash
# After approval, merge via GitHub UI
# or locally:
git checkout develop
git pull origin develop
git merge --no-ff feature/api-gateway-rate-limiting
git push origin develop
```

### Syncing with Main Branch

Only Risk Manager or Team Lead merges `develop` → `main`:

```bash
# On main branch
git checkout main
git pull origin main

# Merge develop (release)
git merge --no-ff develop

# Create release tag
git tag -a v1.2.0 -m "Release version 1.2.0"

# Push
git push origin main
git push origin v1.2.0
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

Located in `.github/workflows/`

#### ci.yml - Continuous Integration

Runs on every push to `develop`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ develop ]
  pull_request:
    branches: [ develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        run: pytest tests/ -v --cov=services --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
      
      - name: Run SonarQube scan
        run: |
          sonar-scanner \
            -Dsonar.projectKey=fraud-detection-engine \
            -Dsonar.sources=services \
            -Dsonar.host.url=${{ secrets.SONAR_HOST_URL }} \
            -Dsonar.login=${{ secrets.SONAR_TOKEN }}
      
      - name: Build Docker images
        run: docker-compose build
```

#### deploy.yml - Continuous Deployment

Runs on release/merge to `main`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker images
        run: |
          docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}
          docker-compose build
          docker-compose push
      
      - name: Deploy to production
        run: |
          # Example: Deploy to Kubernetes, Azure Container Instances, etc.
          kubectl set image deployment/api api=${{ secrets.REGISTRY }}/api:latest
```

### Local Testing Before Commit

```bash
# Run all tests
pytest tests/ -v --cov=services

# Check code quality
pylint services/**/*.py

# Format code
black services/

# Sort imports
isort services/
```

---

## Common Tasks & Commands

### Start Development Environment

```bash
# Start all services (MongoDB, Redis, RabbitMQ, API, Worker, Frontends)
docker-compose up -d

# Verify all services running
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f worker
```

### Stop Services

```bash
# Stop without removing containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and delete volumes (data)
docker-compose down -v
```

### Run Tests

```bash
# Backend tests
pytest tests/ -v

# Backend tests with coverage
pytest tests/ --cov=services --cov-report=html

# Frontend tests (user-app)
cd frontend/user-app && npm test

# E2E tests (Playwright)
cd tests-e2e && npm test
```

### Develop Locally (Without Docker)

```bash
# Install Python dependencies
poetry install
poetry shell

# Run tests locally
pytest tests/unit/ -v

# Run API server locally (requires services via Docker)
python services/api-gateway/src/main.py
# API runs on http://localhost:8000

# Run worker locally
python services/worker-service/src/worker.py
```

### Develop Frontend

```bash
# User App
cd frontend/user-app
npm install
npm run dev  # http://localhost:5173

# Admin Dashboard
cd frontend/admin-dashboard
npm install
npm run dev  # http://localhost:5174
```

### Database Operations

#### MongoDB

```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh -u admin -p fraud2026dev

# List databases
show dbs

# Use fraud database
use fraud

# Find all evaluations
db.evaluations.find()

# Find specific transaction
db.evaluations.findOne({ "_id": "txn_uuid" })

# Count documents
db.evaluations.countDocuments()

# Clear database (WARNING: Destructive!)
db.evaluations.deleteMany({})
```

#### Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# List all keys
KEYS *

# Get user location
GET user:user_123:location

# Get user devices (set)
SMEMBERS user:user_123:devices

# Clear cache (WARNING: Destructive!)
FLUSHALL
```

### Build Docker Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build api
docker-compose build worker

# Build without cache
docker-compose build --no-cache
```

### Generate Code Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=services --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux

# Generate XML for CI/CD
pytest tests/ --cov=services --cov-report=xml
```

---

## Technical Decisions Log

### Decision: Event-Driven Async Processing

**Context**: Should the API wait for fraud evaluation before responding?

**Decision**: Use asynchronous processing with message queue (RabbitMQ)

**Rationale**:
- API responds immediately (202 Accepted) for low latency
- Evaluation happens in background Worker
- Unbounded processing time for complex rules
- System can scale horizontally (add more workers)

**Alternatives Considered**:
- Synchronous: API waits for evaluation (slower, limits throughput)
- Periodic batch: Process transactions every N minutes (higher latency)

**Consequences**:
- ✅ High throughput, low latency
- ✅ Horizontal scaling
- ❌ Added complexity (RabbitMQ, eventual consistency)
- ❌ Requires careful message handling (idempotency, retries)

---

### Decision: Clean Architecture with Layered Separation

**Context**: How to structure business logic so it's independent of frameworks?

**Decision**: Implement Clean Architecture with strict layer separation:
- Domain (no external dependencies)
- Application (use cases, DI)
- Infrastructure (adapters)

**Rationale**:
- Business logic not tied to FastAPI or MongoDB
- Easy to test domain in isolation
- Easy to swap implementations (PostgreSQL instead of MongoDB)
- Scales with team growth

**Trade-offs**:
- ✅ Testable, flexible, scalable
- ❌ More boilerplate, more interfaces
- ❌ Steeper learning curve for junior developers

---

### Decision: Strategy Pattern for Fraud Rules

**Context**: How to structure 7 different fraud detection rules?

**Decision**: Use Strategy pattern—each rule is independent, pluggable, composable

**Code**:

```python
class FraudStrategy(ABC):
    @abstractmethod
    def evaluate(self, transaction: Transaction) -> EvaluationResult:
        pass

# Each rule: AmountThreshold, LocationCheck, etc. implements FraudStrategy

# Composer
class FraudEvaluator:
    def __init__(self, strategies: List[FraudStrategy]):
        self.strategies = strategies  # Flexible composition
    
    def evaluate(self, transaction) -> FraudEvaluation:
        results = [s.evaluate(transaction) for s in self.strategies]
        # Aggregate results...
```

**Benefits**:
- ✅ Each rule tested independently
- ✅ Rules don't interfere with each other
- ✅ Easy to add new rules (just implement FraudStrategy)
- ✅ Easy to enable/disable rules (filter strategies list)
- ✅ Rules are composable in different orders

---

### Decision: MongoDB for Audit Trail (Append-Only)

**Context**: How to store fraud evaluation decisions?

**Decision**: Use MongoDB with append-only collection (no updates)

**Design**:

```python
# Once created, never updated
db.evaluations.insert_one({
    "_id": transaction_id,
    "user_id": "user_123",
    "amount": 500.0,
    "risk_level": "HIGH_RISK",
    "reasons": ["Amount exceeds..."],
    "analyst_decision": "PENDING",  # Updated AFTER by adding new record
    "timestamp": ISO8601,
    "created_at": ISO8601
})

# If analyst approves, create NEW record (not update)
db.evaluations_reviews.insert_one({
    "transaction_id": transaction_id,
    "analyst_id": "analyst_123",
    "decision": "APPROVED",
    "notes": "Customer confirmed",
    "timestamp": ISO8601
})
```

**Trade-offs**:
- ✅ Immutable audit trail (compliance requirement)
- ✅ No accidental overwrites
- ✅ Complete history preserved
- ❌ Requires application-level joins for related data
- ❌ Not relational (can't enforce foreign key constraints)

---

## Known Issues & Workarounds

### Issue #1: Worker Reconnection on RabbitMQ Restart

**Status**: OPEN  
**Severity**: MEDIUM  
**Description**: If RabbitMQ restarts, worker process doesn't automatically reconnect

**Workaround**: Manually restart worker container

```bash
docker-compose restart worker
```

**Planned Fix**: Implement exponential backoff + reconnection logic  
**ETA**: Q1 2026

---

### Issue #2: Redis TTL Not Enforced for User Locations

**Status**: OPEN  
**Severity**: LOW  
**Description**: User location cache entries aren't expiring after 24 hours

**Workaround**: Manually flush Redis cache when needed

```bash
docker-compose exec redis redis-cli FLUSHALL
```

**Root Cause**: TTL parameter not passed to Redis SET command  
**Planned Fix**: Add TTL support to RedisAdapter  
**ETA**: Q1 2026

---

### Issue #3: Location Boundary Conditions

**Status**: CLOSED ✅  
**Severity**: LOW  
**Description**: Haversine distance calculation was incorrect for antipodal points

**Resolution**: Added comprehensive edge case tests and fixed calculation  
**Tests Added**: `test_location_edge_cases.py` (21 tests)  
**Commit**: `fix(location): Handle antipodal points in Haversine`

---

### Known Limitations

1. **No Machine Learning**: Currently rules-based only; ML models not integrated
2. **Single Admin User**: No multi-tenant support yet
3. **No Whitelist/Blacklist**: HU-014 not yet implemented
4. **Limited Geographic Coverage**: Tested with US locations only
5. **No Real-time Alerts**: No Slack/PagerDuty integration yet

---

**Document Version**: 1.0  
**Last Updated**: January 28, 2026  
**Owner**: Engineering Team  
**Status**: Active - Single Source of Truth
