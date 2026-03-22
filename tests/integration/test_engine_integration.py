"""Integration: full Engine.run() against a real Solace broker.

Uses a self-contained fixture template (tests/integration/fixtures/test-artifacts.yaml)
that exercises every supported broker artifact type:
  acl_profile, client_profile, client_username,
  queue, q_sub (subscription),
  rdp, rdp_rc (REST consumer), rdp_qb (queue binding)
"""

import os
from pathlib import Path

import pytest

from semp_workflow.config import AppConfig, SempConfig, WorkflowEntry
from semp_workflow.models import ResultStatus

from .conftest import PREFIX

pytestmark = pytest.mark.integration

# All resources created by this test share this prefix
TEST_PREFIX = f"{PREFIX}ENG"

# Input dict passed to both the "create" and "delete" workflows
INPUTS = {"prefix": TEST_PREFIX}

# Derived resource names — must match the template defaults exactly
ACL_NAME   = f"{TEST_PREFIX}-ACL"
CP_NAME    = f"{TEST_PREFIX}-CP"
CU_NAME    = f"{TEST_PREFIX}-USER"
QUEUE_NAME = f"{TEST_PREFIX}-QUEUE"
RDP_NAME   = f"{TEST_PREFIX}-RDP"
RC_NAME    = f"{TEST_PREFIX}-RC"

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _make_config(workflows: list[WorkflowEntry]) -> AppConfig:
    semp = SempConfig(
        host=os.environ["SEMP_HOST"],
        username=os.environ["SEMP_USERNAME"],
        password=os.environ["SEMP_PASSWORD"],
        msg_vpn=os.environ["SEMP_MSG_VPN"],
        verify_ssl=os.environ.get("SEMP_VERIFY_SSL", "false").lower() == "true",
    )
    return AppConfig(
        semp=semp,
        global_vars={},
        workflows=workflows,
        templates_dir=FIXTURES_DIR,
        use_bundled_templates=False,
    )


@pytest.fixture(autouse=True)
def cleanup_all(semp_client):
    """Delete every resource that may have been created, in dependency order."""
    yield
    for path in [
        f"restDeliveryPoints/{semp_client._enc(RDP_NAME)}"
        f"/queueBindings/{semp_client._enc(QUEUE_NAME)}",
        f"restDeliveryPoints/{semp_client._enc(RDP_NAME)}"
        f"/restConsumers/{semp_client._enc(RC_NAME)}",
        f"restDeliveryPoints/{semp_client._enc(RDP_NAME)}",
        f"queues/{semp_client._enc(QUEUE_NAME)}",
        f"clientUsernames/{semp_client._enc(CU_NAME)}",
        f"clientProfiles/{semp_client._enc(CP_NAME)}",
        f"aclProfiles/{semp_client._enc(ACL_NAME)}",
    ]:
        try:
            semp_client.delete(path)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Dry-run: engine must produce DRYRUN results and create nothing on the broker
# ─────────────────────────────────────────────────────────────────────────────

class TestDryRun:
    def test_all_results_are_dryrun(self):
        from semp_workflow.engine import Engine

        config = _make_config(
            [WorkflowEntry(template="test-artifacts.create", inputs=INPUTS)]
        )
        results = Engine(config, dry_run=True).run()

        assert len(results) == 1
        assert not results[0].has_failures
        assert all(r.status == ResultStatus.DRYRUN for r in results[0].task_results)

    def test_no_broker_objects_created(self, semp_client):
        from semp_workflow.engine import Engine

        Engine(_make_config(
            [WorkflowEntry(template="test-artifacts.create", inputs=INPUTS)]
        ), dry_run=True).run()

        for path in [
            f"queues/{semp_client._enc(QUEUE_NAME)}",
            f"restDeliveryPoints/{semp_client._enc(RDP_NAME)}",
            f"aclProfiles/{semp_client._enc(ACL_NAME)}",
        ]:
            found, _ = semp_client.exists(path)
            assert found is False, f"Dry-run unexpectedly created: {path}"


