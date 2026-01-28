# HU-010: Manual Review & Override of Flagged Transactions

**As a** fraud analyst  
**I want** to review flagged transactions and approve/reject them with optional notes  
**So that** I can override automatic decisions and learn from false positives

## Acceptance Criteria

### Scenario: Review flagged transaction

```gherkin
When I view a HIGH_RISK transaction in the dashboard
Then I see:
  | Information      | Content                     |
  | Transaction ID   | uuid                        |
  | User ID          | user_123                    |
  | Amount           | $2,500                      |
  | Location         | New York                    |
  | Risk Level       | HIGH_RISK                   |
  | Reasons          | ["Amount exceeds threshold",|
  |                  |  "Unknown device"]          |
  | Timestamp        | 2026-01-28T10:30:00Z        |
```

### Scenario: Approve flagged transaction

```gherkin
When I click "APPROVE" on a HIGH_RISK transaction
And I optionally add notes: "Customer confirmed via phone"
Then I receive HTTP 200 OK
And the transaction status changes to APPROVED
And the audit log records my decision with timestamp and actor
```

### Scenario: Reject transaction

```gherkin
When I click "REJECT" on a transaction
And I provide justification: "Card lost - customer reported"
Then the transaction is marked REJECTED
And the customer is notified (via their app or email)
And the audit log includes my decision and reasoning
```

### Scenario: Appeal/Dispute

```gherkin
When a customer disputes a transaction decision
Then a support team can view the analyst's decision and notes
And initiate a re-review with a different analyst
```

## Estimation

- **Story Points**: 5
- **Priority**: HIGH
- **Dependency**: HU-001 to HU-007

## Implementation Notes

- Dashboard review interface for analysts
- Support APPROVE/REJECT with notes
- Real-time status updates
- Customer notifications
- Dispute/appeal workflow
