# HU-016: View and Manage Multiple Cards

**As a** bank customer  
**I want** to view all my linked cards with their details and perform actions on them  
**So that** I can manage my finances and cards effectively from a single dashboard

## Acceptance Criteria

### Scenario: View all linked cards with details

```gherkin
Given I am an authenticated user logged into the user app
When I navigate to the Cards page
Then I should see all my linked cards displayed (paginated if > 3)
And each card should display:
  | Field              | Format/Example           |
  | card_number        | XXXX-XXXX-XXXX-1234      |
  | card_holder_name   | Juan Pérez               |
  | current_balance    | $1,250.50 COP            |
  | expiry_date        | MM/YY                    |
  | card_status        | Active/Blocked           |
  | card_type          | Debit/Credit             |
  | nickname           | "Personal Card" (if set) |
And each card should have action buttons for:
  | Action             | Description                        |
  | View Transactions  | See card-specific movements        |
  | Make Transaction   | Pay/transfer using this card       |
  | Block Card         | Temporarily disable card           |
  | Card Details       | Full card information              |
  | Remove Card        | Unlink from account (HU-015)       |
```

### Scenario: View card-specific transactions

```gherkin
Given I click "View Transactions" on card ending in 1234
When the transaction list loads
Then I should see ONLY transactions made with that specific card
And each transaction displays:
  | Field            | Content                  |
  | transaction_id   | UUID                     |
  | transaction_date | 2026-01-28 14:30:00      |
  | description      | Supermarket Purchase     |
  | amount           | -$45.99 COP              |
  | merchant         | Carrefour                |
  | status           | Completed/Pending/Failed |
  | fraud_score      | 0.15 (if evaluated)      |
And the list should be sorted by date (most recent first)
And I should have filters:
  | Filter           | Options                            |
  | Date Range       | Last 7/30/90 days, Custom          |
  | Status           | All/Completed/Pending/Failed       |
  | Amount Range     | Min-Max input                      |
```

### Scenario: Make transaction from specific card

```gherkin
Given I have an active card selected
When I click "Make Transaction" button
Then a transaction form should appear with:
  | Field              | Validation                              |
  | source_card        | Pre-filled (current card, read-only)    |
  | amount             | Numeric, required, > 0, ≤ card balance  |
  | recipient_user_id  | String, required, exists in system      |
  | description        | Optional, 200 chars max                 |
  | location           | Auto-detected lat/lng (optional manual) |
  | device_id          | Auto-detected from browser/app          |
And when I submit with valid data
Then the system should:
  | Action                  | Behavior                                |
  | Validate balance        | Check card.current_balance ≥ amount     |
  | Create transaction      | POST /api/v1/transactions               |
  | Publish to fraud queue  | fraud.queue (async evaluation)          |
  | Return 202 Accepted     | transaction_id in response              |
And I should see confirmation:
  | Field              | Content                               |
  | success_message    | "Transaction initiated successfully"  |
  | transaction_id     | UUID                                  |
  | amount             | $45.99                                |
  | recipient          | user_id                               |
  | status             | "Pending Evaluation"                  |
  | estimated_time     | "Results in ~2 minutes"               |
```

### Scenario: Transaction fails - insufficient balance

```gherkin
Given my card ending in 1234 has balance $100.00
When I attempt to make a transaction for $150.00
And I submit the transaction form
Then I should receive HTTP 400 Bad Request
And see error:
  | Field              | Content                                  |
  | error_message      | "Insufficient balance on selected card"  |
  | available_balance  | "$100.00"                                |
  | requested_amount   | "$150.00"                                |
```

### Scenario: Cannot transact from blocked card

```gherkin
Given I have a blocked card
When I attempt to click "Make Transaction"
Then the button should be disabled
And a tooltip should appear: "Cannot transact from blocked card. Unblock first."
```

### Scenario: Card blocked status indicator

```gherkin
Given I have a card that is blocked
When I view my cards
Then the blocked card should display:
  | Indicator         | Behavior                        |
  | Status Badge      | "BLOCKED" in red background     |
  | Action Buttons    | "Unblock Card" button available |
  | Transaction Button| Disabled/grayed out             |
  | Visual Treatment  | Dimmed appearance               |
```

### Scenario: Max 3 cards displayed by default

```gherkin
Given I have 5 cards linked
When I navigate to the Cards section
Then only 3 cards should be displayed by default
And I should see a "View All Cards" button
And clicking it should show all 5 cards in paginated view (3 per page)
```

### Scenario: Empty state - no cards linked

```gherkin
Given I have no cards linked to my account
When I navigate to the Cards section
Then I should see:
  | Content                   |
  | "No cards found" message  |
  | "Add Your First Card" CTA |
And the CTA button should navigate to card add form (HU-015)
```

### Scenario: Real-time balance updates

```gherkin
Given I make a transaction from card ending in 1234
When the transaction completes
Then the card balance should update automatically
And I should see a notification: "Card balance updated: $1,204.51"
And the transaction should appear in card-specific transaction history
```

## Acceptance Criteria - Non-Functional

- **Performance**: Card data loads within 2 seconds
- **Real-time**: Balance updates via WebSocket or polling (30s interval)
- **Accessibility**: All buttons and text meet WCAG 2.1 AA standards
- **Responsive**: Layout adapts to mobile (1 card), tablet (2 cards), desktop (3 cards)
- **Security**: Card numbers partially masked (XXXX-XXXX-XXXX-1234)
- **Internationalization**: Support for COP, USD, EUR currencies

## Estimation

- **Story Points**: 13 (increased from 8 due to card-specific transaction isolation)
- **Priority**: HIGH
- **Dependency**: HU-015 (add cards), HU-002 (audit trail)
