"""MCP tools for protocols.io integration."""

from typing import Annotated

from protocol_mcp.clients.protocols_io import ProtocolsIOClient
from protocol_mcp.mcp import mcp
from protocol_mcp.services.protocols_io import (
    format_protocol_for_llm,
    format_search_results,
    get_protocol_detail,
    get_protocol_materials,
    get_protocol_steps,
)
from protocol_mcp.services.protocols_io import (
    search_protocols as search_protocols_service,
)


@mcp.tool
async def search_protocols(
    query: Annotated[str, "Search term (e.g., 'RNA extraction', 'CRISPR knockout')"],
    max_results: Annotated[int, "Number of results to return (1-50)"] = 10,
    peer_reviewed_only: Annotated[bool, "Filter to peer-reviewed protocols only"] = False,
) -> str:
    """Search protocols.io for laboratory protocols.

    Parameters
    ----------
    query : str
        Search term to find protocols.
    max_results : int
        Number of results (1-50), defaults to 10.
    peer_reviewed_only : bool
        If True, only return peer-reviewed protocols.

    Returns
    -------
    str
        Formatted list of matching protocols with title, DOI, URI, and step count.
    """
    max_results = max(1, min(50, max_results))

    async with ProtocolsIOClient() as client:
        response = await search_protocols_service(
            client=client,
            query=query,
            max_results=max_results,
            peer_reviewed_only=peer_reviewed_only,
        )

    return format_search_results(response)


@mcp.tool
async def get_protocol(
    protocol_id: Annotated[str, "Protocol identifier: URI, DOI, or numeric ID from search results"],
    include_steps: Annotated[bool, "Include step-by-step instructions"] = True,
    include_materials: Annotated[bool, "Include materials/reagents list"] = True,
) -> str:
    """Retrieve full protocol details from protocols.io.

    Parameters
    ----------
    protocol_id : str
        Protocol identifier - can be a URI (e.g., 'rna-extraction-abc123'),
        DOI (e.g., '10.17504/protocols.io.xxx'), or numeric ID.
    include_steps : bool
        Whether to include step-by-step instructions, defaults to True.
    include_materials : bool
        Whether to include materials/reagents list, defaults to True.

    Returns
    -------
    str
        Formatted markdown with protocol metadata, materials, and steps.
    """
    async with ProtocolsIOClient() as client:
        protocol = await get_protocol_detail(client, protocol_id)

        steps = None
        materials = None

        if include_steps:
            try:
                steps = await get_protocol_steps(client, protocol_id)
            except Exception as _:  # noqa: BLE001
                steps = []

        if include_materials:
            try:
                materials = await get_protocol_materials(client, protocol_id)
            except Exception as _:  # noqa: BLE001
                materials = []

    return format_protocol_for_llm(
        protocol=protocol,
        steps=steps,
        materials=materials,
        include_steps=include_steps,
        include_materials=include_materials,
    )
