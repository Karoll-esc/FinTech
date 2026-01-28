# Card Management Feature - Deployment Guide

## Overview

This guide covers deploying the Card Management feature (HU-015 & HU-016) across all three microservices:
- **API Gateway** (FastAPI)
- **Fraud Evaluation Service** (Domain + Application + Infrastructure)
- **Frontend** (React Admin Dashboard)

---

## Pre-Deployment Checklist

- [ ] All tests passing locally (`pytest tests/ -v`, `npm test`)
- [ ] Code reviewed and merged to main branch
- [ ] Environment variables configured in deployment environment
- [ ] Docker images built and verified
- [ ] Database migrations reviewed (MongoDB)
- [ ] RabbitMQ queue configuration verified
- [ ] SSL certificates ready (production)
- [ ] Backups of existing data taken
- [ ] Rollback procedure documented and tested

---

## Architecture & Data Flow

```
Frontend (React)
    ↓
API Gateway (FastAPI) → Routes validation → Dependency injection
    ↓
Fraud Evaluation Service → Application layer (use cases) → Domain logic
    ↓
Infrastructure Adapters:
    ├→ MongoDB (Card repository, soft-delete)
    ├→ Redis (Cache invalidation)
    └→ RabbitMQ (Audit events)
```

---

## Phase 1: Database & Infrastructure Setup

### 1.1 MongoDB Collection Setup

**Create cards collection with proper indexes:**

```javascript
// Connect to MongoDB
use fraud_detection_db

// Create collection
db.createCollection("cards")

// Add indexes for performance
db.cards.createIndex({ card_id: 1 }, { unique: true })
db.cards.createIndex({ user_id: 1 })
db.cards.createIndex({ status: 1 })
db.cards.createIndex({ created_at: -1 })
db.cards.createIndex({ user_id: 1, status: 1 })  // Composite for list queries

// Create compound index for duplicate detection
db.cards.createIndex({ user_id: 1, card_number_last_four: 1 })

// Verify indexes
db.cards.getIndexes()
```

**Or via Docker:**

```bash
docker-compose exec mongodb mongosh --eval "
use fraud_detection_db
db.createCollection('cards')
db.cards.createIndex({ card_id: 1 }, { unique: true })
db.cards.createIndex({ user_id: 1 })
db.cards.createIndex({ status: 1 })
db.cards.createIndex({ created_at: -1 })
db.cards.createIndex({ user_id: 1, status: 1 })
db.cards.createIndex({ user_id: 1, card_number_last_four: 1 })
"
```

### 1.2 RabbitMQ Queue Setup

**Create queues and exchanges for card audit events:**

```bash
# Access RabbitMQ management UI
# http://localhost:15672 (user: guest, password: guest)

# Or via Docker:
docker-compose exec rabbitmq rabbitmqctl declare_exchange \
  -p / fraud.events direct durable

docker-compose exec rabbitmq rabbitmqctl declare_queue \
  -p / fraud.audit.events durable

# Bind queue to exchange
docker-compose exec rabbitmq rabbitmqctl bind_queue \
  -p / fraud.audit.events fraud.events card.events
```

**Python script for declarative setup:**

```python
# services/worker-service/setup_rabbitmq.py
import pika
import sys

def setup_rabbitmq(host='localhost', port=5672):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port)
        )
        channel = connection.channel()
        
        # Declare exchange
        channel.exchange_declare(
            exchange='fraud.events',
            exchange_type='direct',
            durable=True
        )
        
        # Declare queue with dead-letter exchange
        channel.queue_declare(
            queue='fraud.audit.events',
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'fraud.events.dlx',
                'x-message-ttl': 86400000  # 24 hours
            }
        )
        
        # Bind queue
        channel.queue_bind(
            exchange='fraud.events',
            queue='fraud.audit.events',
            routing_key='card.events'
        )
        
        print("✅ RabbitMQ setup complete")
        connection.close()
        
    except Exception as e:
        print(f"❌ RabbitMQ setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_rabbitmq()
```

Run: `python services/worker-service/setup_rabbitmq.py`

### 1.3 Redis Cache Configuration

**Ensure Redis is running and accessible:**

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
# Expected output: PONG

# Check memory usage
docker-compose exec redis redis-cli info memory

