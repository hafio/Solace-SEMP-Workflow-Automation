"""Jinja2-based template engine for resolving workflow variables."""

from __future__ import annotations

from typing import Any

from jinja2 import Environment, BaseLoader, StrictUndefined, UndefinedError

from .exceptions import TemplateError


class TemplateEngine:
    """Resolves Jinja2 expressions in workflow action args.

    Context is a dict with keys like 'inputs', 'global_vars'.
    Supports filters like {{ inputs.x | default('fallback') }}.
    """

    def __init__(self) -> None:
        self.env = Environment(
            loader=BaseLoader(),
            undefined=StrictUndefined,
            keep_trailing_newline=False,
        )

    def render(self, value: Any, context: dict[str, Any]) -> Any:
        """Recursively render Jinja2 expressions in a data structure.

        - Strings are rendered as Jinja2 templates.
        - Dicts and lists are walked recursively.
        - Other types are passed through unchanged.
        """
        if isinstance(value, str):
            return self._render_string(value, context)
        if isinstance(value, dict):
            return {k: self.render(v, context) for k, v in value.items()}
        if isinstance(value, list):
            return [self.render(item, context) for item in value]
        return value

    def _render_string(self, text: str, context: dict[str, Any]) -> str:
        """Render a single string through Jinja2."""
        if "{{" not in text and "{%" not in text:
            return text  # Fast path: no template syntax
        try:
            template = self.env.from_string(text)
            return template.render(context)
        except UndefinedError as e:
            raise TemplateError(f"Undefined variable in '{text}': {e}") from e
        except Exception as e:
            raise TemplateError(f"Template rendering error in '{text}': {e}") from e


def validate_inputs(
    provided: dict[str, Any],
    schema: dict[str, dict[str, Any]],
    template_engine: TemplateEngine,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Validate and fill defaults for workflow inputs against a schema.

    Args:
        provided: Input values from config.yaml workflow entry.
        schema: Input schema from the workflow template.
        template_engine: For resolving default values that use Jinja2.
        context: Current context (global_vars etc.) for resolving defaults.

    Returns:
        Validated and complete input dict.
    """
    validated: dict[str, Any] = {}

    for name, spec in schema.items():
        if name in provided:
            val = provided[name]
        elif "default" in spec:
            default_val = spec["default"]
            try:
                # Defaults can be Jinja2 expressions
                val = template_engine.render(default_val, context)
            except TemplateError:
                # Cannot resolve yet (e.g. references inputs.X which isn't in
                # context during the first pass).  Keep the raw value so the
                # engine's second pass can resolve it with full context.
                val = default_val
        elif spec.get("required", False):
            raise TemplateError(f"Required input '{name}' not provided")
        else:
            continue

        # Type coercion
        expected_type = spec.get("type", "string")
        val = _coerce_type(name, val, expected_type)
        validated[name] = val

    # Warn about unexpected inputs
    unexpected = set(provided.keys()) - set(schema.keys())
    if unexpected:
        raise TemplateError(f"Unexpected inputs: {', '.join(sorted(unexpected))}")

    return validated


def _coerce_type(name: str, value: Any, expected_type: str) -> Any:
    """Coerce a value to the expected type."""
    if expected_type == "string":
        return str(value)
    elif expected_type == "integer":
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise TemplateError(f"Input '{name}' must be integer, got: {value}") from e
    elif expected_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1")
        return bool(value)
    return value
