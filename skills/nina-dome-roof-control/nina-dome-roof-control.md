# nina-dome-roof-control.md

## Overview
Controls mechanical roof/dome actuation and slew-sync operations. Provides independent control of dome/roof movement separate from safety monitoring decisions.

## Key Responsibilities
- Controls mechanical opening/closing of dome and roof
- Manages slew synchronization between dome/roof and mount
- Monitors physical status of dome/roof components
- Provides real-time status updates on actuation state
- Ensures safe and timely operation of dome/roof systems

## Input Parameters
- `action`: Action to perform (open, close, sync)
- `timeout_seconds`: Timeout duration for actuation (default: 60)
- `slew_speed_percentage`: Slew speed as percentage of maximum (default: 50%)
- `sync_tolerance_degrees`: Tolerance for mount/dome/sync (default: 0.1)

## Output Format
```json
{
 "action_status": "completed|failed|in_progress",
 "dome_status": {
 "is_open": true|false,
 "current_position": 45.2,
 "target_position": 90.0
 },
 "roof_status": {
 "is_open": true|false,
 "current_position": 30.1,
 "target_position": 60.0
 },
 "slew_sync_status": {
 "is_synchronized": true|false,
 "sync_error": "none|exceeded_tolerance"
 },
 "error_details": "none|timeout|mechanical_failure|communication_error"
}
```

## Safety & Error Handling
- Returns failure if mechanical constraints are violated
- Implements automatic retry for transient failures
- Logs detailed error messages for debugging
- Does not proceed with imaging if dome/roof is not in safe position

## Dependencies
- Requires access to dome/roof control system
- Depends on `nina-equipment-connection` for device status monitoring
- Uses `nina-alerting` to notify when critical actuation failures occur

## Tool Introspection Policy
Before performing any dome/roof actuation, this skill must first verify that:
1. Equipment is properly connected and operational
2. Current weather conditions are safe for opening/closing
3. Target position is within safe operating limits
4. No other equipment is in use that could conflict with dome/roof movement

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Dome/roof actuation is only initiated after proper validation of equipment status and safety conditions.

## Example Use Cases
- Opening the dome/roof before a night observation session
- Synchronizing dome/slew with mount position during a long exposure
- Verifying that the dome/roof is properly closed before starting imaging