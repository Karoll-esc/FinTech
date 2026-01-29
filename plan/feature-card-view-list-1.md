---
goal: Implementar visualización de múltiples tarjetas con saldo (HU-015)
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
owner: Development Team
status: 'Planned'
tags: ['feature', 'frontend', 'backend', 'cards', 'user-interface']
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Plan de implementación para la Historia de Usuario HU-015: Ver Múltiples Tarjetas con Saldo. Esta funcionalidad permitirá a los usuarios visualizar todas sus tarjetas registradas con información clave como saldo actual, últimos 4 dígitos, estado (Activa/Bloqueada/Suspendida), y apodo personalizado. El sistema soportará hasta 3 tarjetas por usuario y ordenará las tarjetas de la más nueva a la más antigua.

**Enfoque TDD/BDD**: Todos los tests se escriben PRIMERO antes de implementar el código (Red → Green → Refactor).

## 1. Requirements & Constraints

**Requisitos Funcionales:**

- **REQ-001**: El usuario debe poder ver una lista de todas sus tarjetas registradas
- **REQ-002**: Cada tarjeta debe mostrar: últimos 4 dígitos (ej: ****1234), saldo actual, estado, y apodo opcional
- **REQ-003**: Las tarjetas deben ordenarse por fecha de creación descendente (más nueva primero)
- **REQ-004**: El sistema debe soportar máximo 3 tarjetas por usuario
- **REQ-005**: Tarjetas con saldo $0.00 deben mostrarse en rojo con etiqueta "Sin fondos"
- **REQ-006**: Usuario sin tarjetas debe ver mensaje: "No tienes tarjetas registradas" con botón "Agregar Primera Tarjeta"
- **REQ-007**: Si el usuario tiene 3 tarjetas, el botón "Agregar Tarjeta" NO debe aparecer
- **REQ-008**: Tiempo de carga debe ser ≤ 500 milisegundos

**Requisitos de Seguridad:**

- **SEC-001**: Solo el usuario autenticado puede ver sus propias tarjetas (validación JWT)
- **SEC-002**: Números de tarjeta deben estar enmascarados excepto últimos 4 dígitos
- **SEC-003**: CVV NUNCA debe ser retornado en ningún endpoint
- **SEC-004**: HTTPS obligatorio en producción
- **SEC-005**: Rate limiting: máximo 10 requests por minuto por usuario

**Requisitos de Testing:**

- **TEST-001**: Cobertura de tests ≥ 95%
- **TEST-002**: Tests unitarios para dominio (modelos, validaciones)
- **TEST-003**: Tests de integración para endpoints API
- **TEST-004**: Tests E2E con Playwright para flujo completo de usuario

**Constraints:**

- **CON-001**: Backend debe seguir Clean Architecture (domain, application, infrastructure layers)
- **CON-002**: Frontend debe usar React 18.3+ con TypeScript y TailwindCSS
- **CON-003**: API debe retornar JSON siguiendo estándar REST
- **CON-004**: Máximo 3 tarjetas por usuario (límite de negocio)
- **CON-005**: No se debe exponer número completo de tarjeta en ningún endpoint

**Guidelines:**

- **GUD-001**: Seguir TDD estricto: Test PRIMERO, luego implementación
- **GUD-002**: Usar Gherkin para tests de aceptación
- **GUD-003**: Commits atómicos con prefijos: test:, feat:, refactor:
- **GUD-004**: Nombres de archivos en kebab-case para frontend, snake_case para backend
- **GUD-005**: Documentar decisiones técnicas no obvias con comentarios "HUMAN REVIEW"

**Patterns:**

- **PAT-001**: Repository Pattern para acceso a datos de tarjetas
- **PAT-002**: DTO Pattern para request/response (Pydantic en backend)
- **PAT-003**: Component Pattern con props typing en React
- **PAT-004**: Custom Hooks para lógica de negocio reutilizable (useCards)
- **PAT-005**: Loading/Error/Success states para UX optimizada

## 2. Implementation Steps

### Implementation Phase 1: Domain Layer (Backend - Pure Business Logic)

