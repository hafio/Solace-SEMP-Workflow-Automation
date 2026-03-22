"""Module registry - auto-discovers and registers all SEMP action modules."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseModule

_REGISTRY: dict[str, BaseModule] = {}


def register(name: str, module: BaseModule) -> None:
    """Register a module action under the given 'object.verb' name."""
    _REGISTRY[name] = module


def get_module(name: str) -> BaseModule:
    """Look up a registered module by 'object.verb' name."""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(f"Unknown module '{name}'. Available: {available}")
    return _REGISTRY[name]


def list_modules() -> list[str]:
    """Return sorted list of all registered module names."""
    return sorted(_REGISTRY.keys())


def get_module_info() -> dict[str, dict]:
    """Return description and param schema for every registered module, sorted by name."""
    return {
        name: {
            "description": mod.description,
            "params": mod.params,
        }
        for name, mod in sorted(_REGISTRY.items())
    }


def _autodiscover() -> None:
    """Import all sibling modules to trigger their MODULES registration."""
    package_dir = Path(__file__).parent
    for _importer, modname, _ispkg in pkgutil.iter_modules([str(package_dir)]):
        if modname == "base":
            continue
        mod = importlib.import_module(f".{modname}", package=__name__)
        if hasattr(mod, "MODULES"):
            for action_name, module_cls in mod.MODULES.items():
                register(action_name, module_cls())


_autodiscover()
