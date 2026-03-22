"""ACL Profile module - acl_profile.add, acl_profile.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import check_name_length, clean_payload, enc
from .base import BaseModule

logger = logging.getLogger(__name__)


class AclProfileAdd(BaseModule):
    description = "Create an ACL profile on the message VPN. Skipped if the profile already exists."
    params = {
        "aclProfileName":              {"type": "string", "required": True,  "description": "Name of the ACL profile"},
        "clientConnectDefaultAction":  {"type": "string", "required": False, "description": "Default action for client connections", "default": "disallow", "enum": ["allow", "disallow"]},
        "publishTopicDefaultAction":   {"type": "string", "required": False, "description": "Default action for publish topic exceptions", "default": "disallow", "enum": ["allow", "disallow"]},
        "subscribeTopicDefaultAction": {"type": "string", "required": False, "description": "Default action for subscribe topic exceptions", "default": "disallow", "enum": ["allow", "disallow"]},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        name = args.get("aclProfileName", "")
        if not name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: aclProfileName")

        if err := check_name_length("aclProfileName", name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"aclProfiles/{enc(name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking ACL profile: {e}")

        if exists:
            return ActionResult(ResultStatus.SKIPPED, f"ACL profile '{name}' already exists")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would create ACL profile '{name}'")

        try:
            payload = clean_payload(args)
            client.create("aclProfiles", payload)
            return ActionResult(
                ResultStatus.OK, f"ACL profile '{name}' created"            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED, f"Failed to create ACL profile '{name}': {e}"
            )


class AclProfileDelete(BaseModule):
    description = "Delete an ACL profile from the message VPN. Skipped if the profile does not exist."
    params = {
        "aclProfileName": {"type": "string", "required": True, "description": "Name of the ACL profile to delete"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        name = args.get("aclProfileName", "")
        if not name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: aclProfileName")

        if err := check_name_length("aclProfileName", name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"aclProfiles/{enc(name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking ACL profile: {e}")

        if not exists:
            return ActionResult(ResultStatus.SKIPPED, f"ACL profile '{name}' does not exist")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would delete ACL profile '{name}'")

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK, f"ACL profile '{name}' deleted"            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED, f"Failed to delete ACL profile '{name}': {e}"
            )


MODULES = {
    "acl_profile.add": AclProfileAdd,
    "acl_profile.delete": AclProfileDelete,
}