**GOAL-001**: Crear modelos de dominio para Card con validaciones de negocio inmutables

| Task     | Description           | Completed | Date       |
| -------- | --------------------- | --------- | ---------- |
| TASK-001 | **[TDD RED]** Escribir test `tests/unit/test_card_models.py` para modelo `Card` con validación de número enmascarado | | |
| TASK-002 | **[TDD RED]** Escribir test para validación: solo últimos 4 dígitos visibles, resto enmascarado | | |
| TASK-003 | **[TDD RED]** Escribir test para enum `CardStatus` (ACTIVE, BLOCKED, SUSPENDED) | | |
| TASK-004 | **[TDD RED]** Escribir test para enum `CardType` (DEBIT, CREDIT) | | |
| TASK-005 | **[TDD RED]** Escribir test edge case: saldo negativo debe lanzar ValueError | | |
| TASK-006 | **[TDD GREEN]** Implementar `Card` value object en `services/fraud-evaluation-service/src/domain/models.py` | | |
| TASK-007 | **[TDD GREEN]** Implementar `CardStatus` enum (ACTIVE=1, BLOCKED=2, SUSPENDED=3) | | |
| TASK-008 | **[TDD GREEN]** Implementar `CardType` enum (DEBIT=1, CREDIT=2) | | |
| TASK-009 | **[TDD GREEN]** Implementar método `mask_card_number()` que retorna solo últimos 4 dígitos | | |
| TASK-010 | **[TDD GREEN]** Implementar validación en `__post_init__`: saldo ≥ 0, card_number longitud válida | | |
| TASK-011 | **[REFACTOR]** Refactorizar si hay duplicación, asegurar inmutabilidad con `frozen=True` | | |
| TASK-012 | Verificar cobertura: `pytest tests/unit/test_card_models.py --cov=services.fraud_evaluation_service.src.domain.models` | | |

### Implementation Phase 2: Application Layer (Use Cases)

**GOAL-002**: Implementar caso de uso GetUserCardsUseCase con ordenamiento y límite de 3 tarjetas

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-013 | **[TDD RED]** Escribir test `tests/unit/test_get_user_cards_use_case.py` para caso exitoso (3 tarjetas) | | |
| TASK-014 | **[TDD RED]** Escribir test para caso vacío (0 tarjetas retorna lista vacía) | | |
| TASK-015 | **[TDD RED]** Escribir test para ordenamiento descendente por created_at | | |
| TASK-016 | **[TDD RED]** Escribir test para verificar enmascaramiento de números | | |
| TASK-017 | **[TDD GREEN]** Implementar `GetUserCardsUseCase` en `services/fraud-evaluation-service/src/application/use_cases/` | | |
| TASK-018 | **[TDD GREEN]** Implementar método `execute(user_id: str) -> List[Card]` | | |
| TASK-019 | **[TDD GREEN]** Inyectar dependencia `CardRepository` (port/interface) vía constructor | | |
| TASK-020 | **[TDD GREEN]** Implementar lógica: fetch from repo, ordenar por created_at DESC, limitar a 3 | | |
| TASK-021 | **[REFACTOR]** Extraer ordenamiento a método privado si es complejo | | |

### Implementation Phase 3: Infrastructure Layer (Repository & Database)

**GOAL-003**: Crear adaptador MongoDB para persistencia de tarjetas

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-022 | Crear interfaz `CardRepository` en `services/fraud-evaluation-service/src/application/ports/` | | |
| TASK-023 | Definir métodos: `get_by_user_id(user_id: str) -> List[Card]`, `save(card: Card) -> None` | | |
| TASK-024 | **[TDD RED]** Escribir test `tests/integration/test_card_repository.py` con MongoDB test container | | |
| TASK-025 | **[TDD RED]** Escribir test para `get_by_user_id` retorna lista vacía si no hay tarjetas | | |
| TASK-026 | **[TDD RED]** Escribir test para guardar tarjeta y recuperarla | | |
| TASK-027 | **[TDD GREEN]** Implementar `MongoDBCardAdapter` en `services/fraud-evaluation-service/src/adapters.py` | | |
| TASK-028 | **[TDD GREEN]** Crear índice en MongoDB: `{ "user_id": 1, "created_at": -1 }` para performance | | |
| TASK-029 | **[TDD GREEN]** Implementar serialización/deserialización Card ↔ BSON | | |
| TASK-030 | **[REFACTOR]** Extraer mapeo a función helper si hay duplicación | | |

