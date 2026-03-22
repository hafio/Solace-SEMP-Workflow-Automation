"""RDP module - rdp.add, rdp.delete, rdp.update."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import check_name_length, clean_payload, coerce_bool, enc
from .base import BaseModule

logger = logging.getLogger(__name__)


def _build_rdp_payload(args: dict) -> dict:
    payload = clean_payload(args)
    if "enabled" in payload:
        payload["enabled"] = coerce_bool(payload["enabled"])
    return payload


class RdpAdd(BaseModule):
    description = "Create a REST Delivery Point (RDP). Skipped if the RDP already exists."
    params = {
        "restDeliveryPointName": {"type": "string",  "required": True,  "description": "Name of the REST Delivery Point"},
        "clientProfileName":     {"type": "string",  "required": False, "description": "Client profile to associate with the RDP", "default": "default"},
        "enabled":               {"type": "boolean", "required": False, "description": "Enable the RDP after creation", "default": "true"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        rdp_name = args.get("restDeliveryPointName", "")
        if not rdp_name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: restDeliveryPointName")

        if err := check_name_length("restDeliveryPointName", rdp_name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"restDeliveryPoints/{enc(rdp_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking RDP: {e}")

        if exists:
            return ActionResult(ResultStatus.SKIPPED, f"RDP '{rdp_name}' already exists")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would create RDP '{rdp_name}'")

        try:
            payload = _build_rdp_payload(args)
            client.create("restDeliveryPoints", payload)
            return ActionResult(ResultStatus.OK, f"RDP '{rdp_name}' created")
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Failed to create RDP '{rdp_name}': {e}")


class RdpDelete(BaseModule):
    description = "Delete a REST Delivery Point. Skipped if the RDP does not exist."
    params = {
        "restDeliveryPointName": {"type": "string", "required": True, "description": "Name of the REST Delivery Point to delete"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        rdp_name = args.get("restDeliveryPointName", "")
        if not rdp_name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: restDeliveryPointName")

        if err := check_name_length("restDeliveryPointName", rdp_name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"restDeliveryPoints/{enc(rdp_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking RDP: {e}")

        if not exists:
            return ActionResult(ResultStatus.SKIPPED, f"RDP '{rdp_name}' does not exist")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would delete RDP '{rdp_name}'")

        try:
            client.delete(path)
            return ActionResult(ResultStatus.OK, f"RDP '{rdp_name}' deleted")
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Failed to delete RDP '{rdp_name}': {e}")


class RdpUpdate(BaseModule):
    description = "Update attributes of an existing RDP. Fails if the RDP does not exist."
    params = {
        "restDeliveryPointName": {"type": "string",  "required": True,  "description": "Name of the REST Delivery Point to update"},
        "clientProfileName":     {"type": "string",  "required": False, "description": "Client profile to associate with the RDP"},
        "enabled":               {"type": "boolean", "required": False, "description": "Enable or disable the RDP"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        rdp_name = args.get("restDeliveryPointName", "")
        if not rdp_name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: restDeliveryPointName")

        if err := check_name_length("restDeliveryPointName", rdp_name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"restDeliveryPoints/{enc(rdp_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking RDP: {e}")

        if not exists:
            return ActionResult(ResultStatus.FAILED, f"RDP '{rdp_name}' does not exist")

        payload = _build_rdp_payload(args)
        payload.pop("restDeliveryPointName", None)

        if not payload:
            return ActionResult(ResultStatus.SKIPPED, "No fields to update")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would update RDP '{rdp_name}'")

        try:
            client.update(path, payload)
            return ActionResult(ResultStatus.OK, f"RDP '{rdp_name}' updated")
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Failed to update RDP '{rdp_name}': {e}")


MODULES = {
    "rdp.add": RdpAdd,
    "rdp.delete": RdpDelete,
    "rdp.update": RdpUpdate,
}
