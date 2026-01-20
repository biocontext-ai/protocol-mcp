"""Pydantic models for protocols.io API responses."""

from pydantic import BaseModel, ConfigDict, Field


class UserObject(BaseModel):
    """User object from protocols.io API."""

    name: str | None = None
    username: str | None = None


class PaginationInfo(BaseModel):
    """Pagination metadata from protocols.io API."""

    current_page: int = 1
    total_pages: int = 1
    total_results: int = 0
    page_size: int = 10


class ProtocolSearchItem(BaseModel):
    """Single protocol item from search results."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    uri: str
    doi: str | None = None
    number_of_steps: int | None = Field(default=None, alias="stats")
    creator: UserObject | None = None
    version_id: int | None = None


class ProtocolSearchResponse(BaseModel):
    """Response from protocols.io search endpoint."""

    items: list[ProtocolSearchItem]
    pagination: PaginationInfo


class ProtocolStep(BaseModel):
    """Single step in a protocol."""

    id: int
    step_number: int | None = None
    title: str | None = None
    description: str | None = None
    section: str | None = None
    duration: int | None = None
    duration_unit: str | None = None


class ProtocolMaterial(BaseModel):
    """Material/reagent in a protocol."""

    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    name: str
    vendor_name: str | None = Field(default=None, alias="vendor")
    catalog_number: str | None = None
    url: str | None = None


class ProtocolDetail(BaseModel):
    """Full protocol details."""

    id: int
    title: str
    uri: str
    doi: str | None = None
    description: str | None = None
    before_start: str | None = None
    warning: str | None = None
    guidelines: str | None = None
    steps: list[ProtocolStep] = Field(default_factory=list)
    materials: list[ProtocolMaterial] = Field(default_factory=list)
    creator: UserObject | None = None
    version_id: int | None = None
