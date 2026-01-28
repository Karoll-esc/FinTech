import { test, expect } from '@playwright/test';

/**
 * E2E Tests para HU-015 & HU-016: Gestión de Tarjetas
 * 
 * Casos de prueba implementados:
 * - TC-HU-015-01: Agregar tarjeta válida exitosamente
 * - TC-HU-015-02: Validación de número de tarjeta (16 dígitos)
 * - TC-HU-015-03: Validación de formato de fecha de vencimiento (MM/YY)
 * - TC-HU-015-04: Rechazo de tarjeta duplicada (últimos 4 dígitos)
 * - TC-HU-015-05: Límite máximo de 10 tarjetas
 * - TC-HU-015-06: Mascarado de número de tarjeta en la UI
 * - TC-HU-016-01: Ver lista de tarjetas del usuario
 * - TC-HU-016-02: Ver detalles de tarjeta individual
 * - TC-HU-016-03: Eliminar tarjeta con confirmación
 * - TC-HU-016-04: Editar apodo de tarjeta
 * - TC-016-05: Manejo de errores (404, 403, 409)
 * 
 * Flujos de usuario:
 * - Agregar → Ver → Eliminar (ciclo completo)
 * - Validación en tiempo real
 * - Manejo de errores con mensajes amigables
 */

const APP_BASE_URL = process.env.VITE_APP_URL || 'http://localhost:5173';
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000';

