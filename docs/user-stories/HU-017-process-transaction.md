---
title: "HU-017: Procesar Transacciones con Validación de Saldo"
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
---

# HU-017: Procesar Transacciones con Validación de Saldo

## Epic: Gestión de Tarjetas de Pago

**As a** cliente de FinTech Bank,  
**I want to** realizar transacciones usando mi tarjeta seleccionada,  
**So that** el sistema valide que tengo saldo suficiente antes de procesar.

---

## Acceptance Criteria (Gherkin)

### Scenario 1: Transacción aprobada con saldo suficiente

```gherkin
Given el usuario está en "Realizar Transferencia"
  And seleccionó la tarjeta "Mi Débito" con saldo $5,000
  And ingresó el monto: $1,500
When hace clic en "Confirmar"
Then el sistema valida el saldo
  And la transacción se aprueba
  And el saldo de la tarjeta se actualiza a $3,500
  And ve un mensaje: "✓ Transferencia completada por $1,500"
```

### Scenario 2: Transacción rechazada por saldo insuficiente

```gherkin
Given el usuario está en "Realizar Transferencia"
  And seleccionó la tarjeta "Mi Débito" con saldo $500
  And ingresó el monto: $750
When hace clic en "Confirmar"
Then el sistema detecta que no hay saldo suficiente
  And la transacción se rechaza
  And ve el mensaje: "Saldo insuficiente en la tarjeta"
  And ve detalle: "Tienes $500 pero necesitas $750"
  And el saldo no cambia
  And NO se carga dinero
```

### Scenario 3: Transacción rechazada por tarjeta bloqueada

```gherkin
Given el usuario seleccionó una tarjeta bloqueada
When intenta hacer una transacción
Then el sistema rechaza la transacción
  And ve el mensaje: "Tu tarjeta está bloqueada"
```

### Scenario 4: Transacción en revisión por fraude

```gherkin
Given el usuario intenta una transacción de monto muy alto
When el sistema detecta riesgo de fraude
Then la transacción se coloca en revisión
  And ve el mensaje: "Tu transacción está siendo revisada por seguridad"
  And el dinero NO se descuenta hasta que sea aprobada
```

### Scenario 5: Transacción de depósito suma al saldo

```gherkin
Given una transacción de tipo DEPÓSITO por $500
When se aprueba la transacción
Then el saldo de la tarjeta AUMENTA (no disminuye)
  And el saldo anterior $3,500 se convierte en $4,000
  And el mensaje muestra: "+ $500"
```

### Scenario 6: Usuario ve saldo actualizado sin recargar

```gherkin
Given se procesó una transacción exitosa
When el saldo se modifica
Then la pantalla se actualiza automáticamente
  And el nuevo saldo se muestra en menos de 1 segundo
```

### Scenario 7: Usuario selecciona entre múltiples tarjetas

```gherkin
Given el usuario tiene 2 tarjetas activas
When abre la pantalla de transferencia
Then ve un selector de tarjeta
  And puede cambiar de una a otra
  And el saldo disponible se actualiza dinámicamente
```

### Scenario 8: Error de conexión al validar

```gherkin
Given el usuario intenta procesar una transacción
  And el servidor no responde
When envía la solicitud
Then ve el mensaje: "No pudimos validar tu transacción"
  And se sugiere reintentar
  And el dinero NO se descuenta
```

---

## Implementation & TDD Notes

**Frontend:**
- Selector de tarjeta en formulario de transacción
- Mostrar saldo disponible de la tarjeta seleccionada
- Loading state mientras se procesa validación
- Mostrar errores específicos (saldo insuficiente vs bloqueada)
- Actualizar saldo sin recargar

**Backend/Logic:**
- Endpoint: `POST /api/v1/transaction/validate`
- Validar: usuario es propietario de la tarjeta
- Validar: tarjeta está ACTIVA
- Validar: saldo >= monto (si es egreso)
- Evaluar fraude (integración HU-001)
- Si APPROVED: descontar/sumar saldo
- Si HIGH_RISK: encolar para revisión manual
- Guardar registro de transacción
- Publicar evento BALANCE_UPDATED

**Security:**
- Validar JWT token
- Validar usuario sea dueño de la tarjeta
- Todas las operaciones en audit trail
- Rate-limit: máx 10 intentos/minuto
- Transacciones atómicas

**Edge Cases:**
- Servidor falla a mitad → Rollback completo
- 2 transacciones simultáneas → Procesar una a la vez
- Fraude bloquea → Encolar para humano

---

## Business Value

**Priority**: CRITICAL

- Validación de saldo previene rechazos sorpresa
- Integración con fraude aumenta seguridad
- Saldo actualizado automáticamente da confianza
- Protege usuario e institución

---

## Success Metrics

| KPI | Target |
|-----|--------|
| Tiempo validación | ≤2 segundos |
| Precisión | 100% |
| Audit trail | 100% transacciones |
| Tasa éxito | >99% |

---

**Story Points**: 5 | **Dependencies**: HU-001, HU-002, HU-015
