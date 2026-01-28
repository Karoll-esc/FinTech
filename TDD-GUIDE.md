# 📋 Guía de Implementación TDD y Conventional Commits

Resumen del Proyecto: Este documento sirve como referencia rápida para implementar funcionalidades utilizando Test-Driven Development (TDD) combinado con un flujo estricto de Conventional Commits. El objetivo es estandarizar la calidad del código y mantener un historial de cambios limpio y descriptivo.

---

## 🔄 El Ciclo TDD + Git Workflow

El objetivo es realizar commits atómicos que cuenten la historia del desarrollo paso a paso.

| Fase | Acción TDD | Tipo de Commit | Estructura del Mensaje de Commit |
|------|-----------|----------------|---------------------------------|
| 🔴 RED | Escribir prueba que falla | test | `test(scope): add failing test for [behavior]` |
| 🟢 GREEN | Código mínimo para pasar | feat / fix | `feat(scope): implement [logic] to pass tests` |
| ♻️ REFACTOR | Mejorar código sin romper tests | refactor | `refactor(scope): optimize [logic] logic` |

---

## 📚 Referencia de Tipos de Commit

- **feat**: Nueva funcionalidad (Fase Green)
- **fix**: Corrección de errores
- **test**: Añadir o corregir pruebas (Fase Red)
- **refactor**: Cambio de código que no corrige bugs ni añade funcionalidad (Fase Refactor)
- **docs**: Solo cambios en documentación
- **style**: Formato (espacios, punto y coma) sin cambios en lógica
- **chore**: Tareas de mantenimiento, dependencias, configuración de build

---

## 📊 Matriz de Prioridad (Planificación)

Define qué historias de usuario atacar primero basándote en riesgo y valor.

### 🔴 Prioridad 1: Core / Reglas de Negocio

**Enfoque**: Lógica pura, Validaciones, Entidades, Modelos de Dominio.

| Funcionalidad / ID | Pruebas Críticas (Unitarias) | Valor de Negocio | Scope Sugerido (Git) |
|-------------------|------------------------------|------------------|----------------------|
| [ID-01] | Validaciones de entrada, inmutabilidad | Integridad de datos | domain/validation |
| [ID-02] | Algoritmos complejos, cálculos financieros | Diferenciador clave | domain/logic |

### 🟡 Prioridad 2: Integración / APIs

**Enfoque**: Controladores, Bases de Datos, Servicios Externos, Middleware.

| Funcionalidad / ID | Pruebas Críticas (Integración) | Valor de Negocio | Scope Sugerido (Git) |
|-------------------|--------------------------------|------------------|----------------------|
| [ID-03] | Endpoints API, Conexión DB | Flujo principal de datos | api/endpoints |
| [ID-04] | Manejo de errores externos (Timeouts) | Resiliencia del sistema | api/adapters |

### 🟢 Prioridad 3: Experiencia de Usuario (E2E)

**Enfoque**: Flujos completos, Interfaz visual, Interacción del usuario.

| Funcionalidad / ID | Pruebas Críticas (E2E) | Valor de Negocio | Scope Sugerido (Git) |
|-------------------|------------------------|------------------|----------------------|
| [ID-05] | Happy path completo (Inicio a Fin) | Satisfacción del usuario | ui/journey |

---

## 🧪 Estrategia de Pruebas (Test Pyramid)

Adapta los porcentajes según la naturaleza del proyecto (ej. más unitarios en librerías de cálculo, más integración en APIs CRUD).

```
           /\
          /  \         E2E Tests (~10%)
         /____\        ↓ Objetivo: Validar flujos críticos de negocio.
        /      \       ↓ Herramientas: Cypress, Playwright.
       /        \      Integration Tests (~20%)
      /__________\     ↓ Objetivo: Validar contratos (API/DB) y comunicación.
     /            \    ↓ Herramientas: Supertest, TestContainers.
    /              \   Unit Tests (~70%)
   /________________\  ↓ Objetivo: Validar lógica aislada y rápida.
                       ↓ Herramientas: Jest, Vitest, Mocha.
```

---

## 📝 Checklist de Implementación por Historia

Copia y pega esta sección para cada nueva funcionalidad que desarrolles.

### Funcionalidad: [Nombre]

**Contexto**: [Breve descripción de qué hace esta funcionalidad]

---

### 1. Nivel Unitario (Lógica de Negocio)

**Objetivo**: Probar la lógica aislada sin dependencias externas.

#### Ciclo de Desarrollo:

1. **🔴 Escribir Test**: Definir inputs y el output esperado (el test debe fallar).
   ```bash
   git commit -m "test([scope]): ensure [function] returns correct value"
   ```

2. **🟢 Implementar**: Escribir la función básica para pasar el test.
   ```bash
   git commit -m "feat([scope]): implement [function] logic"
   ```

3. **♻️ Refactor**: Limpiar código, extraer métodos, mejorar nombres.
   ```bash
   git commit -m "refactor([scope]): simplify [function] complexity"
   ```

#### Plantilla de Test Unitario

```typescript
describe('[Entity/Service Name]', () => {
  // Caso: Éxito
  test('should return [expected result] when [condition is met]', () => {
    // Arrange (Preparar datos)
    // Act (Ejecutar función)
    // Assert (Verificar resultado)
  });

  // Caso: Error / Validación
  test('should throw [SpecificError] when input is invalid', () => {
     // ...
  });

  // Caso: Borde
  test('should handle boundaries (min/max values, empty arrays)', () => {
     // ...
  });
});
```

