# nina-target-observer.md

## Overview
Provides real-time observation status monitoring and updates. Tracks target acquisition, tracking, and imaging progress in real-time.

## Key Responsibilities
- Provides real-time observation status monitoring
- Tracks target acquisition, tracking, and imaging progress
- Updates observation status in real-time
- Generates detailed progress reports
- Alerts on potential issues during observation

## Input Parameters
- `monitor_type`: Type of monitoring (acquisition, tracking, imaging)
- `timeout_seconds`: Timeout duration for monitoring (default: 30)
- `check_interval_seconds`: Interval between status checks (default: 60)
- `threshold_percentage`: Progress threshold for warnings (default: 50%)

## Output Format
```json
{
 "monitoring_status": "active|inactive",
 "observation_status": {
 "is_acquiring": true|false,
 "acquisition_progress_percentage": 75.0,
 "tracking_status": "stable|unstable",
 "imaging_status": "not_started|in_progress|completed"
 },
 "progress_report": {
 "current_phase": "acquisition",
 "estimated_completion_time": "2023-10-05T14:30:00Z",
 "remaining_time_minutes": 30
 },
 "alerts": [
 {
 "type": "progress_warning",
 "severity": "medium",
 "message": "Acquisition progress at 75% - consider adjusting parameters",
 "timestamp": "2023-10-05T14:30:00Z"
 }
 ]
}
```

## Safety & Error Handling
- Returns inactive status if no monitoring is requested
- Implements automatic retry for transient failures
- Logs detailed error messages for debugging
- Does not initiate actions without user confirmation in safety-critical scenarios

## Dependencies
- Requires access to real-time observation data
- Depends on `nina-equipment-connection` for device status monitoring
- Uses `nina-alerting` to notify when critical observation issues occur

## Tool Introspection Policy
Before initiating any observation monitoring, this skill must first verify that:
1. Observation system is operational and within safe operating parameters
2. Target is properly acquired and tracked
3. Current network conditions are stable enough for monitoring
4. No other equipment is in use that could conflict with monitoring operations

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Observation monitoring is only initiated after proper validation of observation status and equipment conditions.

## Example Use Cases
- Monitoring real-time observation status during a night session
- Tracking target acquisition, tracking, and imaging progress
- Generating detailed progress reports for observation managers