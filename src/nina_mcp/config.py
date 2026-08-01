"""Configuration for the NINA MCP server, loaded from environment variables
(or a .env file, if python-dotenv is installed and load_dotenv() picks one up).

All settings have sane defaults for a single-PC amateur astrophotography rig
where NINA and this MCP server run on the same Windows machine.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    # --- ninaAPI (Advanced API plugin) connection ---
    nina_host: str = os.environ.get("NINA_HOST", "127.0.0.1")
    nina_port: int = int(os.environ.get("NINA_PORT", "1888"))
    # Fixed by the plugin itself (v2/api). Kept configurable in case a future
    # major version ships alongside v2, per the plugin's own versioning scheme.
    nina_api_base_path: str = os.environ.get("NINA_API_BASE_PATH", "/v2/api")
    request_timeout_seconds: float = float(os.environ.get("NINA_TIMEOUT", "30"))
    # Direct full base URL override (e.g. NINA_BASE_URL="https://my-rig.ddns.net/v2/api" or via Caddy reverse proxy)
    nina_base_url_override: str = os.environ.get("NINA_BASE_URL", "").strip()

    # --- Target Scheduler plugin (tcpalmer) ---
    # ninaAPI does not expose REST endpoints for Target Scheduler's project /
    # target / exposure-plan data -- it only forwards a couple of read-only
    # status events. Real "control" of TS happens through its SQLite database.
    # Default path matches the documented Windows location. Point this at a
    # UNC/network path if this server doesn't run on the NINA PC itself.
    ts_db_path: str = os.environ.get(
        "TS_DB_PATH",
        os.path.expandvars(r"%LOCALAPPDATA%\NINA\SchedulerPlugin\schedulerdb.sqlite"),
    )
    # Off by default: reading is always allowed, but writing to a user's
    # scheduling database is destructive if something goes wrong. Flip this on
    # deliberately once you trust the tool.
    ts_allow_writes: bool = _bool("TS_ALLOW_WRITES", False)

    @property
    def base_url(self) -> str:
        if self.nina_base_url_override:
            return self.nina_base_url_override.rstrip("/")
        return f"http://{self.nina_host}:{self.nina_port}{self.nina_api_base_path}"


settings = Settings()

