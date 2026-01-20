"""Business logic for protocols.io operations."""

import re
from typing import Any

from protocol_mcp.clients.protocols_io import ProtocolsIOClient
from protocol_mcp.models.protocols_io import (
    PaginationInfo,
    ProtocolDetail,
    ProtocolMaterial,
    ProtocolSearchItem,
    ProtocolSearchResponse,
    ProtocolStep,
    UserObject,
)


def _parse_search_item(item: dict[str, Any]) -> ProtocolSearchItem:
    """Parse a single search result item.

    Parameters
    ----------
    item : dict[str, Any]
        Raw item from API response.

    Returns
    -------
    ProtocolSearchItem
        Parsed search item.
    """
    creator = None
    if item.get("creator"):
        creator = UserObject(
            name=item["creator"].get("name"),
            username=item["creator"].get("username"),
        )

    stats = item.get("stats", {}) or {}
    number_of_steps = stats.get("number_of_steps")

    return ProtocolSearchItem(
        id=item["id"],
        title=item.get("title", ""),
        uri=item.get("uri", ""),
        doi=item.get("doi"),
        number_of_steps=number_of_steps,
        creator=creator,
        version_id=item.get("version_id"),
    )


def _parse_step(step: dict[str, Any]) -> ProtocolStep:
    """Parse a single protocol step.

    Parameters
    ----------
    step : dict[str, Any]
        Raw step from API response.

    Returns
    -------
    ProtocolStep
        Parsed step.
    """
    return ProtocolStep(
        id=step.get("id", 0),
        step_number=step.get("step_number"),
        title=step.get("title"),
        description=step.get("description"),
        section=step.get("section"),
        duration=step.get("duration"),
        duration_unit=step.get("duration_unit"),
    )


def _parse_material(material: dict[str, Any]) -> ProtocolMaterial:
    """Parse a single material/reagent.

    Parameters
    ----------
    material : dict[str, Any]
        Raw material from API response.

    Returns
    -------
    ProtocolMaterial
        Parsed material.
    """
    return ProtocolMaterial(
        id=material.get("id"),
        name=material.get("name", "Unknown"),
        vendor_name=material.get("vendor", {}).get("name")
        if isinstance(material.get("vendor"), dict)
        else material.get("vendor"),
        catalog_number=material.get("catalog_number"),
        url=material.get("url"),
    )


async def search_protocols(
    client: ProtocolsIOClient,
    query: str,
    max_results: int = 10,
    peer_reviewed_only: bool = False,
) -> ProtocolSearchResponse:
    """Search for protocols.

    Parameters
    ----------
    client : ProtocolsIOClient
        HTTP client for API calls.
    query : str
        Search query string.
    max_results : int
        Maximum number of results to return.
    peer_reviewed_only : bool
        Filter to peer-reviewed protocols only.

    Returns
    -------
    ProtocolSearchResponse
        Search results with pagination info.
    """
    filter_params = {}
    if peer_reviewed_only:
        filter_params["filter"] = "peer_reviewed"
    else:
        # Default to searching public protocols
        filter_params["filter"] = "public"

    # Use date ordering instead of relevance (which has a DB error)
    filter_params["order_field"] = "date"
    filter_params["order_dir"] = "desc"

    response = await client.search_protocols(
        query=query,
        page_size=max_results,
        filter_params=filter_params,
    )

    items = [_parse_search_item(item) for item in response.get("items", [])]

    pagination_data = response.get("pagination", {})
    pagination = PaginationInfo(
        current_page=pagination_data.get("current_page", 1),
        total_pages=pagination_data.get("total_pages", 1),
        total_results=pagination_data.get("total_results", len(items)),
        page_size=pagination_data.get("page_size", max_results),
    )

    return ProtocolSearchResponse(items=items, pagination=pagination)


