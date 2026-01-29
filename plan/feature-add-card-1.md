---
goal: "Implementar Historia de Usuario HU-016: Agregar Nueva Tarjeta de forma segura con validación Luhn, encriptación AES-256 y cumplimiento PCI DSS"
version: "1.0"
date_created: "2026-01-28"
last_updated: "2026-01-28"
owner: "FinTech Development Team"
status: "Planned"
tags: ["feature", "card-management", "security", "pci-dss", "critical"]
---

# ��� Plan de Implementación: HU-016 - Agregar Nueva Tarjeta

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implementación completa de la funcionalidad para que clientes registren nuevas tarjetas de pago de forma segura con validación en tiempo real, encriptación de datos sensibles, y cumplimiento de estándares PCI DSS.

---

## 1. Requirements & Constraints

### Requisitos Funcionales
- **REQ-001**: Formulario con 7 campos: número, vencimiento, CVV, cédula, nombre titular, tipo (débito/crédito), apodo (opcional)
- **REQ-002**: Validación automática con algoritmo de Luhn para número de tarjeta
- **REQ-003**: Detección automática de tipo de tarjeta (VISA, Mastercard, Amex) con visualización de ícono
- **REQ-004**: Máximo 3 tarjetas por usuario
- **REQ-005**: Prevención de tarjetas duplicadas (por número completo)
- **REQ-006**: Formateo automático: números (4532-0151-1283-0366), vencimiento (MM/AA)
- **REQ-007**: Validación de fecha de vencimiento (no puede ser pasada)
- **REQ-008**: CVV enmascarado mientras se escribe (●●●)
- **REQ-009**: Nombre por defecto si apodo no se completa (ej: "Tarjeta Débito 0366")
- **REQ-010**: Respuesta exitosa retorna solo últimos 4 dígitos

### Requisitos de Seguridad
- **SEC-001**: CVV NUNCA se almacena en base de datos
- **SEC-002**: CVV NUNCA se retorna en respuesta HTTP
- **SEC-003**: CVV NUNCA se registra en logs
- **SEC-004**: Número de tarjeta encriptado con AES-256 en reposo
- **SEC-005**: Rate-limiting: máximo 5 intentos por minuto por usuario
- **SEC-006**: HTTPS obligatorio en producción
- **SEC-007**: JWT token requerido en autorización
- **SEC-008**: Datos sensibles no se logean nunca

### Requisitos de Cumplimiento
- **COMP-001**: Cumplimiento PCI DSS nivel 1
- **COMP-002**: No transmitir CVV al backend (frontend-only validation aceptable)
- **COMP-003**: Auditoría de intentos fallidos
- **COMP-004**: Encriptación end-to-end

### Constraints Técnicos
- **CON-001**: Máximo response time 2 segundos (frontend + backend)
- **CON-002**: Mantener coverage >95% (actual: 95%)
- **CON-003**: Clean Architecture: domain layer sin imports de FastAPI/Pydantic
- **CON-004**: TDD obligatorio: escribir tests antes de código
- **CON-005**: Sin modificar estructura existente de microservicios

### Patrones a Seguir
- **PAT-001**: Strategy Pattern para validadores de tarjeta (Luhn, Expiry, CardType)
- **PAT-002**: Value Objects inmutables para Card, CardType, ExpiryDate
- **PAT-003**: Repository Pattern para persistencia de tarjetas
- **PAT-004**: Dependency Injection para adapters (MongoDB, Redis)
- **PAT-005**: Use Cases en application layer (CreateCardUseCase)

### Guidelines de Código
- **GUD-001**: Domain models en `domain/` sin dependencias externas
- **GUD-002**: Validadores inmutables con @dataclass(frozen=True)
- **GUD-003**: Tests con pytest.mark.unit y pytest.mark.integration
- **GUD-004**: Componentes React con role-based locators en tests E2E

---

## 2. Implementation Steps

### ��� Implementation Phase 1: Backend Domain Layer (Modelos y Validadores)