---

### 2. Nivel Integración (API / Controladores)

**Objetivo**: Probar que las piezas se comunican correctamente (HTTP, DB).

#### Ciclo de Desarrollo:

1. **🔴 Test**: Llamada al endpoint esperando 200 OK (fallará por 404 o 500).
   ```bash
   git commit -m "test(api): add integration test for [METHOD] /[route]"
   ```

2. **🟢 Implementar**: Crear ruta, controlador y conectar servicio.
   ```bash
   git commit -m "feat(api): expose [METHOD] /[route] endpoint"
   ```

3. **♻️ Refactor**: Añadir middleware de validación, manejo de errores centralizado.
   ```bash
   git commit -m "refactor(api): extract validation middleware"
   ```

#### Plantilla de Test de Integración

```typescript
describe('[HTTP Method] [Route]', () => {
  test('should return 200 and [json structure] on success', async () => {
    // Mockear DB o Servicios Externos si es estrictamente necesario
    const response = await request(app).post('/api/[resource]').send(validPayload);
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('id');
  });

  test('should return 400 when validation fails', async () => {
    const response = await request(app).post('/api/[resource]').send(invalidPayload);
    expect(response.status).toBe(400);
  });
});
```

---

### 3. Nivel E2E (UI / Flujo Completo)

**Objetivo**: Simular el comportamiento del usuario final en un entorno real o semi-real.

#### Ciclo de Desarrollo:

1. **🔴 Test**: Script de navegación que busca un elemento que aún no existe en la UI.
   ```bash
   git commit -m "test(e2e): add scenario for [user flow]"
   ```

2. **🟢 Implementar**: Crear componentes UI, conectar al backend y renderizar datos.
   ```bash
   git commit -m "feat(ui): build [component] and connect integration"
   ```

3. **♻️ Refactor**: Mejorar selectores (data-testid), accesibilidad (a11y).
   ```bash
   git commit -m "refactor(ui): improve accessibility labels"
   ```

#### Plantilla de Test E2E

```typescript
test('User can [perform action] successfully', async ({ page }) => {
  await page.goto('/[page-url]');
  await page.fill('[data-testid="input-name"]', 'test data');
  await page.click('button:has-text("Submit")');
  
  await expect(page.locator('.success-message')).toBeVisible();
});
```

---

## 🤖 Prompts para Copilot/AI (Agnósticos)

Usa estos prompts para acelerar tu flujo TDD sin escribir todo el boilerplate manualmente.

### Prompt 1: Generar Casos de Prueba (Unitarios)

```text
Act as a Senior QA Engineer. Generate a list of edge case unit tests 
for a function/class that handles [CONTEXTO/REGLA DE NEGOCIO].

Consider:
- Null/Undefined inputs
- Boundary values (min, max, exact limits)
- Invalid data types
- Business logic constraints: [MENCIONAR REGLA ESPECIFICA]

Output as a bulleted list describing the tests scenarios.
```

### Prompt 2: Generar Mocks de Datos

```text
Generate a TypeScript interface for [ENTITY NAME] based on the 
following fields: [LIST FIELDS].

Then, create an array of 3 mock objects that represent:
1. A standard valid case (Happy Path).
2. An edge case (Boundary values).
3. A case that triggers specific error logic.
```

### Prompt 3: Generar Tests de Integración

```text
Write a [Jest/Supertest] integration test for a [METHOD] [ROUTE] endpoint.

Scenarios:
- Happy path: Valid input returns 200 OK and expected JSON.
- Error path: Invalid input returns 400 Bad Request.
- Server error: Database failure returns 500 Internal Server Error.

Assume the Express app is exported as 'app'.
```

---

## 🚫 Errores Comunes (Anti-Patrones)

### ❌ Commits Gigantes
**Problema**: No hacer commit de 5 tests y 5 implementaciones juntos.

**Solución**: Sigue el ciclo: 1 Test → Commit → 1 Implementación → Commit.

### ❌ Testear Implementación
**Problema**: No pruebes cómo funciona internamente (ej. métodos privados).

**Solución**: Prueba qué hace (input/output público).

### ❌ Mensajes de Commit Vagos
**Problema**: Evita "wip", "fix tests", "update".

**Solución**: Usa `test(auth): add failing test for login timeout`.

### ❌ Saltarse la Fase Roja
**Problema**: Si el test pasa a la primera sin haber escrito código nuevo, el test está mal diseñado.

**Solución**: Asegúrate de verlo fallar primero.

### ❌ Mocks Excesivos
**Problema**: No mockees todo. En los tests de integración, trata de usar una base de datos en memoria o contenedores si es posible.

**Solución**: Usa contenedores o DBs en memoria para tests de integración.

---

## 📌 Resumen Rápido

| Paso | Acción | Commit |
|------|--------|--------|
| 1 | Escribe test que falla | `test: ...` |
| 2 | Implementa código mínimo | `feat: ...` |
| 3 | Refactoriza sin romper tests | `refactor: ...` |
| 4 | Añade casos edge | `test: ...` (vuelve al paso 1) |

---

**Versión**: 2.0 (Generic TDD + Conventional Commits)  
**Última actualización**: 2026-01-28

