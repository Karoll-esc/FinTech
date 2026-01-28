# HU-001: Receive Transactions via REST API

**As a** system integrator  
**I want** to send transactions to fraud evaluation via a simple REST API  
**So that** I can integrate fraud detection into my transaction processing pipeline

## Acceptance Criteria

### Scenario: Accept valid transaction

```gherkin
Given the API is available at http://localhost:8000
When I POST to /api/v1/transactions/evaluate with valid data
  | field      | value            |
  | user_id    | user_123         |
  | amount     | 500.0            |
  | location   | 4.7110,-74.0721  |
  | device_id  | device_mobile_1  |
Then I receive HTTP 202 Accepted
And the response includes a transaction_id
And the response includes status "processing"
```

### Scenario: Reject missing required field

```gherkin
Given the API is available
When I POST without user_id
Then I receive HTTP 422 Unprocessable Entity
And the error message specifies the missing field
```

### Scenario: Reject negative amount

```gherkin
Given the API is available
When I POST with amount = -500.0
Then I receive HTTP 422 Unprocessable Entity
And the error message specifies "amount must be positive"
```

## Estimation

- **Story Points**: 3
- **Priority**: CRITICAL
- **Dependency**: None

## Implementation Notes

- API endpoint: `POST /api/v1/transactions/evaluate`
- Response status: 202 Accepted (async processing)
- Response includes `transaction_id` for result polling
- Validation: All fields required and must match data types
