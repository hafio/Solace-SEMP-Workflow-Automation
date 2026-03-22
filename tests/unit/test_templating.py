"""Unit tests for templating.py."""

import pytest

from semp_workflow.exceptions import TemplateError
from semp_workflow.templating import TemplateEngine, _coerce_type, validate_inputs


@pytest.fixture
def engine():
    return TemplateEngine()


class TestTemplateEngineRender:
    def test_plain_string_fast_path(self, engine):
        assert engine.render("hello world", {}) == "hello world"

    def test_string_with_variable(self, engine):
        result = engine.render("{{ inputs.x }}", {"inputs": {"x": "foo"}})
        assert result == "foo"

    def test_dict_recursive(self, engine):
        result = engine.render(
            {"key": "{{ inputs.v }}", "plain": "no-template"},
            {"inputs": {"v": "val"}},
        )
        assert result == {"key": "val", "plain": "no-template"}

    def test_list_recursive(self, engine):
        result = engine.render(
            ["{{ inputs.a }}", "{{ inputs.b }}"],
            {"inputs": {"a": "1", "b": "2"}},
        )
        assert result == ["1", "2"]

    def test_integer_passthrough(self, engine):
        assert engine.render(42, {}) == 42

    def test_bool_passthrough(self, engine):
        assert engine.render(True, {}) is True

    def test_none_passthrough(self, engine):
        assert engine.render(None, {}) is None

    def test_undefined_variable_raises(self, engine):
        with pytest.raises(TemplateError, match="Undefined variable"):
            engine.render("{{ inputs.missing }}", {"inputs": {}})

    def test_nested_dict_in_list(self, engine):
        result = engine.render(
            [{"k": "{{ inputs.v }}"}],
            {"inputs": {"v": "deep"}},
        )
        assert result == [{"k": "deep"}]


class TestValidateInputs:
    @pytest.fixture
    def eng(self):
        return TemplateEngine()

    def test_required_provided(self, eng):
        schema = {"domain": {"required": True}}
        result = validate_inputs({"domain": "HQ"}, schema, eng, {})
        assert result["domain"] == "HQ"

    def test_required_missing_raises(self, eng):
        schema = {"domain": {"required": True}}
        with pytest.raises(TemplateError, match="domain"):
            validate_inputs({}, schema, eng, {})

    def test_optional_with_default(self, eng):
        schema = {"owner": {"required": False, "default": "admin"}}
        result = validate_inputs({}, schema, eng, {})
        assert result["owner"] == "admin"

    def test_optional_without_default_omitted(self, eng):
        schema = {"owner": {"required": False}}
        result = validate_inputs({}, schema, eng, {})
        assert "owner" not in result

    def test_provided_overrides_default(self, eng):
        schema = {"owner": {"required": False, "default": "admin"}}
        result = validate_inputs({"owner": "custom"}, schema, eng, {})
        assert result["owner"] == "custom"

    def test_jinja2_default_rendered(self, eng):
        schema = {"name": {"required": False, "default": "{{ global_vars.prefix }}"}}
        result = validate_inputs({}, schema, eng, {"global_vars": {"prefix": "FCM"}})
        assert result["name"] == "FCM"

    def test_unexpected_input_raises(self, eng):
        schema = {"domain": {"required": True}}
        with pytest.raises(TemplateError, match="typo_var"):
            validate_inputs({"domain": "HQ", "typo_var": "x"}, schema, eng, {})

    def test_all_types_coerced(self, eng):
        schema = {
            "count": {"required": False, "default": "5", "type": "integer"},
            "flag": {"required": False, "default": "true", "type": "boolean"},
        }
        result = validate_inputs({}, schema, eng, {})
        assert result["count"] == 5
        assert result["flag"] is True


class TestCoerceType:
    def test_string_converts_int(self):
        assert _coerce_type("x", 42, "string") == "42"

    def test_string_converts_bool(self):
        assert _coerce_type("x", True, "string") == "True"

    def test_integer_from_string(self):
        assert _coerce_type("x", "42", "integer") == 42

    def test_integer_invalid_raises(self):
        with pytest.raises(TemplateError, match="integer"):
            _coerce_type("x", "abc", "integer")

    def test_boolean_true_bool(self):
        assert _coerce_type("x", True, "boolean") is True

    def test_boolean_false_bool(self):
        assert _coerce_type("x", False, "boolean") is False

    def test_boolean_string_true(self):
        assert _coerce_type("x", "true", "boolean") is True

    def test_boolean_string_false(self):
        assert _coerce_type("x", "false", "boolean") is False

    def test_boolean_non_bool_non_str_coerced(self):
        # int 1 → True, int 0 → False via bool()
        assert _coerce_type("x", 1, "boolean") is True
        assert _coerce_type("x", 0, "boolean") is False

    def test_unknown_type_passthrough(self):
        assert _coerce_type("x", "anything", "unknown") == "anything"


class TestRenderStringExceptions:
    def test_general_exception_raises_template_error(self):
        """A non-UndefinedError exception during rendering wraps to TemplateError."""
        engine = TemplateEngine()
        # ZeroDivisionError is not an UndefinedError, so hits the except Exception branch
        with pytest.raises(TemplateError, match="Template rendering error"):
            engine.render("{{ 1 / 0 }}", {})
