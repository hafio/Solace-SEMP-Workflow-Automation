"""Unit tests for config.py."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from semp_workflow.config import (
    AppConfig,
    _get_bundled_templates_source,
    _parse_inputs_schema,
    load_config,
    load_templates,
)
from semp_workflow.exceptions import ConfigError, TemplateError


MINIMAL_CONFIG = textwrap.dedent("""\
    semp:
      host: "https://broker:943"
      username: "admin"
      password: "secret"
      msg_vpn: "default"
    workflows: []
""")

MINIMAL_TEMPLATE = textwrap.dedent("""\
    workflow-templates:
      - name: "my-wf"
        inputs:
          required:
            - domain
          optional:
            owner: "admin"
        actions:
          - name: "Create Queue"
            module: "queue.add"
            args:
              queueName: "Q-{{ inputs.domain }}"
""")


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfig:
    def test_valid_minimal(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_CONFIG)
        cfg = load_config(cfg_file)
        assert isinstance(cfg, AppConfig)
        assert cfg.semp.host == "https://broker:943"
        assert cfg.semp.username == "admin"
        assert cfg.semp.msg_vpn == "default"
        assert cfg.global_vars == {}
        assert cfg.workflows == []

    def test_semp_defaults(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_CONFIG)
        cfg = load_config(cfg_file)
        assert cfg.semp.verify_ssl is False
        assert cfg.semp.timeout == 30

    def test_semp_custom_values(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(textwrap.dedent("""\
            semp:
              host: "https://h:943"
              username: "u"
              password: "p"
              msg_vpn: "vpn"
              verify_ssl: true
              timeout: 60
            workflows: []
        """))
        cfg = load_config(cfg_file)
        assert cfg.semp.verify_ssl is True
        assert cfg.semp.timeout == 60

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ConfigError, match="not found"):
            load_config(tmp_path / "nonexistent.yaml")

    def test_missing_semp_section_raises(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("workflows: []\n")
        with pytest.raises(ConfigError, match="semp"):
            load_config(cfg_file)

    def test_missing_semp_host_raises(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(textwrap.dedent("""\
            semp:
              username: "u"
              password: "p"
              msg_vpn: "v"
            workflows: []
        """))
        with pytest.raises(ConfigError, match="host"):
            load_config(cfg_file)

    def test_global_vars_loaded(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(
            MINIMAL_CONFIG + "global_vars:\n  prefix: FCM\n"
        )
        cfg = load_config(cfg_file)
        assert cfg.global_vars == {"prefix": "FCM"}

    def test_workflows_not_list_raises(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_CONFIG.replace("workflows: []", "workflows: bad"))
        with pytest.raises(ConfigError, match="list"):
            load_config(cfg_file)

    def test_workflow_entry_missing_template_raises(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(
            MINIMAL_CONFIG.replace(
                "workflows: []", "workflows:\n  - inputs:\n      x: y\n"
            )
        )
        with pytest.raises(ConfigError, match="template"):
            load_config(cfg_file)

    def test_workflow_entry_parsed(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(textwrap.dedent("""\
            semp:
              host: "h"
              username: "u"
              password: "p"
              msg_vpn: "v"
            workflows:
              - template: "sap-outbound.new-seq"
                inputs:
                  domain: "HQ"
        """))
        cfg = load_config(cfg_file)
        assert len(cfg.workflows) == 1
        assert cfg.workflows[0].template == "sap-outbound.new-seq"
        assert cfg.workflows[0].inputs == {"domain": "HQ"}

    def test_templates_dir_exists_no_bundled(self, tmp_path):
        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_CONFIG)
        cfg = load_config(cfg_file)
        assert cfg.use_bundled_templates is False
        assert cfg.templates_dir == tmpl_dir

    def test_templates_dir_missing_stores_path(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_CONFIG)
        cfg = load_config(cfg_file)
        # Dir doesn't exist; use_bundled depends on whether bundled pkg is present
        assert cfg.templates_dir == tmp_path / "templates"

    def test_non_dict_yaml_raises(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("- item1\n- item2\n")
        with pytest.raises(ConfigError, match="YAML mapping"):
            load_config(cfg_file)

    def test_bundled_fallback_when_templates_dir_missing(self, tmp_path):
        """When templates_dir doesn't exist and bundled source is available, use_bundled=True."""
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_CONFIG)
        mock_source = MagicMock()
        with patch("semp_workflow.config._get_bundled_templates_source", return_value=mock_source):
            cfg = load_config(cfg_file)
        assert cfg.use_bundled_templates is True


# ---------------------------------------------------------------------------
# _parse_inputs_schema
# ---------------------------------------------------------------------------

class TestParseInputsSchema:
    def test_required_list(self):
        schema = _parse_inputs_schema({"required": ["a", "b"]})
        assert schema["a"] == {"required": True}
        assert schema["b"] == {"required": True}

    def test_optional_with_default(self):
        schema = _parse_inputs_schema({"optional": {"owner": "admin"}})
        assert schema["owner"] == {"required": False, "default": "admin"}

    def test_optional_null_default(self):
        schema = _parse_inputs_schema({"optional": {"owner": None}})
        assert schema["owner"] == {"required": False}
        assert "default" not in schema["owner"]

    def test_mixed(self):
        schema = _parse_inputs_schema({
            "required": ["domain"],
            "optional": {"owner": "admin", "ttl": 0},
        })
        assert schema["domain"]["required"] is True
        assert schema["owner"]["default"] == "admin"
        assert schema["ttl"]["default"] == 0

    def test_empty(self):
        assert _parse_inputs_schema({}) == {}

    def test_none(self):
        assert _parse_inputs_schema(None) == {}


