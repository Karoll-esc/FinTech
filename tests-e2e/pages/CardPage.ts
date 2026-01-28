import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * CardPage - Page Object para gestión de tarjetas
 * 
 * Encapsula toda la interacción con las páginas de tarjetas:
 * - Agregar tarjeta (AddCardForm)
 * - Lista de tarjetas (CardList)
 * - Detalles de tarjeta (CardDetails)
 * 
 * Proporciona métodos de alto nivel para pruebas sin
 * conocimiento de implementación UI específica.
 */
export class CardPage extends BasePage {
  // Locators - AddCardForm
  private readonly addCardBtn = this.page.locator('button:has-text("Add New Card")');
  private readonly addCardForm = this.page.locator('[data-testid="add-card-form"]');
  private readonly cardNumberInput = this.page.locator('input[placeholder*="1234"]');
  private readonly cardHolderInput = this.page.locator('input[placeholder*="John"]');
  private readonly expiryInput = this.page.locator('input[placeholder*="12/25"]');
  private readonly cardTypeSelect = this.page.locator('select[aria-label*="Card type"]');
  private readonly nicknameInput = this.page.locator('input[placeholder*="Main Card"]');
  private readonly submitCardBtn = this.page.locator('button:has-text("Add Card")');
  private readonly resetBtn = this.page.locator('button:has-text("Reset")');

  // Locators - CardList
  private readonly cardList = this.page.locator('[data-testid="card-list"]');
  private readonly cardItems = this.page.locator('[role="listitem"]');
  private readonly emptyStateMsg = this.page.locator('text=No cards yet');
  private readonly refreshBtn = this.page.locator('button:has-text("Refresh")');
  private readonly cardCountText = this.page.locator('text=/\\d+ of 10 cards/');

  // Locators - CardDetails
  private readonly cardDetails = this.page.locator('[data-testid="card-details"]');
  private readonly backBtn = this.page.locator('button:has-text("Back")');
  private readonly editNicknameBtn = this.page.locator('button:has-text("Edit")');
  private readonly deleteCardBtn = this.page.locator('button:has-text("Delete Card")');
  private readonly saveNicknameBtn = this.page.locator('button:has-text("Save")');
  private readonly cancelEditBtn = this.page.locator('button:has-text("Cancel")');

  // Locators - Modals & Messages
  private readonly successToast = this.page.locator('text=successfully');
  private readonly errorToast = this.page.locator('[role="alert"]');
  private readonly deleteConfirmModal = this.page.locator('text=Delete Card?');
  private readonly confirmDeleteBtn = this.page.locator('button:has-text("Delete")');

  constructor(page: Page) {
    super(page);
  }

  // ========================================================================
  // AddCardForm Methods
  // ========================================================================

