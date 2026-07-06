"""Thin async HTTP client for the ninaAPI ("Advanced API") plugin.

Every ninaAPI endpoint returns a consistent JSON envelope:

    {
        "Response": <the actual payload, any shape>,
        "Error": "<message, empty on success>",
        "StatusCode": 200,
        "Success": true,
        "Type": "API" | "Socket"
    }

This wraps that so callers just get `Response` back, or a NinaAPIError.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .config import settings


class NinaAPIError(Exception):
    """Raised for any failure talking to NINA: unreachable host, a device
    that isn't connected, an invalid parameter, etc. `status_code` mirrors
    NINA's own reported status where available."""

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message)


class NinaClient:
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or settings.base_url).rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout or settings.request_timeout_seconds)

    async def aclose(self) -> None:
        await self._client.aclose()

    @staticmethod
    def _clean(params: dict) -> dict:
        """Drop None values so we don't send e.g. `?rotate=None` -- ninaAPI's
        [QueryField] parameters are omitted entirely rather than nulled."""
        return {k: v for k, v in params.items() if v is not None}

    async def get(self, path: str, **params: Any) -> Any:
        url = f"{self.base_url}{path}"
        query = self._clean(params)
        try:
            resp = await self._client.get(url, params=query)
        except httpx.RequestError as e:
            raise NinaAPIError(
                f"Could not reach NINA's Advanced API at {url}. Is NINA running "
                f"with the Advanced API plugin enabled, and the host/port correct? "
                f"({e})"
            ) from e
        return self._unwrap(resp)

    async def post_raw_body(self, path: str, body: str, **params: Any) -> Any:
        """For the one endpoint (`POST /sequence/load`) that takes a raw JSON
        string body (a serialized NINA sequence) rather than query params."""
        url = f"{self.base_url}{path}"
        query = self._clean(params)
        try:
            resp = await self._client.post(
                url, params=query, content=body, headers={"Content-Type": "application/json"}
            )
        except httpx.RequestError as e:
            raise NinaAPIError(f"Could not reach NINA's Advanced API at {url}: {e}") from e
        return self._unwrap(resp)

    @staticmethod
    def _unwrap(resp: httpx.Response) -> Any:
        try:
            data = resp.json()
        except ValueError:
            raise NinaAPIError(
                f"NINA returned a non-JSON response (HTTP {resp.status_code}): "
                f"{resp.text[:300]!r}",
                resp.status_code,
            )
        if not data.get("Success", False):
            raise NinaAPIError(
                data.get("Error") or "NINA reported failure with no error message",
                data.get("StatusCode", resp.status_code),
            )
        return data.get("Response")


# Module-level singleton, reused across all tool calls in this process.
client = NinaClient()
