"""Unit tests for output.py."""

import pytest

from semp_workflow.models import ActionResult, ResultStatus, WorkflowResult
from semp_workflow import output


def _make_wf_result(statuses, name="test"):
    wf = WorkflowResult(workflow_name=name, template_ref=f"wf.{name}")
    for s in statuses:
        wf.task_results.append(
            ActionResult(status=s, message="msg", module="queue.add", task_name="Task")
        )
    return wf


# ---------------------------------------------------------------------------
# print_banner
# ---------------------------------------------------------------------------

class TestPrintBanner:
    def test_prints_semp_heading(self, capsys):
        output.print_banner()
        captured = capsys.readouterr()
        assert "SEMP Workflow Automation" in captured.out

    def test_prints_separator(self, capsys):
        output.print_banner()
        captured = capsys.readouterr()
        assert "=" * 70 in captured.out


# ---------------------------------------------------------------------------
# print_workflow_header
# ---------------------------------------------------------------------------

class TestPrintWorkflowHeader:
    def test_includes_workflow_name(self, capsys):
        output.print_workflow_header("my-wf", "wf.my-wf", {}, index=1)
        captured = capsys.readouterr()
        assert "my-wf" in captured.out

    def test_includes_template_ref(self, capsys):
        output.print_workflow_header("my-wf", "wf.my-wf", {}, index=1)
        captured = capsys.readouterr()
        assert "wf.my-wf" in captured.out

    def test_includes_index(self, capsys):
        output.print_workflow_header("my-wf", "wf.my-wf", {}, index=3)
        captured = capsys.readouterr()
        assert "3" in captured.out

    def test_with_inputs_shown(self, capsys):
        output.print_workflow_header("my-wf", "wf.my-wf", {"domain": "HQ"}, index=1)
        captured = capsys.readouterr()
        assert "domain=HQ" in captured.out

    def test_without_inputs_no_inputs_line(self, capsys):
        output.print_workflow_header("my-wf", "wf.my-wf", {}, index=1)
        captured = capsys.readouterr()
        assert "Inputs:" not in captured.out


# ---------------------------------------------------------------------------
# print_task_result
# ---------------------------------------------------------------------------

class TestPrintTaskResult:
    def test_ok_shows_changed(self, capsys):
        result = ActionResult(
            status=ResultStatus.OK, message="", module="queue.add", task_name="Create Queue"
        )
        output.print_task_result(result)
        assert "changed" in capsys.readouterr().out

    def test_skipped_shows_skipped(self, capsys):
        result = ActionResult(
            status=ResultStatus.SKIPPED, message="", module="queue.add", task_name="T"
        )
        output.print_task_result(result)
        assert "skipped" in capsys.readouterr().out

    def test_dryrun_shows_dryrun(self, capsys):
        result = ActionResult(
            status=ResultStatus.DRYRUN, message="", module="queue.add", task_name="T"
        )
        output.print_task_result(result)
        assert "dryrun" in capsys.readouterr().out

    def test_failed_shows_failed(self, capsys):
        result = ActionResult(
            status=ResultStatus.FAILED, message="Error occurred", module="queue.add", task_name="T"
        )
        output.print_task_result(result)
        out = capsys.readouterr().out
        assert "FAILED" in out
        assert "Error occurred" in out

    def test_task_name_used_when_set(self, capsys):
        result = ActionResult(
            status=ResultStatus.OK, message="", module="queue.add", task_name="My Custom Task"
        )
        output.print_task_result(result)
        assert "My Custom Task" in capsys.readouterr().out

    def test_module_used_as_name_fallback(self, capsys):
        result = ActionResult(
            status=ResultStatus.OK, message="", module="rdp.add", task_name=""
        )
        output.print_task_result(result)
        assert "rdp.add" in capsys.readouterr().out

    def test_message_shown_for_ok(self, capsys):
        result = ActionResult(
            status=ResultStatus.OK, message="Queue created", module="q", task_name="T"
        )
        output.print_task_result(result)
        assert "Queue created" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# print_dry_run_banner
# ---------------------------------------------------------------------------

class TestPrintDryRunBanner:
    def test_prints_dry_run_text(self, capsys):
        output.print_dry_run_banner()
        assert "DRY RUN" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# print_recap
# ---------------------------------------------------------------------------

