"""ACL Publish Topic Exception module - acl_publish_exception.add, acl_publish_exception.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import enc
from .base import BaseModule

logger = logging.getLogger(__name__)


class AclPublishExceptionAdd(BaseModule):
    description = "Add a publish topic exception to an ACL profile. Skipped if the exception already exists."
    params = {
        "aclProfileName":                {"type": "string", "required": True,  "description": "Name of the ACL profile"},
        "publishTopicException":         {"type": "string", "required": True,  "description": "The topic for the exception (may include wildcards)"},
        "publishTopicExceptionSyntax":   {"type": "string", "required": False, "description": "Syntax of the topic", "default": "smf", "enum": ["smf", "mqtt"]},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        profile = args.get("aclProfileName", "")
        topic = args.get("publishTopicException", "")
        syntax = args.get("publishTopicExceptionSyntax", "smf")

        if not profile:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: aclProfileName")
        if not topic:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: publishTopicException")

        path = f"aclProfiles/{enc(profile)}/publishTopicExceptions/{enc(syntax)},{enc(topic)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking publish topic exception: {e}")

        if exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"Publish topic exception '{topic}' already exists on ACL profile '{profile}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would add publish topic exception '{topic}' to ACL profile '{profile}'",
            )

        try:
            payload = {
                "aclProfileName": profile,
                "publishTopicException": topic,
                "publishTopicExceptionSyntax": syntax,
            }
            client.create(f"aclProfiles/{enc(profile)}/publishTopicExceptions", payload)
            return ActionResult(
                ResultStatus.OK,
                f"Publish topic exception '{topic}' added to ACL profile '{profile}'",
            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED,
                f"Failed to add publish topic exception '{topic}' to ACL profile '{profile}': {e}",
            )


class AclPublishExceptionDelete(BaseModule):
    description = "Remove a publish topic exception from an ACL profile. Skipped if the exception does not exist."
    params = {
        "aclProfileName":                {"type": "string", "required": True,  "description": "Name of the ACL profile"},
        "publishTopicException":         {"type": "string", "required": True,  "description": "The topic exception to remove"},
        "publishTopicExceptionSyntax":   {"type": "string", "required": False, "description": "Syntax of the topic", "default": "smf", "enum": ["smf", "mqtt"]},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        profile = args.get("aclProfileName", "")
        topic = args.get("publishTopicException", "")
        syntax = args.get("publishTopicExceptionSyntax", "smf")

        if not profile:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: aclProfileName")
        if not topic:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: publishTopicException")

        path = f"aclProfiles/{enc(profile)}/publishTopicExceptions/{enc(syntax)},{enc(topic)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking publish topic exception: {e}")

        if not exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"Publish topic exception '{topic}' does not exist on ACL profile '{profile}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would remove publish topic exception '{topic}' from ACL profile '{profile}'",
            )

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK,
                f"Publish topic exception '{topic}' removed from ACL profile '{profile}'",
            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED,
                f"Failed to remove publish topic exception '{topic}' from ACL profile '{profile}': {e}",
            )


MODULES = {
    "acl_publish_exception.add": AclPublishExceptionAdd,
    "acl_publish_exception.delete": AclPublishExceptionDelete,
}
