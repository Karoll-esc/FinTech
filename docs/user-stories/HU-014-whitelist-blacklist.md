# HU-014: Whitelist/Blacklist Management

**As a** risk manager  
**I want** to maintain whitelists (trusted users/merchants/locations) and blacklists (blocked users/cards)  
**So that** I can fine-tune fraud detection with business knowledge

## Acceptance Criteria

### Scenario: Whitelist trusted user

```gherkin
When I add user_123 to the whitelist
Then transactions from user_123 bypass certain high-risk checks
And approval rate for this user increases (with audit trail of override)
```

### Scenario: Blacklist suspicious merchant

```gherkin
When I add merchant_abc to the blacklist
Then any transaction with this merchant is automatically flagged HIGH_RISK
And an analyst review is mandatory before approval
```

### Scenario: Geographic exception

```gherkin
When I whitelist location "Office Building at 40.7128,-74.0060"
Then transactions from employees at this location skip location-based checks
And the whitelist rule is logged for audit purposes
```

## Estimation

- **Story Points**: 3
- **Priority**: LOW
- **Dependency**: HU-008, HU-009

## Implementation Notes

- Whitelist: Users, merchants, locations (trusted entities)
- Blacklist: Users, cards, merchants (blocked entities)
- Audit trail for all changes
- Dynamic loading (no restart)