**GOAL-001**: Crear modelos de dominio puro para tarjetas (Card, CardType, ExpiryDate) y validadores (Luhn, tipo, vencimiento) sin dependencias externas.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Crear archivo `services/fraud-evaluation-service/src/domain/card_models.py` con Value Objects: `Card`, `CardType`, `ExpiryDate`, `CardValidation` | | |
| TASK-002 | Implementar `CardType` enum: VISA, MASTERCARD, AMEX (numeric codes) | | |
| TASK-003 | Crear `ExpiryDate` value object con validación de fecha pasada | | |
| TASK-004 | Crear archivo `services/fraud-evaluation-service/src/domain/card_validators.py` | | |
| TASK-005 | Implementar `LuhnValidator` class con método `validate(number: str) → bool` | | |
| TASK-006 | Implementar `CardTypeDetector` con método `detect(number: str) → CardType` para VISA/MC/AMEX | | |
| TASK-007 | Implementar `ExpiryValidator` con método `validate(month: int, year: int) → bool` | | |
| TASK-008 | Crear `CardNumberValidator` class - valida formato y rangos (13-19 dígitos) | | |
| TASK-009 | Crear `CVVValidator` class - valida 3 dígitos (VISA/MC) o 4 (Amex) | | |
| TASK-010 | Escribir tests en `tests/unit/test_card_models.py` (Luhn, tipo, vencimiento) | | |
| TASK-011 | Escribir tests en `tests/unit/test_card_validators.py` con casos límite | | |

**Deliverables**:
- ✅ `domain/card_models.py` - Value Objects con @dataclass(frozen=True)
- ✅ `domain/card_validators.py` - Validadores puros sin side effects
- ✅ `tests/unit/test_card_models.py` - 12+ tests
- ✅ `tests/unit/test_card_validators.py` - 20+ tests (Luhn edge cases)

**Validation Criteria**:
- [ ] `pytest tests/unit/test_card_models.py -v` pasa al 100%
- [ ] `pytest tests/unit/test_card_validators.py -v` pasa al 100%
- [ ] Coverage de domain/card_* ≥99%
- [ ] Sin imports de FastAPI, MongoDB, Pydantic en domain/

---

### ��� Implementation Phase 2: Backend Application Layer (Use Cases)

**GOAL-002**: Crear use case `CreateCardUseCase` que orquesta validación, encriptación y persistencia usando puertos (interfaces).

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-012 | Crear archivo `services/fraud-evaluation-service/src/application/use_cases/create_card.py` | | |
| TASK-013 | Definir `CardRepository` port (interface) en `application/ports/` con métodos: `save()`, `get_by_user()`, `exists()` | | |
| TASK-014 | Definir `EncryptionService` port con métodos: `encrypt(data: str) → str`, `decrypt(data: str) → str` | | |
| TASK-015 | Definir `CardLimitChecker` port para verificar máximo 3 tarjetas por usuario | | |
| TASK-016 | Implementar `CreateCardUseCase` orquestando: validadores → encriptación → repository.save() | | |
| TASK-017 | Implementar lógica de prevención de duplicados usando último número de tarjeta | | |
| TASK-018 | Implementar generación de nombre default si apodo vacío: f"Tarjeta {card_type.name} {last_4_digits}" | | |
| TASK-019 | Escribir tests en `tests/unit/test_create_card_use_case.py` con mocks de puertos | | |
| TASK-020 | Verificar que CVV nunca se persiste (solo validado en dominio) | | |

**Deliverables**:
- ✅ `application/use_cases/create_card.py` - Use case con DI
- ✅ `application/ports/card_repository.py` - Port interface
- ✅ `application/ports/encryption_service.py` - Port interface
- ✅ `tests/unit/test_create_card_use_case.py` - 15+ tests

**Validation Criteria**:
- [ ] `pytest tests/unit/test_create_card_use_case.py -v` pasa al 100%
- [ ] CreateCardUseCase recibe todos los puertos vía constructor (DI)
- [ ] CVV no aparece en ningún output o log
- [ ] Coverage ≥95%

