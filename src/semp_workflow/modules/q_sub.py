"""Queue Subscription module - q_sub.add, q_sub.delete."""

from __future__ import annotations

import logging

from ..exceptions import SEMPError
from ..models import ActionResult, ResultStatus
from ..semp.client import SempClient, ALREADY_EXISTS
from ..semp.helpers import enc
from .base import BaseModule

logger = logging.getLogger(__name__)


class SubscriptionAdd(BaseModule):
    description = "Add a topic subscription to a queue. Skipped if the subscription already exists."
    params = {
        "queueName":         {"type": "string", "required": True, "description": "Name of the queue to subscribe"},
        "subscriptionTopic": {"type": "string", "required": True, "description": "Topic string to subscribe to (wildcards supported, e.g. FCM/SAP/>)"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        queue_name = args.get("queueName", "")
        topic = args.get("subscriptionTopic", "")
        if not queue_name or not topic:
            return ActionResult(
                ResultStatus.FAILED, "Missing required args: queueName, subscriptionTopic"
            )

        if dry_run:
            path = f"queues/{enc(queue_name)}/subscriptions/{enc(topic)}"
            try:
                exists, _ = client.exists(path)
            except SEMPError:
                exists = False
            if exists:
                return ActionResult(ResultStatus.SKIPPED, f"Subscription already exists")
            return ActionResult(ResultStatus.DRYRUN, f"Would add subscription '{topic}' to queue '{queue_name}'")

        try:
            payload = {
                "queueName": queue_name,
                "subscriptionTopic": topic,
            }
            client.create(f"queues/{enc(queue_name)}/subscriptions", payload)
            return ActionResult(
                ResultStatus.OK,
                f"Subscription '{topic}' added to queue '{queue_name}'",            )
        except SEMPError as e:
            if e.semp_code == ALREADY_EXISTS:
                return ActionResult(
                    ResultStatus.SKIPPED,
                    f"Subscription '{topic}' already exists on queue '{queue_name}'",
                )
            return ActionResult(
                ResultStatus.FAILED,
                f"Failed to add subscription: {e}",
            )


class SubscriptionDelete(BaseModule):
    description = "Remove a topic subscription from a queue. Skipped if the subscription does not exist."
    params = {
        "queueName":         {"type": "string", "required": True, "description": "Name of the queue"},
        "subscriptionTopic": {"type": "string", "required": True, "description": "Topic string to unsubscribe"},
    }

    def execute(self, client: SempClient, args: dict, dry_run: bool = False) -> ActionResult:
        queue_name = args.get("queueName", "")
        topic = args.get("subscriptionTopic", "")
        if not queue_name or not topic:
            return ActionResult(
                ResultStatus.FAILED, "Missing required args: queueName, subscriptionTopic"
            )

        path = f"queues/{enc(queue_name)}/subscriptions/{enc(topic)}"

        try:
            exists, _ = client.exists(path)
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Error checking subscription: {e}")

        if not exists:
            return ActionResult(
                ResultStatus.SKIPPED,
                f"Subscription '{topic}' does not exist on queue '{queue_name}'",
            )

        if dry_run:
            return ActionResult(
                ResultStatus.DRYRUN,
                f"Would remove subscription '{topic}' from queue '{queue_name}'",
            )

        try:
            client.delete(path)
            return ActionResult(
                ResultStatus.OK,
                f"Subscription '{topic}' removed from queue '{queue_name}'",            )
        except SEMPError as e:
            return ActionResult(ResultStatus.FAILED, f"Failed to remove subscription: {e}")


MODULES = {
    "q_sub.add": SubscriptionAdd,
    "q_sub.delete": SubscriptionDelete,
}
