# HU-003: Detect High-Amount Transactions

**As a** fraud prevention specialist  
**I want** transactions exceeding a configurable threshold to be flagged as HIGH_RISK  
**So that** I can prevent large fraudulent charges

## Business Rule

Any transaction with `amount > $1,500 USD` is automatically flagged as HIGH_RISK and sent to the analyst review queue.

## Acceptance Criteria

### Scenario: Flag transaction exceeding threshold

```gherkin
Given the amount threshold is configured at $1,500
When a transaction arrives with amount = $2,000
Then the risk_level is HIGH_RISK
And the reason includes "Amount $2,000 exceeds threshold $1,500"
And the transaction is queued for analyst review
```

### Scenario: Approve transaction within threshold

```gherkin
Given the amount threshold is configured at $1,500
When a transaction arrives with amount = $1,200
Then the risk_level is LOW_RISK (or updated by other strategies)
And the transaction is not queued for mandatory review
```

### Scenario: Handle threshold exactly

```gherkin
Given the amount threshold is configured at $1,500
When a transaction arrives with amount = $1,500.00
Then the risk_level is LOW_RISK (exact match is acceptable)
```

## Estimation

- **Story Points**: 3
- **Priority**: HIGH
- **Dependency**: HU-001, HU-002

## Implementation Notes

- Configurable threshold (default: $1,500)
- Risk weight: +30%
- Strategy: Amount-based detection