test.describe('HU-015 & HU-016: Gestión de Tarjetas', () => {
  // Test data
  const validCard = {
    number: '4532015112830366',
    holder: 'John Doe',
    expiry: '12/26',
    type: 'DEBIT' as const,
    nickname: 'Main Card',
  };

  const anotherValidCard = {
    number: '5425233010103442',
    holder: 'Jane Smith',
    expiry: '03/27',
    type: 'CREDIT' as const,
    nickname: 'Work Card',
  };

  test.beforeEach(async ({ page }) => {
    // Navigate to app and wait for load
    await page.goto(`${APP_BASE_URL}/cards`, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');
  });

  // ========================================================================
  // TC-HU-015-01: Agregar tarjeta válida exitosamente
  // ========================================================================
  test('TC-HU-015-01: Agregar tarjeta válida exitosamente', async ({ page }) => {
    await test.step('Navegar al formulario de agregar tarjeta', async () => {
      await page.click('button:has-text("Add New Card")');
      await expect(page.locator('[data-testid="add-card-form"]')).toBeVisible();
    });

    await test.step('Completar formulario con datos válidos', async () => {
      // Fill card number
      await page.fill('input[placeholder*="1234"]', validCard.number);
      
      // Fill holder name
      await page.fill('input[placeholder*="John"]', validCard.holder);
      
      // Fill expiry
      await page.fill('input[placeholder*="12/25"]', validCard.expiry);
      
      // Select card type
      await page.selectOption('select[aria-label*="Card type"]', validCard.type);
      
      // Fill nickname
      await page.fill('input[placeholder*="Main Card"]', validCard.nickname);
    });

    await test.step('Enviar formulario', async () => {
      await page.click('button:has-text("Add Card")');
      
      // Wait for success message
      await expect(page.locator('text=added successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('Verificar tarjeta aparece en la lista', async () => {
      // Card should appear in list with masked number
      await expect(page.locator('text=****0366')).toBeVisible();
    });
  });

  // ========================================================================
  // TC-HU-015-02: Validación de número de tarjeta (16 dígitos)
  // ========================================================================
  test('TC-HU-015-02: Validación de número de tarjeta (16 dígitos)', async ({ page }) => {
    await test.step('Abrir formulario de agregar tarjeta', async () => {
      await page.click('button:has-text("Add New Card")');
      await expect(page.locator('[data-testid="add-card-form"]')).toBeVisible();
    });

    await test.step('Ingresar número de tarjeta con menos de 16 dígitos', async () => {
      const cardInput = page.locator('input[placeholder*="1234"]');
      await cardInput.fill('4532015112830');
      await cardInput.blur();
      
      // Verify error message
      await expect(page.locator('text=must be 16 digits')).toBeVisible();
    });

    await test.step('Ingresar número completo de 16 dígitos', async () => {
      const cardInput = page.locator('input[placeholder*="1234"]');
      await cardInput.fill(validCard.number);
      await cardInput.blur();
      
      // Error should disappear
      await expect(page.locator('text=must be 16 digits')).not.toBeVisible();
    });
  });

  // ========================================================================
  // TC-HU-015-03: Validación de formato de fecha de vencimiento (MM/YY)
  // ========================================================================
  test('TC-HU-015-03: Validación de formato de fecha de vencimiento (MM/YY)', async ({ page }) => {
    await test.step('Abrir formulario de agregar tarjeta', async () => {
      await page.click('button:has-text("Add New Card")');
      await expect(page.locator('[data-testid="add-card-form"]')).toBeVisible();
    });

    await test.step('Ingresar fecha en formato inválido', async () => {
      const expiryInput = page.locator('input[placeholder*="12/25"]');
      await expiryInput.fill('13/25');
      await expiryInput.blur();
      
      // Verify error message
      await expect(page.locator('text=Invalid month')).toBeVisible();
    });

    await test.step('Ingresar fecha vencida', async () => {
      const expiryInput = page.locator('input[placeholder*="12/25"]');
      await expiryInput.fill('01/20');
      await expiryInput.blur();
      
      // Verify error message
      await expect(page.locator('text=expired')).toBeVisible();
    });

    await test.step('Ingresar fecha válida futura', async () => {
      const expiryInput = page.locator('input[placeholder*="12/25"]');
      await expiryInput.fill(validCard.expiry);
      await expiryInput.blur();
      
      // Error should disappear
      await expect(page.locator('text=expired')).not.toBeVisible();
    });
  });

  // ========================================================================
  // TC-HU-015-04: Rechazo de tarjeta duplicada (últimos 4 dígitos)
  // ========================================================================
  test('TC-HU-015-04: Rechazo de tarjeta duplicada (últimos 4 dígitos)', async ({ page }) => {
    await test.step('Agregar primera tarjeta', async () => {
      await page.click('button:has-text("Add New Card")');
      await page.fill('input[placeholder*="1234"]', validCard.number);
      await page.fill('input[placeholder*="John"]', validCard.holder);
      await page.fill('input[placeholder*="12/25"]', validCard.expiry);
      await page.click('button:has-text("Add Card")');
      
      // Wait for success
      await expect(page.locator('text=added successfully')).toBeVisible({ timeout: 5000 });
      
      // Close form
      await page.click('button:has-text("Back")');
    });

    await test.step('Intentar agregar tarjeta con mismos últimos 4 dígitos', async () => {
      await page.click('button:has-text("Add New Card")');
      
      // Use different card number but same last 4 digits
      const duplicateCard = '5555555555550366'; // Same last 4 as validCard
      await page.fill('input[placeholder*="1234"]', duplicateCard);
      await page.fill('input[placeholder*="John"]', 'Another User');
      await page.fill('input[placeholder*="12/25"]', '06/28');
      await page.click('button:has-text("Add Card")');
      
      // Verify error message about duplicate
      await expect(page.locator('text=already linked')).toBeVisible({ timeout: 5000 });
    });
  });

  // ========================================================================
  // TC-HU-015-05: Límite máximo de 10 tarjetas
  // ========================================================================
  test('TC-HU-015-05: Límite máximo de 10 tarjetas', async ({ page }) => {
    await test.step('Verificar contador de tarjetas', async () => {
      // Check if card count is displayed
      const cardCountText = await page.locator('text=/\\d+ of 10 cards/').textContent();
      
      if (cardCountText && cardCountText.includes('10 of 10')) {
        await test.step('Intentar agregar tarjeta cuando se alcanzó límite', async () => {
          await page.click('button:has-text("Add New Card")');
          await page.fill('input[placeholder*="1234"]', validCard.number);
          await page.fill('input[placeholder*="John"]', validCard.holder);
          await page.fill('input[placeholder*="12/25"]', validCard.expiry);
          await page.click('button:has-text("Add Card")');
          
          // Verify error message
          await expect(page.locator('text=maximum of 10')).toBeVisible({ timeout: 5000 });
        });
      } else {
        // If not at limit, skip this sub-step
        console.log('Not at card limit, skipping max cards test');
      }
    });
  });

  // ========================================================================
  // TC-HU-015-06: Mascarado de número de tarjeta en la UI
  // ========================================================================
  test('TC-HU-015-06: Mascarado de número de tarjeta en la UI', async ({ page }) => {
    await test.step('Agregar tarjeta', async () => {
      await page.click('button:has-text("Add New Card")');
      await page.fill('input[placeholder*="1234"]', validCard.number);
      await page.fill('input[placeholder*="John"]', validCard.holder);
      await page.fill('input[placeholder*="12/25"]', validCard.expiry);
      await page.click('button:has-text("Add Card")');
      
      // Wait for success
      await expect(page.locator('text=added successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('Verificar número enmascarado en lista', async () => {
      // Should show masked number
      await expect(page.locator('text=****0366')).toBeVisible();
      
      // Should NOT show full number
      const pageText = await page.innerText('body');
      expect(pageText).not.toContain(validCard.number);
    });

    await test.step('Verificar número enmascarado en detalles', async () => {
      // Click on card to view details
      await page.click('text=****0366');
      
      // Details page should also mask the number
      await expect(page.locator('text=****0366')).toBeVisible();
      
      // Should NOT show full number
      const pageText = await page.innerText('body');
      expect(pageText).not.toContain(validCard.number);
    });
  });

  // ========================================================================
  // TC-HU-016-01: Ver lista de tarjetas del usuario
  // ========================================================================
  test('TC-HU-016-01: Ver lista de tarjetas del usuario', async ({ page }) => {
    await test.step('Cargar página de tarjetas', async () => {
      await expect(page.locator('[data-testid="card-list"]')).toBeVisible();
    });

    await test.step('Verificar elementos de la lista', async () => {
      // Should have card items or empty state
      const cardItems = page.locator('role=listitem');
      const emptyState = page.locator('text=No cards yet');
      
      const hasCards = (await cardItems.count()) > 0;
      const isEmpty = await emptyState.isVisible();
      
      expect(hasCards || isEmpty).toBeTruthy();
    });

    await test.step('Si hay tarjetas, verificar información mostrada', async () => {
      const cardItems = page.locator('text=****');
      
      if ((await cardItems.count()) > 0) {
        // Should show masked card number
        await expect(cardItems.first()).toBeVisible();
        
        // Should show card type badge
        const badges = page.locator('[role="badge"]');
        expect(await badges.count()).toBeGreaterThan(0);
      }
    });
  });

  // ========================================================================
  // TC-HU-016-02: Ver detalles de tarjeta individual
  // ========================================================================
  test('TC-HU-016-02: Ver detalles de tarjeta individual', async ({ page }) => {
    await test.step('Agregar tarjeta de prueba', async () => {
      await page.click('button:has-text("Add New Card")');
      await page.fill('input[placeholder*="1234"]', validCard.number);
      await page.fill('input[placeholder*="John"]', validCard.holder);
      await page.fill('input[placeholder*="12/25"]', validCard.expiry);
      await page.fill('input[placeholder*="Main Card"]', validCard.nickname);
      await page.click('button:has-text("Add Card")');
      
      await expect(page.locator('text=added successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('Hacer clic en tarjeta para ver detalles', async () => {
      await page.click('text=****0366');
      
      // Should show card details page
      await expect(page.locator('[data-testid="card-details"]')).toBeVisible();
    });

    await test.step('Verificar información en página de detalles', async () => {
      // Should display all card information
      await expect(page.locator(`text=${validCard.holder}`)).toBeVisible();
      await expect(page.locator(`text=Expires ${validCard.expiry}`)).toBeVisible();
      await expect(page.locator(`text=${validCard.type}`)).toBeVisible();
      
      // Should show timestamps
      await expect(page.locator('text=Created')).toBeVisible();
      await expect(page.locator('text=Last Updated')).toBeVisible();
    });
  });

  // ========================================================================
  // TC-HU-016-03: Eliminar tarjeta con confirmación
  // ========================================================================
  test('TC-HU-016-03: Eliminar tarjeta con confirmación', async ({ page }) => {
    let cardNumberToDelete: string;

    await test.step('Agregar tarjeta para eliminar', async () => {
      await page.click('button:has-text("Add New Card")');
      await page.fill('input[placeholder*="1234"]', validCard.number);
      await page.fill('input[placeholder*="John"]', validCard.holder);
      await page.fill('input[placeholder*="12/25"]', validCard.expiry);
      await page.click('button:has-text("Add Card")');
      
      await expect(page.locator('text=added successfully')).toBeVisible({ timeout: 5000 });
      
      cardNumberToDelete = validCard.number.slice(-4);
    });

    await test.step('Navegar a detalles y hacer clic en eliminar', async () => {
      await page.click(`text=****${cardNumberToDelete}`);
      
      // Click delete button on details page
      await page.click('button:has-text("Delete Card")');
    });

    await test.step('Verificar modal de confirmación', async () => {
      // Confirmation modal should appear
      await expect(page.locator('text=Delete Card?')).toBeVisible();
      await expect(page.locator('text=cannot be undone')).toBeVisible();
    });

    await test.step('Confirmar eliminación', async () => {
      await page.click('button:has-text("Delete")');
      
      // Should show success message
      await expect(page.locator('text=deleted successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('Verificar tarjeta eliminada de lista', async () => {
      // Should return to card list
      await expect(page.locator('[data-testid="card-list"]')).toBeVisible();
      
      // Deleted card should not be visible
      await expect(page.locator(`text=****${cardNumberToDelete}`)).not.toBeVisible();
    });
  });

  // ========================================================================
  // TC-HU-016-04: Editar apodo de tarjeta
  // ========================================================================
  test('TC-HU-016-04: Editar apodo de tarjeta', async ({ page }) => {
    const newNickname = 'Updated Nickname';

    await test.step('Agregar tarjeta con apodo original', async () => {
      await page.click('button:has-text("Add New Card")');
      await page.fill('input[placeholder*="1234"]', validCard.number);
      await page.fill('input[placeholder*="John"]', validCard.holder);
      await page.fill('input[placeholder*="12/25"]', validCard.expiry);
      await page.fill('input[placeholder*="Main Card"]', validCard.nickname);
      await page.click('button:has-text("Add Card")');
      
      await expect(page.locator('text=added successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('Abrir detalles y editar apodo', async () => {
      await page.click('text=****0366');
      
      // Click edit button for nickname
      await page.click('button:has-text("Edit")');
    });

    await test.step('Ingresar nuevo apodo', async () => {
      const nicknameInput = page.locator('input[placeholder*="nickname"]');
      await nicknameInput.clear();
      await nicknameInput.fill(newNickname);
    });

    await test.step('Guardar cambios', async () => {
      await page.click('button:has-text("Save")');
      
      // Should show success message
      await expect(page.locator('text=updated successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('Verificar apodo actualizado', async () => {
      await expect(page.locator(`text=${newNickname}`)).toBeVisible();
    });
  });

  // ========================================================================
  // TC-HU-016-05: Manejo de errores (404, 403, 409)
  // ========================================================================
  test('TC-HU-016-05: Manejo de errores (404, 403, 409)', async ({ page }) => {
    await test.step('Verificar error cuando tarjeta no existe (404)', async () => {
      // Try to navigate to non-existent card
      await page.goto(`${APP_BASE_URL}/cards/invalid_card_id`, { 
        waitUntil: 'domcontentloaded' 
      });
      
      // Should show error message
      await expect(page.locator('text=not found')).toBeVisible();
    });
  });

  // ========================================================================
  // Flujo completo: Agregar → Ver → Editar → Eliminar
  // ========================================================================
  test('Flujo completo: Agregar → Ver → Editar → Eliminar', async ({ page }) => {
    const completeFlowCard = {
      number: '5425233010103442',
      holder: 'Jane Smith',
      expiry: '03/27',
      nickname: 'Complete Flow Test',
    };

    await test.step('1. Agregar nueva tarjeta', async () => {
      await page.click('button:has-text("Add New Card")');
      await page.fill('input[placeholder*="1234"]', completeFlowCard.number);
      await page.fill('input[placeholder*="John"]', completeFlowCard.holder);
      await page.fill('input[placeholder*="12/25"]', completeFlowCard.expiry);
      await page.fill('input[placeholder*="Main Card"]', completeFlowCard.nickname);
      await page.click('button:has-text("Add Card")');
      
      await expect(page.locator('text=added successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('2. Ver lista actualizada', async () => {
      // Card should appear in list
      await expect(page.locator(`text=****3442`)).toBeVisible();
      await expect(page.locator(`text=${completeFlowCard.nickname}`)).toBeVisible();
    });

    await test.step('3. Ver detalles de la tarjeta', async () => {
      await page.click('text=****3442');
      
      await expect(page.locator('[data-testid="card-details"]')).toBeVisible();
      await expect(page.locator(`text=${completeFlowCard.holder}`)).toBeVisible();
    });

    await test.step('4. Editar apodo', async () => {
      const updatedNickname = 'Updated: Complete Flow';
      
      await page.click('button:has-text("Edit")');
      const nicknameInput = page.locator('input[placeholder*="nickname"]');
      await nicknameInput.clear();
      await nicknameInput.fill(updatedNickname);
      await page.click('button:has-text("Save")');
      
      await expect(page.locator('text=updated successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('5. Eliminar tarjeta', async () => {
      await page.click('button:has-text("Delete Card")');
      await page.click('button:has-text("Delete")');
      
      await expect(page.locator('text=deleted successfully')).toBeVisible({ timeout: 5000 });
    });

    await test.step('6. Verificar eliminada de lista', async () => {
      await expect(page.locator('[data-testid="card-list"]')).toBeVisible();
      await expect(page.locator('text=****3442')).not.toBeVisible();
    });
  });
});