---

### ��� Implementation Phase 3: Backend Infrastructure (Adapters y API Gateway)

**GOAL-003**: Implementar adapters (MongoDB, Encriptación AES-256) y endpoint REST con validación Pydantic.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-021 | Crear `services/fraud-evaluation-service/src/adapters/card_repository_adapter.py` que implementa `CardRepository` con MongoDB | | |
| TASK-022 | Crear `services/fraud-evaluation-service/src/adapters/encryption_adapter.py` con AES-256 (usar cryptography library) | | |
| TASK-023 | Agregar migration MongoDB para colección `cards` con campos: user_id, encrypted_number, last_4_digits, card_type, expiry_month, expiry_year, holder_name, nickname, created_at, updated_at | | |
| TASK-024 | Crear modelo Pydantic en `services/api-gateway/src/schemas/card_schemas.py`: `CreateCardRequest` (sin validación lógica, solo estructura) | | |
| TASK-025 | Crear modelo Pydantic `CardResponse` retornando SOLO: user_id, last_4_digits, card_type, holder_name, nickname, created_at | | |
| TASK-026 | Crear endpoint `POST /api/v1/cards` en `services/api-gateway/src/routes.py` | | |
| TASK-027 | Implementar rate-limiting: máximo 5 intentos por minuto por (user_id + endpoint) usando Redis | | |
| TASK-028 | Agregar logs de auditoría (sin CVV, sin número completo) en endpoint | | |
| TASK-029 | Implementar error handling: duplicado, límite alcanzado, validación fallida | | |
| TASK-030 | Escribir tests en `tests/integration/test_create_card_endpoint.py` | | |

**Deliverables**:
- ✅ `adapters/card_repository_adapter.py` - MongoDB adapter
- ✅ `adapters/encryption_adapter.py` - AES-256 encryption
- ✅ `services/api-gateway/src/schemas/card_schemas.py` - Pydantic models
- ✅ `services/api-gateway/src/routes.py` - POST /api/v1/cards endpoint
- ✅ MongoDB migration para tabla `cards`
- ✅ `tests/integration/test_create_card_endpoint.py` - 10+ tests

**Validation Criteria**:
- [ ] `pytest tests/integration/test_create_card_endpoint.py -v` pasa al 100%
- [ ] Endpoint retorna 201 Created con CardResponse (sin CVV, sin número completo)
- [ ] Duplicados retornan 409 Conflict
- [ ] Rate-limit retorna 429 Too Many Requests después de 5 intentos
- [ ] Número encriptado en BD con AES-256
- [ ] CVV nunca aparece en logs

---

### ��� Implementation Phase 4: Frontend - Componentes React

**GOAL-004**: Crear componentes React para formulario `AddCardForm.tsx` con validación en tiempo real, máscaras, y detección de tipo.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-031 | Crear archivo `frontend/user-app/src/components/Cards/AddCardForm.tsx` | | |
| TASK-032 | Crear `frontend/user-app/src/hooks/useCardValidation.ts` con lógica de validación en tiempo real | | |
| TASK-033 | Crear máscaras automáticas: número (4532-0151-1283-0366), expiry (MM/AA) usando regex | | |
| TASK-034 | Implementar CVV enmascarado (mostrar ●●● mientras se escribe) | | |
| TASK-035 | Integrar detección de tipo (VISA, MC, AMEX) con ícono mostrado en tiempo real | | |
| TASK-036 | Validación visual: campo verde si válido, rojo si inválido | | |
| TASK-037 | Botón "Guardar" deshabilitado hasta llenar todos los campos (apodo es opcional) | | |
| TASK-038 | Mostrar estado "Guardando..." mientras POST está en vuelo | | |
| TASK-039 | Mostrar mensaje de éxito: "Tarjeta agregada exitosamente" y cerrar formulario | | |
| TASK-040 | Mostrar errores específicos: "Ya tienes esta tarjeta registrada", "Número inválido", etc. | | |
| TASK-041 | Implementar lógica de cierre: descartar datos si usuario cancela sin guardar | | |

