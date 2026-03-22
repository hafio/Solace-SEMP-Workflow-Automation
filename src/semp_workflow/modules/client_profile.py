"""Client Profile module - client_profile.add, client_profile.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import check_name_length, clean_payload, coerce_bool, coerce_int, enc
from .base import BaseModule

logger = logging.getLogger(__name__)

BOOL_FIELDS = {
    "allowGuaranteedMsgSendEnabled",
    "allowGuaranteedMsgReceiveEnabled",
    "allowTransactedSessionsEnabled",
    "allowBridgeConnectionsEnabled",
}

INT_FIELDS = {
    "maxConnectionCountPerClientUsername",
    "maxEgressFlowCount",
    "maxIngressFlowCount",
    "maxSubscriptionCount",
}


def _build_profile_payload(args: dict) -> dict:
    payload = clean_payload(args)
    for key in BOOL_FIELDS:
        if key in payload:
            payload[key] = coerce_bool(payload[key])
    for key in INT_FIELDS:
        if key in payload:
            payload[key] = coerce_int(payload[key])
    return payload


class ClientProfileAdd(BaseModule):
    description = "Create a client profile on the message VPN. Skipped if the profile already exists."
    params = {
        "clientProfileName":                    {"type": "string",  "required": True,  "description": "Name of the client profile"},
        "allowGuaranteedMsgSendEnabled":         {"type": "boolean", "required": False, "description": "Allow clients to send guaranteed messages"},
        "allowGuaranteedMsgReceiveEnabled":      {"type": "boolean", "required": False, "description": "Allow clients to receive guaranteed messages"},
        "allowTransactedSessionsEnabled":        {"type": "boolean", "required": False, "description": "Allow clients to use transacted sessions"},
        "allowBridgeConnectionsEnabled":         {"type": "boolean", "required": False, "description": "Allow clients to use bridge connections"},
        "maxConnectionCountPerClientUsername":   {"type": "integer", "required": False, "description": "Maximum connections per client username (0 = unlimited)"},
        "maxEgressFlowCount":                    {"type": "integer", "required": False, "description": "Maximum number of egress flows per client"},
        "maxIngressFlowCount":                   {"type": "integer", "required": False, "description": "Maximum number of ingress flows per client"},
        "maxSubscriptionCount":                  {"type": "integer", "required": False, "description": "Maximum number of subscriptions per client"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        name = args.get("clientProfileName", "")
        if not name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: clientProfileName")

        if err := check_name_length("clientProfileName", name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"clientProfiles/{enc(name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking client profile: {e}")

        if exists:
            return ActionResult(ResultStatus.SKIPPED, f"Client profile '{name}' already exists")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would create client profile '{name}'")

        try:
            payload = _build_profile_payload(args)
            client.create("clientProfiles", payload)
            return ActionResult(
                ResultStatus.OK, f"Client profile '{name}' created"            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED, f"Failed to create client profile '{name}': {e}"
            )


class ClientProfileDelete(BaseModule):
    description = "Delete a client profile from the message VPN. Skipped if the profile does not exist."
    params = {
        "clientProfileName": {"type": "string", "required": True, "description": "Name of the client profile to delete"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        name = args.get("clientProfileName", "")
        if not name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: clientProfileName")

        if err := check_name_length("clientProfileName", name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"clientProfiles/{enc(name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking client profile: {e}")

        if not exists:
            return ActionResult(ResultStatus.SKIPPED, f"Client profile '{name}' does not exist")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would delete client profile '{name}'")

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK, f"Client profile '{name}' deleted"            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED, f"Failed to delete client profile '{name}': {e}"
            )


MODULES = {
    "client_profile.add": ClientProfileAdd,
    "client_profile.delete": ClientProfileDelete,
}
