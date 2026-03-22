"""Configuration and template loading."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigError, TemplateError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config data classes
# ---------------------------------------------------------------------------

@dataclass
class SempConfig:
    """SEMP connection details."""

    host: str
    username: str
    password: str
    msg_vpn: str
    verify_ssl: bool = False
    timeout: int = 30


@dataclass
class WorkflowEntry:
    """A single workflow invocation from the config file."""

    template: str  # "filename.TemplateName"
    inputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class AppConfig:
    """Top-level application configuration."""

    semp: SempConfig
    global_vars: dict[str, Any]
    workflows: list[WorkflowEntry]
    templates_dir: Path = field(default_factory=lambda: Path("templates"))
    use_bundled_templates: bool = False


# ---------------------------------------------------------------------------
# Template data classes
# ---------------------------------------------------------------------------

@dataclass
class ActionSpec:
    """A single action step within a workflow template."""

    name: str
    module: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTemplate:
    """A parsed workflow template."""

    name: str
    inputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    actions: list[ActionSpec] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Bundled template helpers (importlib.resources)
# ---------------------------------------------------------------------------

def _get_bundled_templates_source():
    """Return an importlib.resources Traversable for bundled templates, or None.

    Works inside a .pyz (zip) without any extraction — importlib.resources
    reads the package data directly from the archive.
    Returns None if the bundled_templates package is not available (e.g. in
    development mode where it was never installed into the source tree).
    """
    try:
        from importlib.resources import files
        pkg = files("semp_workflow.bundled_templates")
        if any(f.name.endswith(".yaml") for f in pkg.iterdir()):
            return pkg
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path) -> AppConfig:
    """Load and validate the main config YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ConfigError("Config file must be a YAML mapping")

    # Parse SEMP section
    semp_data = data.get("semp")
    if not semp_data:
        raise ConfigError("Missing 'semp' section in config")

    for required in ("host", "username", "password", "msg_vpn"):
        if required not in semp_data:
            raise ConfigError(f"Missing 'semp.{required}' in config")

    semp = SempConfig(
        host=semp_data["host"],
        username=semp_data["username"],
        password=semp_data["password"],
        msg_vpn=semp_data["msg_vpn"],
        verify_ssl=semp_data.get("verify_ssl", False),
        timeout=semp_data.get("timeout", 30),
    )

    # Parse global vars
    global_vars = data.get("global_vars", {})

    # Parse workflows
    workflows_data = data.get("workflows", [])
    if not isinstance(workflows_data, list):
        raise ConfigError("'workflows' must be a list")

    workflows = []
    for i, wf in enumerate(workflows_data):
        if not isinstance(wf, dict) or "template" not in wf:
            raise ConfigError(f"Workflow entry {i + 1} must have a 'template' field")
        workflows.append(
            WorkflowEntry(
                template=wf["template"],
                inputs=wf.get("inputs", {}),
            )
        )

    # Determine templates source.
    # Precedence (highest first):
    #   1. --templates-dir CLI flag  (applied later in cli.py, overrides use_bundled_templates)
    #   2. templates_dir: in config.yaml, if the directory exists on disk
    #   3. Bundled package data (semp_workflow.bundled_templates) — no temp dir, no extraction
    templates_dir_str = data.get("templates_dir", "templates")
    templates_dir = path.parent / templates_dir_str
    use_bundled = False

    if not templates_dir.exists():
        if _get_bundled_templates_source() is not None:
            logger.debug("templates_dir '%s' not found; using bundled package data", templates_dir)
            use_bundled = True

    return AppConfig(
        semp=semp,
        global_vars=global_vars,
        workflows=workflows,
        templates_dir=templates_dir,
        use_bundled_templates=use_bundled,
    )


def _parse_inputs_schema(inputs_data: dict) -> dict[str, dict[str, Any]]:
    """Parse a template inputs block into a flat schema dict.

    Format:
        inputs:
          required:
            - name1
            - name2
          optional:
            - name: var1
              default: value
            - name: var2
              default: 443
    """
    schema: dict[str, dict[str, Any]] = {}

    if not inputs_data:
        return schema

    for name in (inputs_data.get("required") or []):
        schema[str(name)] = {"required": True}

    for var_name, default_val in (inputs_data.get("optional") or {}).items():
        spec: dict[str, Any] = {"required": False}
        if default_val is not None:
            spec["default"] = default_val
        schema[var_name] = spec

    return schema


def load_templates(source: Path | Any) -> dict[str, WorkflowTemplate]:
    """Load all workflow templates from a filesystem directory or a Traversable.

    Accepts either:
    - Path: a regular filesystem directory (used in dev / when user specifies --templates-dir)
    - Traversable: an importlib.resources object (used for bundled templates inside a .pyz)

    Returns a dict keyed by "filename.TemplateName".
    """
    if isinstance(source, Path):
        if not source.exists():
            raise TemplateError(f"Templates directory not found: {source}")
        yaml_files = sorted(source.glob("*.yaml"), key=lambda p: p.name)
    else:
        # Traversable (importlib.resources) — reads directly from zip, no extraction
        try:
            yaml_files = sorted(
                (f for f in source.iterdir() if f.name.endswith(".yaml")),
                key=lambda f: f.name,
            )
        except Exception as e:
            raise TemplateError(f"Failed to read bundled templates: {e}") from e

    registry: dict[str, WorkflowTemplate] = {}

    for yaml_file in yaml_files:
        # .name and .read_text() work identically on both Path and Traversable
        file_key = yaml_file.name.removesuffix(".yaml")
        logger.debug("Loading template file: %s", yaml_file.name)

        content = yaml_file.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            logger.warning("Skipping %s: not a valid YAML mapping", yaml_file.name)
            continue

        templates_list = data.get("workflow-templates", [])
        if not isinstance(templates_list, list):
            logger.warning("Skipping %s: 'workflow-templates' is not a list", yaml_file.name)
            continue

        for tmpl_data in templates_list:
            name = tmpl_data.get("name")
            if not name:
                logger.warning("Skipping template without 'name' in %s", yaml_file.name)
                continue

            # Parse input schema
            inputs_schema = _parse_inputs_schema(tmpl_data.get("inputs", {}))

            # Parse actions
            actions: list[ActionSpec] = []
            for action_data in tmpl_data.get("actions", []):
                if not isinstance(action_data, dict):
                    continue
                actions.append(
                    ActionSpec(
                        name=action_data.get("name", "Unnamed Action"),
                        module=action_data["module"],
                        args=action_data.get("args", {}),
                    )
                )

            ref_key = f"{file_key}.{name}"
            registry[ref_key] = WorkflowTemplate(
                name=name,
                inputs=inputs_schema,
                actions=actions,
            )
            logger.debug("Registered template: %s", ref_key)

    if not registry:
        logger.warning("No workflow templates found in %s", getattr(source, "name", str(source)))

    return registry
