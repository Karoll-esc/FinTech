# HU-015: View and Manage Multiple Cards

**As a** bank customer  
**I want** to view up to 3 of my cards with their details and perform actions on them  
**So that** I can manage my finances and cards effectively from a single dashboard

## Acceptance Criteria

### Scenario: View all active cards with details

```gherkin
Given I am an authenticated user logged into the user app
When I navigate to the Inicio page
Then I should see up to 3 of my cards displayed
And each card should display:
  | Field              | Format/Example           |
  | card_number        | XXXX-XXXX-XXXX-1234      |
  | card_holder_name   | Juan Pérez               |
  | current_balance    | $1,250.50 COP            |
  | expiry_date        | MM/YY                    |
  | card_status        | Active/Blocked           |
  | card_type          | Debit/Credit             |
And each card should have action buttons for:
  | Action             | Description              |
  | View Transactions  | See card movements       |
  | Transfer Money     | Send funds               |
  | Block Card         | Temporarily disable card |
  | Card Details       | Full card information    |
```

### Scenario: Card blocked status indicator

```gherkin
Given I have a card that is blocked
When I view my cards
Then the blocked card should display:
  | Indicator         | Behavior                        |
  | Status Badge      | "BLOCKED" in red background     |
  | Action Buttons    | "Unblock Card" button available |
  | Transfer Button   | Disabled/grayed out             |
  | Visual Treatment  | Dimmed appearance or striped    |
```

### Scenario: View card transactions

```gherkin
Given I am viewing my cards
When I click "View Transactions" on a specific card
Then a modal or page should open displaying:
  | Field            | Content                  |
  | transaction_date | 2026-01-28 14:30:00     |
  | description      | Supermarket Purchase     |
  | amount           | -$45.99 COP              |
  | merchant         | Carrefour                |
  | status           | Completed/Pending        |
And the list should be sorted by date (most recent first)
And I should have a "Back to Cards" option to return
```

### Scenario: Transfer money from a card

```gherkin
Given I have an active card selected
When I click "Transfer Money" button
Then a transfer page should appear with:
  | Field              | Validation                              |
  | source_card        | Pre-filled (current card)               |
  | amount             | Numeric input, required, > 0            |
  | id_usser           | String           |
  | location           | text field                     |
  | device_id          | text field                     |
  | transaction_id     | text field                     |
  | description        | text field                     |
  | confirm_button     | Disabled until all required fields set  |
And when I complete and submit the form with valid data:
Then I receive a confirmation message:
  | Field              | Content                  |
  | success_message    | "Transfer initiated successfully" |
  | Monto              |number           |
  | Usuario            |number           |
  | Estado             |number           |
  | Risk Score         |number           |
```

### Scenario: Cannot transfer from blocked card

```gherkin
Given I have a blocked card
When I attempt to click "Transfer Money"
Then the button should be disabled
And a tooltip should appear: "Cannot transfer from blocked card"
```

### Scenario: Max 3 cards displayed

```gherkin
Given I have more than 3 cards in my account
When I navigate to the Cards section
Then only 3 cards should be displayed by default
And I should see pagination or a "View All Cards" link
And clicking the link should show all my cards in a paginated view
```

### Scenario: Empty state - no cards

```gherkin
Given I have no cards in my account
When I navigate to the Cards section
Then I should see:
  | Content                   |
  | "No cards found" message  |
  | "Request a Card" button   |
And the request button should navigate to card request form
```

### Scenario: Insufficient permissions

```gherkin
Given I am a guest or restricted user
When I try to access the Cards section
Then I should receive HTTP 403 Forbidden
And the UI should display: "You don't have permission to view cards"
```

### Scenario: Transfer with insufficient balance

```gherkin
Given I have a card with balance $100.00
When I attempt to transfer $150.00
And I submit the transfer form
Then I should receive an error:
  | Field              | Content                                  |
  | error_message      | "Insufficient balance on source card"    |
  | available_balance  | "$100.00"                                |
```

### Scenario: Load card data on page initialization

```gherkin
Given I navigate to the Cards section
When the page loads
Then the system should:
  | Action                  | Behavior                    |
  | Fetch card list         | Async GET /api/v1/cards     |
  | Display loading state   | Skeleton loaders or spinner |
  | Load balance data       | Cache for 5 minutes         |
  | Handle API error        | Show retry button + message |
And the cards should display within 2 seconds
```

## Acceptance Criteria - Non-Functional

- **Performance**: Card data loads within 2 seconds
- **Accessibility**: All buttons and text meet WCAG 2.1 AA standards
- **Responsive**: Layout adapts to mobile, tablet, desktop (3 cards → 2 cards → 1 card layout)
- **Security**: Card numbers partially masked (XXXX-XXXX-XXXX-1234)
- **Internationalization**: Support for multiple currencies and languages

## Estimation

- **Story Points**: 8
- **Priority**: HIGH
- **Dependency**: HU-002 (audit trail for transactions)