# ─────────────────────────────────────────────────────────────────────────────
# Create / idempotency / delete lifecycle
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateAndDelete:
    def test_create_all_artifacts_ok(self):
        """First run: every action should succeed (OK or SKIPPED)."""
        from semp_workflow.engine import Engine

        results = Engine(_make_config(
            [WorkflowEntry(template="test-artifacts.create", inputs=INPUTS)]
        )).run()

        assert len(results) == 1
        assert not results[0].has_failures
        assert all(
            r.status in (ResultStatus.OK, ResultStatus.SKIPPED)
            for r in results[0].task_results
        )

    def test_rerun_all_skipped(self):
        """Second run against an already-provisioned broker: all SKIPPED."""
        from semp_workflow.engine import Engine

        config = _make_config(
            [WorkflowEntry(template="test-artifacts.create", inputs=INPUTS)]
        )
        Engine(config).run()
        results = Engine(config).run()

        assert not results[0].has_failures
        assert all(
            r.status == ResultStatus.SKIPPED for r in results[0].task_results
        )

    def test_all_artifacts_exist_after_create(self, semp_client):
        """Verify the broker actually has the created resources."""
        from semp_workflow.engine import Engine

        Engine(_make_config(
            [WorkflowEntry(template="test-artifacts.create", inputs=INPUTS)]
        )).run()

        for path in [
            f"aclProfiles/{semp_client._enc(ACL_NAME)}",
            f"clientProfiles/{semp_client._enc(CP_NAME)}",
            f"clientUsernames/{semp_client._enc(CU_NAME)}",
            f"queues/{semp_client._enc(QUEUE_NAME)}",
            f"restDeliveryPoints/{semp_client._enc(RDP_NAME)}",
        ]:
            found, _ = semp_client.exists(path)
            assert found is True, f"Expected broker object not found: {path}"

    def test_delete_after_create(self):
        """Create then delete: all delete actions should be OK or SKIPPED."""
        from semp_workflow.engine import Engine

        Engine(_make_config(
            [WorkflowEntry(template="test-artifacts.create", inputs=INPUTS)]
        )).run()

        results = Engine(_make_config(
            [WorkflowEntry(template="test-artifacts.delete", inputs=INPUTS)]
        )).run()

        assert len(results) == 1
        assert not results[0].has_failures
        assert all(
            r.status in (ResultStatus.OK, ResultStatus.SKIPPED)
            for r in results[0].task_results
        )

    def test_delete_again_all_skipped(self):
        """Second delete on an already-clean broker: all SKIPPED."""
        from semp_workflow.engine import Engine

        delete_cfg = _make_config(
            [WorkflowEntry(template="test-artifacts.delete", inputs=INPUTS)]
        )
        Engine(delete_cfg).run()
        results = Engine(delete_cfg).run()

        assert not results[0].has_failures
        assert all(
            r.status == ResultStatus.SKIPPED for r in results[0].task_results
        )

    def test_no_artifacts_remain_after_delete(self, semp_client):
        """Verify the broker has no residual resources after the delete workflow."""
        from semp_workflow.engine import Engine

        Engine(_make_config(
            [WorkflowEntry(template="test-artifacts.create", inputs=INPUTS)]
        )).run()
        Engine(_make_config(
            [WorkflowEntry(template="test-artifacts.delete", inputs=INPUTS)]
        )).run()

        for path in [
            f"aclProfiles/{semp_client._enc(ACL_NAME)}",
            f"clientProfiles/{semp_client._enc(CP_NAME)}",
            f"clientUsernames/{semp_client._enc(CU_NAME)}",
            f"queues/{semp_client._enc(QUEUE_NAME)}",
            f"restDeliveryPoints/{semp_client._enc(RDP_NAME)}",
        ]:
            found, _ = semp_client.exists(path)
            assert found is False, f"Resource still present after delete: {path}"
