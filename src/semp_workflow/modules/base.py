"""Base module class for all SEMP action modules."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import ActionResult
from ..semp.client import SempClient


class BaseModule(ABC):
    """Abstract base for all SEMP action modules.

    Every module implements idempotent execute():
    1. Check current state (does the resource exist?)
    2. If already in desired state -> SKIPPED
    3. If dry_run -> report what would happen, return OK
    4. Perform the action
    5. Return OK on success, FAILED on error
    """

    # One-line description of what this action does
    description: str = ""

    # Parameter schema: param_name -> {type, required, description[, default]}
    params: dict[str, dict] = {}

    @abstractmethod
    def execute(
        self, client: SempClient, args: dict, dry_run: bool = False
    ) -> ActionResult:
        """Execute the module action idempotently."""
        ...