def _normalize_protocol_id(protocol_id: str) -> str:
    """Normalize protocol identifier for API calls.

    Handles URIs, DOIs, and numeric IDs.

    Parameters
    ----------
    protocol_id : str
        Protocol identifier (URI, DOI, or numeric ID).

    Returns
    -------
    str
        Normalized identifier suitable for API calls.
    """
    protocol_id = protocol_id.strip()

    # Handle DOI format (e.g., "10.17504/protocols.io.xxx")
    if protocol_id.startswith("10."):
        return protocol_id

    # Handle full DOI URL
    if "doi.org" in protocol_id:
        match = re.search(r"doi\.org/(.+)$", protocol_id)
        if match:
            return match.group(1)

    # Handle protocols.io URL - extract the URI
    if "protocols.io" in protocol_id:
        match = re.search(r"protocols\.io/(?:view/)?([a-z0-9-]+)", protocol_id)
        if match:
            return match.group(1)

    return protocol_id


async def get_protocol_detail(
    client: ProtocolsIOClient,
    protocol_id: str,
) -> ProtocolDetail:
    """Get full protocol details.

    Parameters
    ----------
    client : ProtocolsIOClient
        HTTP client for API calls.
    protocol_id : str
        Protocol ID, URI, or DOI.

    Returns
    -------
    ProtocolDetail
        Full protocol details.
    """
    normalized_id = _normalize_protocol_id(protocol_id)
    response = await client.get_protocol(normalized_id)

    protocol = response.get("protocol", response)

    creator = None
    if protocol.get("creator"):
        creator = UserObject(
            name=protocol["creator"].get("name"),
            username=protocol["creator"].get("username"),
        )

    return ProtocolDetail(
        id=protocol.get("id", 0),
        title=protocol.get("title", ""),
        uri=protocol.get("uri", ""),
        doi=protocol.get("doi"),
        description=protocol.get("description"),
        before_start=protocol.get("before_start"),
        warning=protocol.get("warning"),
        guidelines=protocol.get("guidelines"),
        steps=[],
        materials=[],
        creator=creator,
        version_id=protocol.get("version_id"),
    )


async def get_protocol_steps(
    client: ProtocolsIOClient,
    protocol_id: str,
) -> list[ProtocolStep]:
    """Get protocol steps.

    Parameters
    ----------
    client : ProtocolsIOClient
        HTTP client for API calls.
    protocol_id : str
        Protocol ID.

    Returns
    -------
    list[ProtocolStep]
        List of protocol steps.
    """
    normalized_id = _normalize_protocol_id(protocol_id)
    response = await client.get_protocol_steps(normalized_id)
    steps_data = response.get("steps", response.get("items", []))
    return [_parse_step(step) for step in steps_data]


async def get_protocol_materials(
    client: ProtocolsIOClient,
    protocol_id: str,
) -> list[ProtocolMaterial]:
    """Get protocol materials.

    Parameters
    ----------
    client : ProtocolsIOClient
        HTTP client for API calls.
    protocol_id : str
        Protocol ID.

    Returns
    -------
    list[ProtocolMaterial]
        List of materials/reagents.
    """
    normalized_id = _normalize_protocol_id(protocol_id)
    response = await client.get_protocol_materials(normalized_id)
    materials_data = response.get("materials", response.get("items", []))
    return [_parse_material(mat) for mat in materials_data]


def format_search_results(response: ProtocolSearchResponse) -> str:
    """Format search results for LLM consumption.

    Parameters
    ----------
    response : ProtocolSearchResponse
        Search response to format.

    Returns
    -------
    str
        Markdown-formatted search results.
    """
    if not response.items:
        return "No protocols found matching your search."

    lines = [f"Found {response.pagination.total_results} protocols:\n"]

    for i, item in enumerate(response.items, 1):
        lines.append(f"## {i}. {item.title}")
        lines.append(f"- **URI:** {item.uri}")
        if item.doi:
            lines.append(f"- **DOI:** {item.doi}")
        if item.number_of_steps:
            lines.append(f"- **Steps:** {item.number_of_steps}")
        if item.creator and item.creator.name:
            lines.append(f"- **Author:** {item.creator.name}")
        lines.append("")

    return "\n".join(lines)


