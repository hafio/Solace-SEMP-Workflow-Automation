"""SEMP Workflow Automation - Ansible-like playbooks for Solace SEMP."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("semp-workflow")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
