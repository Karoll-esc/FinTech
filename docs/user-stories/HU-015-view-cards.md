---
title: "HU-015: Ver Múltiples Tarjetas con Saldo"
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
---

# HU-015: Ver Múltiples Tarjetas con Saldo

## Epic: Gestión de Tarjetas de Pago

**As a** cliente de FinTech Bank,  
**I want to** ver todas mis tarjetas registradas con su saldo actual y estado,  
**So that** pueda seleccionar rápidamente cuál tarjeta usar para cada transacción.

---

## Acceptance Criteria (Gherkin)

### Scenario 1: Usuario con múltiples tarjetas ve el listado

```gherkin
Given el usuario tiene 3 tarjetas registradas
  And cada tarjeta tiene un saldo disponible
When accede a la pantalla "Mis Tarjetas"
Then ve un listado con todas las tarjetas
  And cada tarjeta muestra los últimos 4 dígitos (ej: ****1234)
  And ve el saldo actual de cada tarjeta
  And ve el estado (Activa, Bloqueada, Suspendida)
  And ve un apodo personalizado si lo tiene (ej: "Mi Débito")
  And las tarjetas están ordenadas por más nueva primero
```

### Scenario 2: Usuario sin tarjetas ve un mensaje vacío

```gherkin
Given el usuario no tiene tarjetas registradas
When accede a la pantalla "Mis Tarjetas"
Then ve un mensaje: "No tienes tarjetas registradas"
  And ve una descripción: "Agrega tu primera tarjeta para realizar transferencias"
  And ve un botón prominente: "Agregar Primera Tarjeta"
```

### Scenario 3: Usuario alcanza el límite máximo de tarjetas

```gherkin
Given el usuario tiene exactamente 3 tarjetas registradas
When accede a la pantalla "Mis Tarjetas"
Then el botón "Agregar Tarjeta" no aparece
  And ve un mensaje: "Has alcanzado el máximo de 3 tarjetas"
  And se sugiere que elimine una tarjeta si desea agregar otra
```

### Scenario 4: Tarjeta con saldo cero se muestra diferente

```gherkin
Given una de las tarjetas del usuario tiene saldo $0.00
When ve la lista de tarjetas
Then el saldo se muestra en rojo
  And ve una etiqueta: "Sin fondos"
  And la tarjeta sigue siendo seleccionable para transacciones
```

### Scenario 5: La pantalla carga rápido

```gherkin
Given el usuario accede a "Mis Tarjetas"
When la pantalla comienza a cargar
Then toda la información se muestra en menos de 500 milisegundos
```

---

## Implementation & TDD Notes

**Frontend:**
- Componente `CardList.tsx` que muestra tarjetas en Cards/Grid
- Ícono diferente para Débito vs Crédito
- Colores visuales para estado (verde=activa, rojo=bloqueada)
- Responsive en móvil, tablet y desktop
- Último dígito de tarjeta enmascarado

**Backend/Logic:**
- Endpoint: `GET /api/v1/cards`
- Retorna lista de tarjetas del usuario autenticado
- Ordena por fecha de creación descendente
- NO incluye número de tarjeta completo
- Validar JWT token antes de retornar datos

**Security:**
- Solo el usuario ve sus propias tarjetas
- Números enmascarados excepto últimos 4 dígitos
- CVV nunca se muestra
- HTTPS obligatorio en producción

**Edge Cases:**
- ¿Servidor lento? → Mostrar loading state
- ¿Usuario sin tarjetas? → Mostrar mensaje vacío
- ¿Tarjeta no carga? → Mostrar error parcial

---

## Business Value

**Priority**: CRITICAL

- Permite gestionar múltiples formas de pago
- Saldos visibles previenen sorpresas en transacciones
- Mejor control sobre fondos del usuario

---

## Success Metrics

| KPI | Target |
|-----|--------|
| Tiempo de carga | ≤500 ms |
| Precisión de saldos | 100% |
| Test Coverage | >95% |

---

**Story Points**: 3 | **Dependencies**: GET /api/v1/cards
