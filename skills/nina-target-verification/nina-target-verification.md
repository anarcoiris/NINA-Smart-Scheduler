# nina-target-verification.md

## Overview
Verifies target position accuracy and confirms target visibility before imaging. Provides comprehensive validation of target parameters and conditions.

## Key Responsibilities
- Verifies target position accuracy against known coordinates
- Confirms target visibility based on current conditions
- Validates target parameters before imaging
- Provides detailed validation reports
- Generates recommendations for target adjustments if needed

## Input Parameters
- `target_position`: Target RA/Dec coordinates
- `verification_type`: Type of verification (position, visibility, both)
- `timeout_seconds`: Timeout duration for verification (default: 30)
- `retries`: Number of retry attempts before giving up (default: 3)
- `retry_delay_seconds`: Delay between retry attempts (default: 5)

## Output Format
```json
{
 "verification_status": "verified|failed|in_progress",
 "target_position": "12h 00m 00s +00° 00′",
 "position_accuracy": {
 "accuracy_percentage": 98.5,
 "error_margin_arcsec": 0.03
 },
 "visibility_status": {
 "is_visible": true|false,
 "sky_quality": "excellent|good|fair",
 "atmospheric_interference": "low|medium|high"
 },
 "validation_report": {
 "target_confirmed": true,
 "recommendations": [
 "Consider adjusting target position for better visibility",
 "Monitor for potential atmospheric interference"
 ]
 }
}
```

## Safety & Error Handling
- Returns failed status if any verification fails
- Implements automatic retry for transient failures
- Logs detailed error messages for debugging
- Does not proceed with imaging if target is not verified

## Dependencies
- Requires access to target and equipment control systems
- Depends on `nina-equipment-connection` for device status monitoring
- Uses `nina-alerting` to notify when critical verification failures occur

## Tool Introspection Policy
Before performing any target verification, this skill must first verify that:
1. Target coordinates are valid and within field of view
2. Required equipment (camera, mount) is connected and operational
3. Current weather conditions are suitable for imaging
4. No other equipment is in use that could conflict with verification operations

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Target verification is only initiated after proper validation of target conditions and equipment status.

## Example Use Cases
- Verifying target position accuracy before an observation session
- Confirming target visibility based on current conditions
- Validating target parameters before starting imaging