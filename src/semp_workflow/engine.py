"""Workflow execution engine - orchestrates template resolution, variable
rendering, and module execution."""

from __future__ import annotations

import logging
from typing import Any

from .config import AppConfig, WorkflowEntry, WorkflowTemplate, load_templates, _get_bundled_templates_source
from .exceptions import TemplateError, WorkflowError
from .models import ActionResult, ResultStatus, WorkflowResult
from .modules import get_module
from .output import (
    print_banner,
    print_dry_run_banner,
    print_recap,
    print_task_result,
    print_workflow_header,
)
from .semp.client import SempClient
from .templating import TemplateEngine, validate_inputs

logger = logging.getLogger(__name__)


class Engine:
    """Loads templates, resolves variables, and executes workflows."""

    def __init__(
        self,
        config: AppConfig,
        dry_run: bool = False,
        fail_fast: bool = False,
    ):
        self.config = config
        self.dry_run = dry_run
        self.fail_fast = fail_fast
        self.template_engine = TemplateEngine()

        # Choose templates source (filesystem path or bundled package data)
        if config.use_bundled_templates:
            templates_source = _get_bundled_templates_source()
        else:
            templates_source = config.templates_dir
        self.templates = load_templates(templates_source)

        # Create SEMP client
        self.client = SempClient(
            host=config.semp.host,
            username=config.semp.username,
            password=config.semp.password,
            msg_vpn=config.semp.msg_vpn,
            verify_ssl=config.semp.verify_ssl,
            timeout=config.semp.timeout,
        )

    def run(self) -> list[WorkflowResult]:
        """Execute all workflows defined in the config.

        Returns list of WorkflowResult for recap.
        """
        print_banner()
        if self.dry_run:
            print_dry_run_banner()

        results: list[WorkflowResult] = []

        for i, workflow_entry in enumerate(self.config.workflows):
            try:
                wf_result = self._run_workflow(workflow_entry, i + 1)
                results.append(wf_result)

                if self.fail_fast and wf_result.has_failures:
                    logger.warning(
                        "Fail-fast enabled: stopping after failure in workflow %d",
                        i + 1,
                    )
                    break
            except WorkflowError as e:
                # Template/validation errors — record as a single failed task
                wf_result = WorkflowResult(
                    workflow_name=workflow_entry.template,
                    template_ref=workflow_entry.template,
                    task_results=[
                        ActionResult(
                            status=ResultStatus.FAILED,
                            message=str(e),
                            module="engine",
                            task_name="Template Resolution",
                        )
                    ],
                )
                results.append(wf_result)
                print_task_result(wf_result.task_results[0])

                if self.fail_fast:
                    break

        print_recap(results)
        return results

    def _run_workflow(
        self, entry: WorkflowEntry, index: int
    ) -> WorkflowResult:
        """Execute a single workflow entry."""
        # Resolve template
        template = self._resolve_template(entry.template)

        # Build context for variable resolution
        base_context: dict[str, Any] = {
            "global_vars": self.config.global_vars,
        }

        # Validate and apply defaults to inputs (first pass — global_vars context only)
        validated_inputs = validate_inputs(
            provided=entry.inputs,
            schema=template.inputs,
            template_engine=self.template_engine,
            context=base_context,
        )

        # Full context with resolved inputs
        context: dict[str, Any] = {
            "global_vars": self.config.global_vars,
            "inputs": validated_inputs,
        }

        # Second pass: re-render any input values that themselves contain
        # Jinja2 expressions (e.g. defaults sourced from global_vars that
        # reference other inputs like {{ inputs.domain }}).
        # Iterate key-by-key so errors name the specific input that failed.
        for key in list(validated_inputs):
            try:
                validated_inputs[key] = self.template_engine.render(
                    validated_inputs[key], context
                )
            except TemplateError as e:
                raise WorkflowError(
                    f"Failed to resolve input '{key}': {e}"
                ) from e

        # Detect unresolved Jinja2 expressions after the second pass — a sign
        # of a circular reference (e.g. a defaults to {{ inputs.b }}, b defaults
        # to {{ inputs.a }}) or a typo referencing a non-existent input.
        for key, val in validated_inputs.items():
            if isinstance(val, str) and ("{{" in val or "{%" in val):
                raise WorkflowError(
                    f"Input '{key}' still contains an unresolved Jinja2 expression "
                    f"after rendering — possible circular reference or undefined variable: "
                    f"'{val}'"
                )

        print_workflow_header(
            template.name, entry.template, validated_inputs, index
        )

        wf_result = WorkflowResult(
            workflow_name=template.name,
            template_ref=entry.template,
        )

        # Execute each action
        for action in template.actions:
            task_result = self._run_action(action.name, action.module, action.args, context)
            wf_result.task_results.append(task_result)
            print_task_result(task_result)

            if self.fail_fast and task_result.status == ResultStatus.FAILED:
                logger.warning("Fail-fast: stopping workflow after task '%s'", action.name)
                break

        return wf_result

    def _run_action(
        self,
        task_name: str,
        module_name: str,
        raw_args: dict[str, Any],
        context: dict[str, Any],
    ) -> ActionResult:
        """Resolve args and execute a single action module."""
        try:
            # Resolve Jinja2 variables in args
            resolved_args = self.template_engine.render(raw_args, context)

            # Look up module
            module = get_module(module_name)

            # Execute (idempotent)
            result = module.execute(self.client, resolved_args, dry_run=self.dry_run)
            result.module = module_name
            result.task_name = task_name
            return result

        except TemplateError as e:
            return ActionResult(
                status=ResultStatus.FAILED,
                message=f"Template error: {e}",
                module=module_name,
                task_name=task_name,
            )
        except ValueError as e:
            # Unknown module
            return ActionResult(
                status=ResultStatus.FAILED,
                message=str(e),
                module=module_name,
                task_name=task_name,
            )
        except Exception as e:
            logger.exception("Unexpected error in task '%s'", task_name)
            return ActionResult(
                status=ResultStatus.FAILED,
                message=f"Unexpected error: {e}",
                module=module_name,
                task_name=task_name,
            )

    def _resolve_template(self, template_ref: str) -> WorkflowTemplate:
        """Resolve a 'filename.TemplateName' reference to a WorkflowTemplate."""
        if template_ref not in self.templates:
            available = ", ".join(sorted(self.templates.keys()))
            raise TemplateError(
                f"Template '{template_ref}' not found. Available: {available}"
            )
        return self.templates[template_ref]
