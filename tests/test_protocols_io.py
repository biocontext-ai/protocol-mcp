"""Integration tests for protocols.io MCP tools against real API."""

import os

import pytest
from fastmcp import Client

import protocol_mcp

# Skip all tests if no token is configured
pytestmark = pytest.mark.skipif(
    not os.environ.get("PROTOCOLS_IO_ACCESS_TOKEN"),
    reason="PROTOCOLS_IO_ACCESS_TOKEN not set",
)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear settings cache before each test to pick up env changes."""
    from protocol_mcp.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestSearchProtocols:
    """Tests for the search_protocols tool."""

    @pytest.mark.asyncio
    async def test_search_returns_results_with_expected_structure(self):
        """Search for common term and verify result structure."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("search_protocols", {"query": "PCR", "max_results": 5})

        # Should find results
        assert "Found" in result.data
        assert "protocols" in result.data

        # Results should have expected markdown structure
        assert "## 1." in result.data  # First result header
        assert "**URI:**" in result.data
        assert "**DOI:**" in result.data or "**Steps:**" in result.data

    @pytest.mark.asyncio
    async def test_search_returns_multiple_results(self):
        """Search should return multiple distinct results."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("search_protocols", {"query": "extraction", "max_results": 3})

        # Should have at least 2 results (extraction is common)
        assert "## 1." in result.data
        assert "## 2." in result.data

    @pytest.mark.asyncio
    async def test_search_respects_max_results(self):
        """Search should not return more than max_results."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("search_protocols", {"query": "RNA", "max_results": 2})

        # Should have exactly 2 results at most
        assert "## 1." in result.data
        assert "## 2." in result.data
        assert "## 3." not in result.data

    @pytest.mark.asyncio
    async def test_search_obscure_term_may_return_empty(self):
        """Very specific/obscure search may return no results."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool(
                "search_protocols", {"query": "xyznonexistent12345abcdef", "max_results": 5}
            )

        # Either no results or very few
        assert "No protocols found" in result.data or "Found" in result.data


class TestGetProtocol:
    """Tests for the get_protocol tool."""

    # A well-known, stable protocol with steps and materials
    KNOWN_PROTOCOL_URI = "tissue-cyclic-immunofluorescence-t-cycif-bjiukkew"
    KNOWN_PROTOCOL_DOI = "10.17504/protocols.io.bjiukkew"

    @pytest.mark.asyncio
    async def test_get_protocol_by_uri(self):
        """Get protocol by URI returns full details."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("get_protocol", {"protocol_id": self.KNOWN_PROTOCOL_URI})

        # Should have title as header
        assert "# " in result.data  # Markdown h1
        assert "CyCIF" in result.data or "cycif" in result.data.lower()

        # Should have metadata
        assert "**URI:**" in result.data
        assert "**DOI:**" in result.data
        assert "**Author:**" in result.data

        # Should have description
        assert "## Description" in result.data
        assert len(result.data) > 500  # Non-trivial content

    @pytest.mark.asyncio
    async def test_get_protocol_by_doi(self):
        """Get protocol by DOI works."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("get_protocol", {"protocol_id": self.KNOWN_PROTOCOL_DOI})

        # Should resolve to same protocol
        assert "CyCIF" in result.data or "cycif" in result.data.lower()
        assert "**DOI:**" in result.data

    @pytest.mark.asyncio
    async def test_get_protocol_includes_steps(self):
        """Protocol should include steps by default."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool(
                "get_protocol", {"protocol_id": self.KNOWN_PROTOCOL_URI, "include_steps": True}
            )

        # Should have steps section
        assert "## Steps" in result.data
        assert "**Step" in result.data

    @pytest.mark.asyncio
    async def test_get_protocol_includes_materials(self):
        """Protocol should include materials by default."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool(
                "get_protocol", {"protocol_id": self.KNOWN_PROTOCOL_URI, "include_materials": True}
            )

        # Should have materials section
        assert "## Materials" in result.data or "Reagents" in result.data

    @pytest.mark.asyncio
    async def test_get_protocol_without_steps(self):
        """Can exclude steps from response."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool(
                "get_protocol", {"protocol_id": self.KNOWN_PROTOCOL_URI, "include_steps": False}
            )

        # Should still have title and description
        assert "# " in result.data
        assert "## Description" in result.data

        # Steps section should be absent or empty
        # (checking for Step N pattern which only appears in steps)
        step_count = result.data.count("**Step ")
        assert step_count == 0

    @pytest.mark.asyncio
    async def test_get_protocol_without_materials(self):
        """Can exclude materials from response."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool(
                "get_protocol", {"protocol_id": self.KNOWN_PROTOCOL_URI, "include_materials": False}
            )

        # Should still have title
        assert "# " in result.data

        # Materials header should be absent
        assert "## Materials & Reagents" not in result.data

    @pytest.mark.asyncio
    async def test_get_protocol_metadata_complete(self):
        """Protocol metadata should be properly formatted."""
        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("get_protocol", {"protocol_id": self.KNOWN_PROTOCOL_URI})

        # Check structured metadata format
        lines = result.data.split("\n")

        # Find metadata lines (start with "- **")
        metadata_lines = [l for l in lines if l.startswith("- **")]

        # Should have at least URI, DOI, and Author
        assert len(metadata_lines) >= 2

        # URI and DOI should be present
        has_uri = any("URI:" in l for l in metadata_lines)
        has_doi = any("DOI:" in l for l in metadata_lines)
        assert has_uri
        assert has_doi


class TestProtocolIdentifierFormats:
    """Test different protocol identifier formats."""

    @pytest.mark.asyncio
    async def test_full_url_format(self):
        """Can fetch protocol using full protocols.io URL."""
        full_url = "https://www.protocols.io/view/tissue-cyclic-immunofluorescence-t-cycif-bjiukkew"

        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("get_protocol", {"protocol_id": full_url})

        assert "CyCIF" in result.data or "cycif" in result.data.lower()

    @pytest.mark.asyncio
    async def test_dx_doi_format(self):
        """Can fetch protocol using dx.doi.org format."""
        dx_doi = "dx.doi.org/10.17504/protocols.io.bjiukkew"

        async with Client(protocol_mcp.mcp) as client:
            result = await client.call_tool("get_protocol", {"protocol_id": dx_doi})

        assert "CyCIF" in result.data or "cycif" in result.data.lower()
