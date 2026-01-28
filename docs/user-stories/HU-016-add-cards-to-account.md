# HU-016: Add and Link Cards to Account

**As a** bank customer  
**I want** to add new debit/credit cards to my account  
**So that** I can manage multiple payment methods and track their transactions independently

## Acceptance Criteria

### Scenario: Add a new card successfully

```gherkin
Given I am an authenticated user on the Cards section
When I click "Add New Card" button
Then a card registration form should appear with:
  | Field              | Validation                              |
  | card_number        | 16 digits, required, Luhn algorithm     |
  | card_holder_name   | Alphabetic, required, 3-50 chars        |
  | expiry_date        | MM/YY format, future date required      |
  | cvv                | 3-4 digits, required (encrypted)        |
  | card_type          | Debit/Credit dropdown                   |
  | nickname           | Optional, 20 chars max                  |
And when I submit valid data
Then the system should:
  | Action                  | Behavior                              |
  | Validate card number    | Check Luhn + issuer (Visa/MC/Amex)    |
  | Create card record      | POST /api/v1/cards                    |
  | Link to user_id         | Associate card with current user      |
  | Set initial status      | "Active"                              |
  | Set initial balance     | $0.00 (or sync with issuer API)       |
And I should see: "Card added successfully"
And the new card appears in my cards list
```

### Scenario: Card validation failure

```gherkin
Given I enter an invalid card number "1234-5678-9012-3456"
When I submit the form
Then I should receive validation errors:
  | Field              | Error Message                           |
  | card_number        | "Invalid card number (Luhn check fail)" |
And the form should not submit
```

### Scenario: Duplicate card prevention

```gherkin
Given I already have a card with number ending in 1234
When I try to add the same card again
Then I should receive HTTP 409 Conflict
And see error: "This card is already linked to your account"
```

### Scenario: Max cards limit reached

```gherkin
Given I have 10 cards already linked (system limit)
When I try to add an 11th card
Then I should receive HTTP 429 Too Many Requests
And see: "Maximum of 10 cards per account. Remove a card to add new one."
```

### Scenario: Card removed successfully

```gherkin
Given I have a card I want to remove
When I click "Remove Card" on that card
Then a confirmation modal should appear:
  | Content                                      |
  | "Are you sure? This action cannot be undone" |
  | "Remove" button (danger style)               |
  | "Cancel" button                              |
And when I confirm
Then the system should:
  | Action                  | Behavior                    |
  | Soft-delete card        | DELETE /api/v1/cards/{id}   |
  | Archive transactions    | Keep history, mark inactive |
  | Update UI               | Remove card from list       |
And I should see: "Card removed successfully"
```

## Acceptance Criteria - Non-Functional

- **Security**: CVV encrypted in transit and storage, never logged
- **Performance**: Card validation < 500ms
- **Compliance**: PCI-DSS compliant (tokenize card data)
- **Audit**: All add/remove actions logged to audit trail (HU-002)

## Estimation

- **Story Points**: 13
- **Priority**: HIGH
- **Dependency**: HU-015 (card list view), PCI-DSS compliance setup
