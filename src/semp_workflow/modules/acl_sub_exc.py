"""ACL Subscribe Topic Exception module - acl_subscribe_exception.add, acl_subscribe_exception.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import enc
from .base import BaseModule

logger = logging.getLogger(__name__)


class AclSubscribeExceptionAdd(BaseModule):
    description = "Add a subscribe topic exception to an ACL profile. Skipped if the exception already exists."
    params = {
        "aclProfileName":                  {"type": "string", "required": True,  "description": "Name of the ACL profile"},
        "subscribeTopicException":         {"type": "string", "required": True,  "description": "The topic for the exception (may include wildcards)"},
        "subscribeTopicExceptionSyntax":   {"type": "string", "required": False, "description": "Syntax of the topic", "default": "smf", "enum": ["smf", "mqtt"]},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        profile = args.get("aclProfileName", "")
        topic = args.get("subscribeTopicException", "")
        syntax = args.get("subscribeTopicExceptionSyntax", "smf")

        if not profile:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: aclProfileName")
        if not topic:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: subscribeTopicException")

        path = f"aclProfiles/{enc(profile)}/subscribeTopicExceptions/{enc(syntax)},{enc(topic)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking subscribe topic exception: {e}")

        if exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"Subscribe topic exception '{topic}' already exists on ACL profile '{profile}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would add subscribe topic exception '{topic}' to ACL profile '{profile}'",
            )

        try:
            payload = {
                "aclProfileName": profile,
                "subscribeTopicException": topic,
                "subscribeTopicExceptionSyntax": syntax,
            }
            client.create(f"aclProfiles/{enc(profile)}/subscribeTopicExceptions", payload)
            return ActionResult(
                ResultStatus.OK,
                f"Subscribe topic exception '{topic}' added to ACL profile '{profile}'",
            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED,
                f"Failed to add subscribe topic exception '{topic}' to ACL profile '{profile}': {e}",
            )


class AclSubscribeExceptionDelete(BaseModule):
    description = "Remove a subscribe topic exception from an ACL profile. Skipped if the exception does not exist."
    params = {
        "aclProfileName":                  {"type": "string", "required": True,  "description": "Name of the ACL profile"},
        "subscribeTopicException":         {"type": "string", "required": True,  "description": "The topic exception to remove"},
        "subscribeTopicExceptionSyntax":   {"type": "string", "required": False, "description": "Syntax of the topic", "default": "smf", "enum": ["smf", "mqtt"]},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        profile = args.get("aclProfileName", "")
        topic = args.get("subscribeTopicException", "")
        syntax = args.get("subscribeTopicExceptionSyntax", "smf")

        if not profile:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: aclProfileName")
        if not topic:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: subscribeTopicException")

        path = f"aclProfiles/{enc(profile)}/subscribeTopicExceptions/{enc(syntax)},{enc(topic)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking subscribe topic exception: {e}")

        if not exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"Subscribe topic exception '{topic}' does not exist on ACL profile '{profile}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would remove subscribe topic exception '{topic}' from ACL profile '{profile}'",
            )

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK,
                f"Subscribe topic exception '{topic}' removed from ACL profile '{profile}'",
            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED,
                f"Failed to remove subscribe topic exception '{topic}' from ACL profile '{profile}': {e}",
            )


MODULES = {
    "acl_subscribe_exception.add": AclSubscribeExceptionAdd,
    "acl_subscribe_exception.delete": AclSubscribeExceptionDelete,
}
