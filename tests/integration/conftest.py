"""Integration test fixtures.

Connection settings are loaded from a .env file at the project root
(or from real environment variables, which take precedence).

Copy .env.example -> .env and fill in your broker details:

    SEMP_HOST        e.g. https://localhost:8943
    SEMP_USERNAME    e.g. admin
    SEMP_PASSWORD    e.g. admin
    SEMP_MSG_VPN     e.g. default
    SEMP_VERIFY_SSL  true|false  (default: false)

Run with:
    pytest tests/integration/ -m integration
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from semp_workflow.semp.client import SempClient

# Load .env from the project root (two levels up from this file).
# override=False means real env vars always win over the .env file.
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_FILE, override=False)

REQUIRED_VARS = ("SEMP_HOST", "SEMP_USERNAME", "SEMP_PASSWORD", "SEMP_MSG_VPN")

# All test resources use this prefix to avoid collisions with real resources.
PREFIX = "TEST-SEMP-WF-"


def _missing_vars():
    return [v for v in REQUIRED_VARS if not os.environ.get(v)]


@pytest.fixture(scope="session")
def semp_client():
    missing = _missing_vars()
    if missing:
        pytest.skip(
            f"Integration env vars not set: {', '.join(missing)}. "
            f"Set them in .env (see .env.example) or as real environment variables."
        )
    return SempClient(
        host=os.environ["SEMP_HOST"],
        username=os.environ["SEMP_USERNAME"],
        password=os.environ["SEMP_PASSWORD"],
        msg_vpn=os.environ["SEMP_MSG_VPN"],
        verify_ssl=os.environ.get("SEMP_VERIFY_SSL", "false").lower() == "true",
    )


@pytest.fixture
def cleanup_queues(semp_client):
    """Yield a list to register queue names for deletion after the test."""
    names: list[str] = []
    yield names
    for name in names:
        try:
            semp_client.delete(f"queues/{semp_client._enc(name)}")
        except Exception:
            pass


@pytest.fixture
def cleanup_rdps(semp_client):
    """Yield a list to register RDP names for deletion after the test."""
    names: list[str] = []
    yield names
    for name in names:
        try:
            semp_client.delete(
                f"restDeliveryPoints/{semp_client._enc(name)}"
            )
        except Exception:
            pass