### Implementation Phase 4: API Layer (FastAPI Routes)

**GOAL-004**: Exponer endpoint GET /api/v1/cards con autenticación JWT

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-031 | **[TDD RED]** Escribir test `tests/integration/test_cards_api.py` para GET /api/v1/cards | | |
| TASK-032 | **[TDD RED]** Escribir test para respuesta 200 con lista de 3 tarjetas | | |
| TASK-033 | **[TDD RED]** Escribir test para respuesta 200 con lista vacía (0 tarjetas) | | |
| TASK-034 | **[TDD RED]** Escribir test para respuesta 401 si no hay token JWT | | |
| TASK-035 | **[TDD RED]** Escribir test para respuesta 403 si usuario intenta ver tarjetas de otro usuario | | |
| TASK-036 | **[TDD GREEN]** Crear DTO `CardResponse` en `services/api-gateway/src/routes.py` con Pydantic | | |
| TASK-037 | **[TDD GREEN]** Implementar endpoint `@api_v1_router.get("/cards")` | | |
| TASK-038 | **[TDD GREEN]** Agregar validación JWT con dependencia `get_current_user()` | | |
| TASK-039 | **[TDD GREEN]** Llamar a `GetUserCardsUseCase` y mapear a `List[CardResponse]` | | |
| TASK-040 | **[TDD GREEN]** Asegurar que CVV NO se incluya en respuesta | | |
| TASK-041 | Verificar con Swagger UI: http://localhost:8000/docs | | |

### Implementation Phase 5: Frontend - React Components

**GOAL-005**: Crear componente CardList con estados de carga, vacío y error

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-042 | **[TDD RED]** Escribir test `frontend/user-app/src/components/__tests__/CardList.test.tsx` (Vitest) | | |
| TASK-043 | **[TDD RED]** Escribir test para renderizar 3 tarjetas correctamente | | |
| TASK-044 | **[TDD RED]** Escribir test para mostrar últimos 4 dígitos enmascarados | | |
| TASK-045 | **[TDD RED]** Escribir test para tarjeta con saldo 0 se muestra en rojo | | |
| TASK-046 | **[TDD RED]** Escribir test para estado vacío: mensaje "No tienes tarjetas registradas" | | |
| TASK-047 | **[TDD RED]** Escribir test para botón "Agregar Tarjeta" NO aparece si hay 3 tarjetas | | |
| TASK-048 | **[TDD GREEN]** Crear componente `CardList.tsx` en `frontend/user-app/src/components/` | | |
| TASK-049 | **[TDD GREEN]** Crear componente `CardItem.tsx` para una tarjeta individual | | |
| TASK-050 | **[TDD GREEN]** Implementar lógica: saldo 0 → texto rojo + etiqueta "Sin fondos" | | |
| TASK-051 | **[TDD GREEN]** Implementar estados: loading (skeleton), error (mensaje), success (lista) | | |
| TASK-052 | **[TDD GREEN]** Agregar íconos diferentes para Débito vs Crédito (React Icons) | | |
| TASK-053 | **[REFACTOR]** Extraer lógica de formateo a `utils/cardFormatters.ts` | | |

### Implementation Phase 6: Frontend - Custom Hook & API Integration

