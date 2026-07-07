I'll help you build the proposed SKILL.md files based on the improvement proposal. Let me start with the first few skills to establish a consistent format, then we can continue with the rest.

```markdown
# nina-equipment-connection.md

## Overview
Diagnoses and reconnects ASCOM/INDI device dropouts across camera, mount, focuser, filter wheel, and rotator equipment. Provides real-time status monitoring and automated recovery for disconnected devices.

## Key Responsibilities
- Detects and reports ASCOM/INDI device disconnections
- Diagnoses root causes of connectivity failures
- Automatically attempts reconnection with configurable retry parameters
- Monitors device health and status in real-time
- Provides comprehensive device status reporting

## Input Parameters
- `device_type`: Type of equipment (camera, mount, focuser, filter wheel, rotator)
- `timeout_seconds`: Timeout duration for connection attempts (default: 30)
- `retries`: Number of retry attempts before giving up (default: 3)
- `retry_delay_seconds`: Delay between retry attempts (default: 5)

## Output Format
```json
{
  "status": "connected|disconnected|reconnecting",
  "device_type": "camera|mount|focuser|filter_wheel|rotator",
  "connection_status": {
    "is_connected": true|false,
    "last_connection_time": "2023-10-05T14:30:00Z",
    "error_message": "none|device_not_found|communication_error|timeout"
  },
  "reconnection_attempts": 0,
  "next_retry_time": "2023-10-05T14:35:00Z"
}
```

## Safety & Error Handling
- Returns `disconnected` if device is not found or communication fails
- Implements exponential backoff retry strategy
- Logs detailed error messages for debugging
- Does not force reconnection without user confirmation in safety-critical modes

## Dependencies
- Requires access to ASCOM/INDI device drivers
- Depends on `nina-equipment-monitor` for real-time status updates
- Uses `nina-alerting` to notify when critical failures occur

## Tool Introspection Policy
All equipment connection attempts must first verify device presence and communication capability before attempting any operations. This prevents unauthorized or unsafe device interactions.

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Device reconnection is only attempted after proper diagnostics and user confirmation in safety-critical scenarios.

## Example Use Cases
- Automatic recovery of a disconnected camera during an observation session
- Proactive monitoring of mount health before a long exposure sequence
- Diagnosing filter wheel dropout during a multi-filter observation
```

Now I'll continue with the next skill in the list:

```markdown
# nina-plate-solve.md

## Overview
Owns plate-solving failures and provides comprehensive solve capabilities including blind-solve, nearest-solve, and sync accuracy validation. Acts as the central authority for all plate-solving operations across the NINA stack.

## Key Responsibilities
- Owns all plate-solving operations and failure diagnosis
- Implements blind-solve (no prior plate solution) and nearest-solve (uses closest known solution)
- Validates sync accuracy between mount and plate solution
- Diagnoses and reports failed solve attempts with root cause analysis
- Provides detailed statistics on solve success rates and timing

## Input Parameters
- `solve_method`: Method to use (blind_solve, nearest_solve, auto)
- `target_position`: Target RA/Dec coordinates
- `max_attempts`: Maximum number of solve attempts (default: 5)
- `timeout_seconds`: Timeout for individual solve attempts (default: 30)
- `min_snr_threshold`: Minimum SNR threshold for acceptable solutions (default: 10)

## Output Format
```json
{
  "solve_status": "success|failure",
  "solution_found": true|false,
  "solution_quality": {
    "snr": 12.5,
    "accuracy": "0.03 arcsec",
    "confidence": "high|medium|low"
  },
  "sync_accuracy": {
    "mount_position_error": "0.02 arcsec",
    "solution_alignment": "perfect|slight_offset"
  },
  "error_details": "none|insufficient_stars|poor_sky_conditions|outlier_detection"
}
```

## Safety & Error Handling
- Returns failure if insufficient stars are detected or sky conditions are poor
- Implements automatic retry for transient failures
- Logs detailed error messages for debugging
- Does not proceed with imaging if solve quality is below minimum thresholds

## Dependencies
- Requires access to camera and mount data
- Depends on `nina-target-recommender` for target position input
- Uses `nina-alerting` to notify when critical solve failures occur

## Tool Introspection Policy
Before attempting any plate-solving operation, this skill must first verify that:
1. Camera is properly connected and operational
2. Mount is in a stable position
3. Target coordinates are valid and within field of view
4. Required star fields are visible in the current sky conditions

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Plate-solving operations are only initiated after proper validation of target conditions and equipment status.

## Example Use Cases
- Diagnosing and resolving failed plate-solve attempts during deep-sky imaging
- Implementing blind-solve for new targets with no prior solutions
- Validating mount sync accuracy after a long exposure sequence
```

I'll continue with the next skill:

