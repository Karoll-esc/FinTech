# HU-006: Detect Rapid Succession Transactions

**As a** fraud prevention specialist  
**I want** multiple rapid transactions from the same user to be flagged  
**So that** I can prevent card testing fraud (small charges to verify stolen cards)

## Business Rule

If a user has ≥3 transactions within a 10-minute window, flag as MEDIUM_RISK.

## Acceptance Criteria

### Scenario: Flag rapid transaction sequence

```gherkin
Given a user has performed 2 transactions in the last 5 minutes
When a 3rd transaction arrives
Then the risk_level includes "rapid_transaction"
And risk increases by +15%
And the reason shows "3 transactions in 10 minutes"
```

### Scenario: Approve normal transaction frequency

```gherkin
Given a user normally performs 1-2 transactions per hour
When a new transaction arrives
Then the rapid transaction check passes (LOW_RISK for this rule)
```

## Estimation

- **Story Points**: 3
- **Priority**: MEDIUM
- **Dependency**: HU-001, HU-002

## Implementation Notes

- Time window: 10 minutes
- Threshold: ≥3 transactions
- Risk weight: +15%
- Strategy: Velocity-based detection
