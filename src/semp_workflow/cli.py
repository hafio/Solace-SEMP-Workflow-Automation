"""CLI entry point using Click."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from . import __version__
from .config import load_config, load_templates, _get_bundled_templates_source
from .engine import Engine
from .exceptions import ConfigError, TemplateError, WorkflowError
from .modules import list_modules as get_modules, get_module_info
from .output import print_error, print_module_list, print_validation_ok, render_module_docs_md


@click.group()
@click.version_option(version=__version__, prog_name="semp-workflow")
def main() -> None:
    """SEMP Workflow Automation - Ansible-like playbooks for Solace SEMP."""


@main.command()
@click.option(
    "--config", "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to config YAML file.",
)
@click.option(
    "--templates-dir", "-t",
    type=click.Path(exists=True),
    default=None,
    help="Override the workflow templates directory.",
)
@click.option(
    "--dry-run", "--check",
    is_flag=True,
    default=False,
    help="Show what would be done without making changes.",
)
@click.option(
    "--fail-fast", "-f",
    is_flag=True,
    default=False,
    help="Stop execution on first failure.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable verbose/debug logging.",
)
def run(
    config: str,
    templates_dir: str | None,
    dry_run: bool,
    fail_fast: bool,
    verbose: bool,
) -> None:
    """Execute workflows defined in a config file."""
    _setup_logging(verbose)

    try:
        app_config = load_config(config)

        if templates_dir:
            # Explicit --templates-dir always wins; disable bundled fallback
            app_config.templates_dir = Path(templates_dir)
            app_config.use_bundled_templates = False

        engine = Engine(app_config, dry_run=dry_run, fail_fast=fail_fast)
        results = engine.run()

        if any(r.has_failures for r in results):
            sys.exit(1)

    except (ConfigError, TemplateError) as e:
        print_error(str(e))
        sys.exit(2)
    except WorkflowError as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print_error("Interrupted by user")
        sys.exit(130)


@main.command()
@click.option(
    "--config", "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to config YAML file.",
)
@click.option(
    "--templates-dir", "-t",
    type=click.Path(exists=True),
    default=None,
    help="Override the workflow templates directory.",
)
def validate(config: str, templates_dir: str | None) -> None:
    """Validate config and templates without executing."""
    _setup_logging(False)

    try:
        app_config = load_config(config)

        if templates_dir:
            app_config.templates_dir = Path(templates_dir)
            app_config.use_bundled_templates = False

        # Mirror the same source selection logic as the engine
        if app_config.use_bundled_templates:
            source = _get_bundled_templates_source()
        else:
            source = app_config.templates_dir

        templates = load_templates(source)

        for i, wf in enumerate(app_config.workflows, 1):
            if wf.template not in templates:
                available = ", ".join(sorted(templates.keys()))
                print_error(
                    f"Workflow {i}: template '{wf.template}' not found. "
                    f"Available: {available}"
                )
                sys.exit(2)

        print_validation_ok(config, len(templates), len(app_config.workflows))

    except (ConfigError, TemplateError) as e:
        print_error(str(e))
        sys.exit(2)


@main.command("list-modules")
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    metavar="FILE",
    help="Write module reference docs to a Markdown file (e.g. all-modules.md).",
)
def list_modules_cmd(output: str | None) -> None:
    """List all available action modules."""
    modules = get_modules()
    print_module_list(modules)
    if output:
        md = render_module_docs_md(get_module_info())
        Path(output).write_text(md, encoding="utf-8")
        click.echo(f"Module reference written to: {output}")


@main.command("init")
@click.option(
    "--output-dir", "-o",
    default="templates",
    show_default=True,
    help="Directory to copy bundled templates into.",
)
@click.option(
    "--force", "-f",
    is_flag=True,
    default=False,
    help="Overwrite existing files.",
)
def init_cmd(output_dir: str, force: bool) -> None:
    """Copy bundled workflow templates to a local directory.

    Useful after receiving a .pyz/.zip to get the embedded templates
    as a starting point for customisation.
    """
    from colorama import Fore, Style, init as colorama_init

    colorama_init()

    bundled = _get_bundled_templates_source()
    if bundled is None:
        print_error(
            "No bundled templates found. "
            "This command only works when running from a .pyz built with 'scripts/build_pyz.py'."
        )
        sys.exit(2)

    dst = Path(output_dir)
    dst.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    yaml_files = sorted(
        (f for f in bundled.iterdir() if f.name.endswith(".yaml")),
        key=lambda f: f.name,
    )
    for tmpl in yaml_files:
        target = dst / tmpl.name
        if target.exists() and not force:
            print(f"  {Fore.CYAN}skip{Style.RESET_ALL}  {target}  (already exists, use --force to overwrite)")
            skipped += 1
        else:
            target.write_text(tmpl.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  {Fore.GREEN}write{Style.RESET_ALL} {target}")
            copied += 1

    print(f"\n  {copied} file(s) written, {skipped} skipped -> {dst.resolve()}")


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
