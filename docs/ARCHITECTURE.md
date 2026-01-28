---
title: "ARCHITECTURE - Fraud Detection Engine"
description: "Clean architecture, microservices design, fraud evaluation strategies, async processing, and technology stack"
category: "technical"
audience: ["engineers", "architects", "tech-leads"]
keywords: ["clean-architecture", "microservices", "fraud-detection", "async-processing", "strategy-pattern"]
last_updated: "2026-01-28"
version: "2.0"
source_of_truth: true
ai_friendly: true
---

# 🏗️ ARCHITECTURE - Fraud Detection Engine

**Real-time fraud detection using Clean Architecture, microservices, and async event-driven processing**

---

## System Overview

A **Clean Architecture-based microservice system** for real-time fraud detection using 7 independent, composable fraud strategies. Designed for immediate API response (202 Accepted) with asynchronous background processing, immutable audit trails, and zero-downtime configuration updates.

### Core Characteristics
- ✅ **Clean Architecture**: Domain logic completely decoupled from frameworks
- ✅ **Async-First**: 202 Accepted response + background processing via RabbitMQ
- ✅ **Strategy Pattern**: 7 pluggable fraud detection strategies evaluated in parallel
- ✅ **Immutable Audit Trail**: Append-only MongoDB records for compliance
- ✅ **Zero-Downtime Rules**: Update thresholds via dashboard without restart

### Key Metrics
| Metric | Value |
|--------|-------|
| **Test Coverage** | 95% (162 tests) |
| **API Response** | <100ms (202 Accepted) |
| **Fraud Strategies** | 7 active rules |
| **User Stories** | 14 implemented |
| **Throughput** | 10,000+ tx/sec (async) |

---

## Architecture Overview

```mermaid
graph TB
    subgraph CLIENT["🖥️ CLIENT LAYER"]
        UserApp["📱 User App<br/>(React/Vite)"]
        AdminDash["📊 Admin Dashboard<br/>(React/Vite)"]
    end

    subgraph API["🌐 API GATEWAY<br/>(FastAPI)"]
        REST["REST Endpoints<br/>POST /transaction → 202<br/>GET /audit/*<br/>PUT /config/*"]
        VALIDATE["Pydantic Validation<br/>Dependency Injection"]
    end

    subgraph MESSAGING["🐰 MESSAGE QUEUE<br/>(RabbitMQ)"]
        QUEUE["fraud.queue<br/>TRANSACTION_SUBMITTED"]
    end

    subgraph WORKER["🔄 WORKER SERVICE<br/>(Background)"]
        FETCH["1. Fetch User Context<br/>(Redis)"]
        
        subgraph CORE["🧠 FRAUD CORE<br/>(Pure Python)"]
            S1["Amount<br/>Threshold"]
            S2["Location<br/>Check"]
            S3["Device<br/>Validation"]
            S4["Rapid<br/>Txn"]
            S5["Unusual<br/>Time"]
            S6["Timezone<br/>Shift"]
            S7["Traveling<br/>Velocity"]
            AGG["Aggregate<br/>Risk Level"]
        end
        
        SAVE["3. Persist & Cache<br/>MongoDB + Redis"]
    end

    subgraph DATA["🗄️ DATA LAYER"]
        MONGO["📌 MongoDB 7.0<br/>(Audit Trail)"]
        REDIS["⚡ Redis 7.2<br/>(Performance Cache)"]
    end

    UserApp -->|HTTP/REST| REST
    AdminDash -->|HTTP/REST| REST
    REST --> VALIDATE
    VALIDATE -->|Publish| QUEUE
    REST -->|Query| MONGO
    REST -->|Read/Write| REDIS
    
    QUEUE -->|Consume| FETCH
    FETCH -->|Get Context| REDIS
    FETCH --> S1
    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> AGG
    AGG --> SAVE
    SAVE -->|Write| MONGO
    SAVE -->|Update| REDIS
    
    classDef client fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef api fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef queue fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef worker fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class CLIENT client
    class API api
    class MESSAGING queue
    class WORKER,CORE worker
    class DATA data
```

---

## Layered Architecture

