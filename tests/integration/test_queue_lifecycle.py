"""Integration: full queue + subscription lifecycle via modules."""

import pytest

from semp_workflow.models import ResultStatus
from semp_workflow.modules.q_sub import SubscriptionAdd, SubscriptionDelete
from semp_workflow.modules.queue import QueueAdd, QueueDelete, QueueUpdate

from .conftest import PREFIX

pytestmark = pytest.mark.integration

Q_NAME = f"{PREFIX}QUEUE-LIFECYCLE"
TOPIC = f"{PREFIX}TEST/TOPIC"


@pytest.fixture(autouse=True)
def cleanup(cleanup_queues):
    cleanup_queues.append(Q_NAME)


class TestQueueLifecycle:
    def test_add_creates_queue(self, semp_client):
        result = QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        assert result.status == ResultStatus.OK

    def test_add_again_skipped(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        result = QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        assert result.status == ResultStatus.SKIPPED

    def test_update_changes_queue(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        result = QueueUpdate().execute(
            semp_client, {"queueName": Q_NAME, "maxMsgSpoolUsage": 512}
        )
        assert result.status == ResultStatus.OK

    def test_delete_removes_queue(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        result = QueueDelete().execute(semp_client, {"queueName": Q_NAME})
        assert result.status == ResultStatus.OK

    def test_delete_again_skipped(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        QueueDelete().execute(semp_client, {"queueName": Q_NAME})
        result = QueueDelete().execute(semp_client, {"queueName": Q_NAME})
        assert result.status == ResultStatus.SKIPPED

    def test_update_nonexistent_fails(self, semp_client):
        # Ensure queue doesn't exist
        QueueDelete().execute(semp_client, {"queueName": Q_NAME})
        result = QueueUpdate().execute(
            semp_client, {"queueName": Q_NAME, "owner": "x"}
        )
        assert result.status == ResultStatus.FAILED


class TestSubscriptionLifecycle:
    def test_add_subscription(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        result = SubscriptionAdd().execute(
            semp_client, {"queueName": Q_NAME, "subscriptionTopic": TOPIC}
        )
        assert result.status == ResultStatus.OK

    def test_add_subscription_again_skipped(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        SubscriptionAdd().execute(
            semp_client, {"queueName": Q_NAME, "subscriptionTopic": TOPIC}
        )
        result = SubscriptionAdd().execute(
            semp_client, {"queueName": Q_NAME, "subscriptionTopic": TOPIC}
        )
        assert result.status == ResultStatus.SKIPPED

    def test_delete_subscription(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        SubscriptionAdd().execute(
            semp_client, {"queueName": Q_NAME, "subscriptionTopic": TOPIC}
        )
        result = SubscriptionDelete().execute(
            semp_client, {"queueName": Q_NAME, "subscriptionTopic": TOPIC}
        )
        assert result.status == ResultStatus.OK

    def test_delete_subscription_again_skipped(self, semp_client):
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        result = SubscriptionDelete().execute(
            semp_client, {"queueName": Q_NAME, "subscriptionTopic": TOPIC}
        )
        assert result.status == ResultStatus.SKIPPED
