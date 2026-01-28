# HU-002: Maintain Immutable Audit Trail

**As a** compliance auditor  
**I want** all fraud evaluation decisions to be recorded in an immutable log  
**So that** I can prove regulatory compliance (SOX, GDPR, AML)

## Acceptance Criteria

### Scenario: Log evaluation to audit trail

```gherkin
Given a transaction was evaluated and marked LOW_RISK
When I query GET /api/v1/audit/transaction/{transaction_id}
Then I receive a record containing:
  | Field               | Example                |
  | transaction_id      | uuid                   |
  | user_id             | user_123               |
  | amount              | 500.0                  |
  | risk_level          | LOW_RISK               |
  | strategies_applied  | [amount_threshold, ...] |
  | reasons             | ["Amount acceptable"] |
  | timestamp           | 2026-01-28T10:30:00Z   |
And the record is marked as immutable (no updates allowed)
```

### Scenario: Query audit by user

```gherkin
Given multiple transactions from user_123 exist
When I query GET /api/v1/audit/all?user_id=user_123&limit=50
Then I receive a paginated list of evaluations for that user
And results are sorted by timestamp (newest first)
```

### Scenario: Export audit log

```gherkin
Given audit records exist in MongoDB
When an analyst requests export for compliance review
Then the system generates a CSV/JSON file with all audit trails
And the export includes decision reasoning and timestamps
```

## Estimation

- **Story Points**: 5
- **Priority**: CRITICAL
- **Dependency**: HU-001

## Implementation Notes

- All evaluations stored in MongoDB with immutable flag
- No updates allowed after creation
- Timestamps in ISO 8601 format
- Compliance with SOX, GDPR, PCI DSS, AML