### Domain Layer (Pure Business Logic)
- **No external dependencies**: No FastAPI, MongoDB, Redis, or RabbitMQ imports
- **Entities & Value Objects**: `Transaction`, `FraudEvaluation`, `Location`, `RiskLevel`
- **7 Fraud Strategies**: Each implements `FraudStrategy` interface
- **Use Cases**: `EvaluateTransactionUseCase`, `ReviewTransactionUseCase`, `ConfigureRulesUseCase`

### Application Layer (Orchestration)
- **Dependency Injection**: Use cases receive dependencies via constructor
- **Ports (Interfaces)**: `TransactionRepository`, `CacheService`, `EventPublisher`, `ConfigRepository`
- **No Framework Code**: Pure Python orchestration logic

### Infrastructure Layer (Adapters)
- **MongoDB Adapter**: Implements `TransactionRepository` for append-only audit logs
- **Redis Adapter**: Implements `CacheService` for user profiles, locations, devices
- **RabbitMQ Adapter**: Implements `EventPublisher` for async messaging
- **FastAPI Adapter**: HTTP routes that depend on application layer

---

## Transaction Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant Queue as RabbitMQ
    participant Worker as Worker Service
    participant Core as Fraud Core
    participant DB as MongoDB
    participant Cache as Redis
    
    Client->>API: POST /transaction {user_id, amount, location, device_id}
    API->>API: Validate payload (Pydantic)
    API->>Queue: Publish TRANSACTION_SUBMITTED
    API->>Client: Return 202 Accepted {transaction_id}
    
    Queue->>Worker: Consume message
    Worker->>Cache: GET user profile
    Worker->>Core: Create Transaction entity
    Core->>Core: Apply 7 strategies (parallel)
    Core->>Core: Aggregate risk levels
    Core->>Core: Compute final RiskLevel
    
    Core->>DB: INSERT FraudEvaluation (immutable)
    Core->>Cache: UPDATE user location & devices
    Worker->>Queue: ACK message
    
    Note over DB,Cache: Result ready for query
    
    Client->>API: GET /audit/{transaction_id}
    API->>DB: Query evaluation
    API->>Client: Return FraudEvaluation details
