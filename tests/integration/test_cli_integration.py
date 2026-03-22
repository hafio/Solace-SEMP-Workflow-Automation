"""Integration: CLI commands against a real Solace broker."""

import os
import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from semp_workflow.cli import main

from .conftest import PREFIX

pytestmark = pytest.mark.integration

# Resource names that the CLI test may create via the fixture template
TEST_PREFIX = f"{PREFIX}CLI"
QUEUE_NAME  = f"{TEST_PREFIX}-QUEUE"
RDP_NAME    = f"{TEST_PREFIX}-RDP"
RC_NAME     = f"{TEST_PREFIX}-RC"
CU_NAME     = f"{TEST_PREFIX}-USER"
CP_NAME     = f"{TEST_PREFIX}-CP"
ACL_NAME    = f"{TEST_PREFIX}-ACL"

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _write_config(path, host, username, password, msg_vpn, verify_ssl, templates_dir):
    # Use forward slashes so Windows paths don't trigger YAML escape sequences.
    templates_dir_fwd = str(templates_dir).replace("\\", "/")
    path.write_text(textwrap.dedent(f"""\
        semp:
          host: "{host}"
          username: "{username}"
          password: "{password}"
          msg_vpn: "{msg_vpn}"
          verify_ssl: {str(verify_ssl).lower()}
          timeout: 30
        templates_dir: "{templates_dir_fwd}"
        workflows:
          - template: "test-artifacts.create"
            inputs:
              prefix: "{TEST_PREFIX}"
    """))


@pytest.fixture
def config_file(tmp_path):
    cfg = tmp_path / "config.yaml"
    _write_config(
        cfg,
        host=os.environ["SEMP_HOST"],
        username=os.environ["SEMP_USERNAME"],
        password=os.environ["SEMP_PASSWORD"],
        msg_vpn=os.environ["SEMP_MSG_VPN"],
        verify_ssl=os.environ.get("SEMP_VERIFY_SSL", "false").lower() == "true",
        templates_dir=FIXTURES_DIR,
    )
    return cfg


@pytest.fixture(autouse=True)
def cleanup(semp_client):
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


class TestValidateCommand:
    def test_valid_config_exits_zero(self, config_file):
        runner = CliRunner()
        result = runner.invoke(main, ["validate", "--config", str(config_file)])
        assert result.exit_code == 0

    def test_invalid_template_ref_exits_nonzero(self, tmp_path):
        cfg = tmp_path / "bad.yaml"
        _write_config(
            cfg,
            host=os.environ["SEMP_HOST"],
            username=os.environ["SEMP_USERNAME"],
            password=os.environ["SEMP_PASSWORD"],
            msg_vpn=os.environ["SEMP_MSG_VPN"],
            verify_ssl=False,
            templates_dir=FIXTURES_DIR,
        )
        # Replace the valid template name with a nonexistent one
        cfg.write_text(
            cfg.read_text().replace("test-artifacts.create", "bad.nonexistent")
        )
        runner = CliRunner()
        result = runner.invoke(main, ["validate", "--config", str(cfg)])
        assert result.exit_code != 0


class TestListModulesCommand:
    def test_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["list-modules"])
        assert result.exit_code == 0

    def test_output_contains_queue_add(self):
        runner = CliRunner()
        result = runner.invoke(main, ["list-modules"])
        assert "queue.add" in result.output

    def test_output_contains_all_module_types(self):
        runner = CliRunner()
        result = runner.invoke(main, ["list-modules"])
        for name in [
            "acl_profile.add", "acl_profile.delete",
            "client_profile.add", "client_profile.delete",
            "client_username.add", "client_username.delete",
            "queue.add", "queue.delete", "queue.update",
            "q_sub.add", "q_sub.delete",
            "rdp.add", "rdp.delete",
            "rdp_rc.add", "rdp_rc.delete",
            "rdp_qb.add", "rdp_qb.delete",
        ]:
            assert name in result.output, f"Missing module in list-modules output: {name}"


class TestRunCommand:
    def test_dry_run_exits_zero(self, config_file):
        runner = CliRunner()
        result = runner.invoke(
            main, ["run", "--config", str(config_file), "--dry-run"]
        )
        assert result.exit_code == 0

    def test_run_creates_resources(self, config_file, semp_client):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "--config", str(config_file)])
        assert result.exit_code == 0
        # Verify at least the queue and RDP were actually created
        found_q, _ = semp_client.exists(f"queues/{semp_client._enc(QUEUE_NAME)}")
        found_rdp, _ = semp_client.exists(
            f"restDeliveryPoints/{semp_client._enc(RDP_NAME)}"
        )
        assert found_q is True
        assert found_rdp is True
