"""Unit tests for modules/client_username.py."""

import pytest

from semp_workflow.exceptions import SEMPError
from semp_workflow.models import ResultStatus
from semp_workflow.modules.client_username import ClientUsernameAdd, ClientUsernameDelete


@pytest.fixture
def add_module():
    return ClientUsernameAdd()


@pytest.fixture
def delete_module():
    return ClientUsernameDelete()


class TestClientUsernameAdd:
    def test_skipped_when_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (True, {})
        result = add_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_when_not_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(
            mock_client, {"clientUsername": "user1"}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        mock_client.create.assert_not_called()

    def test_ok_when_created(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.OK

    def test_failed_on_empty_name(self, mock_client, add_module):
        result = add_module.execute(mock_client, {"clientUsername": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_name_too_long(self, mock_client, add_module):
        result = add_module.execute(mock_client, {"clientUsername": "x" * 190})
        assert result.status == ResultStatus.FAILED

    def test_enabled_string_coerced(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        add_module.execute(
            mock_client, {"clientUsername": "user1", "enabled": "false"}
        )
        payload = mock_client.create.call_args[0][1]
        assert payload["enabled"] is False

    def test_failed_on_exists_error(self, mock_client, add_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = add_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_create_error(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        mock_client.create.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = add_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.FAILED


class TestClientUsernameDelete:
    def test_ok_when_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.OK

    def test_skipped_when_not_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (False, None)
        result = delete_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(
            mock_client, {"clientUsername": "user1"}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN

    def test_failed_on_empty_name(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {"clientUsername": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_name_too_long(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {"clientUsername": "x" * 190})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_exists_error(self, mock_client, delete_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = delete_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_delete_error(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        mock_client.delete.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = delete_module.execute(mock_client, {"clientUsername": "user1"})
        assert result.status == ResultStatus.FAILED
