# HU-008: View Current Fraud Rule Configuration

**As a** risk manager  
**I want** to view all active fraud detection rules and their current thresholds  
**So that** I can understand how the system is configured

## Acceptance Criteria

### Scenario: View rule configuration

```gherkin
When I navigate to GET /api/v1/config/thresholds
Then I receive a list of all configured rules with:
  | Field             | Example              |
  | rule_name         | amount_threshold     |
  | description       | "Amount exceeds..."  |
  | current_threshold | 1500.0               |
  | enabled           | true                 |
  | risk_increment    | 30                   |
  | last_modified     | 2026-01-28T10:30:00Z |
```

### Scenario: Filter by rule type

```gherkin
When I query GET /api/v1/config/thresholds?type=location
Then I receive only location-related rules
```

## Estimation

- **Story Points**: 2
- **Priority**: MEDIUM
- **Dependency**: HU-003 to HU-007

## Implementation Notes

- Endpoint: `GET /api/v1/config/thresholds`
- Support filtering by type
- Read-only endpoint (no modifications here)
- Related to HU-009 for updates
