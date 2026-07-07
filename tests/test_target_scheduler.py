import sqlite3
import pytest
from nina_mcp import ts_db
from nina_mcp.config import Settings

# ==============================================================================
# Database Mocking with SQLite Temp Databases
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
    conn.execute("""
        CREATE TABLE Targets (
            Id INTEGER PRIMARY KEY,
            ProjectId INTEGER,
            Name TEXT,
            Active INTEGER
        )
    """)
    conn.execute("INSERT INTO Projects (Id, Name, Priority, Active) VALUES (101, 'M31 Andromeda', 1, 1)")
    conn.execute("INSERT INTO Targets (Id, ProjectId, Name, Active) VALUES (201, 101, 'M31 Center', 1)")
    conn.commit()
    conn.close()
    return db_file


@pytest.mark.asyncio
async def test_ts_update_cell_success(temp_scheduler_db, monkeypatch):
    # Create new settings pointing to the temp database with writes enabled
    new_settings = Settings(ts_db_path=str(temp_scheduler_db), ts_allow_writes=True)
    monkeypatch.setattr("nina_mcp.ts_db.settings", new_settings)
    
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


@pytest.mark.asyncio
async def test_ts_set_project_priority_success(temp_scheduler_db, monkeypatch):
    new_settings = Settings(ts_db_path=str(temp_scheduler_db), ts_allow_writes=True)
    monkeypatch.setattr("nina_mcp.ts_db.settings", new_settings)
    
    from nina_mcp.tools.target_scheduler import ts_set_project_priority
    result = await ts_set_project_priority(project_id=101, priority=3)
    assert result["rows_affected"] == 1
    
    rows = ts_db.read_table("Projects", where_column="Id", where_value=101)
    assert rows[0]["Priority"] == 3


@pytest.mark.asyncio
async def test_ts_toggle_target_enabled_success(temp_scheduler_db, monkeypatch):
    new_settings = Settings(ts_db_path=str(temp_scheduler_db), ts_allow_writes=True)
    monkeypatch.setattr("nina_mcp.ts_db.settings", new_settings)
    
    from nina_mcp.tools.target_scheduler import ts_toggle_target_enabled
    result = await ts_toggle_target_enabled(target_id=201, enabled=False)
    assert result["rows_affected"] == 1
    
    rows = ts_db.read_table("Targets", where_column="Id", where_value=201)
    assert rows[0]["Active"] == 0
