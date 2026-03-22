"""Queue Binding module - rdp_qb.add, rdp_qb.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient, ALREADY_EXISTS
from ..semp.helpers import check_name_length, clean_payload, coerce_bool, enc
from .base import BaseModule

logger = logging.getLogger(__name__)


class QueueBindingAdd(BaseModule):
    description = "Bind a queue to an RDP for message delivery. Skipped if the binding already exists."
    params = {
        "restDeliveryPointName":              {"type": "string",  "required": True,  "description": "Name of the REST Delivery Point"},
        "queueBindingName":                   {"type": "string",  "required": True,  "description": "Name of the queue to bind"},
        "postRequestTarget":                  {"type": "string",  "required": False, "description": "HTTP request target path appended to the REST consumer URL"},
        "gatewayReplaceTargetAuthorityEnabled":{"type": "boolean", "required": False, "description": "Replace the authority in forwarded HTTP requests with the remote host"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        rdp_name = args.get("restDeliveryPointName", "")
        binding_name = args.get("queueBindingName", "")
        if not rdp_name or not binding_name:
            return ActionResult(
                ResultStatus.FAILED, "Missing required args: restDeliveryPointName, queueBindingName"
            )

        for field, value in (("restDeliveryPointName", rdp_name), ("queueBindingName", binding_name)):
            if err := check_name_length(field, value):
                return ActionResult(ResultStatus.FAILED, err)

        path = f"restDeliveryPoints/{enc(rdp_name)}/queueBindings/{enc(binding_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking queue binding: {e}")

        if exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"Queue binding '{binding_name}' already exists on RDP '{rdp_name}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would create queue binding '{binding_name}' on RDP '{rdp_name}'",
            )

        try:
            payload = clean_payload(args)
            payload.pop("restDeliveryPointName", None)  # path param, not a body field
            if "gatewayReplaceTargetAuthorityEnabled" in payload:
                payload["gatewayReplaceTargetAuthorityEnabled"] = coerce_bool(
                    payload["gatewayReplaceTargetAuthorityEnabled"]
                )
            client.create(
                f"restDeliveryPoints/{enc(rdp_name)}/queueBindings", payload
            )
            return ActionResult(
                ResultStatus.OK,
                f"Queue binding '{binding_name}' created on RDP '{rdp_name}'",            )
        except SEMPError as e:
            if e.semp_code == ALREADY_EXISTS:
                return ActionResult(
                    ResultStatus.SKIPPED,
                    f"Queue binding '{binding_name}' already exists on RDP '{rdp_name}'",
                )
            return ActionResult(
                ResultStatus.FAILED, f"Failed to create queue binding: {e}"
            )


class QueueBindingDelete(BaseModule):
    description = "Remove a queue binding from an RDP. Skipped if the binding does not exist."
    params = {
        "restDeliveryPointName": {"type": "string", "required": True, "description": "Name of the REST Delivery Point"},
        "queueBindingName":      {"type": "string", "required": True, "description": "Name of the bound queue to remove"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        rdp_name = args.get("restDeliveryPointName", "")
        binding_name = args.get("queueBindingName", "")
        if not rdp_name or not binding_name:
            return ActionResult(
                ResultStatus.FAILED, "Missing required args: restDeliveryPointName, queueBindingName"
            )

        for field, value in (("restDeliveryPointName", rdp_name), ("queueBindingName", binding_name)):
            if err := check_name_length(field, value):
                return ActionResult(ResultStatus.FAILED, err)

        path = f"restDeliveryPoints/{enc(rdp_name)}/queueBindings/{enc(binding_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking queue binding: {e}")

        if not exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"Queue binding '{binding_name}' does not exist on RDP '{rdp_name}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would delete queue binding '{binding_name}' from RDP '{rdp_name}'",
            )

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK,
                f"Queue binding '{binding_name}' deleted from RDP '{rdp_name}'",            )
        except SEMPError as e:
            return ActionResult(
                ResultStatus.FAILED, f"Failed to delete queue binding: {e}"
            )


MODULES = {
    "rdp_qb.add": QueueBindingAdd,
    "rdp_qb.delete": QueueBindingDelete,
}
