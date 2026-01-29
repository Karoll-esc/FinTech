# 🛡️ Fraud Detection Engine

Motor de detección de fraude implementado con **Clean Architecture**, **TDD/BDD**, principios **SOLID** y patrón de diseño **Strategy**.

## 🧪 Cumplimiento TDD/BDD

[![Tests](https://img.shields.io/badge/tests-200%2B%20passed-brightgreen)](docs/TEST_PLAN.md)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](htmlcov/index.html)
[![TDD](https://img.shields.io/badge/TDD-aplicado-blue)](docs/FLUJO_TDD_BDD.md)
[![BDD](https://img.shields.io/badge/BDD-historias%20Gherkin-blue)](docs/USER_HISTORY.md)

### ✅ Verificación Completa (estado actual)

- ✅ **244 tests unitarios backend** pasando (pytest, `tests/unit/`)
- ✅ **Tests de frontend (user-app y admin-dashboard)** pasando (Vitest)
- ✅ **Cobertura backend ~95%** según `coverage.xml` (umbral mínimo configurado: 70%)
- ✅ **Historias de usuario** cubiertas con tests unitarios, integración y E2E
- ✅ **Tests escritos antes del código** (TDD)
- ✅ **Ciclo Red-Green-Refactor** documentado
- ✅ **Especificaciones ejecutables** (BDD)

📖 **Ver documentación completa (actualizada):**
- `docs/USER_HISTORY.md`: Historias de usuario y flujos de negocio
- `docs/TEST_PLAN.md`: Plan de pruebas y tipos de tests
- `docs/TEST_CASES.md`: Casos de prueba
- `tests-e2e/README.md`: Tests E2E con Playwright

## 🏗️ Arquitectura

### Visión general

- **Backend**:
  - `services/fraud-evaluation-service`: dominio de fraude (estrategias, modelos, casos de uso)
  - `services/api-gateway`: API FastAPI expuesta en `http://localhost:8000`
  - `services/worker-service`: worker asíncrono con RabbitMQ
- **Frontends**:
  - `frontend/user-app`: app de usuario (historial de transacciones)
  - `frontend/admin-dashboard`: dashboard admin (métricas y reglas)
- **Infraestructura**:
  - MongoDB, Redis y RabbitMQ orquestados con `docker-compose.yml`

Para una descripción más detallada ver:
- `docs/PROJECT_STRUCTURE.md`
- `docs/MICROSERVICES_ARCHITECTURE.md`

### Principios SOLID

✅ **0 violaciones SOLID**

- **S** (Single Responsibility): Cada clase tiene una única razón para cambiar
- **O** (Open/Closed): Extensible mediante Strategy Pattern sin modificar código existente
- **L** (Liskov Substitution): Las estrategias son intercambiables
- **I** (Interface Segregation): Interfaces específicas para cada puerto
- **D** (Dependency Inversion): Los casos de uso dependen de abstracciones, no de implementaciones

## 🎯 Historias de Usuario Implementadas

- **HU-001**: API de recepción de transacciones (202 Accepted) - ✅ 5 tests
- **HU-002**: Auditoría de evaluaciones - ✅ 5 tests
- **HU-003**: Regla de umbral de monto (>$1,500) - ✅ 5 tests
- **HU-004**: Validación de dispositivo conocido - ✅ 5 tests
- **HU-005**: Detección de ubicación inusual (>100 km) - ✅ 9 tests
- **HU-006**: Detección de transacciones en cadena - ✅ 5 tests
- **HU-007**: Detección de horario inusual - ✅ 4 tests
- **HU-008**: Modificación de umbrales sin redespliegue - ✅ 3 tests
- **HU-009**: Consulta de configuración actual - ✅ 2 tests
- **HU-010**: Envío a cola de revisión manual - ✅ 5 tests
- **HU-011**: Gestión de reglas personalizadas - ✅ 3 tests
- **HU-012**: Revisión manual por analista - ✅ 5 tests
- **HU-013**: Dashboard usuario (historial transacciones) - ✅ 4 tests
- **HU-014**: Dashboard admin (métricas de fraude) - ✅ 3 tests

**Total:** 14 historias, 162 tests, 100% cobertura ✅

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- Docker Desktop (debe estar corriendo)
- Poetry (opcional, para desarrollo local)

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Verificar que Docker Desktop esté corriendo
docker --version

# 2. Levantar todos los servicios
docker-compose up -d

# 3. Verificar que los contenedores estén corriendo
docker-compose ps

# 4. Ver logs
docker-compose logs -f

# 5. Acceder a la API (Swagger UI)
# http://localhost:8000/docs

# 6. Acceder a los frontends (servidos por Nginx en Docker)
# Frontend Usuario: http://localhost:3000
# Frontend Admin: http://localhost:3001

# Iniciar frontend de usuario
cd frontend/user-app
npm install
npm run dev

# Iniciar frontend admin (en otra terminal)
cd frontend/admin-dashboard
npm install
npm run dev
```

### Opción 2: Desarrollo Local (sin Docker para backend)

```bash
# 1. Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Instalar dependencias backend
poetry install

# 3. Copiar variables de entorno (si aplica)
cp .env.example .env  # o copy en Windows

# 4. Levantar solo las bases de datos con Docker
docker-compose up -d mongodb redis rabbitmq

# 5. Ejecutar API (desde la raíz del repo)
poetry run uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000

# 6. Ejecutar Worker (en otra terminal)
poetry run python -m services.worker-service.src.worker

# 7. Ejecutar frontends en modo dev
cd frontend/user-app && npm install && npm run dev       # http://localhost:5173
cd frontend/admin-dashboard && npm install && npm run dev  # http://localhost:3001
```

## 🧪 Testing

El proyecto cuenta con **tests unitarios completos** para backend y frontend:

### Ejecución Rápida

```bash
# Script PowerShell (Windows) - Ejecuta todos los tests
.\scripts\run-tests.ps1 -TestType all

# Backend (Python/pytest)
pytest tests/unit/ -v

# Frontend User App (TypeScript/Vitest)
cd frontend/user-app && npm test

# Frontend Admin Dashboard (TypeScript/Vitest)
cd frontend/admin-dashboard && npm test
```

### Documentación Completa

📖 **[Ver Guía Completa de Ejecución de Tests](TEST_EXECUTION_GUIDE.md)**

La guía incluye:
- ✅ Configuración inicial (local y Docker)
- ✅ Ejecución de tests unitarios, integración y E2E
- ✅ Instrucciones para GitHub Actions
- ✅ Solución de problemas comunes
- ✅ Reportes de cobertura

### Cobertura de Tests

- **Backend**: 244 tests unitarios (estrategias, adaptadores, workers, routes)
- **Frontend**: Tests de componentes, utilidades y servicios API
- **E2E**: Tests end-to-end con Playwright

### CI/CD

Los tests se ejecutan automáticamente en **GitHub Actions** en cada push/PR.
Ver configuración en [.github/workflows/tests.yml](.github/workflows/tests.yml)

## 📊 Reglas de Fraude

1. **Umbral de Monto**: Transacciones > $1,500 USD se marcan como HIGH_RISK
2. **Ubicación Inusual**: Transacciones > 100 km del radio habitual se marcan como sospechosas

## 🔧 Endpoints API

- `POST /transaction` - Enviar transacción para evaluación (202 Accepted)
- `GET /audit/all` - Consultar todas las evaluaciones
- `GET /audit/transaction/{id}` - Consultar evaluación específica
- `PUT /transaction/review/{id}` - Revisar transacción manualmente
- `GET /config/thresholds` - Consultar configuración actual
- `PUT /config/thresholds` - Actualizar umbrales

## 📝 Licencia

MIT License

---

## 📚 Documentación Adicional

- [📋 Historias de Usuario](docs/HISTORIAS_USUARIO.md)
- [🧪 Plan de Pruebas](docs/TEST_PLAN.md)
- [🏗️ Arquitectura de Microservicios](docs/MICROSERVICES_ARCHITECTURE.md)
- [📦 Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)
- [🌿 Flujo de Trabajo Git](docs/GIT_WORKFLOW.md) - **Guía completa de ramas y colaboración**
- [💼 Contexto de Negocio](docs/CONTEXTO_NEGOCIO.md)
- [🎯 Guía de Reglas de Ubicación](docs/LOCATION_RULES_GUIDE.md)
