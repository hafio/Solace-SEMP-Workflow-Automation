"""Client Username module - client_username.add, client_username.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import check_name_length, clean_payload, coerce_bool, enc
from .base import BaseModule

logger = logging.getLogger(__name__)


def _build_username_payload(args: dict) -> dict:
    payload = clean_payload(args)
    if "enabled" in payload:
        payload["enabled"] = coerce_bool(payload["enabled"])
    return payload


class ClientUsernameAdd(BaseModule):
    description = "Create a client username on the message VPN. Skipped if the username already exists."
    params = {
        "clientUsername":    {"type": "string",  "required": True,  "description": "The client username to create"},
        "clientProfileName": {"type": "string",  "required": False, "description": "Client profile to assign to this username", "default": "default"},
        "aclProfileName":    {"type": "string",  "required": False, "description": "ACL profile to assign to this username", "default": "default"},
        "password":          {"type": "string",  "required": False, "description": "Password for the client username"},
        "enabled":           {"type": "boolean", "required": False, "description": "Enable the client username after creation", "default": "true"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        username = args.get("clientUsername", "")
        if not username:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: clientUsername")

        if err := check_name_length("clientUsername", username):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"clientUsernames/{enc(username)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking client username: {e}")

        if exists:
            return ActionResult(
                ResultStatus.SKIPPED, f"Client username '{username}' already exists"
            )

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would create client username '{username}'")

        try:
            payload = _build_username_payload(args)
            client.create("clientUsernames", payload)
            return ActionResult(
                ResultStatus.OK,
                f"Client username '{username}' created",            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED,
                f"Failed to create client username '{username}': {e}",
            )


class ClientUsernameDelete(BaseModule):
    description = "Delete a client username from the message VPN. Skipped if the username does not exist."
    params = {
        "clientUsername": {"type": "string", "required": True, "description": "The client username to delete"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        username = args.get("clientUsername", "")
        if not username:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: clientUsername")

        if err := check_name_length("clientUsername", username):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"clientUsernames/{enc(username)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking client username: {e}")

        if not exists:
            return ActionResult(
                ResultStatus.SKIPPED, f"Client username '{username}' does not exist"
            )

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would delete client username '{username}'")

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK,
                f"Client username '{username}' deleted",            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED,
                f"Failed to delete client username '{username}': {e}",
            )


MODULES = {
    "client_username.add": ClientUsernameAdd,
    "client_username.delete": ClientUsernameDelete,
}
