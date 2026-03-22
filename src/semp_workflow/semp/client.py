"""SEMP v2 Configuration API client."""

from __future__ import annotations

import logging
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import SEMPError

logger = logging.getLogger(__name__)

# SEMP error codes
NOT_FOUND = 6
ALREADY_EXISTS = 10


class SempClient:
    """Low-level HTTP client for the Solace SEMP v2 Config API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        msg_vpn: str,
        verify_ssl: bool = False,
        timeout: int = 30,
    ):
        self.host = host.rstrip("/")
        self.msg_vpn = msg_vpn
        self.timeout = timeout

        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        # Retry on transient server errors (not connection failures)
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504],
            connect=0,  # Don't retry connection errors
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        if not verify_ssl:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @property
    def vpn_url(self) -> str:
        """Base URL for VPN-scoped SEMP config endpoints."""
        return f"{self.host}/SEMP/v2/config/msgVpns/{self._enc(self.msg_vpn)}"

    @staticmethod
    def _enc(value: str) -> str:
        """URL-encode a path segment (handles /, #, *, > etc.)."""
        return quote(str(value), safe="")

    def _request(
        self, method: str, path: str, payload: dict | None = None
    ) -> dict | None:
        """Execute an HTTP request against the SEMP API.

        Returns the response JSON 'data' field on success.
        Raises SEMPError on failure.
        """
        url = f"{self.vpn_url}/{path}"
        logger.debug("%s %s %s", method, url, payload or "")

        try:
            resp = self.session.request(
                method, url, json=payload, timeout=self.timeout
            )
        except requests.ConnectionError as e:
            raise SEMPError(
                f"Connection failed: {self.host} - is the broker reachable?",
                status_code=0,
            ) from e
        except requests.Timeout as e:
            raise SEMPError(
                f"Request timed out after {self.timeout}s",
                status_code=0,
            ) from e
        except requests.RequestException as e:
            raise SEMPError(f"Request failed: {e}", status_code=0) from e

        body = resp.json() if resp.text else {}
        meta = body.get("meta", {})
        response_code = meta.get("responseCode", resp.status_code)

        if response_code == 200:
            return body.get("data")

        error = meta.get("error", {})
        description = error.get("description", resp.text or "Unknown SEMP error")
        semp_code = error.get("code", 0)
        raise SEMPError(description, status_code=response_code, semp_code=semp_code)

    def exists(self, path: str) -> tuple[bool, dict | None]:
        """Check if a resource exists. Returns (exists, data_or_None)."""
        try:
            data = self._request("GET", path)
            return True, data
        except SEMPError as e:
            if e.semp_code == NOT_FOUND or e.status_code == 404:
                return False, None
            raise

    def create(self, path: str, payload: dict) -> dict | None:
        """POST to create a resource."""
        return self._request("POST", path, payload)

    def update(self, path: str, payload: dict) -> dict | None:
        """PATCH to update a resource."""
        return self._request("PATCH", path, payload)

    def delete(self, path: str) -> None:
        """DELETE a resource."""
        self._request("DELETE", path)

    def test_connection(self) -> bool:
        """Verify connectivity to the broker by fetching the VPN."""
        try:
            url = f"{self.host}/SEMP/v2/config/msgVpns/{self._enc(self.msg_vpn)}"
            resp = self.session.get(url, timeout=self.timeout)
            return resp.status_code == 200
        except requests.RequestException:
            return False
