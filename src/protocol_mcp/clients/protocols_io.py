"""HTTP client for protocols.io API."""

from typing import Any

import httpx

from protocol_mcp.config import ProtocolsIOConfig, get_settings


class ProtocolsIOClient:
    """Async HTTP client for protocols.io API.

    Handles authentication and provides methods for v3 and v4 API endpoints.
    """

    def __init__(self, config: ProtocolsIOConfig | None = None):
        """Initialize the client.

        Parameters
        ----------
        config : ProtocolsIOConfig | None
            Configuration for the client. If None, loads from environment.
        """
        self.config = config or get_settings().protocols_io
        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns
        -------
        dict[str, str]
            Headers dict with Authorization if token is configured.
        """
        headers = {"Accept": "application/json"}
        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token.get_secret_value()}"
        return headers

    async def __aenter__(self) -> "ProtocolsIOClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(headers=self._get_headers(), timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """Make an HTTP request.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, etc.).
        url : str
            Full URL to request.
        **kwargs
            Additional arguments passed to httpx.

        Returns
        -------
        dict[str, Any]
            JSON response as dict.

        Raises
        ------
        RuntimeError
            If client is used outside of context manager.
        httpx.HTTPStatusError
            If response status indicates an error.
        """
        if not self._client:
            raise RuntimeError("Client must be used as async context manager")
        response = await self._client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def search_protocols(
        self,
        query: str,
        page_size: int = 10,
        page_id: int = 1,
        filter_type: str = "public",
        order_field: str = "date",
        order_dir: str = "desc",
    ) -> dict[str, Any]:
        """Search for protocols using v3 API.

        Parameters
        ----------
        query : str
            Search query string.
        page_size : int
            Number of results per page (1-100).
        page_id : int
            Page number (1-indexed).
        filter_type : str
            Protocol filter type. One of: 'public', 'user_public',
            'user_private', 'shared_with_user'. Defaults to 'public'.
        order_field : str
            Sort field: 'activity', 'date', 'name', or 'id'.
            Defaults to 'date'.
        order_dir : str
            Sort direction: 'asc' or 'desc'. Defaults to 'desc'.

        Returns
        -------
        dict[str, Any]
            Raw API response.
        """
        url = f"{self.config.base_url_v3}/protocols"
        params = {
            "filter": filter_type,
            "key": query,
            "page_size": page_size,
            "page_id": page_id,
            "order_field": order_field,
            "order_dir": order_dir,
        }
        return await self._request("GET", url, params=params)

    async def get_protocol(
        self,
        protocol_id: str | int,
        content_format: str = "md",
    ) -> dict[str, Any]:
        """Get protocol details using v4 API.

        Parameters
        ----------
        protocol_id : str | int
            Protocol ID, URI, or DOI.
        content_format : str
            Content format: 'md' for markdown, 'html' for HTML.

        Returns
        -------
        dict[str, Any]
            Raw API response.
        """
        url = f"{self.config.base_url_v4}/protocols/{protocol_id}"
        params = {"content_format": content_format}
        return await self._request("GET", url, params=params)

    async def get_protocol_steps(
        self,
        protocol_id: str | int,
        content_format: str = "md",
    ) -> dict[str, Any]:
        """Get protocol steps using v4 API.

        Parameters
        ----------
        protocol_id : str | int
            Protocol ID.
        content_format : str
            Content format: 'md' for markdown, 'html' for HTML.

        Returns
        -------
        dict[str, Any]
            Raw API response with steps.
        """
        url = f"{self.config.base_url_v4}/protocols/{protocol_id}/steps"
        params = {"content_format": content_format}
        return await self._request("GET", url, params=params)

    async def get_protocol_materials(
        self,
        protocol_id: str | int,
    ) -> dict[str, Any]:
        """Get protocol materials using v4 API.

        Parameters
        ----------
        protocol_id : str | int
            Protocol ID.

        Returns
        -------
        dict[str, Any]
            Raw API response with materials.
        """
        url = f"{self.config.base_url_v4}/protocols/{protocol_id}/materials"
        return await self._request("GET", url)
