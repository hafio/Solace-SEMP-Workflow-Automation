"""Unit tests for models.py."""

from semp_workflow.models import ActionResult, ResultStatus, WorkflowResult


class TestActionResult:
    def test_creation(self):
        r = ActionResult(status=ResultStatus.OK, message="done")
        assert r.status == ResultStatus.OK
        assert r.message == "done"
        assert r.module == ""
        assert r.task_name == ""

    def test_with_module_and_task(self):
        r = ActionResult(
            status=ResultStatus.FAILED,
            message="error",
            module="queue.add",
            task_name="Create Queue",
        )
        assert r.module == "queue.add"
        assert r.task_name == "Create Queue"


class TestWorkflowResult:
    def _make(self, statuses):
        wf = WorkflowResult(workflow_name="test", template_ref="test.wf")
        for s in statuses:
            wf.task_results.append(ActionResult(status=s, message=""))
        return wf

    def test_has_failures_true(self):
        wf = self._make([ResultStatus.OK, ResultStatus.FAILED])
        assert wf.has_failures is True

    def test_has_failures_false_all_ok(self):
        wf = self._make([ResultStatus.OK, ResultStatus.OK])
        assert wf.has_failures is False

    def test_has_failures_false_skipped(self):
        wf = self._make([ResultStatus.SKIPPED, ResultStatus.SKIPPED])
        assert wf.has_failures is False

    def test_has_failures_false_dryrun(self):
        wf = self._make([ResultStatus.DRYRUN])
        assert wf.has_failures is False

    def test_ok_count(self):
        wf = self._make([ResultStatus.OK, ResultStatus.OK, ResultStatus.SKIPPED])
        assert wf.ok_count == 2

    def test_skipped_count(self):
        wf = self._make([ResultStatus.SKIPPED, ResultStatus.OK])
        assert wf.skipped_count == 1

    def test_failed_count(self):
        wf = self._make([ResultStatus.FAILED, ResultStatus.FAILED, ResultStatus.OK])
        assert wf.failed_count == 2

    def test_dryrun_count(self):
        wf = self._make([ResultStatus.DRYRUN, ResultStatus.DRYRUN])
        assert wf.dryrun_count == 2

    def test_empty_results(self):
        wf = WorkflowResult(workflow_name="x", template_ref="x.t")
        assert wf.ok_count == 0
        assert wf.has_failures is False