# ---------------------------------------------------------------------------
# load_templates
# ---------------------------------------------------------------------------

class TestLoadTemplates:
    def test_loads_single_template(self, tmp_path):
        (tmp_path / "my-wf.yaml").write_text(MINIMAL_TEMPLATE)
        registry = load_templates(tmp_path)
        assert "my-wf.my-wf" in registry

    def test_template_inputs_parsed(self, tmp_path):
        (tmp_path / "my-wf.yaml").write_text(MINIMAL_TEMPLATE)
        registry = load_templates(tmp_path)
        tmpl = registry["my-wf.my-wf"]
        assert "domain" in tmpl.inputs
        assert tmpl.inputs["domain"]["required"] is True
        assert "owner" in tmpl.inputs
        assert tmpl.inputs["owner"]["default"] == "admin"

    def test_template_actions_parsed(self, tmp_path):
        (tmp_path / "my-wf.yaml").write_text(MINIMAL_TEMPLATE)
        registry = load_templates(tmp_path)
        tmpl = registry["my-wf.my-wf"]
        assert len(tmpl.actions) == 1
        assert tmpl.actions[0].module == "queue.add"

    def test_multiple_templates_in_one_file(self, tmp_path):
        content = textwrap.dedent("""\
            workflow-templates:
              - name: "wf-a"
                inputs: {}
                actions: []
              - name: "wf-b"
                inputs: {}
                actions: []
        """)
        (tmp_path / "multi.yaml").write_text(content)
        registry = load_templates(tmp_path)
        assert "multi.wf-a" in registry
        assert "multi.wf-b" in registry

    def test_nonexistent_path_raises(self, tmp_path):
        with pytest.raises(TemplateError, match="not found"):
            load_templates(tmp_path / "missing")

    def test_file_without_workflow_templates_key_skipped(self, tmp_path):
        (tmp_path / "bad.yaml").write_text("some_key: value\n")
        registry = load_templates(tmp_path)
        assert len(registry) == 0

    def test_non_mapping_yaml_skipped(self, tmp_path):
        (tmp_path / "bad.yaml").write_text("- item1\n- item2\n")
        registry = load_templates(tmp_path)
        assert len(registry) == 0

    def test_workflow_templates_not_list_skipped(self, tmp_path):
        (tmp_path / "bad.yaml").write_text("workflow-templates: not-a-list\n")
        registry = load_templates(tmp_path)
        assert len(registry) == 0

    def test_template_without_name_skipped(self, tmp_path):
        content = textwrap.dedent("""\
            workflow-templates:
              - inputs: {}
                actions: []
        """)
        (tmp_path / "noname.yaml").write_text(content)
        registry = load_templates(tmp_path)
        assert len(registry) == 0

    def test_non_dict_action_skipped(self, tmp_path):
        content = textwrap.dedent("""\
            workflow-templates:
              - name: "wf"
                inputs: {}
                actions:
                  - "not-a-dict"
        """)
        (tmp_path / "wf.yaml").write_text(content)
        registry = load_templates(tmp_path)
        # Template is registered but non-dict action is skipped
        assert "wf.wf" in registry
        assert len(registry["wf.wf"].actions) == 0

    def test_traversable_source_loads_templates(self):
        """load_templates works with a mock Traversable (simulating importlib.resources)."""
        mock_file = MagicMock()
        mock_file.name = "tmpl.yaml"
        mock_file.read_text.return_value = textwrap.dedent("""\
            workflow-templates:
              - name: "wf"
                inputs: {}
                actions: []
        """)
        mock_source = MagicMock()
        mock_source.iterdir.return_value = [mock_file]
        registry = load_templates(mock_source)
        assert "tmpl.wf" in registry

    def test_traversable_iterdir_exception_raises(self):
        mock_source = MagicMock()
        mock_source.iterdir.side_effect = Exception("zip read error")
        with pytest.raises(TemplateError, match="Failed to read bundled"):
            load_templates(mock_source)

    def test_yaml_anchors_resolved(self):
        # Use the real examples templates to verify anchor support
        examples_dir = Path(__file__).parent.parent.parent / "examples" / "templates"
        if not examples_dir.exists():
            pytest.skip("examples/templates not found")
        registry = load_templates(examples_dir)
        assert len(registry) > 0
        # Inbound templates use YAML anchors
        assert "sap-inbound.new-seq" in registry
        assert "sap-inbound.new-non-seq" in registry


# ---------------------------------------------------------------------------
# _get_bundled_templates_source
# ---------------------------------------------------------------------------

class TestGetBundledTemplatesSource:
    def test_returns_pkg_when_yaml_present(self):
        mock_file = MagicMock()
        mock_file.name = "sap-outbound.yaml"
        mock_pkg = MagicMock()
        mock_pkg.iterdir.return_value = [mock_file]
        with patch("importlib.resources.files", return_value=mock_pkg):
            result = _get_bundled_templates_source()
        assert result is mock_pkg

    def test_returns_none_when_no_yaml(self):
        mock_file = MagicMock()
        mock_file.name = "readme.txt"
        mock_pkg = MagicMock()
        mock_pkg.iterdir.return_value = [mock_file]
        with patch("importlib.resources.files", return_value=mock_pkg):
            result = _get_bundled_templates_source()
        assert result is None

    def test_returns_none_on_exception(self):
        with patch("importlib.resources.files", side_effect=Exception("pkg not found")):
            result = _get_bundled_templates_source()
        assert result is None