```

---

## Fraud Evaluation Strategies

| # | Strategy | Rule | Impact | Implementation |
|---|----------|------|--------|-----------------|
| 1️⃣ | **Amount Threshold** | Amount > $1,500 | +30% risk | Configurable via admin dashboard |
| 2️⃣ | **Location Check** | Distance > 100 km | +25% risk | Requires GPS location in request |
| 3️⃣ | **Device Validation** | Unknown device_id | +20% risk | Tracks devices in Redis per user |
| 4️⃣ | **Rapid Transactions** | 3+ in 10 min | +15% risk | Time-window counter in Redis |
| 5️⃣ | **Unusual Time** | Off-hours activity | +10% risk | User behavior profile |
| 6️⃣ | **Timezone Shift** | Location/TZ mismatch | +15% risk | Detects impossible jumps |
| 7️⃣ | **Traveling Velocity** | Speed > 900 km/h | +25% risk | Last known location check |

**Result**: Risk increments summed → Risk Level determined:
- **0-33%** = `LOW_RISK` (auto-approve)
- **34-66%** = `MEDIUM_RISK` (queue for human review)
- **67%+** = `HIGH_RISK` (require approval)

---

## Design Patterns & Best Practices

| Pattern | Purpose | Example |
|---------|---------|---------|
| **Strategy** | Pluggable fraud rules | Each strategy independent, testable, composable |
| **Dependency Injection** | Decouple from concrete implementations | Use cases receive dependencies via constructor |
| **Repository** | Abstract data access | Swap MongoDB for PostgreSQL without touching domain |
| **Event-Driven** | Async, loosely coupled services | RabbitMQ events decouple API from Worker |
| **Immutability** | Audit trail compliance | Append-only MongoDB, no updates after creation |

---

## Technology Stack

```
🐍 Backend          FastAPI 0.104+, Python 3.11+, asyncio/uvicorn
🌐 Frontend         React 18.3+, TypeScript 5.x, Vite 6.x, TailwindCSS
🗄️ Database         MongoDB 7.0 (audit), Redis 7.2 (cache)
🐰 Messaging        RabbitMQ 3.12 (async processing)
📦 Package Manager  Poetry (lock file, reproducible builds)
🧪 Testing          pytest 7.4+, coverage 7.3+ (95% coverage)
🐳 Containerization Docker 24.0+, Docker Compose 2.20+
```

---

## Deployment & Configuration

### Local Development
```bash
docker-compose up -d
# Services: API (8000), Admin (3001), User App (3000)
```

### Configuration Management
- **Dynamic Rules**: Update thresholds via `PUT /api/v1/config/thresholds`
- **Zero Downtime**: New transactions use updated rules immediately
- **Event-Driven**: Workers reload rules from `RULE_UPDATED` event

### Security & Compliance
- **HTTPS/TLS**: Enforced in production
- **Data Protection**: No card storage, masked sensitive data in logs
- **Compliance**: PCI DSS, GDPR, SOX, AML-ready
- **Audit Trail**: Immutable timestamps, actor info, complete reasoning

---

**Version**: 2.0 | **Updated**: Jan 28, 2026 | **Status**: Active Source of Truth

---

## Layered Architecture

### Domain Layer

**Location**: `services/fraud-evaluation-service/src/domain/`

Implements pure business logic with no external dependencies.

#### Core Models

```python
# Value Objects & Entities
- Transaction(user_id, amount, location, device_id, timestamp)
- Location(latitude, longitude)
- RiskLevel(LOW_RISK, MEDIUM_RISK, HIGH_RISK)
- FraudEvaluation(transaction_id, risk_level, reasons, strategies_applied)
```

#### Fraud Strategies

Implemented using the **Strategy Pattern**. Each strategy evaluates one aspect:

| Strategy | Rule | Threshold | Risk Increment |
|----------|------|-----------|-----------------|
| **AmountThreshold** | Amount exceeds configured limit | $1,500 USD | +30% |
| **LocationCheck** | Distance from known location > 100 km | 100 km | +25% |
| **DeviceValidation** | Device_id not in user's known devices | N/A | +20% |
| **RapidTransaction** | Multiple txns in short time window | 3+ in 10 min | +15% |
| **UnusualTime** | Transaction outside user's typical hours | Configurable | +10% |
| **TimezoneShift** | Timezone inconsistent with location | N/A | +15% |
| **TravelingVelocity** | Impossible geographic distance/time | >900 km/h | +25% |

```python
# Strategy Interface (Port)
class FraudStrategy(ABC):
    @abstractmethod
    def evaluate(self, transaction: Transaction) -> EvaluationResult:
        """Returns risk_level, reasons, and risk_increment"""
        pass

# Composition
class FraudEvaluator:
    def __init__(self, strategies: List[FraudStrategy]):
        self.strategies = strategies
    
    def evaluate(self, transaction: Transaction) -> FraudEvaluation:
        # Apply all strategies, aggregate results
        pass
```

### Application Layer

**Location**: `services/fraud-evaluation-service/src/application/`

Orchestrates use cases using dependency injection. Depends on domain models and repository/cache interfaces.

#### Use Cases

1. **EvaluateTransactionUseCase**
   - Input: Transaction data
   - Process: Apply all strategies, compute aggregated risk level
   - Output: FraudEvaluation record
   - Dependencies: `FraudEvaluator`, `TransactionRepository`, `CacheService`

2. **ReviewTransactionUseCase**
   - Input: Transaction ID, analyst decision, justification
   - Process: Update evaluation, store manual override
   - Output: Updated FraudEvaluation
   - Dependencies: `TransactionRepository`, `AuditLogger`

3. **ConfigureRulesUseCase** (HU-008/009)
   - Input: Rule parameters (thresholds, enabled/disabled flags)
   - Process: Validate, persist, invalidate caches
   - Output: Configuration confirmed
   - Dependencies: `ConfigRepository`, `CacheService`, `EventPublisher`

#### Ports (Interfaces)

```python
# Repositories (Data Access)
TransactionRepository:
  - save(fraud_evaluation: FraudEvaluation) → None
  - get_by_id(transaction_id: str) → Optional[FraudEvaluation]
  - get_by_user(user_id: str, limit: int) → List[FraudEvaluation]

