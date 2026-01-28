# HU-005: Detect Geographically Impossible Transactions

**As a** fraud prevention specialist  
**I want** transactions from unusual locations (far from the user's historical location) to be flagged  
**So that** I can prevent geographical takeover attacks

## Business Rule

Calculate Haversine distance between current transaction location and user's last known location. If distance > 100 km, flag as MEDIUM/HIGH_RISK.

## Acceptance Criteria

### Scenario: Flag suspicious location distance

```gherkin
Given user's last known location is New York (40.7128, -74.0060)
When a transaction arrives from Miami (25.7617, -80.1918) ~1,760 km away
Then the risk_level includes "unusual_location"
And risk increases by +25%
And the reason shows distance: "1,760 km from last known location"
```

### Scenario: Approve nearby location

```gherkin
Given user's last known location is New York (40.7128, -74.0060)
When a transaction arrives from Brooklyn (40.6782, -73.9442) ~7 km away
Then no location-related risk is triggered
And the strategy passes (LOW_RISK for this rule)
```

### Scenario: Handle new user (no historical location)

```gherkin
Given a user is new and has no previous transactions
When the first transaction arrives
Then the location check is skipped
And the reason is "no_historical_location"
And risk does not increase
```

## Estimation

- **Story Points**: 5
- **Priority**: HIGH
- **Dependency**: HU-001, HU-002

## Implementation Notes

- Haversine distance calculation (kilometers)
- Distance threshold: 100 km
- Risk weight: +25%
- Handles new users (no historical data)
- Strategy: Geolocation anomaly detection