**Deliverables**:
- ✅ `frontend/user-app/src/components/Cards/AddCardForm.tsx` - Form component
- ✅ `frontend/user-app/src/hooks/useCardValidation.ts` - Validation hook
- ✅ `frontend/user-app/src/utils/cardFormatting.ts` - Máscaras y formateo
- ✅ `frontend/user-app/src/utils/cardDetection.ts` - Detección de tipo (Luhn check)

**Validation Criteria**:
- [ ] Formulario abre cuando usuario hace clic en "Agregar Tarjeta"
- [ ] Número válido se formatea automáticamente (4532-0151-1283-0366)
- [ ] Tipo detectado correctamente (VISA, MC, AMEX)
- [ ] Campos inválidos muestran borde rojo + mensaje de error
- [ ] Botón guardador solo habilitado cuando válido
- [ ] CVV nunca visible en DevTools o Network

---

### ��� Implementation Phase 5: Frontend - Integración con API

**GOAL-005**: Conectar componente AddCardForm al endpoint `POST /api/v1/cards` con manejo de errores y estado de carga.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-042 | Crear servicio `frontend/user-app/src/services/cardService.ts` con método `addCard(data)` | | |
| TASK-043 | Implementar interceptor Axios para agregar JWT token en header Authorization | | |
| TASK-044 | Manejo de errores 409 (duplicado), 429 (rate-limit), 400 (validación), 500 (servidor) | | |
| TASK-045 | Mostrar spinner/loading mientras API responde | | |
| TASK-046 | Refrescar lista de tarjetas después de agregar exitosamente | | |
| TASK-047 | Integrar con Zustand store para estado global de tarjetas | | |

**Deliverables**:
- ✅ `frontend/user-app/src/services/cardService.ts` - API integration
- ✅ Zustand store actualizado para estado de tarjetas

**Validation Criteria**:
- [ ] AddCardForm envía POST a `POST /api/v1/cards`
- [ ] JWT token incluido en headers
- [ ] Errores mostrados al usuario (sin exponer CVV)
- [ ] Loading state visible mientras API procesa
- [ ] CardList (HU-015) se actualiza automáticamente

---

### ��� Implementation Phase 6: End-to-End Tests (Playwright)

**GOAL-006**: Escribir 7 tests E2E que validen los 7 scenarios de aceptación usando Playwright.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-048 | Crear archivo `tests-e2e/tests/add-card.spec.ts` | | |
| TASK-049 | Test 1: Formulario abre correctamente con todos los campos | | |
| TASK-050 | Test 2: Usuario ingresa número válido, se formatea y detecta tipo VISA | | |
| TASK-051 | Test 3: Usuario ingresa número inválido, muestra error en rojo | | |
| TASK-052 | Test 4: Usuario ingresa fecha expirada, muestra error | | |
| TASK-053 | Test 5: Usuario completa y guarda, ve éxito y formulario cierra | | |
| TASK-054 | Test 6: Usuario intenta duplicado, ve error "Ya tienes esta tarjeta" | | |
| TASK-055 | Test 7: Usuario omite apodo, tarjeta se crea con nombre default | | |
| TASK-056 | Usar role-based locators: getByRole, getByLabel, getByText | | |
| TASK-057 | Usar test.step() para agrupar acciones y mejorar reporting | | |
| TASK-058 | Usar auto-retrying assertions: await expect(locator).toHaveText() | | |

**Deliverables**:
- ✅ `tests-e2e/tests/add-card.spec.ts` - 7 tests Playwright
- ✅ Page Object Model en `tests-e2e/pages/CardPage.ts` (reutilizable)

**Validation Criteria**:
- [ ] `npx playwright test tests-e2e/tests/add-card.spec.ts` pasa al 100%
- [ ] Todos los 7 scenarios implementados
- [ ] Sin timeouts hard-coded
- [ ] Role-based locators solo (no ID selectores)

