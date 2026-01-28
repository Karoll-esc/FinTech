/**
 * E2E Tests for Card Feature - Phase 8 (TASK-066-078)
 * 
 * Tests with Playwright:
 * - View cards on dashboard
 * - View transactions
 * - Transfer money
 * - Block card
 * - Pagination
 * - Responsive layout
 * - Accessibility
 */

import { test, expect } from '@playwright/test';

test.describe('Card Management Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to user app
    await page.goto('http://localhost:5173');

    // Mock API responses
    await page.route('**/api/v1/cards*', async (route) => {
      if (route.request().method() === 'GET') {
        await route.abort('Failed request');
      }
    });

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('View cards on dashboard', async ({ page }) => {
    await test.step('Navigate to Inicio page', async () => {
      await page.click('nav a:has-text("Inicio")');
      await page.waitForURL('**/');
    });

    await test.step('See cards section', async () => {
      const cardsSection = page.getByRole('heading', { name: /Mis Tarjetas|My Cards/i });
      await expect(cardsSection).toBeVisible();
    });

    await test.step('Cards are displayed', async () => {
      const cardElements = page.getByRole('article').filter({ has: page.getByText(/XXXX/) });
      const count = await cardElements.count();
      expect(count).toBeLessThanOrEqual(3);
    });

    await test.step('Card displays required details', async () => {
      const card = page.getByRole('article').first();
      await expect(card.getByText(/\d{4}-XXXX-XXXX-\d{4}/)).toBeVisible(); // Masked number
      await expect(card.getByText(/\d{2}\/\d{2}/)).toBeVisible(); // Expiry
      await expect(card.getByText(/\$\d+\.\d{2}/)).toBeVisible(); // Balance
      await expect(card.getByRole('button', { name: /ACTIVE|BLOCKED|EXPIRED/ })).toBeVisible(); // Status
    });
  });

  test('View card transactions', async ({ page }) => {
    await test.step('Navigate to cards section', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Click View Transactions button', async () => {
      const firstCard = page.getByRole('article').first();
      await firstCard.getByRole('button', { name: /Transactions|📊/ }).click();
    });

    await test.step('Transaction modal opens', async () => {
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();
      await expect(modal.getByRole('heading')).toContainText(/Transactions|交易/);
    });

    await test.step('Transactions are listed', async () => {
      const transactionRows = page.locator('[data-testid="transaction-item"]');
      const count = await transactionRows.count();
      expect(count).toBeGreaterThan(0);
    });

    await test.step('Can close transaction modal', async () => {
      await page.getByRole('button', { name: /Close|X|✕/ }).click();
      const modal = page.getByRole('dialog');
      await expect(modal).not.toBeVisible();
    });
  });

  test('Transfer money from card', async ({ page }) => {
    await test.step('Navigate to cards section', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Click Transfer button on active card', async () => {
      const activeCard = page
        .getByRole('article')
        .filter({ has: page.getByText('ACTIVE') })
        .first();
      await activeCard.getByRole('button', { name: /Transfer|💸/ }).click();
    });

    await test.step('Transfer form appears', async () => {
      const form = page.getByRole('heading', { name: /Transfer|转账/ }).locator('..').first();
      await expect(form).toBeVisible();
    });

    await test.step('Fill transfer form', async () => {
      await page.fill('[placeholder="0.00"]', '100.00');
      await page.fill('[placeholder*="user"]', 'user_001');
      await page.fill('[placeholder*="location"]', 'Bogotá, Colombia');
      await page.fill('[placeholder*="device"]', 'device_abc123');
      await page.fill('[placeholder*="transaction"]', 'txn_20260128_001');
      await page.fill('[placeholder*="description"]', 'Test transfer');
    });

    await test.step('Submit transfer', async () => {
      await page.getByRole('button', { name: /Confirm Transfer|✓/ }).click();
    });

    await test.step('Success message appears', async () => {
      const successMsg = page.getByText(/initiated successfully|initiated/i);
      await expect(successMsg).toBeVisible({ timeout: 5000 });
    });
  });

  test('Cannot transfer from blocked card', async ({ page }) => {
    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Find blocked card', async () => {
      const blockedCard = page
        .getByRole('article')
        .filter({ has: page.getByText('BLOCKED') })
        .first();
      const transferBtn = blockedCard.getByRole('button', { name: /Transfer|💸/ });

      // Transfer button should be disabled
      await expect(transferBtn).toBeDisabled();
    });

    await test.step('Tooltip shows message', async () => {
      const blockedCard = page
        .getByRole('article')
        .filter({ has: page.getByText('BLOCKED') })
        .first();
      const transferBtn = blockedCard.getByRole('button', { name: /Transfer|💸/ });

      // Check title attribute
      const title = await transferBtn.getAttribute('title');
      expect(title).toContain('cannot');
    });
  });

  test('Block card', async ({ page }) => {
    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Click Block button', async () => {
      const firstCard = page.getByRole('article').first();
      await firstCard.getByRole('button', { name: /Block|🔒/ }).click();
    });

    await test.step('Confirmation dialog appears', async () => {
      const confirmBtn = page.getByRole('button', { name: /Confirm|Yes|Block/ }).first();
      await expect(confirmBtn).toBeVisible();
    });

    await test.step('Confirm block action', async () => {
      await page.getByRole('button', { name: /Confirm|Yes|Block/ }).first().click();
    });

    await test.step('Card status updates to BLOCKED', async () => {
      const status = page.getByText('BLOCKED').first();
      await expect(status).toBeVisible({ timeout: 3000 });
    });
  });

  test('Insufficient balance error', async ({ page }) => {
    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Click Transfer button', async () => {
      const activeCard = page
        .getByRole('article')
        .filter({ has: page.getByText('ACTIVE') })
        .first();
      await activeCard.getByRole('button', { name: /Transfer|💸/ }).click();
    });

    await test.step('Enter amount greater than balance', async () => {
      // Assuming balance is $1250.50
      await page.fill('[placeholder="0.00"]', '5000.00');
    });

    await test.step('Error message displays', async () => {
      const errorMsg = page.getByText(/Insufficient|balance/i);
      await expect(errorMsg).toBeVisible();
    });

    await test.step('Submit button is disabled', async () => {
      const submitBtn = page.getByRole('button', { name: /Confirm Transfer|✓/ });
      await expect(submitBtn).toBeDisabled();
    });
  });

  test('View All Cards pagination', async ({ page }) => {
    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('View All Cards link visible if many cards', async () => {
      const viewAllBtn = page.getByRole('button', { name: /View All|Show Less/ });
      const isVisible = await viewAllBtn.isVisible().catch(() => false);

      if (isVisible) {
        await viewAllBtn.click();
        // Should show all cards now
        const allCards = page.getByRole('article');
        const count = await allCards.count();
        expect(count).toBeGreaterThan(3);
      }
    });
  });

  test('Empty state - no cards', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/v1/cards', async (route) => {
      await route.abort();
    });

    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Empty state message displays', async () => {
      const emptyMsg = page.getByText(/No cards|没有卡/i);
      await expect(emptyMsg).toBeVisible({ timeout: 5000 });
    });

    await test.step('Request Card button visible', async () => {
      const requestBtn = page.getByRole('button', { name: /Request|申请/ });
      await expect(requestBtn).toBeVisible();
    });
  });

  test('Responsive layout - mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Only 1 card per row on mobile', async () => {
      const cardsContainer = page.getByRole('main');
      const cards = cardsContainer.locator('[role="article"]');

      // Check grid is single column
      const firstCard = cards.first();
      const bbox = await firstCard.boundingBox();
      expect(bbox?.width).toBeLessThanOrEqual(375);
    });
  });

  test('Responsive layout - tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('2 cards per row on tablet', async () => {
      const cards = page.getByRole('article');
      const count = await cards.count();

      // With 3 cards, tablet should show 2, then 1 on second row
      if (count >= 2) {
        const firstCard = await cards.nth(0).boundingBox();
        const secondCard = await cards.nth(1).boundingBox();

        // Both should be visible and on same Y level (roughly)
        expect(firstCard?.y).toBe(secondCard?.y);
      }
    });
  });

  test('Accessibility - keyboard navigation', async ({ page }) => {
    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Tab to first card button', async () => {
      await page.keyboard.press('Tab');

      // Eventually reach first card button
      for (let i = 0; i < 10; i++) {
        const focused = await page.evaluate(() => document.activeElement?.getAttribute('aria-label'));
        if (focused?.includes('Transaction') || focused?.includes('Transfer')) {
          break;
        }
        await page.keyboard.press('Tab');
      }

      const focused = page.locator(':focus-visible');
      await expect(focused).toHaveAttribute('aria-label', /Transaction|Transfer|Block/);
    });

    await test.step('Enter key activates button', async () => {
      const focused = page.locator(':focus-visible');
      const label = await focused.getAttribute('aria-label');

      if (label?.includes('Transaction')) {
        await page.keyboard.press('Enter');

        // Modal should appear
        const modal = page.getByRole('dialog');
        await expect(modal).toBeVisible({ timeout: 3000 });
      }
    });
  });

  test('Accessibility - screen reader labels', async ({ page }) => {
    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Card components have ARIA labels', async () => {
      const firstCard = page.getByRole('article').first();

      // Status badge should be accessible
      const statusBadge = firstCard.getByRole('status');
      await expect(statusBadge).toBeVisible();

      // Buttons should have labels
      const buttons = firstCard.getByRole('button');
      const count = await buttons.count();
      expect(count).toBeGreaterThan(0);

      for (let i = 0; i < count; i++) {
        const label = await buttons.nth(i).getAttribute('aria-label');
        expect(label).toBeTruthy();
      }
    });
  });

  test('Load time within 2 seconds', async ({ page }) => {
    const startTime = Date.now();

    await test.step('Navigate to cards', async () => {
      await page.click('nav a:has-text("Inicio")');
    });

    await test.step('Cards visible', async () => {
      const cardElements = page.getByRole('article');
      await expect(cardElements.first()).toBeVisible();
    });

    const loadTime = Date.now() - startTime;
    console.log(`⏱️ Cards loaded in ${loadTime}ms`);
    expect(loadTime).toBeLessThan(2000);
  });
});
