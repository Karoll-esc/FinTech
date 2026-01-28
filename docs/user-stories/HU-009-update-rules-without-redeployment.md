# HU-009: Update Fraud Rules Without Redeployment

**As a** risk manager  
**I want** to change fraud detection thresholds and enable/disable rules via the dashboard  
**So that** I can respond to emerging fraud patterns within minutes (not hours/days)

## Acceptance Criteria

### Scenario: Update single threshold

```gherkin
When I submit PUT /api/v1/config/thresholds with:
  {
    "rule_name": "amount_threshold",
    "new_threshold": 2000.0,
    "enabled": true
  }
Then I receive HTTP 200 OK
And the configuration is persisted to MongoDB
And the Worker service reloads configuration from DB
And within 10 seconds, new transactions use the updated threshold
```

### Scenario: Disable a rule

```gherkin
When I submit PUT /api/v1/config/thresholds with:
  {
    "rule_name": "location_check",
    "enabled": false
  }
Then the location check is skipped for subsequent transactions
And existing audit logs are not modified
```

### Scenario: Validate threshold value

```gherkin
When I submit PUT with an invalid value (e.g., negative amount)
Then I receive HTTP 400 Bad Request
And the configuration is NOT changed
And the system remains stable
```

### Scenario: Audit configuration change

```gherkin
When a rule configuration is updated
Then the change is logged with:
  | Field      | Value          |
  | actor      | risk_manager_1 |
  | rule_name  | amount_thresh  |
  | old_value  | 1500           |
  | new_value  | 2000           |
  | timestamp  | 2026-01-28...  |
```

## Estimation

- **Story Points**: 5
- **Priority**: HIGH
- **Dependency**: HU-008

## Implementation Notes

- Endpoint: `PUT /api/v1/config/thresholds`
- Dynamic reload: No container restart needed
- Configuration sourced from MongoDB
- RabbitMQ event notification for workers
- Full audit trail of all changes
