---
title: "HU-016: Agregar Nueva Tarjeta"
version: 1.0
date_created: 2026-01-28
last_updated: 2026-01-28
---

# HU-016: Agregar Nueva Tarjeta

## Epic: Gestión de Tarjetas de Pago

**As a** cliente de FinTech Bank,  
**I want to** registrar una nueva tarjeta de forma segura,  
**So that** pueda usarla para realizar transacciones y pagos.

---

## Acceptance Criteria (Gherkin)

### Scenario 1: Formulario se abre correctamente

```gherkin
Given el usuario está en "Mis Tarjetas"
  And tiene menos de 3 tarjetas registradas
When hace clic en "Agregar Tarjeta"
Then se abre un formulario con los campos:
  - Número de Tarjeta
  - Fecha de Vencimiento (MM/AA)
  - CVV (enmascarado mientras escribe)
  - Cédula/Documento de Identidad
  - Nombre del Titular
  - Tipo de Tarjeta (Débito o Crédito)
  - Apodo (opcional)
  And el botón "Guardar" está deshabilitado hasta completar todo
```

### Scenario 2: Usuario ingresa número válido

```gherkin
Given el formulario está abierto
When el usuario ingresa: 4532015112830366
Then el número se formatea automáticamente: 4532-0151-1283-0366
  And se detecta el tipo: VISA (mostrar ícono)
  And el campo se marca como válido (borde verde)
```

### Scenario 3: Usuario ingresa número inválido

```gherkin
Given el formulario está abierto
When el usuario ingresa: 1234567890123456
Then el campo se marca como inválido (borde rojo)
  And ve el mensaje: "Número de tarjeta inválido"
  And el botón "Guardar" permanece deshabilitado
```

### Scenario 4: Usuario ingresa fecha expirada

```gherkin
Given el formulario está abierto
  And la fecha de hoy es enero 2026
When el usuario ingresa: 12/24 (diciembre 2024)
Then ve el mensaje: "La tarjeta ha expirado"
  And el campo se marca como inválido
```

### Scenario 5: Usuario completa y guarda el formulario

```gherkin
Given el formulario está completamente lleno con datos válidos
When hace clic en "Guardar Tarjeta"
Then el botón muestra "Guardando..."
  And la tarjeta se crea y aparece en "Mis Tarjetas"
  And ve un mensaje de éxito: "Tarjeta agregada exitosamente"
  And el formulario se cierra
```

### Scenario 6: Usuario intenta registrar tarjeta duplicada

```gherkin
Given el usuario ya tiene una tarjeta terminada en 0366
When intenta registrar otra tarjeta con el mismo número
Then ve el mensaje: "Ya tienes esta tarjeta registrada"
  And el formulario permanece abierto
```

### Scenario 7: El apodo es opcional

```gherkin
Given el formulario está completo
When el usuario no completa el campo "Apodo"
  And hace clic en "Guardar"
Then la tarjeta se crea correctamente
  And aparece en la lista con un nombre por defecto: "Tarjeta Débito 0366"
```

---

## Implementation & TDD Notes

**Frontend:**
- Componente `AddCardForm.tsx` con validación en tiempo real
- Máscaras automáticas para número, vencimiento, CVV
- Detección automática de tipo (VISA, Mastercard, Amex) con iconos
- El CVV se muestra enmascarado mientras se escribe
- Validación visual: campo verde=válido, rojo=inválido

**Backend/Logic:**
- Endpoint: `POST /api/v1/cards`
- Validar número con algoritmo de Luhn
- Validar CVV: 3 dígitos (VISA/MC) o 4 (Amex)
- Validar fecha de vencimiento no sea pasada
- Encriptar número antes de almacenar
- Retornar solo últimos 4 dígitos, nunca el número completo
- Verificar máximo 3 tarjetas por usuario

**Security:**
- CVV nunca se almacena en BD
- CVV nunca se retorna en response
- CVV nunca se registra en logs
- Número de tarjeta encriptado (AES-256)
- Rate-limit: máx 5 intentos por minuto
- HTTPS obligatorio
- JWT token requerido

**Edge Cases:**
- Usuario intenta duplicado → Error claro
- Formato incorrecto → Validación en tiempo real
- Servidor rechaza → Mostrar error sin CVV
- Usuario cierra sin guardar → Descartar datos

---

## Business Value

**Priority**: CRITICAL

- Permite agregar múltiples tarjetas
- Proceso seguro que no almacena CVV
- Cumple regulaciones PCI DSS
- Mejora confianza del usuario

---

## Success Metrics

| KPI | Target |
|-----|--------|
| Tiempo completo | ≤2 segundos |
| Tasa de éxito | >95% primer intento |
| CVV en logs | 0 ocurrencias |
| Rate-limiting | ≤5 intentos/minuto |

---

**Story Points**: 5 | **Dependencies**: POST /api/v1/cards, Luhn validation