---

### ��� Implementation Phase 7: Validación, Coverage, Seguridad

**GOAL-007**: Asegurar coverage >95%, sin vulnerabilidades, y cumplimiento de PCI DSS.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-059 | Ejecutar `pytest tests/ --cov=services --cov-report=html` | | |
| TASK-060 | Asegurar coverage ≥95% para card_models.py, card_validators.py, create_card.py | | |
| TASK-061 | Ejecutar linter: `pylint services/` sin errores de seguridad | | |
| TASK-062 | Escanear secretos: `git-secrets` para CVV/números hardcodeados | | |
| TASK-063 | Validar AES-256: verificar que `encryption_adapter.py` usa `cryptography.hazmat` | | |
| TASK-064 | Audit logs: verificar que logs de intento fallido NO contienen CVV | | |
| TASK-065 | Rate-limiting: verificar Redis key format y TTL correcto | | |
| TASK-066 | Load test: verificar endpoint puede manejar 100 requests/segundo | | |

**Deliverables**:
- ✅ Coverage report >95%
- ✅ Linter clean
- ✅ Security scan report

**Validation Criteria**:
- [ ] `pytest --cov-fail-under=95` pasa
- [ ] `bandit services/` sin issues de seguridad
- [ ] CVV nunca en logs (grep -r "CVV" services/ returns 0)
- [ ] AES-256 implementado correctamente

---

## 3. Alternatives

- **ALT-001**: Almacenar CVV en Redis con TTL de 5 minutos (REJECTED - violaría PCI DSS, CVV nunca debe persistirse)
- **ALT-002**: Usar biblioteca externa para validación Luhn (REJECTED - mantener lógica propia para control total)
- **ALT-003**: Generar Device Fingerprint automático (OUT OF SCOPE - corresponde a HU-004)
- **ALT-004**: Permitir editar tarjetas (REJECTED - HU-016 es solo "Agregar", editar es futura)

---

## 4. Dependencies

- **DEP-001**: HU-015 completada (CardList component, sin AddCardForm aún)
- **DEP-002**: MongoDB colección `cards` migrada
- **DEP-003**: Redis configurado para rate-limiting
- **DEP-004**: Biblioteca `cryptography` instalada (para AES-256)
- **DEP-005**: JWT authentication funcionando (API Gateway)
- **DEP-006**: Zustand store para estado global de tarjetas

**External Libraries to Install**:
```toml
# pyproject.toml
cryptography = "^41.0.0"  # AES-256 encryption
pydantic = "^2.5.0"        # Validation (ya existe)

# frontend/user-app/package.json
"lucide-react": "^0.x"     # Iconos de tarjetas (VISA, MC, AMEX)
```

---

## 5. Files

### Backend Files to Create/Modify

| File | Purpose | Type |
|------|---------|------|
| `services/fraud-evaluation-service/src/domain/card_models.py` | Value Objects Card, CardType, ExpiryDate | NEW |
| `services/fraud-evaluation-service/src/domain/card_validators.py` | Luhn, tipo, vencimiento, formato | NEW |
| `services/fraud-evaluation-service/src/application/use_cases/create_card.py` | CreateCardUseCase orquestación | NEW |
| `services/fraud-evaluation-service/src/application/ports/card_repository.py` | CardRepository interface | NEW |
| `services/fraud-evaluation-service/src/application/ports/encryption_service.py` | EncryptionService interface | NEW |
| `services/fraud-evaluation-service/src/adapters/card_repository_adapter.py` | MongoDB adapter | NEW |
| `services/fraud-evaluation-service/src/adapters/encryption_adapter.py` | AES-256 adapter | NEW |
| `services/api-gateway/src/schemas/card_schemas.py` | Pydantic models | NEW |
| `services/api-gateway/src/routes.py` | POST /api/v1/cards endpoint | MODIFY |
| `tests/unit/test_card_models.py` | Unit tests dominio | NEW |
| `tests/unit/test_card_validators.py` | Unit tests validadores | NEW |
| `tests/unit/test_create_card_use_case.py` | Unit tests use case | NEW |
| `tests/integration/test_create_card_endpoint.py` | Integration tests API | NEW |

