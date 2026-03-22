"""Integration tests for SempClient against a real Solace broker."""

import pytest

from semp_workflow.semp.client import SempClient

from .conftest import PREFIX

pytestmark = pytest.mark.integration

Q_NAME = f"{PREFIX}CLIENT-TEST"


@pytest.fixture(autouse=True)
def cleanup(semp_client, cleanup_queues):
    cleanup_queues.append(Q_NAME)


class TestConnectivity:
    def test_connection_returns_true(self, semp_client):
        assert semp_client.test_connection() is True


class TestExistence:
    def test_nonexistent_queue_returns_false(self, semp_client):
        found, data = semp_client.exists(
            f"queues/{semp_client._enc(Q_NAME)}"
        )
        assert found is False
        assert data is None

    def test_created_queue_returns_true(self, semp_client):
        semp_client.create("queues", {"queueName": Q_NAME, "accessType": "exclusive"})
        found, data = semp_client.exists(f"queues/{semp_client._enc(Q_NAME)}")
        assert found is True
        assert data is not None

    def test_deleted_queue_returns_false(self, semp_client):
        semp_client.create("queues", {"queueName": Q_NAME, "accessType": "exclusive"})
        semp_client.delete(f"queues/{semp_client._enc(Q_NAME)}")
        found, _ = semp_client.exists(f"queues/{semp_client._enc(Q_NAME)}")
        assert found is False
