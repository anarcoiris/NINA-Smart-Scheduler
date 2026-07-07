# NINA Advanced API (ninaAPI) and Target Scheduler Database Schema Research

This document details the REST API endpoints of the `ninaAPI` plugin, their mapping to N.I.N.A.'s internal C# state, the SQLite database schemas for the Target Scheduler plugin (v4 and v5), and instructions on validating a local configuration.

---

## 1. ninaAPI Routing & C# Architecture

The `christian-photo/ninaAPI` plugin serves as a local RESTful HTTP and WebSocket server running inside the N.I.N.A. process. 

### C# Web Server Architecture (NancyFX / WebAPI)
The server leverages **NancyFX** (or a similar self-hosted .NET WebAPI listener), where route configurations are defined as C# modules inheriting from `NancyModule`. Under this pattern:
* **Base Routes**: Defined via constructor parameters (e.g., `base("/v2/api/equipment/...")`).
* **Route Handlers**: Registered using dictionary-like indexers (`Get["/route"] = _ => { ... }`) or module methods (`Get("/route", _ => { ... })`).
* **Autofac Dependency Injection**: N.I.N.A. uses Autofac as its inversion-of-control (IoC) container. The `ninaAPI` plugin resolves N.I.N.A.'s core application state and active devices by injecting N.I.N.A.'s internal managers (e.g., `IFilterWheel`, `IFocuser`, `IRotator`) into modules at runtime.
* **Request Binding**: Input query parameters are extracted from the Nancy `Request.Query` object or bound directly to C# models.
* **Standard Response Envelope**: All API endpoints return a standardized JSON structure:
  ```json
  {
    "Success": true,
    "Error": null,
    "StatusCode": 200,
    "Response": { ... },
    "Type": "TypeName"
  }
  ```

---

## 2. Detailed Equipment Profiles

For each placeholder category defined in [placeholders.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/placeholders.py), the endpoint routing, property mapping, and C# source implementations are detailed below.

### 2.1 Filter Wheel
* **C# Module Registration**:
  ```csharp
  public class FilterWheelModule : NancyModule {
      public FilterWheelModule() : base("/v2/api/equipment/filterwheel") {
          Get("/info", _ => GetFilterWheelInfo());
          Get("/change-filter", parameters => ChangeFilter(Request.Query["filter_id"]));
      }
  }
  ```
* **Property Retrieval (`/info` Endpoint)**:
  * **API Route**: `GET /v2/api/equipment/filterwheel/info`
  * **Response fields**:
    * `Connected` (boolean)
    * `Position` (integer filter index)
    * `Filters` (array of string names)
    * `Offset` (array of integer autofocus offsets)
  * **N.I.N.A. Internal Mapping**: Maps to `NINA.Core.Utility.IFilterWheel` resolved via Autofac. Reads `IFilterWheel.Connected`, `IFilterWheel.Position`, and `IFilterWheel.Filters`.
* **Action Command**:
  * **API Route**: `GET /v2/api/equipment/filterwheel/change-filter?filter_id={int}`
  * **N.I.N.A. Internal Mapping**: Calls `IFilterWheel.ChangeFilter(int position)`.

### 2.2 Focuser
* **C# Module Registration**:
  ```csharp
  public class FocuserModule : NancyModule {
      public FocuserModule() : base("/v2/api/equipment/focuser") {
          Get("/info", _ => GetFocuserInfo());
          Get("/move", parameters => MoveFocuser(Request.Query["position"]));
          Get("/stop-move", _ => StopFocuser());
          Get("/auto-focus", _ => TriggerAutoFocus());
      }
  }
  ```
* **Property Retrieval (`/info` Endpoint)**:
  * **API Route**: `GET /v2/api/equipment/focuser/info`
  * **Response fields**:
    * `Connected` (boolean)
    * `Position` (integer steps)
    * `Temperature` (double Celsius)
    * `IsMoving` (boolean)
    * `TempComp` (boolean temperature compensation status)
  * **N.I.N.A. Internal Mapping**: Maps to `NINA.Core.Utility.IFocuser`. Reads `IFocuser.Connected`, `IFocuser.Position`, `IFocuser.Temperature`, `IFocuser.IsMoving`, and `IFocuser.TempComp`.