**GOAL-006**: Crear custom hook useCards para gestionar estado y llamadas API

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-054 | **[TDD RED]** Escribir test `frontend/user-app/src/hooks/__tests__/useCards.test.ts` | | |
| TASK-055 | **[TDD RED]** Escribir test para loading state inicial | | |
| TASK-056 | **[TDD RED]** Escribir test para success state con 3 tarjetas | | |
| TASK-057 | **[TDD RED]** Escribir test para error state si API falla (500) | | |
| TASK-058 | **[TDD GREEN]** Crear hook `useCards.ts` en `frontend/user-app/src/hooks/` | | |
| TASK-059 | **[TDD GREEN]** Implementar fetch de GET /api/v1/cards con Axios | | |
| TASK-060 | **[TDD GREEN]** Manejar estados: `{ cards, isLoading, error, refetch }` | | |
| TASK-061 | **[TDD GREEN]** Agregar interceptor Axios para agregar token JWT automáticamente | | |
| TASK-062 | **[REFACTOR]** Mover configuración Axios a `services/api.ts` | | |

### Implementation Phase 7: Frontend - Page Integration & Routing

**GOAL-007**: Integrar componente CardList en página CardsPage con routing

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-063 | Crear página `CardsPage.tsx` en `frontend/user-app/src/pages/` | | |
| TASK-064 | Importar y usar hook `useCards()` | | |
| TASK-065 | Renderizar `<CardList cards={cards} isLoading={isLoading} error={error} />` | | |
| TASK-066 | Agregar ruta `/cards` en `App.tsx` (React Router) | | |
| TASK-067 | Agregar navegación desde HomePage: botón "Mis Tarjetas" | | |
| TASK-068 | Implementar responsive design: Grid en desktop, List en móvil | | |

### Implementation Phase 8: End-to-End Tests (Playwright)

**GOAL-008**: Validar flujo completo con tests E2E según criterios de aceptación

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-069 | Crear `tests-e2e/tests/cards-list.spec.ts` | | |
| TASK-070 | **[Scenario 1]** Test: Usuario con 3 tarjetas ve listado completo | | |
| TASK-071 | **[Scenario 2]** Test: Usuario sin tarjetas ve mensaje vacío con botón "Agregar Primera Tarjeta" | | |
| TASK-072 | **[Scenario 3]** Test: Usuario con 3 tarjetas NO ve botón "Agregar Tarjeta" | | |
| TASK-073 | **[Scenario 4]** Test: Tarjeta con saldo 0 se muestra en rojo con etiqueta "Sin fondos" | | |
| TASK-074 | **[Scenario 5]** Test: Tiempo de carga < 500ms (performance assertion) | | |
| TASK-075 | Crear Page Object `CardsPage` en `tests-e2e/pages/` | | |
| TASK-076 | Usar locators accesibles: `getByRole()`, `getByText()`, `getByLabel()` | | |
| TASK-077 | Ejecutar tests: `npm test` en tests-e2e/ | | |

### Implementation Phase 9: Performance & Security

**GOAL-009**: Optimizar performance y asegurar compliance de seguridad

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-078 | Implementar caché Redis para GET /api/v1/cards (TTL: 60 segundos) | | |
| TASK-079 | Agregar rate limiting en endpoint: 10 requests/minuto por usuario | | |
| TASK-080 | Verificar que CVV NO se persiste en base de datos (audit DB schema) | | |
| TASK-081 | Implementar logging de accesos a endpoint para auditoría | | |
| TASK-082 | Configurar HTTPS en nginx para producción | | |
| TASK-083 | Ejecutar prueba de carga: 100 usuarios concurrentes deben recibir respuesta < 500ms | | |
| TASK-084 | Escanear vulnerabilidades con `npm audit` y `safety check` (Python) | | |

### Implementation Phase 10: Documentation & Deployment

**GOAL-010**: Documentar API y desplegar cambios

| Task     | Description           | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-085 | Actualizar Swagger docs con ejemplo de respuesta GET /api/v1/cards | | |
| TASK-086 | Documentar endpoint en README.md de api-gateway | | |
| TASK-087 | Crear migración de base de datos si se requiere nuevo schema | | |
| TASK-088 | Actualizar `docker-compose.yml` si hay nuevas variables de entorno | | |
| TASK-089 | Ejecutar suite completa de tests: `./scripts/run-tests-unified.ps1` | | |
| TASK-090 | Verificar coverage ≥ 95%: `pytest --cov=services --cov-report=html` | | |
| TASK-091 | Crear PR con template: tests escritos primero, 2+ aprobaciones requeridas | | |
| TASK-092 | Merge a `main` y desplegar a staging para QA manual | | |

