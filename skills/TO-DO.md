# NINA Skill Architecture Improvement Proposal

## Overview

This document outlines key structural gaps and risks in the current NINA skill architecture, along with actionable recommendations for improvement. The analysis focuses on both the existing 10 skills and the proposed expansion to 40 skills.

---

## Key Gaps & Risks (Existing 10 Skills)

### 1. Plate-solving has no owner
The plate-solving functionality is currently fragmented across multiple skills:
- `nina-sequencer` (validation)
- `nina-config-editor` (solver settings)
- Implicitly `nina-target-recommender` (framing)

**Recommendation**: Split into a dedicated skill `nina-plate-solve` and have all existing skills defer to it by name rather than handling it themselves.

### 2. Calibration frames are entirely absent
Calibration frames (darks, flats, bias) are missing from the core workflow. While `nina-sequencer` references cooling, there's no ownership for:
- Matching darks to gain/temp/exposure
- Scheduling flat panel runs

**Recommendation**: Add a dedicated skill `nina-calibration-library` to own calibration frame acquisition and scheduling.

### 3. Equipment connectivity is assumed, never diagnosed
Skills like `nina-image-eval`, `nina-guiding-monitor`, and `nina-weather-safety` assume device connectivity but lack error handling for missing data.

**Recommendation**: Add `nina-equipment-connection` to diagnose and reconnect ASCOM/INDI dropouts across all equipment. Each skill should include a check: "if data is missing rather than bad, defer instead of reporting false gaps."

### 4. No notification layer exists
All skills report directly to the router in text form. There's no mechanism to push alerts or notifications to humans.

**Recommendation**: Add `nina-alerting` with capabilities to:
- Push notifications for aborts and manual interventions
- Flag findings that should escalate beyond logging

### 5. Nothing sits above the single sequence
While `nina-sequencer` handles Start/End within a sequence, there's no ownership of the overall NINA process lifecycle.

**Recommendation**: Add skills to manage the meta-level process:
- `nina-startup-shutdown`: Meta-level "is the whole stack up" safe start and shutdown verification
- `nina-session-preflight`: Single go/no-go gate run before startup

### 6. Shared boilerplate is duplicated ten times
Every skill independently restates common policies like tool introspection and destructive-action warnings.

**Recommendation**: Extract a shared policy document `references/nina-shared-conventions.md` that includes:
- Tool introspection policy
- Destructive-action policy
- Output contract template

All skills should reference this single document rather than re-authoring policies.

### 7. nina-field-notes needs formal namespace registry
The current key convention (`category.rig.parameter-style`) is sustainable at 10 skills but will break at scale with new categories like maintenance schedules and ROI trends.

**Recommendation**: Establish a formal namespace registry for `nina-field-notes` that:
- Publishes and enforces valid category values
- Defines key patterns to prevent collisions and sprawl

### 8. Router relies on prose self-limiting, not a manifest
Skills currently define ownership through hand-written descriptions, which becomes brittle at scale.

**Recommendation**: Replace prose with a centralized router/manifest.md or JSON capability table that maps intent keywords to owning skills. This enables:
- Clear ownership boundaries
- Easier maintenance and scaling

### 9. Zero eval coverage
None of the 10 skills have example trigger prompts or near-miss prompts.

**Recommendation**: Generate 5-8 examples per skill, including deliberate near-misses to catch overlap (e.g., a moon question that should go to `nina-lunar-filter` vs. one that should go to `nina-target-recommender`).

### 10. Weather/moon reasoning is about to get crowded
Multiple skills share weather/moon logic:
- `nina-target-recommender` and `nina-lunar-filter` share moon logic
- `nina-weather-safety` and `nina-guiding-monitor` share wind data

**Recommendation**: Re-confirm the "consume, don't re-derive" principle before adding new skills like `nina-forecast-longrange`, `nina-astro-events`, and `nina-allsky-monitor`.

---

