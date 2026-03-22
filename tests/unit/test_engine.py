"""Unit tests for engine.py."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from semp_workflow.config import AppConfig, SempConfig, WorkflowEntry, load_templates
from semp_workflow.exceptions import SEMPError, TemplateError
from semp_workflow.models import ActionResult, ResultStatus, WorkflowResult


SIMPLE_TEMPLATE = textwrap.dedent("""\
    workflow-templates:
      - name: "simple"
        inputs:
          required:
            - domain
          optional:
            queue_name: "{{ global_vars.q_name_tpl }}"
        actions:
          - name: "Create Queue"
            module: "queue.add"
            args:
              queueName: "{{ inputs.queue_name }}"
""")

CIRCULAR_TEMPLATE = textwrap.dedent("""\
    workflow-templates:
      - name: "circ"
        inputs:
          optional:
            a: "{{ inputs.b }}"
            b: "{{ inputs.a }}"
        actions: []
""")

MULTI_ACTION_TEMPLATE = textwrap.dedent("""\
    workflow-templates:
      - name: "multi"
        inputs:
          required:
            - domain
        actions:
          - name: "Create Queue"
            module: "queue.add"
            args:
              queueName: "{{ inputs.domain }}"
          - name: "Add Sub"
            module: "subscription.add"
            args:
              queueName: "{{ inputs.domain }}"
              subscriptionTopic: "FCM/>"
