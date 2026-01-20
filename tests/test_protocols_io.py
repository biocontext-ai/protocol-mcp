"""Integration tests for protocols.io MCP tools."""

import httpx
import pytest
from fastmcp import Client
from pytest_httpx import HTTPXMock
from tests.fixtures.protocols_io_responses import (
    EMPTY_SEARCH_RESPONSE,
    PROTOCOL_DETAIL_RESPONSE,
    PROTOCOL_MATERIALS_RESPONSE,
    PROTOCOL_STEPS_RESPONSE,
    SEARCH_RESPONSE,
)

import protocol_mcp


@pytest.mark.asyncio
async def test_search_protocols_returns_formatted_results(httpx_mock: HTTPXMock):
    """Test that search returns properly formatted results."""
    httpx_mock.add_response(
        url="https://www.protocols.io/api/v3/protocols?key=RNA&page_size=10&page_id=1&filter=public&order_field=date&order_dir=desc",
        json=SEARCH_RESPONSE,
    )

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("search_protocols", {"query": "RNA"})

    # Verify data from fixture appears in formatted output
    first_protocol = SEARCH_RESPONSE["items"][0]
    assert first_protocol["title"] in result.data
    assert first_protocol["uri"] in result.data
    assert first_protocol["doi"] in result.data
    assert first_protocol["creator"]["name"] in result.data
    assert str(SEARCH_RESPONSE["pagination"]["total_results"]) in result.data


@pytest.mark.asyncio
async def test_search_protocols_handles_empty_results(httpx_mock: HTTPXMock):
    """Test that search handles no results gracefully."""
    httpx_mock.add_response(
        url="https://www.protocols.io/api/v3/protocols?key=nonexistent_xyz_query&page_size=10&page_id=1&filter=public&order_field=date&order_dir=desc",
        json=EMPTY_SEARCH_RESPONSE,
    )

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("search_protocols", {"query": "nonexistent_xyz_query"})

    assert "No protocols found" in result.data


@pytest.mark.asyncio
async def test_search_protocols_with_peer_reviewed_filter(httpx_mock: HTTPXMock):
    """Test that peer_reviewed_only filter is applied."""
    httpx_mock.add_response(
        url="https://www.protocols.io/api/v3/protocols?key=RNA&page_size=10&page_id=1&filter=peer_reviewed&order_field=date&order_dir=desc",
        json=SEARCH_RESPONSE,
    )

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("search_protocols", {"query": "RNA", "peer_reviewed_only": True})

    assert "RNA Extraction" in result.data


@pytest.mark.asyncio
async def test_get_protocol_returns_full_details(httpx_mock: HTTPXMock):
    """Test that get_protocol returns full protocol with steps and materials."""
    protocol_id = "rna-extraction-from-tissue-samples-abc123"

    httpx_mock.add_response(
        url=f"https://www.protocols.io/api/v4/protocols/{protocol_id}?content_format=md",
        json=PROTOCOL_DETAIL_RESPONSE,
    )
    httpx_mock.add_response(
        url=f"https://www.protocols.io/api/v4/protocols/{protocol_id}/steps?content_format=md",
        json=PROTOCOL_STEPS_RESPONSE,
    )
    httpx_mock.add_response(
        url=f"https://www.protocols.io/api/v4/protocols/{protocol_id}/materials",
        json=PROTOCOL_MATERIALS_RESPONSE,
    )

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("get_protocol", {"protocol_id": protocol_id})

    # Check metadata
    assert "RNA Extraction from Tissue Samples" in result.data
    assert "10.17504/protocols.io.abc123" in result.data
    assert "Jane Doe" in result.data

    # Check description and warnings
    assert "high-quality RNA" in result.data
    assert "TRIzol is toxic" in result.data

    # Check materials
    assert "TRIzol Reagent" in result.data
    assert "Thermo Fisher" in result.data
    assert "Chloroform" in result.data

    # Check steps
    assert "Sample Preparation" in result.data
    assert "Phase Separation" in result.data
    assert "Homogenize" in result.data


@pytest.mark.asyncio
async def test_get_protocol_without_steps(httpx_mock: HTTPXMock):
    """Test that get_protocol respects include_steps=False."""
    protocol_id = "rna-extraction-from-tissue-samples-abc123"

    httpx_mock.add_response(
        url=f"https://www.protocols.io/api/v4/protocols/{protocol_id}?content_format=md",
        json=PROTOCOL_DETAIL_RESPONSE,
    )
    httpx_mock.add_response(
        url=f"https://www.protocols.io/api/v4/protocols/{protocol_id}/materials",
        json=PROTOCOL_MATERIALS_RESPONSE,
    )

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("get_protocol", {"protocol_id": protocol_id, "include_steps": False})

    # Should have title and materials
    assert "RNA Extraction from Tissue Samples" in result.data
    assert "TRIzol Reagent" in result.data

    # Should not have detailed step content (step titles may appear in description)
    assert "Homogenize 50-100 mg" not in result.data


@pytest.mark.asyncio
async def test_get_protocol_without_materials(httpx_mock: HTTPXMock):
    """Test that get_protocol respects include_materials=False."""
    protocol_id = "rna-extraction-from-tissue-samples-abc123"

    httpx_mock.add_response(
        url=f"https://www.protocols.io/api/v4/protocols/{protocol_id}?content_format=md",
        json=PROTOCOL_DETAIL_RESPONSE,
    )
    httpx_mock.add_response(
        url=f"https://www.protocols.io/api/v4/protocols/{protocol_id}/steps?content_format=md",
        json=PROTOCOL_STEPS_RESPONSE,
    )

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("get_protocol", {"protocol_id": protocol_id, "include_materials": False})

    # Should have title and steps
    assert "RNA Extraction from Tissue Samples" in result.data
    assert "Sample Preparation" in result.data

    # Should not have materials section with vendor info
    assert "Thermo Fisher" not in result.data
    assert "Cat# 15596026" not in result.data


@pytest.mark.asyncio
async def test_auth_header_sent_when_token_configured(httpx_mock: HTTPXMock, monkeypatch):
    """Test that Authorization header is sent when token is configured."""
    monkeypatch.setenv("PROTOCOLS_IO_ACCESS_TOKEN", "test-token-12345")

    # Clear the cached settings
    from protocol_mcp.config import get_settings

    get_settings.cache_clear()

    captured_request = None

    def capture_request(request):
        nonlocal captured_request
        captured_request = request
        return httpx.Response(status_code=200, json=SEARCH_RESPONSE)

    httpx_mock.add_callback(capture_request)

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("search_protocols", {"query": "RNA"})

    assert captured_request is not None
    assert captured_request.headers.get("Authorization") == "Bearer test-token-12345"
    assert "RNA Extraction" in result.data

    # Clear cache after test
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_search_respects_max_results_bounds(httpx_mock: HTTPXMock):
    """Test that max_results is bounded between 1 and 50."""
    # Test with value > 50 (should be clamped to 50)
    httpx_mock.add_response(
        url="https://www.protocols.io/api/v3/protocols?key=RNA&page_size=50&page_id=1&filter=public&order_field=date&order_dir=desc",
        json=SEARCH_RESPONSE,
    )

    async with Client(protocol_mcp.mcp) as client:
        result = await client.call_tool("search_protocols", {"query": "RNA", "max_results": 100})

    assert "RNA Extraction" in result.data
