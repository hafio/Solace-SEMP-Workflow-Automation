"""Unit tests for modules/queue.py."""

import pytest

from semp_workflow.exceptions import SEMPError
from semp_workflow.models import ResultStatus
from semp_workflow.modules.queue import QueueAdd, QueueDelete, QueueUpdate


@pytest.fixture
def add_module():
    return QueueAdd()


@pytest.fixture
def delete_module():
    return QueueDelete()


@pytest.fixture
def update_module():
    return QueueUpdate()


# ---------------------------------------------------------------------------
# QueueAdd
# ---------------------------------------------------------------------------

class TestQueueAdd:
    def test_skipped_when_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (True, {})
        result = add_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.SKIPPED
        mock_client.create.assert_not_called()

    def test_dryrun_when_not_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(mock_client, {"queueName": "Q1"}, dry_run=True)
        assert result.status == ResultStatus.DRYRUN
        mock_client.create.assert_not_called()

    def test_ok_when_created(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        mock_client.create.return_value = {}
        result = add_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.OK
        mock_client.create.assert_called_once()

    def test_failed_on_exists_error(self, mock_client, add_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = add_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_create_error(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        mock_client.create.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = add_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_empty_name(self, mock_client, add_module):
        result = add_module.execute(mock_client, {"queueName": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_name_too_long(self, mock_client, add_module):
        result = add_module.execute(mock_client, {"queueName": "x" * 201})
        assert result.status == ResultStatus.FAILED

    def test_max_ttl_zero_disables(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(mock_client, {"queueName": "Q1", "maxTtl": 0})
        payload = mock_client.create.call_args[0][1]
        assert payload["respectTtlEnabled"] is False

    def test_max_ttl_positive_enables(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(mock_client, {"queueName": "Q1", "maxTtl": 300})
        payload = mock_client.create.call_args[0][1]
        assert payload["respectTtlEnabled"] is True

    def test_max_redelivery_minus_one_becomes_zero(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(mock_client, {"queueName": "Q1", "maxRedeliveryCount": -1})
        payload = mock_client.create.call_args[0][1]
        assert payload["maxRedeliveryCount"] == 0
        assert payload["redeliveryEnabled"] is False

    def test_max_redelivery_positive(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(mock_client, {"queueName": "Q1", "maxRedeliveryCount": 5})
        payload = mock_client.create.call_args[0][1]
        assert payload["maxRedeliveryCount"] == 5
        assert payload["redeliveryEnabled"] is True

    def test_ingress_enabled_string_coerced(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(mock_client, {"queueName": "Q1", "ingressEnabled": "true"})
        payload = mock_client.create.call_args[0][1]
        assert payload["ingressEnabled"] is True

    def test_create_path_is_queues(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(mock_client, {"queueName": "Q1"})
        path_arg = mock_client.create.call_args[0][0]
        assert path_arg == "queues"


# ---------------------------------------------------------------------------
# QueueDelete
# ---------------------------------------------------------------------------

class TestQueueDelete:
    def test_ok_when_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.OK
        mock_client.delete.assert_called_once()

    def test_skipped_when_not_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (False, None)
        result = delete_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.SKIPPED
        mock_client.delete.assert_not_called()

    def test_dryrun_when_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(mock_client, {"queueName": "Q1"}, dry_run=True)
        assert result.status == ResultStatus.DRYRUN
        mock_client.delete.assert_not_called()

    def test_failed_on_empty_name(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {"queueName": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_name_too_long(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {"queueName": "x" * 201})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_exists_error(self, mock_client, delete_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = delete_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_delete_error(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        mock_client.delete.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = delete_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.FAILED


# ---------------------------------------------------------------------------
# QueueUpdate
# ---------------------------------------------------------------------------

class TestQueueUpdate:
    def test_ok_when_exists(self, mock_client, update_module):
        mock_client.exists.return_value = (True, {})
        result = update_module.execute(
            mock_client, {"queueName": "Q1", "maxMsgSpoolUsage": 1024}
        )
        assert result.status == ResultStatus.OK
        mock_client.update.assert_called_once()

    def test_failed_when_not_exists(self, mock_client, update_module):
        mock_client.exists.return_value = (False, None)
        result = update_module.execute(
            mock_client, {"queueName": "Q1", "maxMsgSpoolUsage": 1024}
        )
        assert result.status == ResultStatus.FAILED

    def test_skipped_on_empty_payload(self, mock_client, update_module):
        mock_client.exists.return_value = (True, {})
        # Only queueName provided — nothing to update after removing it
        result = update_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.SKIPPED
        mock_client.update.assert_not_called()

    def test_dryrun_when_exists(self, mock_client, update_module):
        mock_client.exists.return_value = (True, {})
        result = update_module.execute(
            mock_client, {"queueName": "Q1", "owner": "user"}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        mock_client.update.assert_not_called()

    def test_queue_name_not_in_update_payload(self, mock_client, update_module):
        mock_client.exists.return_value = (True, {})
        update_module.execute(mock_client, {"queueName": "Q1", "owner": "admin"})
        payload = mock_client.update.call_args[0][1]
        assert "queueName" not in payload

    def test_failed_on_empty_name(self, mock_client, update_module):
        result = update_module.execute(mock_client, {"queueName": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_name_too_long(self, mock_client, update_module):
        result = update_module.execute(mock_client, {"queueName": "x" * 201})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_exists_error(self, mock_client, update_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = update_module.execute(mock_client, {"queueName": "Q1", "owner": "u"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_update_error(self, mock_client, update_module):
        mock_client.exists.return_value = (True, {})
        mock_client.update.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = update_module.execute(mock_client, {"queueName": "Q1", "owner": "u"})
        assert result.status == ResultStatus.FAILED