## Proposed 30 Additional Skills (Grouped by Cluster)

### A. Equipment & Optical Train Mechanics
- `nina-equipment-connection` — Diagnose/reconnect ASCOM/INDI dropouts across camera, mount, focuser, filter wheel, rotator  
- `nina-plate-solve` — Owns solve failures, blind-solve vs. nearest-solve, sync accuracy  
- `nina-calibration-library` — Dark/flat/bias acquisition scheduling and library completeness per gain/temp/exposure combo  
- `nina-rotator-framing` — Single-panel rotator/FOV framing math  
- `nina-dome-roof-control` — Mechanical roof/dome actuation and slew-sync, distinct from safety monitor's go/no-go verdict  

### B. Observatory Infrastructure
- `nina-power-management` — PDU/UPS status, smart-plug power-cycling of stuck gear, remote-site battery runtime  
- `nina-network-watchdog` — Remote-observatory link health, latency, session-drop detection  
- `nina-disk-storage` — Disk space monitoring/forecast on acquisition PC, non-destructive cleanup suggestions only  
- `nina-allsky-monitor` — All-sky camera feed interpretation for cloud/satellite/aircraft cross-check, visual confirmation layer for weather safety  
- `nina-startup-shutdown` — Meta-level "is the whole stack up" safe unattended start and safe shutdown/park verification  

### C. Notifications & Reporting
- `nina-alerting` — Push notifications (send_notification) for aborts, manual-intervention-needed, session-complete  
- `nina-morning-report` — End-of-session human-readable recap synthesizing image-eval + guiding + weather + scheduler-monitor  
- `nina-session-roi` — Usable-imaging-time vs. lost-to-weather/equipment time, trend over a season  
- `nina-forecast-longrange` — Multi-day/week clear-window and seeing forecasting for trip planning, distinct from tonight-focused weather safety  
- `nina-astro-events` — Meteor shower / satellite flare / ISS pass / occultation awareness, opportunistic or avoidance  

### D. Data Pipeline & Post-Processing Handoff
- `nina-data-transfer` — Post-session sync/backup to NAS/cloud, file-count integrity check  
- `nina-siril-handoff` — Stage/trigger Siril calibration+stacking, pulling library refs from calibration library  
- `nina-palette-planner` — SHO/HOO/bicolor narrowband combination recommendations from actually-acquired filters  
- `nina-stack-eval` — Post-stack quality (integrated SNR estimate, residual gradient, star shape), distinct from per-sub nina-image-eval  
- `nina-archive-catalog` — Long-term metadata catalog of completed projects/stacks  

### E. Maintenance & Asset Tracking
- `nina-maintenance-log` — Collimation/cleaning/cable schedule and reminders, feeds nina-field-notes  
- `nina-config-version-control` — Git-like diff/rollback for profile & sequence JSON, safety net above nina-config-editor  
- `nina-plugin-update-manager` — NINA core + plugin version tracking, changelog review before recommending an update  
- `nina-polar-alignment` — Polar-align routine execution/interpretation (e.g. three-point error reporting)  
- `nina-backlash-calibration` — Focuser/mount backlash measurement procedure, results recorded for nina-config-editor to consume  

### F. Advanced Planning & Multi-Rig
- `nina-mosaic-planner` — Multi-panel framing, overlap %, acquisition order, distinct from single-panel nina-rotator-framing  
- `nina-multi-rig-coordinator` — Coordinate 2+ independent NINA instances sharing a site (priority conflicts, shared dome contention)  
- `nina-eaa-live-stack` — Electronically-assisted-astronomy/live-stacking session support, different cadence/goals than deep integration  
- `nina-pier-limits-safety` — Meridian/pier-side limits, cable-snag zones, custom no-go regions distinct from altitude conditions  
- `nina-session-preflight` — Single go/no-go gate (equipment connected, cooling reached, disk space, forecast) run before nina-startup-shutdown  

---
