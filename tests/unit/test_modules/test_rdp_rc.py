"""Unit tests for modules/rdp_rc.py."""

import pytest

from semp_workflow.exceptions import SEMPError
from semp_workflow.models import ResultStatus
from semp_workflow.modules.rdp_rc import RdpRestConsumerAdd, RdpRestConsumerDelete


@pytest.fixture
def add_module():
    return RdpRestConsumerAdd()


@pytest.fixture
def delete_module():
    return RdpRestConsumerDelete()


_ARGS = {
    "restDeliveryPointName": "RDP1",
    "restConsumerName": "RC1",
}


class TestRdpRestConsumerAdd:
    def test_skipped_when_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (True, {})
        result = add_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_when_not_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(mock_client, _ARGS, dry_run=True)
        assert result.status == ResultStatus.DRYRUN
        mock_client.create.assert_not_called()

    def test_ok_when_created(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.OK
        mock_client.create.assert_called_once()

    def test_failed_on_missing_rdp_name(self, mock_client, add_module):
        result = add_module.execute(mock_client, {"restConsumerName": "RC1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_missing_consumer_name(self, mock_client, add_module):
        result = add_module.execute(mock_client, {"restDeliveryPointName": "RDP1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_consumer_name_too_long(self, mock_client, add_module):
        result = add_module.execute(
            mock_client,
            {"restDeliveryPointName": "RDP1", "restConsumerName": "x" * 33},
        )
        assert result.status == ResultStatus.FAILED

    def test_rdp_name_not_in_body(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(
            mock_client,
            {**_ARGS, "remoteHost": "backend.example.com"},
        )
        payload = mock_client.create.call_args[0][1]
        assert "restDeliveryPointName" not in payload

    def test_bool_fields_coerced(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(
            mock_client,
            {**_ARGS, "tlsEnabled": "true", "enabled": "false"},
        )
        payload = mock_client.create.call_args[0][1]
        assert payload["tlsEnabled"] is True
        assert payload["enabled"] is False

    def test_int_fields_coerced(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(
            mock_client,
            {**_ARGS, "remotePort": "8443", "outgoingConnectionCount": "5"},
        )
        payload = mock_client.create.call_args[0][1]
        assert payload["remotePort"] == 8443
        assert payload["outgoingConnectionCount"] == 5

    def test_failed_on_exists_error(self, mock_client, add_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = add_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.FAILED

    def test_failed_on_create_error(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        mock_client.create.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = add_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.FAILED


class TestRdpRestConsumerDelete:
    def test_ok_when_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.OK
        mock_client.delete.assert_called_once()

    def test_skipped_when_not_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (False, None)
        result = delete_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(mock_client, _ARGS, dry_run=True)
        assert result.status == ResultStatus.DRYRUN
        mock_client.delete.assert_not_called()

    def test_failed_on_missing_args(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {"restDeliveryPointName": "RDP1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_consumer_name_too_long(self, mock_client, delete_module):
        result = delete_module.execute(
            mock_client,
            {"restDeliveryPointName": "RDP1", "restConsumerName": "x" * 33},
        )
        assert result.status == ResultStatus.FAILED

    def test_failed_on_exists_error(self, mock_client, delete_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = delete_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.FAILED

    def test_failed_on_delete_error(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        mock_client.delete.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = delete_module.execute(mock_client, _ARGS)
        assert result.status == ResultStatus.FAILED