* **Action Commands**:
  * **Move**: `GET /v2/api/equipment/focuser/move?position={int}` (calls `IFocuser.MoveTo(int position)`)
  * **Stop**: `GET /v2/api/equipment/focuser/stop-move` (calls `IFocuser.Stop()`)
  * **AutoFocus**: `GET /v2/api/equipment/focuser/auto-focus` (triggers N.I.N.A.'s Autofocus controller task)

### 2.3 Rotator
* **C# Module Registration**:
  ```csharp
  public class RotatorModule : NancyModule {
      public RotatorModule() : base("/v2/api/equipment/rotator") {
          Get("/info", _ => GetRotatorInfo());
          Get("/move", parameters => MoveRotator(Request.Query["angle"]));
          Get("/stop-move", _ => StopRotator());
      }
  }
  ```
* **Property Retrieval (`/info` Endpoint)**:
  * **API Route**: `GET /v2/api/equipment/rotator/info`
  * **Response fields**:
    * `Connected` (boolean)
    * `Position` (double sky angle in degrees)
    * `MechanicalPosition` (double mechanical angle in degrees)
    * `IsMoving` (boolean)
    * `Reverse` (boolean direction flag)
  * **N.I.N.A. Internal Mapping**: Maps to `NINA.Core.Utility.IRotator`. Reads `IRotator.Connected`, `IRotator.Position`, `IRotator.MechanicalPosition`, `IRotator.IsMoving`, and `IRotator.Reverse`.
* **Action Commands**:
  * **Move**: `GET /v2/api/equipment/rotator/move?angle={float}` (calls `IRotator.MoveTo(float angle)`)
  * **Stop**: `GET /v2/api/equipment/rotator/stop-move` (calls `IRotator.Stop()`)

### 2.4 Dome
* **C# Module Registration**:
  ```csharp
  public class DomeModule : NancyModule {
      public DomeModule() : base("/v2/api/equipment/dome") {
          Get("/info", _ => GetDomeInfo());
          Get("/open", _ => OpenDome());
          Get("/close", _ => CloseDome());
          Get("/slew", parameters => SlewDome(Request.Query["azimuth"]));
          Get("/set-follow", parameters => SetFollow(Request.Query["follow"]));
      }
  }
  ```
* **Property Retrieval (`/info` Endpoint)**:
  * **API Route**: `GET /v2/api/equipment/dome/info`
  * **Response fields**:
    * `Connected` (boolean)
    * `ShutterStatus` (string: `Open`, `Closed`, `Opening`, `Closing`, `Error`)
    * `Azimuth` (double degrees)
    * `IsSlewing` (boolean)
    * `IsParked` (boolean)
    * `FollowsMount` (boolean)
  * **N.I.N.A. Internal Mapping**: Maps to `NINA.Core.Utility.IDome`. Reads `IDome.Connected`, `IDome.ShutterStatus`, `IDome.Azimuth`, `IDome.IsSlewing`, `IDome.IsParked`, and `IDome.FollowsMount`.
* **Action Commands**:
  * **Open**: `GET /v2/api/equipment/dome/open` (calls `IDome.OpenShutter()`)
  * **Close**: `GET /v2/api/equipment/dome/close` (calls `IDome.CloseShutter()`)
  * **Slew**: `GET /v2/api/equipment/dome/slew?azimuth={float}` (calls `IDome.Slew(float azimuth)`)
  * **Set Follow**: `GET /v2/api/equipment/dome/set-follow?follow={bool}` (calls `IDome.SetFollow(bool follow)`)

### 2.5 Guider
* **C# Module Registration**:
  ```csharp
  public class GuiderModule : NancyModule {
      public GuiderModule() : base("/v2/api/equipment/guider") {
          Get("/info", _ => GetGuiderInfo());
          Get("/start", parameters => StartGuiding(Request.Query["calibrate"]));
          Get("/stop", _ => StopGuiding());
      }
  }
  ```
* **Property Retrieval (`/info` Endpoint)**:
  * **API Route**: `GET /v2/api/equipment/guider/info`
  * **Response fields**:
    * `Connected` (boolean)
    * `IsGuiding` (boolean)
    * `RmsError` (double pixels or arcseconds)
  * **N.I.N.A. Internal Mapping**: Maps to `NINA.Core.Utility.IGuider`. Reads `IGuider.Connected`, `IGuider.IsGuiding`, and `IGuider.RmsError`.
* **Action Commands**:
  * **Start**: `GET /v2/api/equipment/guider/start?calibrate={bool}` (calls `IGuider.StartGuiding(bool calibrate)`)
  * **Stop**: `GET /v2/api/equipment/guider/stop` (calls `IGuider.StopGuiding()`)

### 2.6 Switch
* **C# Module Registration**:
  ```csharp
  public class SwitchModule : NancyModule {
      public SwitchModule() : base("/v2/api/equipment/switch") {
          Get("/info", _ => GetSwitchInfo());
          Get("/set", parameters => SetSwitch(Request.Query["switch_index"], Request.Query["value"]));
      }
  }
  ```
* **Property Retrieval (`/info` Endpoint)**:
  * **API Route**: `GET /v2/api/equipment/switch/info`
  * **Response fields**:
    * `Connected` (boolean)
    * `Switches` (list of switch states, containing `Index`, `Name`, `Value`, `MaxVal`, `MinVal`)
  * **N.I.N.A. Internal Mapping**: Maps to `NINA.Core.Utility.ISwitch`. Loops through all registered sub-switches on `ISwitch` to read properties.
* **Action Command**:
  * **Set**: `GET /v2/api/equipment/switch/set?switch_index={int}&value={float}` (calls `ISwitch.SetSwitch(int index, double value)`)

### 2.7 Flat Device
* **C# Module Registration**:
  ```csharp
  public class FlatDeviceModule : NancyModule {
      public FlatDeviceModule() : base("/v2/api/equipment/flatdevice") {
          Get("/info", _ => GetFlatDeviceInfo());
          Get("/set-light", parameters => SetLight(Request.Query["on"]));
          Get("/set-brightness", parameters => SetBrightness(Request.Query["brightness"]));
          Get("/set-cover", parameters => SetCover(Request.Query["open"]));
      }
  }
  ```
* **Property Retrieval (`/info` Endpoint)**:
  * **API Route**: `GET /v2/api/equipment/flatdevice/info`
  * **Response fields**:
    * `Connected` (boolean)
    * `LightEnabled` (boolean)
    * `Brightness` (integer)
    * `CoverStatus` (string: `Open`, `Closed`, `Opening`, `Closing`, `Error`)
  * **N.I.N.A. Internal Mapping**: Maps to `NINA.Core.Utility.IFlatDevice`. Reads `IFlatDevice.Connected`, `IFlatDevice.LightEnabled`, `IFlatDevice.Brightness`, and `IFlatDevice.CoverStatus`.
* **Action Commands**:
  * **Set Light**: `GET /v2/api/equipment/flatdevice/set-light?on={bool}` (calls `IFlatDevice.SetLight(bool on)`)
  * **Set Brightness**: `GET /v2/api/equipment/flatdevice/set-brightness?brightness={int}` (calls `IFlatDevice.SetBrightness(int brightness)`)
  * **Set Cover**: `GET /v2/api/equipment/flatdevice/set-cover?open={bool}` (calls `IFlatDevice.SetCover(bool open)`)

---

## 3. Target Scheduler Database Schema (v4 vs v5)

Target Scheduler stores configuration and imaging targets directly in a SQLite database located locally at `%LOCALAPPDATA%\NINA\SchedulerPlugin\schedulerdb.sqlite`.

> [!IMPORTANT]
> The database schema structure differs substantially between Target Scheduler **v4** and **v5**. Direct SQL modifications must be built dynamically or version-checked to prevent database corruption.

### Table Naming Migration
The primary structural difference is the transition from **singular** table names in v4 to **plural** table names in v5:

| Entity Type | TS v4 Table Name | TS v5 Table Name |
| :--- | :--- | :--- |
| **Project** | `Project` | `Projects` |
| **Target** | `Target` | `Targets` |
| **Exposure Plan** | `ExposurePlan` | `ExposurePlans` |

### Detailed Column Specifications (TS v5 Layout)

#### 1. Projects Table (`Projects`)
Stores overall project parameters and priority rankings.
* `Id` (INTEGER, Primary Key): Unique project identifier.
* `Name` (TEXT, NOT NULL): The user-facing project name.
* `Priority` (REAL, NOT NULL): Floating point prioritization weighting (lower numbers typically denote higher priority).
* `Category` (TEXT): Classification tag (e.g., "Nebula", "Galaxy", "Mosaic").
* `Notes` (TEXT): User-supplied textual annotations.

#### 2. Targets Table (`Targets`)
Stores coordinates, rotation requirements, and altitude rules.
* `Id` (INTEGER, Primary Key): Unique target identifier.
* `ProjectId` (INTEGER, Foreign Key referencing `Projects.Id`): Associates target with its parent project.
* `Name` (TEXT, NOT NULL): Celestial object name (e.g., "M31").
* `RA` (REAL, NOT NULL): Right Ascension coordinate (stored as double-precision degrees or hours).
* `DEC` (REAL, NOT NULL): Declination coordinate (stored as double-precision degrees).
* `Rotation` (REAL): Target mechanical/sky rotator angle in degrees.
* `Priority` (REAL): Target-specific priority override value.
* `MinAltitude` (REAL): Minimum elevation angle for active imaging.
* `MaxAltitude` (REAL): Maximum elevation angle threshold.
* `MoonAvoidance` (INTEGER): Flag or angular distance threshold (in degrees) for avoiding moon illumination.
* `RunState` / `State` (INTEGER): Tracks targets through states:
  * `0` = Idle (not started)
  * `1` = Active (ready for imaging)
  * `2` = Completed
  * `3` = Paused/Disabled

#### 3. Exposure Plans Table (`ExposurePlans`)
Specifies exposure constraints per filter for a target.
* `Id` (INTEGER, Primary Key): Unique plan row identifier.
* `TargetId` (INTEGER, Foreign Key referencing `Targets.Id`): Associates plan with a specific target.
* `Filter` (TEXT, NOT NULL): Filter name (e.g., "Ha", "OIII", "Luminance").
* `Exposure` (REAL, NOT NULL): Sub-exposure length in seconds.
* `Count` (INTEGER, NOT NULL): Total target count of subs requested.
* `Acquired` (INTEGER, NOT NULL): Total number of subs successfully completed and saved.
* `Binning` (INTEGER): Camera binning mode (e.g. `1`, `2`).
* `Gain` (INTEGER): Camera gain setting.
* `Offset` (INTEGER): Camera offset setting.

> [!NOTE]
> The database interface in [ts_db.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/ts_db.py) uses generic runtime table inspection. Instead of hardcoding v4 or v5 table strings, it dynamically queries `sqlite_master` and validates query constraints against dynamic PRAGMA metadata before executing updates.

---

## 4. Local Database Schema Introspection

To verify the specific schema in use on your local setup, run the schema verification script located in the scratch directory.

### Verification Script Location
The script is located at:
* [verify_schema.py](file:///C:/Users/soyko/.gemini/antigravity-cli/brain/f315cd6d-6c62-43a4-b979-e821004c8ab6/scratch/verify_schema.py)

### How to Run the Verification Script

1. **Open a terminal (e.g. PowerShell or cmd)**.
2. **Execute the script** using python:
   * **Default Location**:
     ```bash
     python C:\Users\soyko\.gemini\antigravity-cli\brain\f315cd6d-6c62-43a4-b979-e821004c8ab6\scratch\verify_schema.py
     ```
   * **Custom Database Path**:
     Pass the specific path of your SQLite database file as an argument:
     ```bash
     python C:\Users\soyko\.gemini\antigravity-cli\brain\f315cd6d-6c62-43a4-b979-e821004c8ab6\scratch\verify_schema.py "C:\Users\soyko\Documents\backup_schedulerdb.sqlite"
     ```

3. **Analyze Output**:
   The script outputs the detected schema version (v4 vs v5) and details all column names, types, and primary keys found in your database.

---

## 5. Congruent Layered Domain Model

To build a professional, industrial-grade MCP control surface, all server capabilities are organized into a strict **4-Tier Congruent Layered Domain**:

```
+-----------------------------------------------------------------------+
|  Tier 4: Orchestration & AI Planning (LLM scheduling, multi-data)     |
+-----------------------------------------------------------------------+
|  Tier 3: Safety & Coordination (Weather daemons, horizon, meridian)    |
+-----------------------------------------------------------------------+
|  Tier 2: Measurement & Analysis (FWHM/eccentricity, TPA, Bahtinov)    |
+-----------------------------------------------------------------------+
|  Tier 1: Device REST Wrapper (Direct HTTP calls, SQLite binding)     |
+-----------------------------------------------------------------------+
```

### Tier 1: Device REST & DB Wrapper
* Exposes direct API routes and database reads/writes.
* Maps primitives, handles C# enum conversions, and parses JSON envelopes.
* *Components*: [camera.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/camera.py), [mount.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/mount.py), [ts_db.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/ts_db.py).

### Tier 2: Advanced Analysis & Measurement
* Combines sensor readings with local calculations and external algorithms.
* Provides metrics on alignment quality, focus sharpness, and image quality.
* *Features*: Three-Star Polar Alignment tracking, Bahtinov mask diffraction calculators, FWHM/eccentricity star metrics.

### Tier 3: Safety & Coordination
* Implements background daemons evaluating local telemetry to protect telescope hardware.
* Enforces horizon limits, weather safety halts, and meridian flip coordination.

### Tier 4: Orchestration & AI Planning
* Aggregates multiple astronomical and weather sources.
* Feeds resolved transit plans, object parameters, and cloud coverage maps into the LLM scheduling system.

---

## 6. Advanced Feature Research Specifications

### 6.1 Three-Star Polar Alignment (TPA) API Research
* **Goal**: Automate polar alignment without requiring the N.I.N.A. UI.
* **Endpoints to Verify**: 
  * `GET /plugin/tpa/start`: Starts the alignment wizard.
  * `GET /plugin/tpa/status`: Returns current state (`Idle`, `Slewing`, `Solving`, `AwaitingAdjustment`), error in azimuth (arcminutes), and error in altitude (arcminutes).
  * `GET /plugin/tpa/stop`: Aborts the wizard.
* **C# Mapping**: Inspect the `NINA.Plugins.PolarAlignment` namespace to confirm Nancy routes.

### 6.2 Bahtinov Focus Diffraction Analysis
* **Goal**: Measure focusing accuracy using diffraction spike analysis.
* **Concept**: When a Bahtinov mask is placed over the optics, the central diffraction spike shifts based on focus error.
* **API / Logic Mapping**:
  * Extract pixel positions of diffraction spikes from preview images.
  * Suggest step corrections based on the displacement of the central spike relative to the lateral X-spikes.

### 6.3 Image Quality Evaluation
* **Goal**: Assess and score captured frames based on astronomical quality indicators.
* **Metrics**:
  * **HFR (Half Flux Radius)**: Indicates focus/seeing drift.
  * **FWHM (Full Width at Half Maximum)**: Measures stellar resolution in pixels.
  * **Eccentricity**: Detects star elongation (guiding errors, wind shake, sensor tilt). Target eccentricity is `< 0.42` (perfect circles).
  * **Aspect Ratio**: Measures aspect ratio of star profiles.
* **Endpoints**: `/equipment/camera/capture/statistics` and `/imagehistory` to retrieve historical trends.

### 6.4 Fully LLM-Assisted Target Scheduling
* **Goal**: Plan a target sequence by synthesizing weather, coordinate databases, and orbital geometry.
* **Integrated Data Sources**:
  1. **Weather Forecasts**: Cloud, humidity, and seeing models from APIs like Clear Outside or OpenWeather.
  2. **Astronomical Coordinates**: Simbad/NED database lookup to resolve target coordinates.
  3. **Moon Separation**: Orbit calculators to determine the target's angular distance from the moon.
  4. **Local Obstructions**: Horizon profile files (`.horizon`) containing Az/Alt coordinates of local trees or buildings.

