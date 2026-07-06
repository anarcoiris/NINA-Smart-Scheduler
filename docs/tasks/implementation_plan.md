# Implementation Plan: Tasks and Milestones

This document details the tasks and roadmap required to build out the placeholder tools and database helpers for [nina-mcp](file:///C:/Users/soyko/Documents/nina-mcp).

---

## Phase 1: Research, Environment Setup, and Verification

* [ ] **Task 1.1: Clone and Inspect Upstream Source**
  * Clone the [christian-photo/ninaAPI](https://github.com/christian-photo/ninaAPI) repository.
  * Inspect the source code files located under `WebService/V2/Equipment/` to verify parameters, return types, and routes for action placeholders.
  * Confirm parameter details in:
    * `FilterWheel.cs` for the `/equipment/filterwheel/change-filter` endpoint.
    * `Focuser.cs` for the `/equipment/focuser/move` and `/equipment/focuser/stop-move` endpoints.
    * `Rotator.cs` for the `/equipment/rotator/move` and `/equipment/rotator/stop-move` endpoints.
    * `Dome.cs` for the `/equipment/dome/open`, `/equipment/dome/close`, and `/equipment/dome/slew` endpoints.
    * `Guider.cs` for the `/equipment/guider/start` and `/equipment/guider/stop` endpoints.
    * `Switch.cs` for the `/equipment/switch/set` endpoint.
    * `FlatDevice.cs` for the `/equipment/flatdevice/set-light` endpoint.

* [ ] **Task 1.2: Introspect Target Scheduler Schema**
  * Create a scratch script `scratch/schema_inspect.py` using connection helpers in [ts_db.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/ts_db.py).
  * Run the script on a live or test instance of `schedulerdb.sqlite` to dump tables, columns, constraints, and data types.
  * Document structural differences between Target Scheduler v4 and v5 databases (specifically table names like `Project`/`Projects`, `Target`/`Targets`, and column names representing priority or activation status).

* [ ] **Task 1.3: Verify Environment Setup**
  * Confirm that project configuration loaded from [config.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/config.py) functions as expected.
  * Verify that environment settings like `NINA_HOST`, `NINA_PORT`, `TS_DB_PATH`, and `TS_ALLOW_WRITES` are correctly picked up.
  * Install development dependencies (including `pytest` and `pytest-asyncio` for executing mock tests).

---

## Phase 2: Refactoring Placeholders into Dedicated Modules

* [ ] **Task 2.1: Refactor Filter Wheel & Focuser Tools**
  * Create the module [filterwheel.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/filterwheel.py) by moving logic from [placeholders.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/placeholders.py).
  * Implement the active tool:
    * `nina_filterwheel_change_filter(filter_id: int)`: Calls `GET /equipment/filterwheel/change-filter` with the specified filter ID.
  * Create the module [focuser.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/focuser.py).
  * Implement the active tools:
    * `nina_focuser_move(position: int)`: Calls `GET /equipment/focuser/move` to drive the focuser to an absolute position.
    * `nina_focuser_stop()`: Calls `GET /equipment/focuser/stop-move` to cancel any ongoing movement.

* [ ] **Task 2.2: Refactor Rotator & Dome Tools**
  * Create the module [rotator.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/rotator.py).
  * Implement the active tools:
    * `nina_rotator_move(angle: float)`: Calls `GET /equipment/rotator/move` to slew the rotator to a sky angle.
    * `nina_rotator_stop()`: Calls `GET /equipment/rotator/stop-move` to cancel rotation.
  * Create the module [dome.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/dome.py).
  * Implement the active tools:
    * `nina_dome_open()`: Calls `GET /equipment/dome/open` to open the shutter.
    * `nina_dome_close()`: Calls `GET /equipment/dome/close` to close the shutter.
    * `nina_dome_slew(azimuth: float)`: Calls `GET /equipment/dome/slew` to align the dome to a target azimuth.

* [ ] **Task 2.3: Refactor Switch & Flat Device Actions**
  * Create the module [switch.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/switch.py).
  * Implement the active tool:
    * `nina_switch_set(switch_index: int, value: float)`: Calls `GET /equipment/switch/set` to modify relay state or value.
  * Create the module [flatdevice.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/flatdevice.py).
  * Implement the active tool:
    * `nina_flatdevice_set_light(on: bool)`: Calls `GET /equipment/flatdevice/set-light` to turn the panel light on or off.
  * Create the module [guider.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/guider.py).
  * Implement the active tools:
    * `nina_guider_start(calibrate: bool)`: Calls `GET /equipment/guider/start`.
    * `nina_guider_stop()`: Calls `GET /equipment/guider/stop`.

* [ ] **Task 2.4: Module Registration & Placeholder Cleanup**
  * Register the newly created files (e.g. `filterwheel`, `focuser`, `rotator`, `dome`, `switch`, `flatdevice`, `guider`) in [server.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/server.py).
  * Remove the placeholder code block registrations in [placeholders.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/placeholders.py) once their active endpoints have been moved to dedicated modules.

---

## Phase 3: Safe, Typed Database Writes for Target Scheduler

* [ ] **Task 3.1: Confirm Safe DB Write Enforcement**
  * Ensure that write requests use parameterized inputs and check the state of settings in [config.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/config.py) to prevent writing when `TS_ALLOW_WRITES` is `False`.
  * Ensure that the core database helper [update_cell](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/ts_db.py#L117) strictly limits edits to single rows and single columns.

* [ ] **Task 3.2: Implement Typed DB Actions**
  * Expose high-level wrappers inside [target_scheduler.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/tools/target_scheduler.py):
    * `ts_set_project_priority(project_id: int, priority: int)`: Bumps or decreases priority inside the `Projects` table.
    * `ts_set_project_enabled(project_id: int, enabled: bool)`: Toggles active status inside the `Projects` table.
    * `ts_set_target_enabled(target_id: int, enabled: bool)`: Toggles active status inside the `Targets` table.
  * Adapt naming conventions depending on whether TS4 or TS5 schemas are active.

---

## Phase 4: Setting Up Test Suites

* [ ] **Task 4.1: Test Suite Structuring**
  * Create a `tests/` directory at the project root.
  * Add `tests/test_tools.py` for validating API endpoints.
  * Add `tests/test_target_scheduler.py` for database tools.

* [ ] **Task 4.2: Implement HTTP Layer Mocking**
  * Use `httpx.MockTransport` inside testing scripts to intercept requests from [nina_client.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/nina_client.py) and return appropriate success/error JSON response envelopes.

* [ ] **Task 4.3: Implement Database Layer Mocking**
  * Configure testing fixtures to generate a temporary SQLite database using python's `tmp_path` fixture.
  * Set up schemas for `Projects` and `Targets` on the temporary database.
  * Patch settings in [config.py](file:///C:/Users/soyko/Documents/nina-mcp/src/nina_mcp/config.py) to point `TS_DB_PATH` to the temporary file for the duration of the test.

* [ ] **Task 4.4: Mock Test Code Sample**
  * Implement test fixtures and assertions following this pattern:

```python
import sqlite3
import httpx
import pytest
from unittest.mock import patch
from nina_mcp.nina_client import NinaClient, NinaAPIError
from nina_mcp import ts_db

# ==============================================================================
# 1. API Mocking with httpx.MockTransport
# ==============================================================================

@pytest.mark.asyncio
async def test_filterwheel_change_filter_success():
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/api/equipment/filterwheel/change-filter"
        assert request.url.params.get("filter") == "2"
        return httpx.Response(
            status_code=200,
            json={
                "Response": {"message": "Filter changed successfully"},
                "Error": "",
                "StatusCode": 200,
                "Success": True,
                "Type": "API"
            }
        )

    transport = httpx.MockTransport(handle_request)
    mock_client = NinaClient(base_url="http://127.0.0.1:1888/v2/api")
    mock_client._client = httpx.AsyncClient(transport=transport)
    
    with patch("nina_mcp.tools.filterwheel.client", mock_client):
        from nina_mcp.tools.filterwheel import nina_filterwheel_change_filter
        res = await nina_filterwheel_change_filter(filter_id=2)
        assert res["message"] == "Filter changed successfully"


@pytest.mark.asyncio
async def test_filterwheel_change_filter_failure():
    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=400,
            json={
                "Response": None,
                "Error": "Filter wheel disconnected",
                "StatusCode": 400,
                "Success": False,
                "Type": "API"
            }
        )

    transport = httpx.MockTransport(handle_request)
    mock_client = NinaClient(base_url="http://127.0.0.1:1888/v2/api")
    mock_client._client = httpx.AsyncClient(transport=transport)
    
    with patch("nina_mcp.tools.filterwheel.client", mock_client):
        from nina_mcp.tools.filterwheel import nina_filterwheel_change_filter
        with pytest.raises(NinaAPIError) as exc_info:
            await nina_filterwheel_change_filter(filter_id=9)
        assert "Filter wheel disconnected" in str(exc_info.value)
        assert exc_info.value.status_code == 400


# ==============================================================================
# 2. Database Mocking with SQLite Temp Databases
# ==============================================================================

@pytest.fixture
def temp_scheduler_db(tmp_path):
    db_file = tmp_path / "schedulerdb.sqlite"
    conn = sqlite3.connect(db_file)
    # Replicate NINA Target Scheduler database structures
    conn.execute("""
        CREATE TABLE Projects (
            Id INTEGER PRIMARY KEY,
            Name TEXT,
            Priority INTEGER,
            Active INTEGER
        )
    """)
    conn.execute("INSERT INTO Projects (Id, Name, Priority, Active) VALUES (101, 'M31 Andromeda', 1, 1)")
    conn.commit()
    conn.close()
    return db_file


@pytest.mark.asyncio
async def test_ts_update_cell_success(temp_scheduler_db, monkeypatch):
    # Dynamically direct client configuration to point to our temp database
    monkeypatch.setattr("nina_mcp.config.settings.ts_db_path", str(temp_scheduler_db))
    monkeypatch.setattr("nina_mcp.config.settings.ts_allow_writes", True)
    
    from nina_mcp.tools.target_scheduler import ts_update_cell
    result = await ts_update_cell(
        table="Projects",
        id_column="Id",
        id_value=101,
        column="Priority",
        value=5
    )
    assert result["rows_affected"] == 1
    
    # Read back values to verify correctness
    rows = ts_db.read_table("Projects", where_column="Id", where_value=101)
    assert rows[0]["Priority"] == 5
```

---

## Phase 5: Verification, Registration, and Final Documentation

* [ ] **Task 5.1: Local Testing Verification**
  * Execute pytest suite locally: `pytest tests/` to confirm that all test assertions verify success and failure paths.
  * Start up the server locally via stdio or run `mcp dev src/nina_mcp/server.py` to check MCP tool compilation.
  * Run [test_client.py](file:///C:/Users/soyko/Documents/nina-mcp/test_client.py) to list all active tools and verify signatures match the API configuration.

* [ ] **Task 5.2: Documentation Verification & Updates**
  * Ensure all 58+ active tools are listed correctly in [INDEX.md](file:///C:/Users/soyko/Documents/nina-mcp/INDEX.md) and [README.md](file:///C:/Users/soyko/Documents/nina-mcp/README.md).
  * Confirm that invariants described in [CONTRIBUTING.md](file:///C:/Users/soyko/Documents/nina-mcp/CONTRIBUTING.md) are strictly preserved.

