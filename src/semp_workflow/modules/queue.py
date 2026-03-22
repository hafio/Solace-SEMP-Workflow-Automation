"""Queue module - queue.add, queue.delete, queue.update."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient
from ..semp.helpers import check_name_length, clean_payload, coerce_bool, coerce_int, enc
from .base import BaseModule

logger = logging.getLogger(__name__)

BOOL_FIELDS = {"ingressEnabled", "egressEnabled"}
INT_FIELDS = {"maxMsgSpoolUsage", "maxTtl", "maxRedeliveryCount"}


def _build_queue_payload(args: dict) -> dict:
    """Build a SEMP queue payload with proper type coercion."""
    payload = clean_payload(args)
    for key in BOOL_FIELDS:
        if key in payload:
            payload[key] = coerce_bool(payload[key])
    for key in INT_FIELDS:
        if key in payload:
            payload[key] = coerce_int(payload[key])
    # Derive respectTtlEnabled from maxTtl: 0 disables it, any positive value enables it
    if "maxTtl" in payload:
        payload["respectTtlEnabled"] = payload["maxTtl"] > 0
    if "maxRedeliveryCount" in payload:
        # -1 is a sentinel meaning "disable redelivery and set count to 0"
        if payload["maxRedeliveryCount"] == -1:
            payload["maxRedeliveryCount"] = 0
            payload["redeliveryEnabled"] = False
        else:
            payload["redeliveryEnabled"] = (payload["maxRedeliveryCount"] != 0)
    return payload


class QueueAdd(BaseModule):
    description = "Create a queue on the message VPN. Skipped if the queue already exists."
    params = {
        "queueName":                          {"type": "string",  "required": True,  "description": "Name of the queue to create"},
        "accessType":                         {"type": "string",  "required": False, "description": "Message delivery pattern", "default": "exclusive", "enum": ["exclusive", "non-exclusive"]},
        "owner":                              {"type": "string",  "required": False, "description": "Client username that owns the queue"},
        "permission":                         {"type": "string",  "required": False, "description": "Permission for non-owner clients", "default": "no-access", "enum": ["no-access", "read-only", "consume", "modify-topic", "delete"]},
        "deadMsgQueue":                       {"type": "string",  "required": False, "description": "Name of the dead-message queue for undeliverable messages"},
        "maxMsgSpoolUsage":                   {"type": "integer", "required": False, "description": "Maximum spool usage in MB (0 = unlimited)"},
        "maxTtl":                             {"type": "integer", "required": False, "description": "Maximum time-to-live for messages in seconds. 0 disables TTL enforcement; any positive value enables it automatically."},
        "ingressEnabled":                     {"type": "boolean", "required": False, "description": "Allow clients to send messages to the queue", "default": "true"},
        "egressEnabled":                      {"type": "boolean", "required": False, "description": "Allow clients to consume messages from the queue", "default": "true"},
        "maxRedeliveryCount":                 {"type": "integer", "required": False, "description": "Maximum redelivery attempts before routing to DMQ (0 = unlimited)"},
        "rejectMsgToSenderOnDiscardBehavior": {"type": "string",  "required": False, "description": "Action when a message is discarded", "enum": ["never", "when-queue-enabled", "always"]},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        queue_name = args.get("queueName", "")
        if not queue_name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: queueName")

        if err := check_name_length("queueName", queue_name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"queues/{enc(queue_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking queue: {e}")

        if exists:
            return ActionResult(ResultStatus.SKIPPED, f"Queue '{queue_name}' already exists")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would create queue '{queue_name}'")

        try:
            payload = _build_queue_payload(args)
            client.create("queues", payload)
            return ActionResult(ResultStatus.OK, f"Queue '{queue_name}' created")
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Failed to create queue '{queue_name}': {e}")


class QueueDelete(BaseModule):
    description = "Delete a queue from the message VPN. Skipped if the queue does not exist."
    params = {
        "queueName": {"type": "string", "required": True, "description": "Name of the queue to delete"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        queue_name = args.get("queueName", "")
        if not queue_name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: queueName")

        if err := check_name_length("queueName", queue_name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"queues/{enc(queue_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking queue: {e}")

        if not exists:
            return ActionResult(ResultStatus.SKIPPED, f"Queue '{queue_name}' does not exist")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would delete queue '{queue_name}'")

        try:
            client.delete(path)
            return ActionResult(ResultStatus.OK, f"Queue '{queue_name}' deleted")
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Failed to delete queue '{queue_name}': {e}")


class QueueUpdate(BaseModule):
    description = "Update attributes of an existing queue. Fails if the queue does not exist."
    params = {
        "queueName":                          {"type": "string",  "required": True,  "description": "Name of the queue to update"},
        "accessType":                         {"type": "string",  "required": False, "description": "Message delivery pattern", "enum": ["exclusive", "non-exclusive"]},
        "owner":                              {"type": "string",  "required": False, "description": "Client username that owns the queue"},
        "permission":                         {"type": "string",  "required": False, "description": "Permission for non-owner clients", "enum": ["no-access", "read-only", "consume", "modify-topic", "delete"]},
        "deadMsgQueue":                       {"type": "string",  "required": False, "description": "Name of the dead-message queue for undeliverable messages"},
        "maxMsgSpoolUsage":                   {"type": "integer", "required": False, "description": "Maximum spool usage in MB (0 = unlimited)"},
        "maxTtl":                             {"type": "integer", "required": False, "description": "Maximum time-to-live for messages in seconds. 0 disables TTL enforcement; any positive value enables it automatically."},
        "ingressEnabled":                     {"type": "boolean", "required": False, "description": "Allow clients to send messages to the queue"},
        "egressEnabled":                      {"type": "boolean", "required": False, "description": "Allow clients to consume messages from the queue"},
        "maxRedeliveryCount":                 {"type": "integer", "required": False, "description": "Maximum redelivery attempts before routing to DMQ (0 = unlimited)"},
        "rejectMsgToSenderOnDiscardBehavior": {"type": "string",  "required": False, "description": "Action when a message is discarded", "enum": ["never", "when-queue-enabled", "always"]},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        queue_name = args.get("queueName", "")
        if not queue_name:
            return ActionResult(ResultStatus.FAILED, "Missing required arg: queueName")

        if err := check_name_length("queueName", queue_name):
            return ActionResult(ResultStatus.FAILED, err)

        path = f"queues/{enc(queue_name)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking queue: {e}")

        if not exists:
            return ActionResult(ResultStatus.FAILED, f"Queue '{queue_name}' does not exist")

        payload = _build_queue_payload(args)
        payload.pop("queueName", None)

        if not payload:
            return ActionResult(ResultStatus.SKIPPED, "No fields to update")

        if dry_run:
            return ActionResult(ResultStatus.DRYRUN, f"Would update queue '{queue_name}'")

        try:
            client.update(path, payload)
            return ActionResult(ResultStatus.OK, f"Queue '{queue_name}' updated")
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Failed to update queue '{queue_name}': {e}")


MODULES = {
    "queue.add": QueueAdd,
    "queue.delete": QueueDelete,
    "queue.update": QueueUpdate,
}
