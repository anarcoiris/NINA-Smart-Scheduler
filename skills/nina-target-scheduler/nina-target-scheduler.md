# nina-target-scheduler.md

## Overview
Schedules target observations based on current conditions, equipment capabilities, and historical data. Provides intelligent scheduling of observation sequences across multiple targets.

## Key Responsibilities
- Schedules target observations based on current conditions
- Considers equipment capabilities when scheduling targets
- Validates schedule feasibility before execution
- Provides detailed scheduling reports
- Generates recommendations for optimal scheduling

## Input Parameters
- `schedule_type`: Type of schedule (single_target, multi_target_sequence)
- `observation_conditions`: Current observing conditions
- `equipment_capabilities`: Equipment capabilities
- `historical_data_days`: Historical data period (default: 30 days)
- `priority_level`: Priority level for scheduling (high|medium|low)

## Output Format
```json
{
 "scheduling_status": "scheduled|failed|in_progress",
 "target_schedule": [
 {
 "target_name": "M42",
 "scheduled_time": "2023-10-05T14:30:00Z",
 "priority": "high",
 "duration_minutes": 60
 }
 ],
 "schedule_validation": {
 "is_feasible": true|false,
 "constraints_met": true|false,
 "recommendations": [
 "Consider adjusting target order for better visibility"
 ]
 },
 "scheduling_rationale": "Based on current weather conditions and equipment capabilities, M42 is scheduled for optimal viewing time"
}
```

## Safety & Error Handling
- Returns failed status if schedule is not feasible
- Implements automatic retry for transient data failures
- Logs detailed error messages for debugging
- Does not proceed with imaging without proper schedule validation

## Dependencies
- Requires access to current observing conditions and historical data
- Depends on `nina-equipment-connection` for device status monitoring
- Uses `nina-alerting` to notify when critical scheduling issues occur

## Tool Introspection Policy
Before scheduling any targets, this skill must first verify that:
1. Current observing conditions are suitable for imaging
2. Equipment capabilities are within operational limits
3. Historical data is available and valid
4. No other equipment is in use that could conflict with scheduling operations

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Target scheduling is only initiated after proper validation of observing conditions and equipment status.

## Example Use Cases
- Scheduling target observations based on current weather conditions
- Providing intelligent scheduling for multi-target sequences
- Validating schedule feasibility before execution