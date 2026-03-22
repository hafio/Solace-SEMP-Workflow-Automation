"""Data models for SEMP Workflow Automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResultStatus(Enum):
    """Result of an idempotent action."""

    OK = "ok"          # action ran and changed something
    SKIPPED = "skipped"
    FAILED = "failed"
    DRYRUN = "dryrun"  # would have changed something (dry-run mode)


@dataclass
class ActionResult:
    """Result of a single task execution."""

    status: ResultStatus
    message: str
    module: str = ""
    task_name: str = ""


@dataclass
class WorkflowResult:
    """Aggregated result of a complete workflow execution."""

    workflow_name: str
    template_ref: str
    task_results: list[ActionResult] = field(default_factory=list)

    @property
    def ok_count(self) -> int:
        return sum(1 for t in self.task_results if t.status == ResultStatus.OK)

    @property
    def skipped_count(self) -> int:
        return sum(1 for t in self.task_results if t.status == ResultStatus.SKIPPED)

    @property
    def failed_count(self) -> int:
        return sum(1 for t in self.task_results if t.status == ResultStatus.FAILED)

    @property
    def dryrun_count(self) -> int:
        return sum(1 for t in self.task_results if t.status == ResultStatus.DRYRUN)

    @property
    def has_failures(self) -> bool:
        return self.failed_count > 0