```markdown
# nina-calibration-library.md

## Overview
Owns the complete calibration frame library including dark, flat, and bias frames. Manages acquisition scheduling, library completeness validation, and metadata tracking for all calibration types across gain/temp/exposure combinations.

## Key Responsibilities
- Manages dark, flat, and bias frame acquisition scheduling
- Validates library completeness for each gain/temp/exposure combo
- Tracks calibration frame metadata including timestamps, conditions, and quality metrics
- Provides automated scheduling based on current observing conditions
- Generates recommendations for when new calibration frames are needed

## Input Parameters
- `calibration_type`: Type of calibration (dark, flat, bias)
- `gain_setting`: Camera gain setting (default: auto)
- `temperature_setting`: Target temperature (default: ambient)
- `exposure_duration_seconds`: Exposure duration (default: 10)
- `schedule_mode`: Scheduling mode (auto|manual|on_demand)

## Output Format
```json
{
  "calibration_status": "scheduled|completed|pending|failed",
  "acquisition_plan": {
    "target_gain": 1.0,
    "target_temperature": 25.0,
    "exposure_duration": 10,
    "schedule_time": "2023-10-05T14:30:00Z",
    "priority": "high|medium|low"
  },
  "library_status": {
    "complete": true|false,
    "missing_frames": ["dark_10s_gain1", "flat_10s_gain2"],
    "quality_metrics": {
      "average_snr": 15.2,
      "uniformity_score": 0.98
    }
  },
  "recommendations": [
    "Acquire dark frame at 25°C for gain 1.0",
    "Schedule flat frame acquisition after next moon phase"
  ]
}
```

## Safety & Error Handling
- Returns failure if equipment is not available or conditions are unsuitable
- Implements automatic retry for transient failures
- Logs detailed error messages for debugging
- Does not proceed with imaging if calibration library is incomplete

## Dependencies
- Requires access to camera and mount data
- Depends on `nina-equipment-connection` for device status monitoring
- Uses `nina-alerting` to notify when critical calibration failures occur

## Tool Introspection Policy
Before initiating any calibration frame acquisition, this skill must first verify that:
1. Required equipment (camera, mount) is connected and operational
2. Target temperature and gain settings are valid
3. Current observing conditions are suitable for calibration
4. Equipment is not in use for primary imaging

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Calibration frame acquisition is only initiated after proper validation of equipment status and observing conditions.

## Example Use Cases
- Scheduling dark frames for different gain settings during a multi-exposure sequence
- Validating flat frame library completeness before deep-sky imaging
- Recommending when new calibration frames are needed based on current conditions
```

I'll continue with the next skill:

```markdown
# nina-rotator-framing.md

## Overview
Provides single-panel rotator/FOV framing math for optimal field of view alignment. Calculates optimal positioning and overlap percentages to ensure complete target coverage.

## Key Responsibilities
- Performs rotator positioning calculations for optimal FOV alignment
- Calculates optimal overlap percentages between panels
- Determines acquisition order for multi-panel observations
- Validates that the entire target field is within the rotator's FOV
- Provides detailed framing recommendations based on target characteristics

## Input Parameters
- `target_position`: Target RA/Dec coordinates
- `rotator_position`: Current rotator position (degrees)
- `field_of_view_degrees`: Field of view size in degrees
- `overlap_percentage`: Desired overlap percentage between panels (default: 10%)
- `acquisition_order`: Order of panel acquisition (sequential|random)

## Output Format
```json
{
  "framing_status": "valid|invalid",
  "rotator_position": 45.2,
  "field_coverage": {
    "target_coverage_percentage": 98.5,
    "overlap_percentage": 10.0,
    "edge_coverage": "complete|partial"
  },
  "acquisition_order": ["panel_1", "panel_2"],
  "recommendations": [
    "Move rotator to position 45.2 for optimal coverage",
    "Increase overlap to 15% for better edge coverage"
  ]
}
```

## Safety & Error Handling
- Returns invalid if target is outside the rotator's field of view
- Implements automatic validation of target position against FOV limits
- Logs detailed error messages for debugging
- Does not proceed with imaging if framing is deemed invalid

## Dependencies
- Requires access to mount and camera data
- Depends on `nina-target-recommender` for target position input
- Uses `nina-alerting` to notify when critical framing issues occur

## Tool Introspection Policy
Before performing any rotator framing calculations, this skill must first verify that:
1. Target coordinates are valid and within field of view
2. Rotator is properly connected and operational
3. Field of view parameters are reasonable and within limits
4. Equipment is in a stable position

## Destructive Action Policy
No destructive actions are performed by this skill. All operations are non-destructive and reversible. Rotator positioning is only recommended after proper validation of target conditions and equipment status.

## Example Use Cases
- Calculating optimal rotator positioning for deep-sky targets
- Determining required overlap percentages for multi-panel observations
- Validating field coverage before starting a long exposure sequence
```

I'll continue with the next skill:

```markdown
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
```

This completes the first 5 skills in the proposed architecture. Each skill follows a consistent format with clear sections for overview, responsibilities, inputs/outputs, safety policies, dependencies, and examples. I can continue building the remaining skills if you'd like me to proceed.