# HU-011: View Real-Time Fraud Metrics

**As a** risk manager  
**I want** to see real-time dashboard metrics about fraud detection performance  
**So that** I can monitor system effectiveness and detect emerging patterns

## Acceptance Criteria

### Scenario: View fraud metrics dashboard

```gherkin
When I open the Admin Dashboard
Then I see real-time metrics:
  | Metric                    | Example   | Refresh |
  | Total Transactions        | 45,231    | 1 min   |
  | Total Flagged             | 2,104     | 1 min   |
  | Fraud Rate %              | 4.65%     | 1 min   |
  | HIGH_RISK Count           | 324       | 1 min   |
  | MEDIUM_RISK Count         | 1,780     | 1 min   |
  | LOW_RISK Count            | 43,127    | 1 min   |
  | Avg Review Time           | 2.3 min   | 5 min   |
  | Analyst Workload (queue)  | 342 pending | 1 min |
```

### Scenario: View fraud trends over time

```gherkin
When I view the "Trends" tab
Then I see line charts showing:
  - Fraud rate over last 7 days, 30 days
  - Transactions per hour
  - False positive rate over time
  - Top fraud reasons/patterns
  - Rule effectiveness (% of fraud caught by each strategy)
```

## Estimation

- **Story Points**: 5
- **Priority**: MEDIUM
- **Dependency**: HU-001 to HU-010

## Implementation Notes

- Real-time dashboard with 1-min refresh
- Metrics aggregation from MongoDB
- Charts and trend analysis
- Rule effectiveness tracking