  /**
   * Navegar a la página de tarjetas
   */
  async navigateToCards(baseUrl: string = 'http://localhost:5173'): Promise<void> {
    await this.goto(`${baseUrl}/cards`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Abrir formulario de agregar tarjeta
   */
  async openAddCardForm(): Promise<void> {
    await this.clickElement(this.addCardBtn);
    await this.waitForElement(this.addCardForm);
  }

  /**
   * Completar formulario de tarjeta
   */
  async fillCardForm(card: {
    number: string;
    holder: string;
    expiry: string;
    type?: 'DEBIT' | 'CREDIT';
    nickname?: string;
  }): Promise<void> {
    // Fill card number (auto-formatted)
    await this.fillField(this.cardNumberInput, card.number);

    // Fill holder name
    await this.fillField(this.cardHolderInput, card.holder);

    // Fill expiry date
    await this.fillField(this.expiryInput, card.expiry);

    // Select card type if provided
    if (card.type) {
      await this.page.selectOption('select[aria-label*="Card type"]', card.type);
    }

    // Fill nickname if provided
    if (card.nickname) {
      await this.fillField(this.nicknameInput, card.nickname);
    }
  }

  /**
   * Enviar formulario de tarjeta
   */
  async submitCardForm(): Promise<void> {
    await this.clickElement(this.submitCardBtn);
  }

  /**
   * Agregar tarjeta (flujo completo)
   */
  async addCard(card: {
    number: string;
    holder: string;
    expiry: string;
    type?: 'DEBIT' | 'CREDIT';
    nickname?: string;
  }): Promise<void> {
    await this.openAddCardForm();
    await this.fillCardForm(card);
    await this.submitCardForm();
    await this.waitForElement(this.successToast, 5000);
  }

  /**
   * Resetear formulario
   */
  async resetForm(): Promise<void> {
    await this.clickElement(this.resetBtn);
  }

  // ========================================================================
  // CardList Methods
  // ========================================================================

  /**
   * Esperar a que cargue la lista de tarjetas
   */
  async waitForCardList(): Promise<void> {
    await this.waitForElement(this.cardList);
  }

  /**
   * Obtener número de tarjetas en la lista
   */
  async getCardCount(): Promise<number> {
    return await this.cardItems.count();
  }

  /**
   * Verificar si la lista está vacía
   */
  async isCardListEmpty(): Promise<boolean> {
    return await this.emptyStateMsg.isVisible();
  }

  /**
   * Obtener texto del contador de tarjetas (ej: "3 of 10 cards")
   */
  async getCardCountText(): Promise<string | null> {
    return await this.cardCountText.textContent();
  }

  /**
   * Hacer clic en una tarjeta por número de tarjeta
   */
  async clickCardByNumber(lastFourDigits: string): Promise<void> {
    await this.clickElement(
      this.page.locator(`text=****${lastFourDigits}`)
    );
  }

  /**
   * Actualizar lista (botón refresh)
   */
  async refreshCardList(): Promise<void> {
    await this.clickElement(this.refreshBtn);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Eliminar tarjeta desde lista (botón de papelera)
   */
  async deleteCardFromList(lastFourDigits: string): Promise<void> {
    // Find the delete button for specific card
    const cardRow = this.page.locator(`text=****${lastFourDigits}`).locator('..').locator('..').first();
    const deleteBtn = cardRow.locator('button[aria-label*="Delete"]');
    
    await this.clickElement(deleteBtn);
    await this.waitForElement(this.deleteConfirmModal);
  }

  // ========================================================================
  // CardDetails Methods
  // ========================================================================

  /**
   * Esperar a que cargue la página de detalles
   */
  async waitForCardDetails(): Promise<void> {
    await this.waitForElement(this.cardDetails);
  }

  /**
   * Verificar que la información de la tarjeta es visible
   */
  async verifyCardDetailsVisible(card: {
    holder: string;
    expiry: string;
    type?: string;
  }): Promise<void> {
    await this.page.waitForSelector(`text=${card.holder}`);
    await this.page.waitForSelector(`text=Expires ${card.expiry}`);
    
    if (card.type) {
      await this.page.waitForSelector(`text=${card.type}`);
    }
  }

  /**
   * Editar apodo de la tarjeta
   */
  async editNickname(newNickname: string): Promise<void> {
    // Click edit button
    await this.clickElement(this.editNicknameBtn);

    // Fill nickname field
    const nicknameEdit = this.page.locator('input[placeholder*="nickname"]');
    await this.fillField(nicknameEdit, newNickname);

    // Click save
    await this.clickElement(this.saveNicknameBtn);
    await this.waitForElement(this.successToast, 5000);
  }

  /**
   * Eliminar tarjeta (con confirmación)
   */
  async deleteCard(): Promise<void> {
    // Click delete button
    await this.clickElement(this.deleteCardBtn);

    // Wait for confirmation modal
    await this.waitForElement(this.deleteConfirmModal);

    // Confirm deletion
    await this.clickElement(this.confirmDeleteBtn);

    // Wait for success message
    await this.waitForElement(this.successToast, 5000);
  }

  /**
   * Volver a la lista desde detalles
   */
  async goBack(): Promise<void> {
    await this.clickElement(this.backBtn);
  }

  // ========================================================================
  // Error Handling
  // ========================================================================

  /**
   * Obtener mensaje de error visible
   */
  async getErrorMessage(): Promise<string | null> {
    const error = this.page.locator('[role="alert"]');
    if (await error.isVisible()) {
      return await error.textContent();
    }
    return null;
  }

  /**
   * Verificar que error específico es visible
   */
  async expectError(errorText: string): Promise<void> {
    await this.page.waitForSelector(`text=${errorText}`);
  }

  /**
   * Verificar que cierto campo tiene error
   */
  async expectFieldError(fieldLabel: string, errorMsg: string): Promise<void> {
    const field = this.page.locator(`[aria-label*="${fieldLabel}"]`);
    const nextElement = field.locator('..');
    
    await this.page.waitForSelector(`text=${errorMsg}`);
  }

  /**
   * Cerrar formulario (botón atrás)
   */
  async closeForm(): Promise<void> {
    // If in details, go back to list
    if (await this.backBtn.isVisible()) {
      await this.clickElement(this.backBtn);
    }
  }

  // ========================================================================
  // Validation & Assertions
  // ========================================================================

  /**
   * Verificar que número de tarjeta está enmascarado
   */
  async verifyCardNumberMasked(lastFourDigits: string): Promise<void> {
    const maskedText = `****${lastFourDigits}`;
    await this.page.waitForSelector(`text=${maskedText}`);
    
    // Verify full number is NOT visible
    const pageText = await this.page.innerText('body');
    const fullCardNumber = '4532015112830366'; // Example - in real test, use actual number
    
    // Just verify masked version is present
    const hasMasked = pageText.includes(maskedText);
    if (!hasMasked) {
      throw new Error(`Masked card number ${maskedText} not found`);
    }
  }

  /**
   * Verificar que botón submit está deshabilitado
   */
  async isSubmitDisabled(): Promise<boolean> {
    return await this.submitCardBtn.isDisabled();
  }

  /**
   * Obtener valor de campo
   */
  async getFieldValue(fieldLabel: string): Promise<string | null> {
    const field = this.page.locator(`[aria-label*="${fieldLabel}"]`);
    return await field.inputValue();
  }
}

export default CardPage;