## 3. Alternatives

Enfoques alternativos considerados y razones para no elegirlos:

- **ALT-001**: **GraphQL en lugar de REST** - Rechazado porque el proyecto ya usa REST en todos los endpoints existentes. Introducir GraphQL solo para tarjetas agregaría complejidad innecesaria y fragmentaría la arquitectura.

- **ALT-002**: **Server-Side Rendering (SSR) con Next.js** - Rechazado porque la aplicación es completamente privada (requiere autenticación) y no se beneficiaría de SEO. Vite + SPA es más ligero y suficiente.

- **ALT-003**: **Retornar número completo de tarjeta enmascarado en backend** - Rechazado por seguridad. Mejor NO almacenar ni transmitir número completo. Solo guardar últimos 4 dígitos + hash del número completo para validación.

- **ALT-004**: **Infinite scroll en lugar de límite fijo de 3 tarjetas** - Rechazado porque el límite de 3 es un requerimiento de negocio explícito (HU-015, Scenario 3).

- **ALT-005**: **State management con Redux** - Rechazado porque Zustand es más ligero y el estado de tarjetas es simple. Redux sería over-engineering para este caso de uso.

- **ALT-006**: **Guardar tarjetas en LocalStorage** - Rechazado por seguridad. Los datos sensibles deben estar solo en backend protegido con autenticación.

## 4. Dependencies

Dependencias necesarias para la implementación:

- **DEP-001**: **Backend - Pydantic**: Para validación de DTOs en FastAPI (ya instalado en proyecto)
- **DEP-002**: **Backend - PyJWT**: Para validación de tokens JWT en autenticación (ya instalado)
- **DEP-003**: **Backend - Motor (async MongoDB)**: Para acceso a MongoDB asíncrono (verificar versión ≥ 3.3)
- **DEP-004**: **Backend - Redis-py**: Para caché de endpoint GET /api/v1/cards (ya instalado)
- **DEP-005**: **Frontend - Axios**: Para llamadas HTTP (ya instalado en user-app)
- **DEP-006**: **Frontend - React Icons**: Para íconos de tarjetas (instalar: `npm install react-icons`)
- **DEP-007**: **Frontend - React Router v6**: Para navegación (ya instalado)
- **DEP-008**: **Frontend - TailwindCSS**: Para estilos (ya configurado)
- **DEP-009**: **Testing - Vitest**: Para tests unitarios de frontend (ya instalado)
- **DEP-010**: **Testing - Playwright**: Para tests E2E (ya instalado en tests-e2e/)
- **DEP-011**: **Testing - pytest-asyncio**: Para tests asíncronos de FastAPI (verificar instalación)
- **DEP-012**: **Testing - httpx**: Para tests de cliente HTTP asíncrono (instalar: `pip install httpx`)

## 5. Files

Archivos que serán creados o modificados durante la implementación:

**NUEVOS ARCHIVOS:**