# Set up TTL policies (optional)
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Phase 2: Backend Deployment

### 2.1 API Gateway Updates

**File locations:**
- Routes: `services/api-gateway/src/routes/cards.py`
- Schemas: `services/api-gateway/src/schemas/card_schemas.py`
- Main app: `services/api-gateway/src/main.py`

**Deployment steps:**

```bash
# 1. Build API Gateway Docker image
cd services/api-gateway
docker build -t fintech-api-gateway:latest .

# 2. Tag for registry (if using container registry)
docker tag fintech-api-gateway:latest myregistry.azurecr.io/fintech-api-gateway:latest

# 3. Push to registry (optional)
docker push myregistry.azurecr.io/fintech-api-gateway:latest

# 4. Update docker-compose.yml with new image tag
# docker-compose.yml: services.api-gateway.image: fintech-api-gateway:latest

# 5. Restart service
docker-compose down api-gateway
docker-compose up -d api-gateway

# 6. Verify health
curl http://localhost:8000/docs
curl http://localhost:8000/health
```

**Environment variables needed:**

```bash
# .env or docker-compose.yml
MONGODB_URI=mongodb://mongodb:27017/fraud_detection_db
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
LOG_LEVEL=INFO
API_PORT=8000
```

### 2.2 Fraud Evaluation Service Updates

**File locations:**
- Domain models: `services/fraud-evaluation-service/src/domain/models.py`
- Validators: `services/fraud-evaluation-service/src/domain/validation/card_validators.py`
- Use cases: `services/fraud-evaluation-service/src/application/usecases/card_usecases.py`
- MongoDB adapter: `services/fraud-evaluation-service/src/infrastructure/adapters/mongodb/card_repository.py`

**Deployment steps:**

```bash
# 1. Build service Docker image
cd services/fraud-evaluation-service
docker build -t fintech-fraud-evaluation:latest .

# 2. Tag and push (optional)
docker tag fintech-fraud-evaluation:latest myregistry.azurecr.io/fintech-fraud-evaluation:latest
docker push myregistry.azurecr.io/fintech-fraud-evaluation:latest

# 3. Update docker-compose and restart
docker-compose down fraud-evaluation-service
docker-compose up -d fraud-evaluation-service

# 4. Verify logs
docker-compose logs fraud-evaluation-service
```

### 2.3 Worker Service Updates

**File locations:**
- Consumer: `services/worker-service/src/consumer.py`
- Card event handlers: `services/worker-service/src/handlers/card_handlers.py`
- RabbitMQ publisher: `services/fraud-evaluation-service/src/infrastructure/adapters/rabbitmq/audit_event_publisher.py`

**Deployment steps:**

```bash
# 1. Build Worker Docker image
cd services/worker-service
docker build -t fintech-worker:latest .

# 2. Tag and push
docker tag fintech-worker:latest myregistry.azurecr.io/fintech-worker:latest
docker push myregistry.azurecr.io/fintech-worker:latest

# 3. Update docker-compose and restart
docker-compose down worker-service
docker-compose up -d worker-service

# 4. Monitor queue processing
docker-compose logs -f worker-service
```

---

## Phase 3: Frontend Deployment

### 3.1 Admin Dashboard Updates

**File locations:**
- Components: `frontend/admin-dashboard/src/components/cards/`
- Hooks: `frontend/admin-dashboard/src/hooks/useCard.ts`
- API client: `frontend/admin-dashboard/src/services/api.ts`
- Types: `frontend/admin-dashboard/src/types/index.ts`

**Build and deploy:**

```bash
# 1. Build frontend
cd frontend/admin-dashboard
npm install
npm run build

# 2. Output is in dist/
# dist/ contains static assets for web server

# 3. Copy to web server or Docker
docker build -t fintech-admin-dashboard:latest .

# 4. Update docker-compose
docker-compose down admin-dashboard
docker-compose up -d admin-dashboard

# 5. Verify
curl http://localhost:3001
# or access via browser: http://localhost:3001
```

**Environment variables:**

```bash
# frontend/admin-dashboard/.env.production
VITE_API_BASE_URL=https://api.fintech.example.com
VITE_API_TIMEOUT=10000
VITE_LOG_LEVEL=error
```

