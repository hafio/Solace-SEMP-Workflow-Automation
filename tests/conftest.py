"""Root conftest — shared fixtures and marker registration."""

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: requires a live Solace broker",
    )


@pytest.fixture
def mock_client(mocker):
    from semp_workflow.semp.client import SempClient
    return mocker.MagicMock(spec=SempClient)
