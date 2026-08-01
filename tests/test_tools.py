import httpx
import pytest
from unittest.mock import patch
from nina_mcp.nina_client import NinaClient, NinaAPIError

# ==============================================================================
# API Mocking with httpx.MockTransport
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


@pytest.mark.asyncio
async def test_focuser_move_success():
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/api/equipment/focuser/move"
        assert request.url.params.get("position") == "1500"
        return httpx.Response(
            status_code=200,
            json={
                "Response": {"message": "Focuser moved"},
                "Error": "",
                "StatusCode": 200,
                "Success": True,
                "Type": "API"
            }
        )

    transport = httpx.MockTransport(handle_request)
    mock_client = NinaClient(base_url="http://127.0.0.1:1888/v2/api")
    mock_client._client = httpx.AsyncClient(transport=transport)
    
    with patch("nina_mcp.tools.focuser.client", mock_client):
        from nina_mcp.tools.focuser import nina_focuser_move
        res = await nina_focuser_move(position=1500)
        assert res["message"] == "Focuser moved"


@pytest.mark.asyncio
async def test_system_status_aggregated():
    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "Response": {"Connected": True, "Name": "Mock Device"},
                "Error": "",
                "StatusCode": 200,
                "Success": True,
                "Type": "API"
            }
        )

    transport = httpx.MockTransport(handle_request)
    mock_client = NinaClient(base_url="https://astrorig.ddns.net/v2/api")
    mock_client._client = httpx.AsyncClient(transport=transport)

    with patch("nina_mcp.tools.system_status.client", mock_client):
        from nina_mcp.tools.system_status import nina_get_system_status
        status = await nina_get_system_status()
        assert status["api_endpoint"] == "https://astrorig.ddns.net/v2/api"
        assert "devices" in status
        assert status["devices"]["camera"]["Connected"] is True


@pytest.mark.asyncio
async def test_launcher_already_running():
    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"Response": [], "Error": "", "StatusCode": 200, "Success": True, "Type": "API"}
        )

    transport = httpx.MockTransport(handle_request)
    mock_client = NinaClient(base_url="http://127.0.0.1:1888/v2/api")
    mock_client._client = httpx.AsyncClient(transport=transport)

    with patch("nina_mcp.tools.launcher.client", mock_client):
        from nina_mcp.tools.launcher import nina_ensure_running
        res = await nina_ensure_running()
        assert res["status"] == "running"
        assert res["api_ready"] is True


@pytest.mark.asyncio
async def test_create_calibration_sequence():
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/api/sequence/load"
        return httpx.Response(
            status_code=200,
            json={"Response": {"status": "success"}, "Error": "", "StatusCode": 200, "Success": True, "Type": "API"}
        )

    transport = httpx.MockTransport(handle_request)
    mock_client = NinaClient(base_url="http://127.0.0.1:1888/v2/api")
    mock_client._client = httpx.AsyncClient(transport=transport)

    with patch("nina_mcp.tools.sequence_templates.client", mock_client):
        from nina_mcp.tools.sequence_templates import nina_create_calibration_sequence
        res = await nina_create_calibration_sequence(image_type="DARK", count=10, exposure_time=30.0)
        assert res["status"] == "loaded"
        assert res["image_type"] == "DARK"
        assert res["count"] == 10



