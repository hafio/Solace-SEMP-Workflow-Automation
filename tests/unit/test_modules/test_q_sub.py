"""Unit tests for modules/q_sub.py."""

import pytest

from semp_workflow.exceptions import SEMPError
from semp_workflow.models import ResultStatus
from semp_workflow.modules.q_sub import SubscriptionAdd, SubscriptionDelete
from semp_workflow.semp.client import ALREADY_EXISTS


@pytest.fixture
def add_module():
    return SubscriptionAdd()


@pytest.fixture
def delete_module():
    return SubscriptionDelete()


class TestSubscriptionAdd:
    def test_ok_when_not_exists(self, mock_client, add_module):
        mock_client.create.return_value = {}
        result = add_module.execute(
            mock_client, {"queueName": "Q1", "subscriptionTopic": "FCM/>"}
        )
        assert result.status == ResultStatus.OK

    def test_skipped_on_already_exists_error(self, mock_client, add_module):
        mock_client.create.side_effect = SEMPError(
            "already exists", status_code=400, semp_code=ALREADY_EXISTS
        )
        result = add_module.execute(
            mock_client, {"queueName": "Q1", "subscriptionTopic": "FCM/>"}
        )
        assert result.status == ResultStatus.SKIPPED

    def test_failed_on_other_error(self, mock_client, add_module):
        mock_client.create.side_effect = SEMPError("err", status_code=400, semp_code=99)
        result = add_module.execute(
            mock_client, {"queueName": "Q1", "subscriptionTopic": "FCM/>"}
        )
        assert result.status == ResultStatus.FAILED

    def test_failed_on_missing_args(self, mock_client, add_module):
        result = add_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.FAILED

    def test_dryrun_not_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (False, None)
        result = add_module.execute(
            mock_client,
            {"queueName": "Q1", "subscriptionTopic": "FCM/>"},
            dry_run=True,
        )
        assert result.status == ResultStatus.DRYRUN
        mock_client.create.assert_not_called()

    def test_dryrun_already_exists(self, mock_client, add_module):
        mock_client.exists.return_value = (True, {})
        result = add_module.execute(
            mock_client,
            {"queueName": "Q1", "subscriptionTopic": "FCM/>"},
            dry_run=True,
        )
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_exists_check_error_treated_as_not_exists(self, mock_client, add_module):
        # When dry_run and exists() raises, treat as not-exists → return DRYRUN
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = add_module.execute(
            mock_client,
            {"queueName": "Q1", "subscriptionTopic": "FCM/>"},
            dry_run=True,
        )
        assert result.status == ResultStatus.DRYRUN


class TestSubscriptionDelete:
    def test_ok_when_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(
            mock_client, {"queueName": "Q1", "subscriptionTopic": "FCM/>"}
        )
        assert result.status == ResultStatus.OK
        mock_client.delete.assert_called_once()

    def test_skipped_when_not_exists(self, mock_client, delete_module):
        mock_client.exists.return_value = (False, None)
        result = delete_module.execute(
            mock_client, {"queueName": "Q1", "subscriptionTopic": "FCM/>"}
        )
        assert result.status == ResultStatus.SKIPPED

    def test_failed_on_missing_args(self, mock_client, delete_module):
        result = delete_module.execute(mock_client, {"queueName": "Q1"})
        assert result.status == ResultStatus.FAILED

    def test_dryrun(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        result = delete_module.execute(
            mock_client,
            {"queueName": "Q1", "subscriptionTopic": "FCM/>"},
            dry_run=True,
        )
        assert result.status == ResultStatus.DRYRUN
        mock_client.delete.assert_not_called()

    def test_failed_on_exists_error(self, mock_client, delete_module):
        mock_client.exists.side_effect = SEMPError("err", status_code=500, semp_code=1)
        result = delete_module.execute(
            mock_client, {"queueName": "Q1", "subscriptionTopic": "FCM/>"}
        )
        assert result.status == ResultStatus.FAILED

    def test_failed_on_delete_error(self, mock_client, delete_module):
        mock_client.exists.return_value = (True, {})
        mock_client.delete.side_effect = SEMPError("err", status_code=400, semp_code=1)
        result = delete_module.execute(
            mock_client, {"queueName": "Q1", "subscriptionTopic": "FCM/>"}
        )
        assert result.status == ResultStatus.FAILED
