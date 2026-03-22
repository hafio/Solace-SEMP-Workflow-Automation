"""Ansible-style colored console output."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from colorama import Fore, Style, init as colorama_init

from .models import ResultStatus

if TYPE_CHECKING:
    from .models import ActionResult, WorkflowResult

# Initialize colorama for Windows support
colorama_init()

SEPARATOR = "=" * 70
TASK_SEP = "-" * 70


def print_banner() -> None:
    print(f"\n{Style.BRIGHT}{SEPARATOR}")
    print("  SEMP Workflow Automation")
    print(f"{SEPARATOR}{Style.RESET_ALL}\n")


def print_workflow_header(
    workflow_name: str, template_ref: str, inputs: dict, index: int = 0
) -> None:
    print(f"\n{Style.BRIGHT}PLAY {index} [{workflow_name}] ({template_ref}){Style.RESET_ALL}")
    if inputs:
        input_str = ", ".join(f"{k}={v}" for k, v in inputs.items())
        print(f"  Inputs: {input_str}")
    print(TASK_SEP)


def print_task_result(result: ActionResult) -> None:
    """Print a single task result with color-coded status."""
    status = result.status
    name = result.task_name or result.module

    if status == ResultStatus.OK:
        color = Fore.YELLOW
        label = "changed"
    elif status == ResultStatus.DRYRUN:
        color = Fore.CYAN
        label = "dryrun"
    elif status == ResultStatus.SKIPPED:
        color = Fore.CYAN
        label = "skipped"
    else:
        color = Fore.RED
        label = "FAILED"

    # Pad task name for alignment
    task_display = f"TASK [{name}]"
    padding = max(1, 55 - len(task_display))
    dots = "." * padding

    print(
        f"  {task_display} {dots} "
        f"{color}{Style.BRIGHT}{label}{Style.RESET_ALL}"
    )
    if result.message:
        msg_color = Fore.RED if status == ResultStatus.FAILED else ""
        print(f"    => {msg_color}{result.message}{Style.RESET_ALL}")


def print_dry_run_banner() -> None:
    print(f"\n{Fore.CYAN}{Style.BRIGHT}** DRY RUN MODE ** "
          f"No changes will be made{Style.RESET_ALL}")


def print_recap(results: list[WorkflowResult]) -> None:
    """Print the final recap summary."""
    print(f"\n{Style.BRIGHT}{SEPARATOR}")
    print(f"RECAP{Style.RESET_ALL}")
    print(SEPARATOR)

    total_ok = 0
    total_dryrun = 0
    total_skipped = 0
    total_failed = 0

    for i, wf in enumerate(results, 1):
        ok = wf.ok_count
        dryrun = wf.dryrun_count
        skipped = wf.skipped_count
        failed = wf.failed_count

        total_ok += ok
        total_dryrun += dryrun
        total_skipped += skipped
        total_failed += failed

        failed_str = (
            f"{Fore.RED}failed={failed}{Style.RESET_ALL}"
            if failed
            else f"failed={failed}"
        )

        print(
            f"  Workflow {i} ({wf.workflow_name}): "
            f"{Fore.YELLOW}changed={ok}{Style.RESET_ALL}  "
            f"{Fore.CYAN}dryrun={dryrun}{Style.RESET_ALL}  "
            f"{Fore.CYAN}skipped={skipped}{Style.RESET_ALL}  "
            f"{failed_str}"
        )

    print(TASK_SEP)
    total_failed_str = (
        f"{Fore.RED}{Style.BRIGHT}failed={total_failed}{Style.RESET_ALL}"
        if total_failed
        else f"failed={total_failed}"
    )
    print(
        f"  {Style.BRIGHT}Total: "
        f"{Style.BRIGHT}{Fore.YELLOW}changed={total_ok}{Style.RESET_ALL}  "
        f"{Style.BRIGHT}{Fore.CYAN}dryrun={total_dryrun}{Style.RESET_ALL}  "
        f"{Style.BRIGHT}{Fore.CYAN}skipped={total_skipped}{Style.RESET_ALL}  "
        f"{total_failed_str}"
    )
    print(SEPARATOR)

    if total_failed:
        print(f"\n{Fore.RED}{Style.BRIGHT}Some tasks failed!{Style.RESET_ALL}")
        sys.exit(1)
    else:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}All tasks completed successfully.{Style.RESET_ALL}")


def print_module_list(modules: list[str]) -> None:
    """Print all available modules grouped by object."""
    print(f"\n{Style.BRIGHT}Available Modules:{Style.RESET_ALL}\n")

    # Group by object prefix
    groups: dict[str, list[str]] = {}
    for name in modules:
        obj, verb = name.split(".", 1)
        groups.setdefault(obj, []).append(verb)

    for obj in sorted(groups):
        print(f"  {Style.BRIGHT}{obj}{Style.RESET_ALL}")
        for verb in sorted(groups[obj]):
            print(f"    - {obj}.{verb}")
        print()


def print_validation_ok(config_path: str, template_count: int, workflow_count: int) -> None:
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Validation passed!{Style.RESET_ALL}")
    print(f"  Config: {config_path}")
    print(f"  Templates loaded: {template_count}")
    print(f"  Workflows defined: {workflow_count}")


def print_error(message: str) -> None:
    print(f"\n{Fore.RED}{Style.BRIGHT}ERROR: {message}{Style.RESET_ALL}", file=sys.stderr)


def render_module_docs_md(module_info: dict[str, dict]) -> str:
    """Render all module metadata as a Markdown document."""
    lines: list[str] = []
    lines.append("# SEMP Workflow Automation — Module Reference")
    lines.append("")
    lines.append("All actions are **idempotent**: each checks current state before acting.")
    lines.append("Result states: `changed` (action ran), `skipped` (already in desired state), `dryrun` (would change), `failed` (error).")
    lines.append("")

    # Group by object prefix (queue, rdp, …)
    groups: dict[str, list[str]] = {}
    for name in module_info:
        obj, _ = name.split(".", 1)
        groups.setdefault(obj, []).append(name)

    # Table of contents
    lines.append("## Contents")
    lines.append("")
    for obj in sorted(groups):
        anchor = obj.replace("_", "-")
        lines.append(f"- [{obj}](#{anchor})")
    lines.append("")
    lines.append("---")
    lines.append("")

    for obj in sorted(groups):
        lines.append(f"## {obj}")
        lines.append("")

        for action_name in sorted(groups[obj]):
            info = module_info[action_name]
            description = info["description"]
            params = info["params"]

            lines.append(f"### `{action_name}`")
            lines.append("")
            if description:
                lines.append(description)
                lines.append("")

            if params:
                lines.append("| Parameter | Type | Required | Default | Description |")
                lines.append("|-----------|------|----------|---------|-------------|")
                for param_name, meta in params.items():
                    ptype    = meta.get("type", "string")
                    required = "Yes" if meta.get("required") else "No"
                    default  = f"`{meta['default']}`" if "default" in meta else "—"
                    desc     = meta.get("description", "")
                    if "enum" in meta:
                        allowed = ", ".join(f"`{v}`" for v in meta["enum"])
                        desc = f"{desc} ({allowed})" if desc else allowed
                    lines.append(f"| `{param_name}` | {ptype} | {required} | {default} | {desc} |")
                lines.append("")
            else:
                lines.append("_No parameters._")
                lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)
