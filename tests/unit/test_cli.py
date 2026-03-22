"""Unit tests for cli.py - all commands via click.testing.CliRunner."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from semp_workflow.cli import main
from semp_workflow.exceptions import ConfigError, TemplateError, WorkflowError
from semp_workflow.models import ActionResult, ResultStatus, WorkflowResult


MINIMAL_CONFIG = textwrap.dedent("""\
    semp:
      host: "https://broker:943"
      username: "admin"
      password: "secret"
      msg_vpn: "default"
    workflows: []
""")

MINIMAL_TEMPLATE = textwrap.dedent("""\
    workflow-templates:
      - name: "my-wf"
        inputs:
          required:
            - domain
        actions: []
""")


@pytest.fixture
def runner():
    return CliRunner()


def _failed_workflow():
    wf = WorkflowResult(workflow_name="wf", template_ref="wf.test")
    wf.task_results = [
        ActionResult(status=ResultStatus.FAILED, message="err", module="m", task_name="t")
    ]
    return wf


# ---------------------------------------------------------------------------
# run command
# ---------------------------------------------------------------------------

class TestRunCommand:
    def test_config_error_exits_2(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.load_config", side_effect=ConfigError("bad config")):
            result = runner.invoke(main, ["run", "--config", str(cfg)])
        assert result.exit_code == 2

    def test_template_error_exits_2(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.load_config", side_effect=TemplateError("bad tmpl")):
            result = runner.invoke(main, ["run", "--config", str(cfg)])
        assert result.exit_code == 2

    def test_workflow_error_exits_1(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.load_config", side_effect=WorkflowError("bad")):
            result = runner.invoke(main, ["run", "--config", str(cfg)])
        assert result.exit_code == 1

    def test_keyboard_interrupt_exits_130(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.load_config", side_effect=KeyboardInterrupt()):
            result = runner.invoke(main, ["run", "--config", str(cfg)])
        assert result.exit_code == 130

    def test_success_exits_0(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.Engine") as MockEngine:
            MockEngine.return_value.run.return_value = []
            result = runner.invoke(main, ["run", "--config", str(cfg)])
        assert result.exit_code == 0

    def test_failures_exits_1(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.Engine") as MockEngine:
            MockEngine.return_value.run.return_value = [_failed_workflow()]
            result = runner.invoke(main, ["run", "--config", str(cfg)])
        assert result.exit_code == 1

    def test_dry_run_flag_passed_to_engine(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.Engine") as MockEngine:
            MockEngine.return_value.run.return_value = []
            runner.invoke(main, ["run", "--config", str(cfg), "--dry-run"])
        call_kwargs = MockEngine.call_args[1]
        assert call_kwargs.get("dry_run") is True

    def test_fail_fast_flag_passed_to_engine(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.Engine") as MockEngine:
            MockEngine.return_value.run.return_value = []
            runner.invoke(main, ["run", "--config", str(cfg), "--fail-fast"])
        call_kwargs = MockEngine.call_args[1]
        assert call_kwargs.get("fail_fast") is True

    def test_templates_dir_override(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        with patch("semp_workflow.cli.Engine") as MockEngine:
            MockEngine.return_value.run.return_value = []
            runner.invoke(
                main, ["run", "--config", str(cfg), "--templates-dir", str(tmpl_dir)]
            )
        # Engine was called — the config's templates_dir was updated before Engine was created
        assert MockEngine.called


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------

class TestValidateCommand:
    def test_valid_config_with_templates_dir_exits_0(self, runner, tmp_path):
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        (tmpl_dir / "wf.yaml").write_text(MINIMAL_TEMPLATE)
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG + f"templates_dir: {tmpl_dir}\n")
        result = runner.invoke(main, ["validate", "--config", str(cfg)])
        assert result.exit_code == 0

    def test_config_error_exits_2(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.load_config", side_effect=ConfigError("bad")):
            result = runner.invoke(main, ["validate", "--config", str(cfg)])
        assert result.exit_code == 2

    def test_template_error_exits_2(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        with patch("semp_workflow.cli.load_config", side_effect=TemplateError("bad tmpl")):
            result = runner.invoke(main, ["validate", "--config", str(cfg)])
        assert result.exit_code == 2

    def test_missing_template_ref_exits_2(self, runner, tmp_path):
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        (tmpl_dir / "wf.yaml").write_text(MINIMAL_TEMPLATE)
        cfg = tmp_path / "config.yaml"
        cfg.write_text(textwrap.dedent(f"""\
            semp:
              host: "h"
              username: "u"
              password: "p"
              msg_vpn: "v"
            templates_dir: {tmpl_dir}
            workflows:
              - template: "wf.nonexistent"
                inputs: {{}}
        """))
        result = runner.invoke(main, ["validate", "--config", str(cfg)])
        assert result.exit_code == 2

    def test_templates_dir_override(self, runner, tmp_path):
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        (tmpl_dir / "wf.yaml").write_text(MINIMAL_TEMPLATE)
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        result = runner.invoke(
            main, ["validate", "--config", str(cfg), "--templates-dir", str(tmpl_dir)]
        )
        assert result.exit_code == 0

    def test_bundled_templates_used_when_no_dir(self, runner, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(MINIMAL_CONFIG)
        mock_file = MagicMock()
        mock_file.name = "wf.yaml"
        mock_file.read_text.return_value = MINIMAL_TEMPLATE
        mock_bundled = MagicMock()
        mock_bundled.iterdir.return_value = [mock_file]
        with (
            patch("semp_workflow.cli._get_bundled_templates_source", return_value=mock_bundled),
            patch("semp_workflow.config._get_bundled_templates_source", return_value=mock_bundled),
        ):
            result = runner.invoke(main, ["validate", "--config", str(cfg)])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# list-modules command
# ---------------------------------------------------------------------------

class TestListModulesCommand:
    def test_exits_0(self, runner):
        result = runner.invoke(main, ["list-modules"])
        assert result.exit_code == 0

    def test_output_contains_queue(self, runner):
        result = runner.invoke(main, ["list-modules"])
        assert "queue" in result.output

    def test_output_file_written(self, runner, tmp_path):
        out_file = tmp_path / "modules.md"
        result = runner.invoke(main, ["list-modules", "--output", str(out_file)])
        assert result.exit_code == 0
        assert out_file.exists()
        content = out_file.read_text()
        assert "# SEMP Workflow Automation" in content

    def test_output_file_path_echoed(self, runner, tmp_path):
        out_file = tmp_path / "modules.md"
        result = runner.invoke(main, ["list-modules", "--output", str(out_file)])
        assert str(out_file) in result.output


# ---------------------------------------------------------------------------
# init command
# ---------------------------------------------------------------------------

class TestInitCommand:
    def test_no_bundled_exits_2(self, runner):
        with patch("semp_workflow.cli._get_bundled_templates_source", return_value=None):
            result = runner.invoke(main, ["init"])
        assert result.exit_code == 2

    def test_copies_bundled_files(self, runner, tmp_path):
        mock_file = MagicMock()
        mock_file.name = "sap-outbound.yaml"
        mock_file.read_text.return_value = "workflow-templates: []\n"
        mock_bundled = MagicMock()
        mock_bundled.iterdir.return_value = [mock_file]
        out_dir = tmp_path / "out"
        with patch("semp_workflow.cli._get_bundled_templates_source", return_value=mock_bundled):
            result = runner.invoke(main, ["init", "--output-dir", str(out_dir)])
        assert result.exit_code == 0
        assert (out_dir / "sap-outbound.yaml").exists()
        assert (out_dir / "sap-outbound.yaml").read_text() == "workflow-templates: []\n"

    def test_skip_existing_without_force(self, runner, tmp_path):
        mock_file = MagicMock()
        mock_file.name = "sap-outbound.yaml"
        mock_file.read_text.return_value = "new content"
        mock_bundled = MagicMock()
        mock_bundled.iterdir.return_value = [mock_file]
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        (out_dir / "sap-outbound.yaml").write_text("original content")
        with patch("semp_workflow.cli._get_bundled_templates_source", return_value=mock_bundled):
            result = runner.invoke(main, ["init", "--output-dir", str(out_dir)])
        assert result.exit_code == 0
        # original content preserved
        assert (out_dir / "sap-outbound.yaml").read_text() == "original content"

    def test_overwrite_with_force(self, runner, tmp_path):
        mock_file = MagicMock()
        mock_file.name = "sap-outbound.yaml"
        mock_file.read_text.return_value = "new content"
        mock_bundled = MagicMock()
        mock_bundled.iterdir.return_value = [mock_file]
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        (out_dir / "sap-outbound.yaml").write_text("old content")
        with patch("semp_workflow.cli._get_bundled_templates_source", return_value=mock_bundled):
            result = runner.invoke(main, ["init", "--output-dir", str(out_dir), "--force"])
        assert result.exit_code == 0
        assert (out_dir / "sap-outbound.yaml").read_text() == "new content"

    def test_summary_printed(self, runner, tmp_path):
        mock_file = MagicMock()
        mock_file.name = "sap-outbound.yaml"
        mock_file.read_text.return_value = "content"
        mock_bundled = MagicMock()
        mock_bundled.iterdir.return_value = [mock_file]
        out_dir = tmp_path / "out"
        with patch("semp_workflow.cli._get_bundled_templates_source", return_value=mock_bundled):
            result = runner.invoke(main, ["init", "--output-dir", str(out_dir)])
        # Should print "1 file(s) written, 0 skipped"
        assert "1 file(s) written" in result.output


# ---------------------------------------------------------------------------
# --version option
# ---------------------------------------------------------------------------

class TestVersionOption:
    def test_version_exits_0(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0

    def test_version_output_contains_prog_name(self, runner):
        result = runner.invoke(main, ["--version"])
        assert "semp-workflow" in result.output
