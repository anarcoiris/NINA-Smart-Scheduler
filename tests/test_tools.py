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
