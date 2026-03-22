"""Unit tests for __main__.py - python -m semp_workflow entry point."""

from unittest.mock import patch
import runpy


def test_main_module_calls_cli():
    """Running as __main__ calls the CLI main() function."""
    with patch("semp_workflow.cli.main") as mock_main:
        runpy.run_module("semp_workflow", run_name="__main__", alter_sys=True)
    mock_main.assert_called_once()