# Cache (High-Speed Lookup)
CacheService:
  - get(key: str) → Optional[Any]
  - set(key: str, value: Any, ttl_seconds: int) → None
  - delete(key: str) → None

# Messaging (Async Events)
EventPublisher:
  - publish(event_type: str, payload: Dict) → None

# Configuration
ConfigRepository:
  - get_rule_config(rule_name: str) → RuleConfig
  - set_rule_config(rule_name: str, config: RuleConfig) → None
```

### Infrastructure Layer

**Location**: `services/api-gateway/src`, `services/fraud-evaluation-service/src/adapters.py`, `services/worker-service/src`

Implements ports and provides HTTP/database/messaging interfaces.

#### Adapters

```
Repositories:
  └── MongoDBAdapter (implements TransactionRepository)
      └── Collections: transactions (auditable, append-only)

Cache:
  └── RedisAdapter (implements CacheService)
      └── Keys: user:{user_id}:location, rules:*, config:*

Messaging:
  └── RabbitMQAdapter (implements EventPublisher)
      └── Exchanges: fraud.evaluations, fraud.reviews

HTTP:
  └── FastAPI (implements REST API)
      └── Routes: /transaction, /audit/*, /config/*
```

---

## Microservices Structure

### 1. API Gateway (`services/api-gateway`)

**Responsibility**: HTTP request handling, validation, dependency injection.

**Key Endpoints:**

```
POST /api/v1/transactions/evaluate
  ├─ Request: { user_id, amount, location, device_id }
  └─ Response: 202 Accepted with transaction_id

GET /api/v1/audit/all
  ├─ Query: ?user_id=, ?risk_level=, ?limit=100
  └─ Response: [FraudEvaluation]

GET /api/v1/audit/transaction/{id}
  ├─ Response: FraudEvaluation detail

PUT /api/v1/transaction/review/{id}
  ├─ Request: { decision: APPROVED|REJECTED, justification }
  └─ Response: Updated FraudEvaluation

GET /api/v1/config/thresholds
  └─ Response: Current rule configuration

PUT /api/v1/config/thresholds
  ├─ Request: { rule_name, threshold_value }
  └─ Response: Configuration updated

GET /health
  └─ Response: { status: "healthy" }
```

**Technologies**: FastAPI 0.104+, Pydantic, Python 3.11+

### 2. Fraud Evaluation Service (`services/fraud-evaluation-service`)

**Responsibility**: Core business logic for fraud detection.

**Key Classes**:

- `Transaction`: Domain entity
- `FraudEvaluation`: Result entity
- `FraudStrategy` (ABC): Strategy pattern base
- `*Strategy`: Concrete strategy implementations
- `EvaluateTransactionUseCase`: Main orchestrator
- `MongoDBAdapter`, `RedisAdapter`, `RabbitMQAdapter`: Infrastructure adapters

**No HTTP dependency**: Pure Python module, importable by both API and Worker.

### 3. Worker Service (`services/worker-service`)

**Responsibility**: Asynchronous background processing of transactions.

**Flow**:

```python
while True:
    message = rabbitmq.consume('fraud.queue')  # blocks
    transaction = Transaction.from_dict(message)
    
    # Use the fraud-evaluation-service
    evaluation = EvaluateTransactionUseCase(
        repositories=...,
        strategies=...
    ).execute(transaction)
    
    # Persist result
    mongodb.save(evaluation)
    
    # Update caches
    redis.update_user_location(...)
    redis.update_user_device(...)
    
    # Acknowledge message
    rabbitmq.acknowledge(message)
```

**Technologies**: RabbitMQ client library, asyncio or threading

---

## Data Flow & Async Processing

### Complete Transaction Lifecycle

```mermaid
sequenceDiagram
    actor Client as External System
    participant API as API Gateway<br/>(FastAPI)
    participant Queue as RabbitMQ<br/>(Message Broker)
    participant Worker as Worker Service<br/>(Background)
    participant Core as Fraud Evaluation<br/>(Core Logic)
    participant DB as MongoDB<br/>(Audit Trail)
    participant Cache as Redis<br/>(Performance Cache)
    
    Client->>API: 1. POST /transaction<br/>{user_id, amount, location, device_id}
    
    API->>API: 2. Validate payload<br/>(Pydantic model)
    
    API->>Queue: 3. Publish message<br/>transaction_id: uuid
    
    API->>Client: 4. Return 202 Accepted<br/>(transaction_id, status)
    
    Queue->>Worker: 5. Consume message<br/>(Pull from queue)
    
    Worker->>Cache: 6. Fetch user profile<br/>(location, devices, behavior)
    
    Worker->>Core: 7. Construct Transaction entity<br/>
    
    Core->>Core: 8. Apply 7 strategies<br/>in parallel
    
    Core->>Core: 9. Aggregate risk levels<br/>(HIGH/MEDIUM/LOW)
    
    Core->>DB: 10. Save FraudEvaluation<br/>(immutable record)
    
    Core->>Cache: 11. Update user cache<br/>(new location, new device)
    
    Worker->>Queue: 12. ACK message<br/>(remove from queue)
    
    Note over DB,Cache: Result ready for query
    
    Client->>API: 13. GET /audit/{txn_id}<br/>(optional, later)
    
    API->>DB: 14. Query evaluation<br/>
    
    API->>Client: 15. Return full FraudEvaluation
```

### Caching Strategy

**Redis Key Structure:**

```
user:{user_id}:location
  └─ { "latitude": 40.7128, "longitude": -74.0060 }
  └─ TTL: 24 hours

user:{user_id}:devices
  └─ Set: { "device_abc", "device_def", "device_ghi" }
  └─ TTL: 30 days

user:{user_id}:transactions:hourly
  └─ Counter (for rapid transaction detection)
  └─ TTL: 1 hour

rules:*
  └─ Cached rule configuration (thresholds, enabled flags)
  └─ TTL: Invalidated on update
```

### Configuration Updates (HU-008/009)

```
Admin updates rule threshold via dashboard
        ↓
PUT /api/v1/config/thresholds
        ↓
API validates & persists to MongoDB
        ↓
Publish RULE_UPDATED event to RabbitMQ
        ↓
Worker + API subscribe to RULE_UPDATED
        ↓
Reload rules from DB (no restart needed)
        ↓
New transactions use updated thresholds
```

---

## Design Patterns

### 1. Strategy Pattern

Each fraud detection rule is an independent strategy:

```python
class FraudStrategy(ABC):
    @abstractmethod
    def evaluate(self, transaction: Transaction) -> EvaluationResult:
        pass

class AmountThresholdStrategy(FraudStrategy):
    def evaluate(self, transaction: Transaction) -> EvaluationResult:
        if transaction.amount > self.threshold:
            return EvaluationResult(
                risk_level=RiskLevel.HIGH_RISK,
                reasons=[f"Amount ${transaction.amount} exceeds threshold ${self.threshold}"],
                risk_increment=30
            )
        return EvaluationResult(risk_level=RiskLevel.LOW_RISK)
```

**Benefits**: Easy to add new strategies, test independently, enable/disable dynamically.

### 2. Dependency Injection (DI)

Use cases receive dependencies via constructor, not importing them directly:

```python
class EvaluateTransactionUseCase:
    def __init__(
        self, 
        repository: TransactionRepository,
        cache: CacheService,
        strategies: List[FraudStrategy]
    ):
        self.repository = repository
        self.cache = cache
        self.strategies = strategies
    
    def execute(self, transaction: Transaction) -> FraudEvaluation:
        # Can swap implementations without changing use case
        pass
```

**Benefits**: Testable (mock dependencies), decoupled from concrete implementations.

### 3. Repository Pattern

Data access is abstracted behind interfaces:

```python
class TransactionRepository(ABC):
    @abstractmethod
    def save(self, evaluation: FraudEvaluation) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, transaction_id: str) -> Optional[FraudEvaluation]:
        pass

class MongoDBAdapter(TransactionRepository):
    def save(self, evaluation: FraudEvaluation) -> None:
        self.db.evaluations.insert_one(evaluation.to_dict())
    
    def get_by_id(self, transaction_id: str) -> Optional[FraudEvaluation]:
        doc = self.db.evaluations.find_one({"_id": transaction_id})
        return FraudEvaluation.from_dict(doc) if doc else None
```

**Benefits**: Can swap MongoDB for PostgreSQL without touching domain logic.

### 4. Event-Driven Architecture

Services communicate asynchronously via RabbitMQ:

```
API publishes: TRANSACTION_SUBMITTED
Worker subscribes: TRANSACTION_SUBMITTED
Worker publishes: EVALUATION_COMPLETE
Admin Dashboard subscribes: EVALUATION_COMPLETE
```

**Benefits**: Loose coupling, horizontal scaling, message durability.

---

## Technology Stack

### Backend

| Component | Technology | Version | Why Chosen |
|-----------|-----------|---------|-----------|
| **Language** | Python | 3.11+ | Type hints, mature ecosystem, fast development |
| **Web Framework** | FastAPI | 0.104+ | Async, OpenAPI docs, validation with Pydantic |
| **Async Runtime** | asyncio/uvicorn | Built-in | Non-blocking I/O, high throughput |
| **Database** | MongoDB | 7.0 | Document-oriented, flexible schema, good for audit logs |
| **Cache** | Redis | 7.2 | In-memory, high speed, TTL support |
| **Message Broker** | RabbitMQ | 3.12 | Reliable delivery, management UI, cluster support |
| **Package Manager** | Poetry | Latest | Lock file, virtual env, reproducible builds |
| **Testing** | pytest | 7.4+ | Rich plugins, fixtures, async support |
| **Code Coverage** | coverage.py | 7.3+ | Line/branch coverage, HTML reports |

### Frontend

| Component | Technology | Version | Why Chosen |
|-----------|-----------|---------|-----------|
| **Framework** | React | 18.3+ | Component reuse, ecosystem, performance |
| **Build Tool** | Vite | 6.x | Fast HMR, optimized bundles, zero-config |
| **Language** | TypeScript | 5.x | Type safety, better IDE support, fewer runtime errors |
| **Styling** | TailwindCSS | 4.x | Utility-first, no CSS bloat, dark mode |
| **State** | Zustand | Latest | Minimal, simple API, no boilerplate |
| **Charts** | Recharts | Latest | Declarative, React-idiomatic, responsive |
| **Tables** | TanStack Table | v8 | Headless, sortable/filterable, virtual scrolling |
| **UI Components** | Headless UI | Latest | Accessible, unstyled, works with Tailwind |
| **HTTP Client** | Axios | Latest | Interceptors, retry logic, request cancellation |

### DevOps

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **Containerization** | Docker | 24.0+ | Reproducible deployments |
| **Orchestration** | Docker Compose | 2.20+ | Development & testing |
| **CI/CD** | GitHub Actions | - | Workflows: test, build, deploy |
| **Code Quality** | SonarQube | Community | Code smells, security, coverage |
| **Logging** | stdout/stderr | - | Docker captures, ELK stack ready |

---

## Infrastructure & Deployment

### Local Development

```bash
docker-compose up -d

# Services available:
# - API: http://localhost:8000
# - RabbitMQ UI: http://localhost:15672
# - User App: http://localhost:3000
# - Admin Dashboard: http://localhost:3001
# - MongoDB: localhost:27017
# - Redis: localhost:6379
```

### docker-compose.yml Structure

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USERNAME}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    ports:
      - "5672:5672"
      - "15672:15672"

  api:
    build: ./services/api-gateway
    environment:
      MONGODB_URL: mongodb://admin:${MONGODB_PASSWORD}@mongodb:27017
      RABBITMQ_URL: amqp://fraud:${RABBITMQ_PASSWORD}@rabbitmq:5672
      REDIS_URL: redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
      - redis
      - rabbitmq

  worker:
    build: ./services/worker-service
    environment: [same as api]
    depends_on:
      - mongodb
      - redis
      - rabbitmq

  frontend-user:
    build: ./frontend/user-app
    ports:
      - "3000:80"

  frontend-admin:
    build: ./frontend/admin-dashboard
    ports:
      - "3001:80"

volumes:
  mongo_data:
  redis_data:
```

### Environment Variables

All sensitive values are read from `.env` file:

```env
# MongoDB
MONGODB_USERNAME=admin
MONGODB_PASSWORD=<secure_password>
MONGODB_URL=mongodb://admin:<password>@mongodb:27017

# RabbitMQ
RABBITMQ_USERNAME=fraud
RABBITMQ_PASSWORD=<secure_password>
RABBITMQ_URL=amqp://fraud:<password>@rabbitmq:5672

# Redis
REDIS_URL=redis://redis:6379

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

---

## System Diagrams

### High-Level System Architecture

```mermaid
graph TB
    subgraph CLIENT["🖥️ CLIENT LAYER"]
        UserApp["📱 User Mobile App<br/>(React/Vite)<br/>- Transaction List<br/>- Status Display"]
        AdminDash["📊 Admin Dashboard<br/>(React/Vite)<br/>- Metrics & Dashboards<br/>- Manual Review<br/>- Configuration Mgmt"]
    end

    subgraph API_LAYER["🌐 API GATEWAY LAYER<br/>(FastAPI 0.104+)"]
        Routes["Route Handlers<br/>POST /transaction → 202<br/>GET /audit/*<br/>PUT /review/*<br/>GET/PUT /config/*"]
        Validation["✓ Validation<br/>(Pydantic)"]
        DI["⚙️ DI Container"]
        Logging["📋 Logging"]
    end

    subgraph DATA_LAYER["🗄️ DATA & MESSAGING LAYER"]
        RabbitMQ["🐰 RabbitMQ 3.12<br/>(Message Broker)<br/>- fraud.queue"]
        MongoDB["🍃 MongoDB 7.0<br/>(Append-only Audit)<br/>- transactions collection"]
        Redis["⚡ Redis 7.2<br/>(Performance Cache)<br/>- User profiles<br/>- Rule config"]
    end

    subgraph WORKER["🔄 WORKER SERVICE<br/>(Background Processing)"]
        Consume["1️⃣ Consume from<br/>RabbitMQ"]
        FetchContext["2️⃣ Fetch User Context<br/>(Location, Devices,<br/>Behavior)"]
        
        subgraph CORE["🧠 FRAUD EVALUATION CORE"]
            Strategy1["📌 Amount Threshold<br/>($1,500 limit)"]
            Strategy2["📍 Location Check<br/>(100 km radius)"]
            Strategy3["📱 Device Validation<br/>(Known devices)"]
            Strategy4["⚡ Rapid Transaction<br/>(3+ in 10 min)"]
            Strategy5["🕐 Unusual Time<br/>(Off-hours)"]
            Strategy6["🌍 Timezone Shift<br/>(Location/TZ mismatch)"]
            Strategy7["✈️ Traveling Velocity<br/>(>900 km/h)"]
            Aggregate["🎯 Aggregate Results<br/>Compute Final Risk Level<br/>LOW | MEDIUM | HIGH"]
        end
        
        Persist["3️⃣ Persist & Notify<br/>- MongoDB (audit)<br/>- Redis (cache)<br/>- Publish events"]
    end

    %% Connections
    UserApp -->|HTTPS/REST| Routes
    AdminDash -->|HTTPS/REST| Routes
    
    Routes --> Validation
    Routes --> DI
    Routes --> Logging
    
    Routes -->|Publish| RabbitMQ
    Routes -->|Query/Update| MongoDB
    Routes -->|Read/Write| Redis
    
    RabbitMQ -->|Consume| Consume
    Consume --> FetchContext
    FetchContext --> Strategy1
    
    Redis -->|User Profile| FetchContext
    
    Strategy1 --> Strategy2
    Strategy2 --> Strategy3
    Strategy3 --> Strategy4
    Strategy4 --> Strategy5
    Strategy5 --> Strategy6
    Strategy6 --> Strategy7
    Strategy7 --> Aggregate
    
    Aggregate --> Persist
    
    Persist -->|Write| MongoDB
    Persist -->|Update| Redis
    
    %% Styling
    classDef client fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    classDef api fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    classDef data fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    classDef worker fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef core fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    
    class CLIENT client
    class API_LAYER api
    class DATA_LAYER data
    class WORKER worker
    class CORE core
```

---

**Version**: 2.0 | **Updated**: Jan 28, 2026 | **Status**: Active Source of Truth