### 3.2 Nginx Configuration

**If using Nginx as reverse proxy:**

```nginx
# nginx.conf or docker/nginx/default.conf
server {
    listen 3001;
    server_name localhost;
    
    # Admin Dashboard
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        # Cache busting for static assets
        location ~* \.(js|css|jpg|jpeg|png|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API proxy (if needed)
    location /api/ {
        proxy_pass http://api-gateway:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-User-ID $http_x_user_id;
        
        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET,POST,PUT,DELETE,OPTIONS' always;
    }
}
```

---

## Phase 4: Testing & Validation

### 4.1 Backend Tests

```bash
# Run all backend tests
cd /path/to/fintech
pytest tests/unit/ tests/integration/ -v --cov=services

# Expected output: 220+ tests passing, >95% coverage
# Specifically for cards:
pytest tests/unit/test_card_models.py -v
pytest tests/unit/test_card_validators.py -v
pytest tests/unit/test_card_usecases.py -v
pytest tests/integration/test_card_repository.py -v
```

### 4.2 Frontend Tests

```bash
# Run frontend component tests
cd frontend/admin-dashboard
npm test

# Expected output: 40+ card component tests passing
```

### 4.3 E2E Tests

```bash
# Run Playwright E2E tests
cd tests-e2e
npm install
npm test

# Or with UI for debugging
npx playwright test --ui

# Expected: 11 card management test cases passing
```

### 4.4 API Smoke Tests

```bash
# Test API endpoints
curl -X GET http://localhost:8000/health

# Test card endpoints with sample user
curl -X POST http://localhost:8000/cards \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-001" \
  -d '{
    "card_number": "4532015112830366",
    "card_holder_name": "Test User",
    "expiry_date": "12/25",
    "card_type": "DEBIT",
    "nickname": "Test Card"
  }'

# Verify response is 201 with masked card number
```

---

## Phase 5: Production Deployment

### 5.1 Docker Compose Production

**Create docker-compose.prod.yml:**

```yaml
version: '3.8'
services:
  api-gateway:
    image: myregistry.azurecr.io/fintech-api-gateway:v1.0.0
    ports:
      - "8000:8000"
    environment:
      MONGODB_URI: ${MONGODB_URI}
      REDIS_URL: ${REDIS_URL}
      RABBITMQ_URL: ${RABBITMQ_URL}
      LOG_LEVEL: INFO
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  fraud-evaluation-service:
    image: myregistry.azurecr.io/fintech-fraud-evaluation:v1.0.0
    environment:
      MONGODB_URI: ${MONGODB_URI}
      REDIS_URL: ${REDIS_URL}
      RABBITMQ_URL: ${RABBITMQ_URL}
      LOG_LEVEL: INFO
    restart: always
    depends_on:
      - mongodb
      - redis
      - rabbitmq

  worker-service:
    image: myregistry.azurecr.io/fintech-worker:v1.0.0
    environment:
      MONGODB_URI: ${MONGODB_URI}
      REDIS_URL: ${REDIS_URL}
      RABBITMQ_URL: ${RABBITMQ_URL}
      LOG_LEVEL: INFO
    restart: always
    depends_on:
      - mongodb
      - rabbitmq

  admin-dashboard:
    image: myregistry.azurecr.io/fintech-admin-dashboard:v1.0.0
    ports:
      - "3001:3001"
    environment:
      VITE_API_BASE_URL: https://api.fintech.example.com
    restart: always

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
      MONGO_INITDB_DATABASE: fraud_detection_db
    volumes:
      - mongodb_data:/data/db
    restart: always

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: always

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    restart: always

volumes:
  mongodb_data:
```

**Deploy:**

```bash
# Load environment variables
export $(cat .env.prod | xargs)

# Deploy with production compose file
docker-compose -f docker-compose.prod.yml up -d

# Verify all services
docker-compose ps

# Check logs
docker-compose logs -f api-gateway
```

### 5.2 Kubernetes Deployment (Optional)

**Create Kubernetes manifests:**

