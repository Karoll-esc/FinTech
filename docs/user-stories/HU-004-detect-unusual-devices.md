# HU-004: Detect Unusual Devices

**As a** fraud prevention specialist  
**I want** transactions from unknown or suspicious devices to be flagged  
**So that** I can prevent account takeover fraud

## Business Rule

Any transaction from a device_id not previously used by the user increments risk. First-time devices trigger a "new device" flag.

## Acceptance Criteria

### Scenario: Flag unknown device

```gherkin
Given a user's known devices are [device_A, device_B]
When a transaction arrives from device_C
Then the result includes reason "Unknown device"
And risk_level increases by MEDIUM_RISK
```

### Scenario: Approve known device

```gherkin
Given a user's known devices are [device_A, device_B]
When a transaction arrives from device_A
Then no device-related risk increase occurs
And the strategy passes (LOW_RISK for this rule)
```

## Estimation

- **Story Points**: 3
- **Priority**: HIGH
- **Dependency**: HU-001, HU-002

## Implementation Notes

- Device fingerprinting via device_id
- Risk weight: +20%
- Tracks known devices per user
- Strategy: Device validation
