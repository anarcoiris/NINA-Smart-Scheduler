# nina-target-commander.md

## Overview
Executes target command sequences for observatory equipment. Provides a unified interface for executing complex target operations across multiple subsystems.

## Key Responsibilities
- Executes target command sequences for observatory equipment
- Coordinates complex target operations across multiple subsystems
- Validates target parameters before execution
- Provides real-time status updates on command execution
- Generates recommendations for optimal target selection

## Input Parameters
- `command_sequence`: Sequence of commands to execute (e.g., "acquire_target", "track_target")
- `target_position`: Target RA/Dec coordinates
- `timeout_seconds`: Timeout duration for command execution (default: 30)
- `retries`: Number of retry attempts before giving up (default: 3)
- `retry_delay_seconds`: Delay between retry attempts (default: 5)

## Output Format
```json
{
 "command_status": "executed|failed|in_progress",
 "target_position": "12h 00m 00s +00° 00′",
 "execution_sequence": [
 {
 "step": 1,
 "command": "acquire_target",
 "status": "completed",
 "timestamp": "2023-10-05T14:30:00Z"
 }
 ],
 "error_details": "none|timeout|command_not_found|parameter_error",
 "recommendations": [
 "Consider adjusting target position for better visibility",
 "Monitor for potential atmospheric interference"
 ]
}
```

## Safety & Error Handling
- Returns failed status if any command fails validation
- Implements automatic retry for transient failures
- Logs detailed error messages for debugging
- Does not proceed with imaging if any critical command fails

## Dependencies
- Requires access to target and equipment control systems
- Depends on `nina-equipment-connection` for device status monitoring
- Uses `nina-alerting` to notify when critical command failures occur

## Tool Introspection Policy
Before executing any target command sequence, this skill must first verify that:
1. Target coordinates are valid and within field of view
2. Required equipment (camera, mount) is connected and operational
3. Current weather conditions are suitable for target acquisition
4. No other equipment is in use that could conflict with command execution

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Command execution is only initiated after proper validation of target conditions and equipment status.

## Example Use Cases
- Executing complex target acquisition sequences for deep-sky imaging
- Coordinating multi-system operations during long exposure sequences
- Validating target parameters before starting an observation session