def format_steps_for_llm(steps: list[ProtocolStep]) -> str:
    """Format protocol steps for LLM consumption.

    Parameters
    ----------
    steps : list[ProtocolStep]
        List of steps to format.

    Returns
    -------
    str
        Markdown-formatted steps.
    """
    if not steps:
        return "No steps available."

    lines = ["## Steps\n"]
    for step in steps:
        step_num = step.step_number or step.id
        if step.section:
            lines.append(f"### Section: {step.section}\n")
        if step.title:
            lines.append(f"**Step {step_num}: {step.title}**")
        else:
            lines.append(f"**Step {step_num}**")
        if step.description:
            lines.append(step.description)
        if step.duration and step.duration_unit:
            lines.append(f"*Duration: {step.duration} {step.duration_unit}*")
        lines.append("")

    return "\n".join(lines)


def format_materials_for_llm(materials: list[ProtocolMaterial]) -> str:
    """Format protocol materials for LLM consumption.

    Parameters
    ----------
    materials : list[ProtocolMaterial]
        List of materials to format.

    Returns
    -------
    str
        Markdown-formatted materials list.
    """
    if not materials:
        return ""

    lines = ["## Materials & Reagents\n"]
    for mat in materials:
        entry = f"- **{mat.name}**"
        if mat.vendor_name:
            entry += f" ({mat.vendor_name}"
            if mat.catalog_number:
                entry += f", Cat# {mat.catalog_number}"
            entry += ")"
        elif mat.catalog_number:
            entry += f" (Cat# {mat.catalog_number})"
        lines.append(entry)

    return "\n".join(lines)


def format_protocol_for_llm(
    protocol: ProtocolDetail,
    steps: list[ProtocolStep] | None = None,
    materials: list[ProtocolMaterial] | None = None,
    include_steps: bool = True,
    include_materials: bool = True,
) -> str:
    """Format full protocol for LLM consumption.

    Parameters
    ----------
    protocol : ProtocolDetail
        Protocol details.
    steps : list[ProtocolStep] | None
        Protocol steps (if fetched separately).
    materials : list[ProtocolMaterial] | None
        Protocol materials (if fetched separately).
    include_steps : bool
        Whether to include steps in output.
    include_materials : bool
        Whether to include materials in output.

    Returns
    -------
    str
        Markdown-formatted protocol.
    """
    lines = [f"# {protocol.title}\n"]

    # Metadata
    lines.append(f"- **URI:** {protocol.uri}")
    if protocol.doi:
        lines.append(f"- **DOI:** {protocol.doi}")
    if protocol.creator and protocol.creator.name:
        lines.append(f"- **Author:** {protocol.creator.name}")
    lines.append("")

    # Description
    if protocol.description:
        lines.append("## Description\n")
        lines.append(protocol.description)
        lines.append("")

    # Warning
    if protocol.warning:
        lines.append("## Warning\n")
        lines.append(f"⚠️ {protocol.warning}")
        lines.append("")

    # Before starting
    if protocol.before_start:
        lines.append("## Before Starting\n")
        lines.append(protocol.before_start)
        lines.append("")

    # Guidelines
    if protocol.guidelines:
        lines.append("## Guidelines\n")
        lines.append(protocol.guidelines)
        lines.append("")

    # Materials
    if include_materials:
        mats = materials if materials is not None else protocol.materials
        if mats:
            lines.append(format_materials_for_llm(mats))
            lines.append("")

    # Steps
    if include_steps:
        step_list = steps if steps is not None else protocol.steps
        if step_list:
            lines.append(format_steps_for_llm(step_list))

    return "\n".join(lines)