- **FILE-001**: `services/fraud-evaluation-service/src/domain/models.py` - Agregar clases `Card`, `CardStatus`, `CardType`
- **FILE-002**: `services/fraud-evaluation-service/src/application/use_cases/get_user_cards.py` - Caso de uso GetUserCardsUseCase
- **FILE-003**: `services/fraud-evaluation-service/src/application/ports/card_repository.py` - Interface CardRepository
- **FILE-004**: `services/fraud-evaluation-service/src/adapters.py` - Agregar MongoDBCardAdapter
- **FILE-005**: `services/api-gateway/src/routes.py` - Agregar endpoint GET /api/v1/cards
- **FILE-006**: `frontend/user-app/src/components/CardList.tsx` - Componente lista de tarjetas
- **FILE-007**: `frontend/user-app/src/components/CardItem.tsx` - Componente tarjeta individual
- **FILE-008**: `frontend/user-app/src/hooks/useCards.ts` - Custom hook para gestión de tarjetas
- **FILE-009**: `frontend/user-app/src/pages/CardsPage.tsx` - Página de tarjetas
- **FILE-010**: `frontend/user-app/src/utils/cardFormatters.ts` - Funciones de formateo
- **FILE-011**: `tests/unit/test_card_models.py` - Tests unitarios de modelos
- **FILE-012**: `tests/unit/test_get_user_cards_use_case.py` - Tests de caso de uso
- **FILE-013**: `tests/integration/test_card_repository.py` - Tests de repositorio
- **FILE-014**: `tests/integration/test_cards_api.py` - Tests de endpoint API
- **FILE-015**: `frontend/user-app/src/components/__tests__/CardList.test.tsx` - Tests de componente
- **FILE-016**: `frontend/user-app/src/hooks/__tests__/useCards.test.ts` - Tests de hook
- **FILE-017**: `tests-e2e/tests/cards-list.spec.ts` - Tests E2E
- **FILE-018**: `tests-e2e/pages/CardsPage.ts` - Page Object Model

**ARCHIVOS MODIFICADOS:**

- **FILE-019**: `frontend/user-app/src/App.tsx` - Agregar ruta /cards
- **FILE-020**: `frontend/user-app/src/pages/HomePage.tsx` - Agregar botón "Mis Tarjetas"
- **FILE-021**: `services/api-gateway/src/main.py` - Registrar nuevas rutas si es necesario
- **FILE-022**: `docker-compose.yml` - Agregar variables de entorno si se requieren
- **FILE-023**: `README.md` - Actualizar documentación de endpoints

## 6. Testing

Tests que deben implementarse para garantizar calidad (TDD: tests escritos PRIMERO):

**UNIT TESTS (Backend):**

- **TEST-001**: `test_card_model_creation()` - Crear Card válida con todos los campos
- **TEST-002**: `test_card_model_mask_number()` - Verificar enmascaramiento muestra solo últimos 4 dígitos
- **TEST-003**: `test_card_model_negative_balance_raises_error()` - Saldo negativo debe fallar
- **TEST-004**: `test_card_status_enum_values()` - Enum tiene ACTIVE, BLOCKED, SUSPENDED
- **TEST-005**: `test_get_user_cards_use_case_success()` - Retorna 3 tarjetas ordenadas
- **TEST-006**: `test_get_user_cards_use_case_empty()` - Retorna lista vacía si no hay tarjetas
- **TEST-007**: `test_get_user_cards_use_case_orders_by_created_at_desc()` - Orden correcto

**INTEGRATION TESTS (Backend):**

- **TEST-008**: `test_card_repository_save_and_retrieve()` - Guardar y recuperar tarjeta de MongoDB
- **TEST-009**: `test_card_repository_get_by_user_id_empty()` - Usuario sin tarjetas retorna []
- **TEST-010**: `test_cards_api_get_success_200()` - GET /api/v1/cards retorna 200 con lista
- **TEST-011**: `test_cards_api_get_unauthorized_401()` - Sin JWT retorna 401
- **TEST-012**: `test_cards_api_get_forbidden_403()` - Usuario A no puede ver tarjetas de Usuario B
- **TEST-013**: `test_cards_api_cvv_not_in_response()` - CVV nunca aparece en response JSON

**UNIT TESTS (Frontend):**

- **TEST-014**: `test_card_list_renders_three_cards()` - Renderiza 3 tarjetas correctamente
- **TEST-015**: `test_card_list_shows_masked_number()` - Muestra ****1234 correctamente
- **TEST-016**: `test_card_list_zero_balance_red()` - Tarjeta con saldo 0 tiene texto rojo
- **TEST-017**: `test_card_list_empty_state()` - Sin tarjetas muestra mensaje + botón agregar
- **TEST-018**: `test_card_list_no_add_button_when_three_cards()` - Botón agregar NO aparece con 3 tarjetas
- **TEST-019**: `test_use_cards_hook_loading_state()` - Hook inicia con isLoading=true
- **TEST-020**: `test_use_cards_hook_success_state()` - Después de fetch, cards pobladas
- **TEST-021**: `test_use_cards_hook_error_state()` - Si API falla, error state se setea

