"""Integration: full RDP + REST Consumer + Queue Binding lifecycle via modules."""

import pytest

from semp_workflow.models import ResultStatus
from semp_workflow.modules.queue import QueueAdd, QueueDelete
from semp_workflow.modules.rdp import RdpAdd, RdpDelete
from semp_workflow.modules.rdp_qb import QueueBindingAdd, QueueBindingDelete
from semp_workflow.modules.rdp_rc import RdpRestConsumerAdd, RdpRestConsumerDelete

from .conftest import PREFIX

pytestmark = pytest.mark.integration

RDP_NAME = f"{PREFIX}RDP-LIFECYCLE"
RC_NAME = f"{PREFIX}RC"
Q_NAME = f"{PREFIX}QUEUE-RDP"


@pytest.fixture(autouse=True)
def cleanup(semp_client, cleanup_queues, cleanup_rdps):
    cleanup_queues.append(Q_NAME)
    cleanup_rdps.append(RDP_NAME)


class TestRdpLifecycle:
    def test_rdp_add(self, semp_client):
        result = RdpAdd().execute(semp_client, {"restDeliveryPointName": RDP_NAME})
        assert result.status == ResultStatus.OK

    def test_rdp_add_skipped(self, semp_client):
        RdpAdd().execute(semp_client, {"restDeliveryPointName": RDP_NAME})
        result = RdpAdd().execute(semp_client, {"restDeliveryPointName": RDP_NAME})
        assert result.status == ResultStatus.SKIPPED

    def test_rest_consumer_add(self, semp_client):
        RdpAdd().execute(semp_client, {"restDeliveryPointName": RDP_NAME})
        result = RdpRestConsumerAdd().execute(
            semp_client,
            {
                "restDeliveryPointName": RDP_NAME,
                "restConsumerName": RC_NAME,
                "remoteHost": "backend.example.com",
                "remotePort": 443,
                "tlsEnabled": True,
            },
        )
        assert result.status == ResultStatus.OK

    def test_queue_binding_add(self, semp_client):
        RdpAdd().execute(semp_client, {"restDeliveryPointName": RDP_NAME})
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        result = QueueBindingAdd().execute(
            semp_client,
            {
                "restDeliveryPointName": RDP_NAME,
                "queueBindingName": Q_NAME,
                "postRequestTarget": "/api/receive",
            },
        )
        assert result.status == ResultStatus.OK

    def test_full_teardown(self, semp_client):
        # Setup
        RdpAdd().execute(semp_client, {"restDeliveryPointName": RDP_NAME})
        QueueAdd().execute(semp_client, {"queueName": Q_NAME})
        RdpRestConsumerAdd().execute(
            semp_client,
            {"restDeliveryPointName": RDP_NAME, "restConsumerName": RC_NAME},
        )
        QueueBindingAdd().execute(
            semp_client,
            {"restDeliveryPointName": RDP_NAME, "queueBindingName": Q_NAME},
        )

        # Teardown in correct order
        r1 = QueueBindingDelete().execute(
            semp_client,
            {"restDeliveryPointName": RDP_NAME, "queueBindingName": Q_NAME},
        )
        r2 = RdpRestConsumerDelete().execute(
            semp_client,
            {"restDeliveryPointName": RDP_NAME, "restConsumerName": RC_NAME},
        )
        r3 = RdpDelete().execute(semp_client, {"restDeliveryPointName": RDP_NAME})
        r4 = QueueDelete().execute(semp_client, {"queueName": Q_NAME})

        assert r1.status == ResultStatus.OK
        assert r2.status == ResultStatus.OK
        assert r3.status == ResultStatus.OK
        assert r4.status == ResultStatus.OK
