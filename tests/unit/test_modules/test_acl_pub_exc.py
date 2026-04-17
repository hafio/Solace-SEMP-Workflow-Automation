"""Unit tests for modules/acl_pub_exc.py."""

import pytest

from semp_workflow.exceptions import SEMPError
from semp_workflow.models import ResultStatus
from semp_workflow.modules.acl_pub_exc import AclPublishExceptionAdd, AclPublishExceptionDelete


ARGS = {
    "aclProfileName": "acl-test",
    "publishTopicException": "FCM/SAP/AIF/TEST/>",
    "publishTopicExceptionSyntax": "smf",
}


@pytest.fixture
def add_module():
    return AclPublishExceptionAdd()


@pytest.fixture
def delete_module():
    return AclPublishExceptionDelete()


class TestAclPublishExceptionAdd:
    def test_skipped_when_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (True, {})
        result = add_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_when_not_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(mock_client, ARGS, dry_run=True)
        assert result.status == ResultStatus.DRYRUN
        mock_client.create.assert_not_called()

    def test_ok_when_created(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.OK
        mock_client.create.assert_called_once()

    def test_failed_on_empty_profile(self, mock_client, add_module):
        result = add_module.execute(mock_client, {**ARGS, "aclProfileName": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_empty_topic(self, mock_client, add_module):
        result = add_module.execute(mock_client, {**ARGS, "publishTopicException": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_exists_error(self, mock_client, add_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = add_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.FAILED

    def test_failed_on_create_error(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        mock_client.create.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = add_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.FAILED

    def test_default_syntax_is_smf(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        args_no_syntax = {"aclProfileName": "acl-test", "publishTopicException": "test/topic"}
        result = add_module.execute(mock_client, args_no_syntax)
        assert result.status == ResultStatus.OK
        payload = mock_client.create.call_args[0][1]
        assert payload["publishTopicExceptionSyntax"] == "smf"


class TestAclPublishExceptionDelete:
    def test_ok_when_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.OK

    def test_skipped_when_not_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (False, None)
        result = delete_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(mock_client, ARGS, dry_run=True)
        assert result.status == ResultStatus.DRYRUN
        mock_client.delete.assert_not_called()

    def test_failed_on_empty_profile(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {**ARGS, "aclProfileName": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_empty_topic(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {**ARGS, "publishTopicException": ""})
        assert result.status == ResultStatus.FAILED

    def test_failed_on_exists_error(self, mock_client, delete_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = delete_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.FAILED

    def test_failed_on_delete_error(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        mock_client.delete.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = delete_module.execute(mock_client, ARGS)
        assert result.status == ResultStatus.FAILED