class TestPrintRecap:
    def test_success_prints_completed(self, capsys):
        wf = _make_wf_result([ResultStatus.OK])
        output.print_recap([wf])
        assert "completed successfully" in capsys.readouterr().out

    def test_failure_exits_1(self):
        wf = _make_wf_result([ResultStatus.FAILED])
        with pytest.raises(SystemExit) as exc_info:
            output.print_recap([wf])
        assert exc_info.value.code == 1

    def test_failure_prints_some_tasks_failed(self, capsys):
        wf = _make_wf_result([ResultStatus.FAILED])
        with pytest.raises(SystemExit):
            output.print_recap([wf])
        assert "failed" in capsys.readouterr().out

    def test_counts_in_output(self, capsys):
        wf = _make_wf_result([ResultStatus.OK, ResultStatus.SKIPPED, ResultStatus.DRYRUN])
        output.print_recap([wf])
        out = capsys.readouterr().out
        assert "changed=1" in out
        assert "skipped=1" in out
        assert "dryrun=1" in out

    def test_multiple_workflows_indexed(self, capsys):
        output.print_recap([_make_wf_result([ResultStatus.OK], "wf1"),
                             _make_wf_result([ResultStatus.OK], "wf2")])
        out = capsys.readouterr().out
        assert "Workflow 1" in out
        assert "Workflow 2" in out

    def test_empty_results_no_exit(self, capsys):
        output.print_recap([])
        # Should not raise SystemExit
        assert "completed successfully" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# print_module_list
# ---------------------------------------------------------------------------

class TestPrintModuleList:
    def test_groups_by_object_prefix(self, capsys):
        output.print_module_list(["queue.add", "queue.delete", "rdp.add"])
        out = capsys.readouterr().out
        assert "queue" in out
        assert "rdp" in out

    def test_lists_verbs(self, capsys):
        output.print_module_list(["queue.add", "queue.delete"])
        out = capsys.readouterr().out
        assert "queue.add" in out
        assert "queue.delete" in out


# ---------------------------------------------------------------------------
# print_validation_ok
# ---------------------------------------------------------------------------

class TestPrintValidationOk:
    def test_prints_config_path(self, capsys):
        output.print_validation_ok("/path/to/config.yaml", 5, 3)
        out = capsys.readouterr().out
        assert "/path/to/config.yaml" in out

    def test_prints_template_count(self, capsys):
        output.print_validation_ok("cfg.yaml", 7, 2)
        out = capsys.readouterr().out
        assert "7" in out

    def test_prints_workflow_count(self, capsys):
        output.print_validation_ok("cfg.yaml", 5, 4)
        out = capsys.readouterr().out
        assert "4" in out

    def test_prints_passed(self, capsys):
        output.print_validation_ok("cfg.yaml", 1, 1)
        assert "passed" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# print_error
# ---------------------------------------------------------------------------

class TestPrintError:
    def test_prints_to_stderr(self, capsys):
        output.print_error("Something went wrong")
        captured = capsys.readouterr()
        assert "Something went wrong" in captured.err

    def test_message_prefixed_with_error(self, capsys):
        output.print_error("bad input")
        assert "ERROR" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# render_module_docs_md
# ---------------------------------------------------------------------------

class TestRenderModuleDocsMd:
    def test_returns_markdown_header(self):
        md = output.render_module_docs_md({
            "queue.add": {"description": "Add a queue", "params": {}}
        })
        assert "# SEMP Workflow Automation" in md

    def test_includes_module_name(self):
        md = output.render_module_docs_md({
            "queue.add": {"description": "Add a queue", "params": {}}
        })
        assert "queue.add" in md

    def test_no_params_shows_placeholder(self):
        md = output.render_module_docs_md({
            "rdp.delete": {"description": "Delete RDP", "params": {}}
        })
        assert "_No parameters._" in md

    def test_params_shown_in_table(self):
        md = output.render_module_docs_md({
            "queue.add": {
                "description": "Add a queue",
                "params": {
                    "queueName": {
                        "type": "string",
                        "required": True,
                        "description": "Queue name",
                    }
                },
            }
        })
        assert "queueName" in md
        assert "Yes" in md

    def test_default_shown_in_table(self):
        md = output.render_module_docs_md({
            "queue.add": {
                "description": "",
                "params": {
                    "maxTtl": {
                        "type": "integer",
                        "required": False,
                        "default": 0,
                    }
                },
            }
        })
        assert "`0`" in md

    def test_enum_included_in_description(self):
        md = output.render_module_docs_md({
            "queue.add": {
                "description": "",
                "params": {
                    "accessType": {
                        "type": "string",
                        "required": False,
                        "enum": ["exclusive", "non-exclusive"],
                        "description": "",
                    }
                },
            }
        })
        assert "exclusive" in md

    def test_table_of_contents_generated(self):
        md = output.render_module_docs_md({
            "queue.add": {"description": "", "params": {}},
            "rdp.add": {"description": "", "params": {}},
        })
        assert "## Contents" in md
        assert "queue" in md
        assert "rdp" in md