### Frontend Files to Create/Modify

| File | Purpose | Type |
|------|---------|------|
| `frontend/user-app/src/components/Cards/AddCardForm.tsx` | Formulario agregar tarjeta | NEW |
| `frontend/user-app/src/hooks/useCardValidation.ts` | Hook de validación | NEW |
| `frontend/user-app/src/utils/cardFormatting.ts` | Máscaras y formateo | NEW |
| `frontend/user-app/src/utils/cardDetection.ts` | Detección de tipo Luhn | NEW |
| `frontend/user-app/src/services/cardService.ts` | API integration | NEW |
| `frontend/user-app/src/components/Cards/CardList.tsx` | Integración con AddCardForm | MODIFY |
| `tests-e2e/tests/add-card.spec.ts` | E2E tests Playwright | NEW |
| `tests-e2e/pages/CardPage.ts` | Page Object Model | NEW |

### Infrastructure Files

| File | Purpose | Type |
|------|---------|------|
| `migrations/001_create_cards_table.py` | MongoDB collection schema | NEW |
| `.github/workflows/ci.yml` | CI pipeline (validar tests) | MODIFY |

---

## 6. Testing

### Unit Tests (TDD First)

| Test File | Count | Coverage | Key Scenarios |
|-----------|-------|----------|----------------|
| `test_card_models.py` | 12 | CardType, ExpiryDate immutability | Válido, inválido, expirado |
| `test_card_validators.py` | 20 | Luhn, tipo, vencimiento | VISA válido, MC, AMEX, 4-digit CVV |
| `test_create_card_use_case.py` | 15 | Orquestación, puertos | Éxito, duplicado, límite 3 tarjetas |
| **Total Unit** | **47** | **≥95%** | **Domain + Application** |

**Example Test Structure** (`test_card_validators.py`):

```python
@pytest.mark.unit
class TestLuhnValidator:
    def test_valid_visa_number(self):
        # Test VISA 4532015112830366
        assert LuhnValidator.validate("4532015112830366") == True
    
    def test_invalid_luhn_checksum(self):
        # Test 1234567890123456 (invalid)
        assert LuhnValidator.validate("1234567890123456") == False
    
    def test_edge_case_single_digit(self):
        # Test "5" (too short)
        assert LuhnValidator.validate("5") == False

@pytest.mark.unit
class TestCardTypeDetector:
    def test_detect_visa(self):
        assert CardTypeDetector.detect("4532015112830366") == CardType.VISA
    
    def test_detect_mastercard(self):
        assert CardTypeDetector.detect("5425233010103442") == CardType.MASTERCARD
    
    def test_detect_amex(self):
        assert CardTypeDetector.detect("374245455400126") == CardType.AMEX
```

### Integration Tests

| Test File | Count | Coverage | Key Scenarios |
|-----------|-------|----------|----------------|
| `test_create_card_endpoint.py` | 10 | API + adapters | 201 Created, 409 Conflict, 429 Rate-limit |

**Example Test**:

```python
@pytest.mark.integration
async def test_create_card_success(client, authenticated_user, db):
    response = await client.post("/api/v1/cards", json={
        "number": "4532015112830366",
        "expiry_month": 12,
        "expiry_year": 2026,
        "cvv": "123",
        "holder_name": "Juan Pérez",
        "document_id": "1234567890"
    })
    assert response.status_code == 201
    # Verify number encrypted in DB
    card_in_db = await db.cards.find_one({"user_id": authenticated_user.id})
    assert card_in_db["last_4_digits"] == "0366"
    assert card_in_db["encrypted_number"] != "4532015112830366"
```

### E2E Tests (Playwright)

| Test File | Count | Coverage | Scenarios |
|-----------|-------|----------|-----------|
| `add-card.spec.ts` | 7 | All AC | Todos los 7 gherkin scenarios |

