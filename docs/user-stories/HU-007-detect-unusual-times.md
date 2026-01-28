# HU-007: Detect Unusual Transaction Times

**As a** fraud prevention specialist  
**I want** transactions outside a user's typical behavior hours to be flagged  
**So that** I can catch account compromises (fraudster operating at different times than legitimate user)

## Business Rule

If transaction timestamp is >2 standard deviations outside the user's historical transaction hours, flag as MEDIUM_RISK.

## Acceptance Criteria

### Scenario: Flag unusual transaction time

```gherkin
Given a user typically transacts 9 AM - 5 PM weekdays
When a transaction arrives at 3 AM on Sunday
Then the risk_level includes "unusual_time"
And risk increases by +10%
And the reason shows "Transaction at unusual hour"
```

### Scenario: Approve typical transaction time

```gherkin
Given a user typically transacts 9 AM - 5 PM weekdays
When a transaction arrives at 2 PM on Tuesday
Then no time-related risk is triggered
```

## Estimation

- **Story Points**: 3
- **Priority**: MEDIUM
- **Dependency**: HU-001, HU-002

## Implementation Notes

- Statistical model: μ ± 2σ (mean ± 2 standard deviations)
- Risk weight: +10%
- Accounts for timezone
- Strategy: Temporal anomaly detection
