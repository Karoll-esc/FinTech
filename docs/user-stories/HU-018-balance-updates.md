---
title: "HU-018: Actualización Automática de Saldo"
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
---

# HU-018: Actualización Automática de Saldo

## Epic: Gestión de Tarjetas de Pago

**As a** cliente de FinTech Bank,  
**I want to** que mi saldo se actualice automáticamente sin recargar,  
**So that** siempre veo información actualizada y confiable.

---

## Acceptance Criteria (Gherkin)

### Scenario 1: Saldo se actualiza después de transacción aprobada

```gherkin
Given el usuario está en "Mis Tarjetas"
  And ve el saldo: "Mi Débito: $5,000"
When realiza una transacción exitosa de $1,500
Then el saldo se actualiza automáticamente a $3,500
  And la actualización ocurre en menos de 1 segundo
  And NO necesita recargar la página
```

### Scenario 2: Saldo se actualiza al regresar a la pantalla

```gherkin
Given el usuario realizó una transacción
When navega a otra pantalla
  And luego regresa a "Mis Tarjetas"
Then el saldo se sincroniza automáticamente
  And muestra el saldo correcto actualizado
```

### Scenario 3: Múltiples pestañas se sincronizan

```gherkin
Given el usuario tiene "Mis Tarjetas" abierto en 2 pestañas
When realiza una transacción en la pestaña 2
Then la pestaña 1 detecta el cambio automáticamente
  And el saldo se actualiza en ambas pestañas
  And sin necesidad de cambiar de pestaña
```

### Scenario 4: Saldo no cambia si transacción se rechaza

```gherkin
Given una transacción es rechazada
When el sistema muestra el error
Then el saldo no cambia
  And la UI no se actualiza
  And solo se muestra el mensaje de error
```

### Scenario 5: Saldo pendiente hasta aprobación de fraude

```gherkin
Given una transacción requiere revisión manual por seguridad
When se marca como PENDING_REVIEW
Then el saldo NO se descuenta inmediatamente
  And se muestra: "Tu transacción está siendo revisada"
  And cuando sea aprobada por un humano, se descuenta y actualiza
```

---

## Implementation & TDD Notes

**Frontend:**
- Hook `useCardBalance()` para polling/WebSocket automático
- Actualizar solo el valor del saldo (no recargar toda)
- Animación suave cuando saldo cambia
- Sincronización entre pestañas usando localStorage
- Reintentar fetch si falla (hasta 3 veces)

**Backend/Logic:**
- Evento `BALANCE_UPDATED` publicado tras aprobar transacción
- Endpoint `GET /api/v1/cards` retorna saldos actuales
- Endpoint `WS /ws/cards` para WebSocket (opcional)
- Transacciones atómicas: saldo nunca inconsistente

**Strategy 1: Polling (Simple)**
- Cada 30 segundos, fetch en background
- Si saldo cambió, actualizar UI
- Sin spinner: es silencioso

**Strategy 2: WebSocket (Ideal)**
- Conexión continua con servidor
- Servidor envía evento cuando saldo cambia
- Latencia <100ms vs 30 segundos
- Fallback a polling si falla

**Edge Cases:**
- Usuario offline → Usar último saldo, sincronizar al volver online
- 2 transacciones simultáneas → Saldo final correcto
- Actualización no llega → Reintentar, mostrar warning

---

## Business Value

**Priority**: HIGH

- Mejor experiencia: cambios en tiempo real
- Confianza: información siempre actualizada
- Reduce confusión: saldo correcto sin recargas
- Diferencia vs competencia

---

## Success Metrics

| KPI | Target |
|-----|--------|
| Latencia | ≤1 segundo |
| Precisión | 100% |
| Disponibilidad | 99.9% |
| Tasa error | <0.1% |

---

**Story Points**: 3 | **Dependencies**: HU-015, HU-017