**Example E2E Test**:

```typescript
test('Scenario 2: Usuario ingresa número válido', async ({ page }) => {
  const cardPage = new CardPage(page);
  
  await test.step('Abrir formulario', async () => {
    await cardPage.clickAddCardButton();
  });
  
  await test.step('Ingresar número VISA válido', async () => {
    await cardPage.enterCardNumber('4532015112830366');
  });
  
  await test.step('Verificar formateo automático', async () => {
    await expect(cardPage.cardNumberInput).toHaveValue('4532-0151-1283-0366');
  });
  
  await test.step('Verificar detección de tipo VISA', async () => {
    await expect(cardPage.visaIcon).toBeVisible();
    await expect(cardPage.cardNumberField).toHaveClass(/border-green/);
  });
});
```

**Coverage Summary**:
- ✅ Unit: 47 tests (domain + application)
- ✅ Integration: 10 tests (API + adapters)
- ✅ E2E: 7 tests (Playwright, user flows)
- ✅ **Total: 64 tests, Coverage ≥95%**

---

## 7. Risks & Assumptions

### Risks

- **RISK-001**: **CVV Exposure**: Si CVV se loguea accidentalmente, violación PCI DSS crítica
  - *Mitigation*: Implementar guard clauses en logging, usar secret masking en CI/CD
  
- **RISK-002**: **Encriptación débil**: AES-256 mal implementado = datos comprometidos
  - *Mitigation*: Usar `cryptography.hazmat` library (producción-ready), código review por security
  
- **RISK-003**: **Rate-limiting bypass**: Redis con TTL incorrecto = ataque de fuerza bruta
  - *Mitigation*: Tests específicos para rate-limiting, monitoreo en producción
  
- **RISK-004**: **Duplicados no detectados**: Comparación de números sin encripción = lógica débil
  - *Mitigation*: Usar last_4_digits + card_type + expiry para identificación única
  
- **RISK-005**: **Frontend CVV storage**: Si CVV se guarda en localStorage = exposición
  - *Mitigation*: CVV ONLY en memory durante validación, nunca persistir

### Assumptions

- **ASSUMPTION-001**: MongoDB colección `cards` ya existe (migración a crear)
- **ASSUMPTION-002**: Redis funcionando para rate-limiting
- **ASSUMPTION-003**: JWT authentication ya implementada en API Gateway
- **ASSUMPTION-004**: HU-015 (CardList) completada y funcional
- **ASSUMPTION-005**: `cryptography` library disponible en `pyproject.toml`
- **ASSUMPTION-006**: Frontend puede ejecutar Luhn validation antes de enviar al backend
- **ASSUMPTION-007**: HTTPS en producción (required para datos sensibles)

---

## 8. Related Specifications / Further Reading

- [HU-015: View Cards](../user-stories/HU-015-view-cards.md) - Prerequisite (CardList component)
- [HU-017: Process Transaction](../user-stories/HU-017-process-transaction.md) - Usará tarjetas registradas
- [ARCHITECTURE.md - Clean Architecture](../ARCHITECTURE.md#layered-architecture) - Domain/Application/Infrastructure layers
- [CONTEXT.md - TDD Workflow](../CONTEXT.md#tddbdd-workflow) - Red → Green → Refactor cycle
- [PCI DSS Compliance Guidelines](https://www.pcisecuritystandards.org/) - External reference
- [Cryptography Library Docs](https://cryptography.io/) - AES-256 implementation
- [Playwright Best Practices](../CONTEXT.md#testing-standards) - E2E test patterns

---

**Plan Status**: Ready for implementation (Planned → In Progress)
**Last Updated**: 2026-01-28
**Next Steps**: 
1. Assign tasks a developers
2. Crear ramas: `feature/HU-016-add-card`
3. Iniciar con Phase 1 (domain models)
4. TDD: Red → Green → Refactor para cada task
5. PR review antes de merge