```yaml
# k8s/card-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fintech-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fintech-api
  template:
    metadata:
      labels:
        app: fintech-api
    spec:
      containers:
      - name: api
        image: myregistry.azurecr.io/fintech-api-gateway:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: mongodb-uri
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis-url
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## Phase 6: Monitoring & Logging

### 6.1 Logging Setup

**Configure centralized logging:**

```python
# services/api-gateway/src/logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging(log_level='INFO'):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # JSON logging for ELK/Splunk
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    return logger

# Usage in routes
logger = setup_logging()
logger.info("Card added", extra={"card_id": card.card_id, "user_id": user_id})
```

### 6.2 Monitoring Metrics

**Track key metrics:**
- Cards added per day
- API response times (p95, p99)
- Error rates by endpoint
- RabbitMQ queue depth
- MongoDB query performance
- Cache hit/miss ratios

**Using Prometheus:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fintech-api'
    static_configs:
      - targets: ['localhost:8000/metrics']

  - job_name: 'fintech-mongodb'
    static_configs:
      - targets: ['localhost:27017']
```

---

## Rollback Procedure

### If deployment fails:

```bash
# 1. Identify which service failed
docker-compose logs api-gateway
docker-compose logs fraud-evaluation-service

# 2. Revert to previous image
docker-compose down api-gateway
docker pull myregistry.azurecr.io/fintech-api-gateway:v0.9.0
docker-compose up -d api-gateway

# 3. Verify rollback
curl http://localhost:8000/health

# 4. Check MongoDB for data consistency
docker-compose exec mongodb mongosh --eval "
use fraud_detection_db
db.cards.countDocuments()
"

# 5. Document incident
# Create ROLLBACK.md with timestamp, reason, actions taken
```

---

## Post-Deployment Verification

- [ ] All services running: `docker-compose ps`
- [ ] API responds: `curl http://localhost:8000/health`
- [ ] Can add card: `POST /cards` returns 201
- [ ] Can list cards: `GET /cards` returns 200
- [ ] Can view card: `GET /cards/{id}` returns 200
- [ ] Can update card: `PUT /cards/{id}` returns 200
- [ ] Can delete card: `DELETE /cards/{id}` returns 204
- [ ] Soft-delete verified (status=INACTIVE in MongoDB)
- [ ] Audit events published to RabbitMQ
- [ ] Frontend loads at http://localhost:3001
- [ ] Card form works (can add test card)
- [ ] E2E tests pass: `npm test`
- [ ] No errors in logs: `docker-compose logs`

---

## Troubleshooting

### API Gateway not starting

```bash
# Check logs
docker-compose logs api-gateway

# Common issues:
# 1. Port 8000 already in use
lsof -i :8000
kill -9 <PID>

# 2. Database connection error
docker-compose logs mongodb

# 3. Missing environment variables
echo $MONGODB_URI
```

### MongoDB connection timeout

```bash
# Verify MongoDB is running
docker-compose exec mongodb mongosh admin --eval "db.version()"

# Check connection string
# Should be: mongodb://mongodb:27017/fraud_detection_db (inside Docker)
# or: mongodb://localhost:27017/fraud_detection_db (local)
```

### RabbitMQ not publishing events

```bash
# Check queue
docker-compose exec rabbitmq rabbitmqctl list_queues

# Expected output should include: fraud.audit.events

# Monitor messages
docker-compose exec rabbitmq rabbitmqctl list_queues name messages
```

### Frontend not loading

```bash
# Check if admin-dashboard service is running
docker-compose ps admin-dashboard

# Verify port
curl http://localhost:3001

# Check nginx logs
docker-compose logs admin-dashboard
```

---

## Support & Documentation

- **API Documentation**: [docs/CARDS-API.md](../CARDS-API.md)
- **Architecture**: [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
- **Test Results**: Run `pytest tests/ --html=report.html`
- **E2E Tests**: [tests-e2e/README.md](../../tests-e2e/README.md)

---

## Deployment Checklist

**Pre-deployment:**
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Release notes written
- [ ] Backup taken

**During deployment:**
- [ ] Services start without errors
- [ ] Health checks pass
- [ ] Database indexes created
- [ ] RabbitMQ queues configured
- [ ] Logs monitored for errors

**Post-deployment:**
- [ ] API responding
- [ ] Frontend accessible
- [ ] Sample transactions processed
- [ ] Audit events logged
- [ ] Performance acceptable
- [ ] No alert
