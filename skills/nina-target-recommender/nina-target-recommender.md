# nina-target-recommender.md

## Overview
Provides intelligent target recommendations based on current observing conditions, equipment capabilities, and historical data. Acts as the central authority for target selection across the NINA stack.

## Key Responsibilities
- Provides intelligent target recommendations based on current conditions
- Analyzes historical data to identify optimal targets
- Considers equipment capabilities when recommending targets
- Validates target suitability before recommendation
- Generates detailed reports on target selection rationale

## Input Parameters
- `recommendation_type`: Type of recommendation (new_target, follow_up, backup)
- `observation_conditions`: Current observing conditions (weather, sky quality)
- `equipment_capabilities`: Equipment capabilities (mount, camera)
- `historical_data_days`: Historical data period (default: 30 days)
- `priority_level`: Priority level for recommendations (high|medium|low)

## Output Format
```json
{
 "recommendation_status": "recommended|not_applicable",
 "target_recommendations": [
 {
 "target_name": "M42",
 "ra_dec": "12h 00m 00s +00° 00′",
 "confidence_level": 0.95,
 "suitability_score": 0.87,
 "reasoning": "Good visibility with minimal atmospheric interference"
 }
 ],
 "recommendation_rationale": "Based on current weather conditions and equipment capabilities, M42 is recommended as it has excellent visibility and is within the optimal field of view",
 "priority_level": "high"
}
```

## Safety & Error Handling
- Returns not_applicable if no suitable targets are found
- Implements automatic retry for transient data failures
- Logs detailed error messages for debugging
- Does not proceed with imaging without proper target validation

## Dependencies
- Requires access to current observing conditions and historical data
- Depends on `nina-equipment-connection` for device status monitoring
- Uses `nina-alerting` to notify when critical target selection issues occur

## Tool Introspection Policy
Before providing any target recommendations, this skill must first verify that:
1. Current observing conditions are suitable for imaging
2. Equipment capabilities are within operational limits
3. Historical data is available and valid
4. No other equipment is in use that could conflict with target selection

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Target recommendations are only provided after proper validation of observing conditions and equipment status.

## Example Use Cases
- Recommending new targets based on current weather conditions
- Providing backup targets in case of primary target failure
- Identifying optimal targets for long exposure sequences