**E2E TESTS (Playwright):**

- **TEST-022**: `test_e2e_user_views_three_cards()` - Flujo completo: login → navegar a tarjetas → ver 3 tarjetas
- **TEST-023**: `test_e2e_empty_state_shows_add_button()` - Usuario nuevo ve botón "Agregar Primera Tarjeta"
- **TEST-024**: `test_e2e_three_cards_hides_add_button()` - Con 3 tarjetas, botón NO visible
- **TEST-025**: `test_e2e_zero_balance_card_red()` - Tarjeta sin fondos se muestra en rojo
- **TEST-026**: `test_e2e_load_time_under_500ms()` - Tiempo de carga < 500ms

**PERFORMANCE TESTS:**

- **TEST-027**: `test_load_cards_under_500ms()` - Endpoint responde en < 500ms (p95)
- **TEST-028**: `test_concurrent_users_100()` - 100 usuarios concurrentes sin degradación

## 7. Risks & Assumptions

**RISKS:**

- **RISK-001**: **Migración de datos existentes** - Si ya hay tarjetas en el sistema legacy, se requiere script de migración. Mitigación: Crear script de migración y probarlo en staging primero.

- **RISK-002**: **Compliance PCI-DSS** - Almacenar cualquier dato de tarjeta requiere certificación PCI. Mitigación: NO almacenar número completo, solo últimos 4 dígitos + hash. Consultar con equipo de seguridad.

- **RISK-003**: **Performance con muchos usuarios** - Si hay 10,000+ usuarios consultando simultáneamente, puede haber carga en MongoDB. Mitigación: Implementar caché Redis con TTL de 60 segundos.

- **RISK-004**: **Cambio en límite de tarjetas** - El límite de 3 tarjetas puede cambiar en el futuro. Mitigación: Hacer límite configurable en backend (variable de entorno MAX_CARDS_PER_USER).

- **RISK-005**: **Frontend no maneja estados de error** - Si la API falla, el usuario puede quedar sin feedback. Mitigación: Implementar toast notifications para errores con react-hot-toast.

**ASSUMPTIONS:**

- **ASSUMPTION-001**: El usuario ya está autenticado cuando accede a /cards (JWT existe en localStorage)

- **ASSUMPTION-002**: El backend de autenticación ya expone endpoint para validar JWT (no hay que implementarlo)

- **ASSUMPTION-003**: MongoDB ya está configurado y accesible en docker-compose (no requiere setup adicional)

- **ASSUMPTION-004**: No se requiere sincronización en tiempo real (WebSocket). Refetch manual es suficiente.

- **ASSUMPTION-005**: El diseño UI/UX será proporcionado por equipo de diseño o se usará estilo por defecto de TailwindCSS

- **ASSUMPTION-006**: Los últimos 4 dígitos de la tarjeta son suficientes para que el usuario identifique cuál es cada tarjeta

## 8. Related Specifications / Further Reading

- [HU-015: Ver Múltiples Tarjetas con Saldo](../docs/user-stories/HU-015-view-cards.md) - Historia de usuario original
- [HU-016: Agregar Nueva Tarjeta](../docs/user-stories/HU-016-add-card.md) - Funcionalidad relacionada (agregar tarjetas)
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - Arquitectura del sistema (Clean Architecture, microservices)
- [CONTEXT.md](../docs/CONTEXT.md) - Guía de desarrollo, TDD workflow, Git workflow
- [PRODUCT.md](../docs/PRODUCT.md) - Visión de producto y user stories completas
- [PCI DSS Compliance Guide](https://www.pcisecuritystandards.org/) - Estándares de seguridad para datos de tarjetas
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/security/) - Autenticación y seguridad en FastAPI
- [React Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library) - Guía de testing en React
- [Playwright Best Practices](https://playwright.dev/docs/best-practices) - E2E testing con Playwright
