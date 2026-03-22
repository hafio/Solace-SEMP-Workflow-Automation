"""RDP REST Consumer module - rdp_rc.add, rdp_rc.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import check_name_length, clean_payload, coerce_bool, coerce_int, enc
from .base import BaseModule

logger = logging.getLogger(__name__)


def _build_consumer_payload(args: dict) -> dict:
    payload = clean_payload(args)
    payload.pop("restDeliveryPointName", None)  # path param, not a body field
    for bool_field in ("tlsEnabled", "enabled"):
        if bool_field in payload:
            payload[bool_field] = coerce_bool(payload[bool_field])
    for int_field in ("remotePort", "outgoingConnectionCount"):
        if int_field in payload:
            payload[int_field] = coerce_int(payload[int_field])
    return payload


class RdpRestConsumerAdd(BaseModule):
    description = "Add a REST consumer to an RDP. Skipped if the consumer already exists."
    params = {
        # restDeliveryPointName is a path parameter only (Read-Only per SEMP schema) — not sent in body
        "restConsumerName":                {"type": "string",  "required": True,  "description": "Name of the REST consumer"},
        "remoteHost":                      {"type": "string",  "required": False, "description": "Hostname or IP address of the remote HTTP server"},
        # remotePort and tlsEnabled must always be provided together (SEMP requires constraint)
        "remotePort":                      {"type": "integer", "required": False, "description": "TCP port of the remote HTTP server (default: 8080)"},
        "tlsEnabled":                      {"type": "boolean", "required": False, "description": "Use TLS for the connection (default: false)"},
        "enabled":                         {"type": "boolean", "required": False, "description": "Enable the REST consumer after creation (default: false)"},
        "httpMethod":                      {"type": "string",  "required": False, "description": "HTTP method for message delivery", "default": "post", "enum": ["post", "put"]},
        "outgoingConnectionCount":         {"type": "integer", "required": False, "description": "Number of simultaneous outgoing HTTP connections (default: 3)"},
        "authenticationScheme":            {"type": "string",  "required": False, "description": "Authentication scheme", "default": "none", "enum": ["none", "http-basic", "client-certificate", "http-header", "oauth-client", "oauth-jwt", "transparent", "aws"]},
        "authenticationHttpBasicUsername": {"type": "string",  "required": False, "description": "Username for HTTP Basic authentication (requires authenticationHttpBasicPassword)"},
        "authenticationHttpBasicPassword": {"type": "string",  "required": False, "description": "Password for HTTP Basic authentication (requires authenticationHttpBasicUsername)"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        rdp_name = args.get("restDeliveryPointName", "")
        consumer_name = args.get("restConsumerName", "")
        if not rdp_name or not consumer_name:
            return ActionResult(
                ResultStatus.FAILED,
                "Missing required args: restDeliveryPointName, restConsumerName",
            )

        for field, value in (("restDeliveryPointName", rdp_name), ("restConsumerName", consumer_name)):
            if err := check_name_length(field, value):
                return ActionResult(ResultStatus.FAILED, err)

        path = f"restDeliveryPoints/{enc(rdp_name)}/restConsumers/{enc(consumer_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking REST consumer: {e}")

        if exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"REST consumer '{consumer_name}' already exists on RDP '{rdp_name}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would create REST consumer '{consumer_name}' on RDP '{rdp_name}'",
            )

        try:
            payload = _build_consumer_payload(args)
            client.create(
                f"restDeliveryPoints/{enc(rdp_name)}/restConsumers", payload
            )
            return ActionResult(
                ResultStatus.OK,
                f"REST consumer '{consumer_name}' created on RDP '{rdp_name}'",            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED, f"Failed to create REST consumer: {e}"
            )


class RdpRestConsumerDelete(BaseModule):
    description = "Remove a REST consumer from an RDP. Skipped if the consumer does not exist."
    params = {
        "restDeliveryPointName": {"type": "string", "required": True, "description": "Name of the parent REST Delivery Point"},
        "restConsumerName":      {"type": "string", "required": True, "description": "Name of the REST consumer to delete"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        rdp_name = args.get("restDeliveryPointName", "")
        consumer_name = args.get("restConsumerName", "")
        if not rdp_name or not consumer_name:
            return ActionResult(
                ResultStatus.FAILED,
                "Missing required args: restDeliveryPointName, restConsumerName",
            )

        for field, value in (("restDeliveryPointName", rdp_name), ("restConsumerName", consumer_name)):
            if err := check_name_length(field, value):
                return ActionResult(ResultStatus.FAILED, err)

        path = f"restDeliveryPoints/{enc(rdp_name)}/restConsumers/{enc(consumer_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking REST consumer: {e}")

        if not exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"REST consumer '{consumer_name}' does not exist on RDP '{rdp_name}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would delete REST consumer '{consumer_name}' from RDP '{rdp_name}'",
            )

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK,
                f"REST consumer '{consumer_name}' deleted from RDP '{rdp_name}'",            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED, f"Failed to delete REST consumer: {e}"
            )


MODULES = {
    "rdp_rc.add": RdpRestConsumerAdd,
    "rdp_rc.delete": RdpRestConsumerDelete,
}