""")


def _make_config(tmp_path, templates_content=SIMPLE_TEMPLATE):
    tmpl_dir = tmp_path / "templates"
    tmpl_dir.mkdir()
    (tmpl_dir / "wf.yaml").write_text(templates_content)

    semp = SempConfig(
        host="https://broker:943",
        username="admin",
        password="secret",
        msg_vpn="default",
    )
    return AppConfig(
        semp=semp,
        # q_name_tpl contains embedded Jinja2 so the second-pass re-render
        # can resolve {{ inputs.domain }} after the first pass unwraps it.
        global_vars={"q_name_tpl": "Q-{{ inputs.domain }}"},
        workflows=[],
        templates_dir=tmpl_dir,
        use_bundled_templates=False,
    )


@pytest.fixture(autouse=True)
def patch_output():
    """Suppress all console output and prevent sys.exit(1) from print_recap."""
    with (
        patch("semp_workflow.engine.print_banner"),
        patch("semp_workflow.engine.print_recap"),
        patch("semp_workflow.engine.print_dry_run_banner"),
        patch("semp_workflow.engine.print_workflow_header"),
        patch("semp_workflow.engine.print_task_result"),
    ):
        yield


@pytest.fixture
def mock_semp_client():
    client = MagicMock()
    client.exists.return_value = (False, None)
    client.create.return_value = {}
    return client


def _make_engine(config, mock_client, dry_run=False, fail_fast=False):
    from semp_workflow.engine import Engine
    with patch("semp_workflow.engine.SempClient", return_value=mock_client):
        engine = Engine(config, dry_run=dry_run, fail_fast=fail_fast)
    return engine


class TestResolveTemplate:
    def test_found(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        engine = _make_engine(config, mock_semp_client)
        tmpl = engine._resolve_template("wf.simple")
        assert tmpl.name == "simple"

    def test_not_found_raises(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        engine = _make_engine(config, mock_semp_client)
        with pytest.raises(TemplateError, match="not found"):
            engine._resolve_template("wf.missing")


class TestRunAction:
    def test_success(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        engine = _make_engine(config, mock_semp_client)
        context = {"inputs": {"queue_name": "MY-QUEUE"}, "global_vars": {}}
        result = engine._run_action(
            "Create Queue", "queue.add", {"queueName": "{{ inputs.queue_name }}"}, context
        )
        assert result.status == ResultStatus.OK

    def test_unknown_module_fails(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        engine = _make_engine(config, mock_semp_client)
        result = engine._run_action("Task", "nonexistent.module", {}, {})
        assert result.status == ResultStatus.FAILED

    def test_template_error_fails(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        engine = _make_engine(config, mock_semp_client)
        # Undefined variable in args → TemplateError → FAILED
        result = engine._run_action(
            "Task", "queue.add", {"queueName": "{{ inputs.undefined_var }}"}, {}
        )
        assert result.status == ResultStatus.FAILED

    def test_module_and_task_name_set(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        engine = _make_engine(config, mock_semp_client)
        context = {"inputs": {"queue_name": "Q"}, "global_vars": {}}
        result = engine._run_action("My Task", "queue.add", {"queueName": "Q"}, context)
        assert result.task_name == "My Task"
        assert result.module == "queue.add"


class TestRunWorkflow:
    def test_valid_inputs_runs_actions(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        config.workflows = [WorkflowEntry(template="wf.simple", inputs={"domain": "HQ"})]
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        assert len(results) == 1
        assert not results[0].has_failures

    def test_required_input_missing_produces_failed_result(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        config.workflows = [WorkflowEntry(template="wf.simple", inputs={})]
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        assert results[0].has_failures
        assert "domain" in results[0].task_results[0].message

    def test_unexpected_input_produces_failed_result(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        config.workflows = [
            WorkflowEntry(template="wf.simple", inputs={"domain": "HQ", "typo": "bad"})
        ]
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        assert results[0].has_failures

    def test_second_pass_renders_input_default(self, tmp_path, mock_semp_client):
        # queue_name default = "Q-{{ inputs.domain }}" — requires second pass
        config = _make_config(tmp_path)
        config.workflows = [WorkflowEntry(template="wf.simple", inputs={"domain": "HQ"})]
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        # The queue.add call should have been made with queueName="Q-HQ"
        call_args = mock_semp_client.create.call_args
        assert call_args is not None
        payload = call_args[0][1]  # second positional arg to create()
        assert payload["queueName"] == "Q-HQ"

    def test_circular_reference_produces_failed_result(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path, templates_content=CIRCULAR_TEMPLATE)
        config.workflows = [WorkflowEntry(template="wf.circ", inputs={})]
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        assert results[0].has_failures


class TestRunOptions:
    def test_dry_run_produces_dryrun_results(self, tmp_path, mock_semp_client):
        mock_semp_client.exists.return_value = (False, None)
        config = _make_config(tmp_path)
        config.workflows = [WorkflowEntry(template="wf.simple", inputs={"domain": "HQ"})]
        engine = _make_engine(config, mock_semp_client, dry_run=True)
        results = engine.run()
        assert all(
            r.status == ResultStatus.DRYRUN
            for wf in results
            for r in wf.task_results
        )
        mock_semp_client.create.assert_not_called()

    def test_fail_fast_stops_after_first_failure(self, tmp_path, mock_semp_client):
        # Two workflows: first missing required input (fails), second valid
        config = _make_config(tmp_path)
        config.workflows = [
            WorkflowEntry(template="wf.simple", inputs={}),       # will fail
            WorkflowEntry(template="wf.simple", inputs={"domain": "HQ"}),  # would succeed
        ]
        engine = _make_engine(config, mock_semp_client, fail_fast=True)
        results = engine.run()
        assert len(results) == 1  # stopped after first

    def test_multiple_workflows_all_run_without_fail_fast(self, tmp_path, mock_semp_client):
        config = _make_config(tmp_path)
        config.workflows = [
            WorkflowEntry(template="wf.simple", inputs={"domain": "HQ"}),
            WorkflowEntry(template="wf.simple", inputs={"domain": "SG"}),
        ]
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        assert len(results) == 2


class TestBundledTemplates:
    def test_bundled_templates_loaded_when_configured(self, mock_semp_client):
        """Engine uses _get_bundled_templates_source() when use_bundled_templates=True."""
        template_content = textwrap.dedent("""\
            workflow-templates:
              - name: "bundled-wf"
                inputs: {}
                actions: []
        """)
        mock_file = MagicMock()
        mock_file.name = "bundled.yaml"
        mock_file.read_text.return_value = template_content
        mock_bundled = MagicMock()
        mock_bundled.iterdir.return_value = [mock_file]

        semp = SempConfig(
            host="https://broker:943",
            username="admin",
            password="secret",
            msg_vpn="default",
        )
        config = AppConfig(
            semp=semp,
            global_vars={},
            workflows=[],
            templates_dir=Path("nonexistent"),
            use_bundled_templates=True,
        )
        with (
            patch("semp_workflow.engine._get_bundled_templates_source", return_value=mock_bundled),
            patch("semp_workflow.engine.SempClient", return_value=mock_semp_client),
        ):
            from semp_workflow.engine import Engine
            engine = Engine(config)
        assert "bundled.bundled-wf" in engine.templates


class TestRunActionEdgeCases:
    def test_unexpected_exception_returns_failed(self, tmp_path, mock_semp_client):
        """Unexpected exceptions in module.execute are caught and return FAILED."""
        config = _make_config(tmp_path)
        engine = _make_engine(config, mock_semp_client)
        mock_module = MagicMock()
        mock_module.execute.side_effect = RuntimeError("totally unexpected")
        with patch("semp_workflow.engine.get_module", return_value=mock_module):
            result = engine._run_action("Task", "queue.add", {}, {})
        assert result.status == ResultStatus.FAILED
        assert "Unexpected error" in result.message

    def test_fail_fast_stops_within_workflow(self, tmp_path, mock_semp_client):
        """With fail_fast=True, engine stops after first FAILED action in a workflow."""
        two_action_template = textwrap.dedent("""\
            workflow-templates:
              - name: "two-actions"
                inputs:
                  required:
                    - domain
                actions:
                  - name: "Action 1"
                    module: "queue.add"
                    args:
                      queueName: "{{ inputs.domain }}"
                  - name: "Action 2"
                    module: "queue.add"
                    args:
                      queueName: "{{ inputs.domain }}-2"
        """)
        config = _make_config(tmp_path, templates_content=two_action_template)
        config.workflows = [WorkflowEntry(template="wf.two-actions", inputs={"domain": "HQ"})]
        # First create call fails with a SEMP error → QueueAdd returns FAILED
        mock_semp_client.exists.return_value = (False, None)
        mock_semp_client.create.side_effect = SEMPError("err", status_code=500, semp_code=99)
        engine = _make_engine(config, mock_semp_client, fail_fast=True)
        results = engine.run()
        # Only one task result — stopped after the first FAILED action
        assert len(results[0].task_results) == 1
        assert results[0].task_results[0].status == ResultStatus.FAILED

    def test_fail_fast_workflow_failure_then_workflow_stops(self, tmp_path, mock_semp_client):
        """With fail_fast=True and a workflow task failure, subsequent workflows don't run."""
        config = _make_config(tmp_path)
        # First workflow fails (missing required input), second would succeed
        config.workflows = [
            WorkflowEntry(template="wf.simple", inputs={"domain": "HQ"}),
            WorkflowEntry(template="wf.simple", inputs={"domain": "SG"}),
        ]
        # Make first workflow's action fail
        mock_semp_client.exists.return_value = (False, None)
        mock_semp_client.create.side_effect = SEMPError("err", status_code=500, semp_code=99)
        engine = _make_engine(config, mock_semp_client, fail_fast=True)
        results = engine.run()
        assert len(results) == 1  # stopped after the first workflow failure

    def test_second_pass_template_error_produces_failed(self, tmp_path, mock_semp_client):
        """A TemplateError during second-pass rendering raises WorkflowError → FAILED result."""
        # global_vars.tpl = "{{ inputs.undefined_var }}" — resolves in first pass to that string,
        # then fails in second pass because inputs.undefined_var is not in validated_inputs.
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        (tmpl_dir / "wf.yaml").write_text(textwrap.dedent("""\
            workflow-templates:
              - name: "second-pass-err"
                inputs:
                  optional:
                    name: "{{ global_vars.tpl }}"
                actions: []
        """))
        semp = SempConfig(
            host="https://broker:943", username="admin",
            password="secret", msg_vpn="default",
        )
        config = AppConfig(
            semp=semp,
            global_vars={"tpl": "{{ inputs.undefined_var }}"},
            workflows=[WorkflowEntry(template="wf.second-pass-err", inputs={})],
            templates_dir=tmpl_dir,
            use_bundled_templates=False,
        )
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        assert results[0].has_failures

    def test_circular_detection_via_global_vars_produces_failed(self, tmp_path, mock_semp_client):
        """Circular references detected after second pass (both inputs still contain {{)."""
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        (tmpl_dir / "wf.yaml").write_text(textwrap.dedent("""\
            workflow-templates:
              - name: "circular"
                inputs:
                  optional:
                    a: "{{ global_vars.tpl_a }}"
                    b: "{{ global_vars.tpl_b }}"
                actions: []
        """))
        semp = SempConfig(
            host="https://broker:943", username="admin",
            password="secret", msg_vpn="default",
        )
        # After first pass: a = "{{ inputs.b }}", b = "{{ inputs.a }}"
        # After second pass: a renders {{ inputs.b }} = "{{ inputs.a }}" — still has {{
        # → circular detection fires
        config = AppConfig(
            semp=semp,
            global_vars={"tpl_a": "{{ inputs.b }}", "tpl_b": "{{ inputs.a }}"},
            workflows=[WorkflowEntry(template="wf.circular", inputs={})],
            templates_dir=tmpl_dir,
            use_bundled_templates=False,
        )
        engine = _make_engine(config, mock_semp_client)
        results = engine.run()
        assert results[0].has_failures
