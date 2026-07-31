package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("queue.add", queueAdd{})
	register("queue.delete", queueDelete{})
	register("queue.update", queueUpdate{})
}

// buildQueuePayload builds a SEMP queue payload with type coercion and derives
// respectTtlEnabled/redeliveryEnabled.
func buildQueuePayload(args map[string]any) (map[string]any, error) {
	payload := semp.CleanPayload(args)
	coerceBoolFields(payload, "ingressEnabled", "egressEnabled")
	if err := coerceIntFields(payload, "maxMsgSpoolUsage", "maxTtl", "maxRedeliveryCount"); err != nil {
		return nil, err
	}
	// Derive respectTtlEnabled from maxTtl: 0 disables it, positive enables it.
	if v, ok := payload["maxTtl"]; ok {
		payload["respectTtlEnabled"] = v.(int) > 0
	}
	if v, ok := payload["maxRedeliveryCount"]; ok {
		// -1 is a sentinel meaning "disable redelivery and set count to 0".
		if v.(int) == -1 {
			payload["maxRedeliveryCount"] = 0
			payload["redeliveryEnabled"] = false
		} else {
			payload["redeliveryEnabled"] = v.(int) != 0
		}
	}
	return payload, nil
}

type queueAdd struct{}

func (queueAdd) Description() string {
	return "Create a queue on the message VPN. Skipped if the queue already exists."
}

func (queueAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "queueName", Type: "string", Required: true, Description: "Name of the queue to create"},
		{Name: "accessType", Type: "string", Description: "Message delivery pattern", Default: "exclusive", Enum: []string{"exclusive", "non-exclusive"}},
		{Name: "owner", Type: "string", Description: "Client username that owns the queue"},
		{Name: "permission", Type: "string", Description: "Permission for non-owner clients", Default: "no-access", Enum: []string{"no-access", "read-only", "consume", "modify-topic", "delete"}},
		{Name: "deadMsgQueue", Type: "string", Description: "Name of the dead-message queue for undeliverable messages"},
		{Name: "maxMsgSpoolUsage", Type: "integer", Description: "Maximum spool usage in MB (0 = unlimited)"},
		{Name: "maxTtl", Type: "integer", Description: "Maximum time-to-live for messages in seconds. 0 disables TTL enforcement; any positive value enables it automatically."},
		{Name: "ingressEnabled", Type: "boolean", Description: "Allow clients to send messages to the queue", Default: "true"},
		{Name: "egressEnabled", Type: "boolean", Description: "Allow clients to consume messages from the queue", Default: "true"},
		{Name: "maxRedeliveryCount", Type: "integer", Description: "Maximum redelivery attempts before routing to DMQ (0 = unlimited)"},
		{Name: "rejectMsgToSenderOnDiscardBehavior", Type: "string", Description: "Action when a message is discarded", Enum: []string{"never", "when-queue-enabled", "always"}},
	}
}

func (queueAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	queueName := argStr(args, "queueName", "")
	if queueName == "" {
		return failed("Missing required arg: queueName")
	}
	if err := semp.CheckNameLength("queueName", queueName); err != "" {
		return failed(err)
	}

	path := "queues/" + semp.Enc(queueName)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking queue: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("Queue '%s' already exists", queueName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would create queue '%s'", queueName))
	}

	payload, err := buildQueuePayload(args)
	if err != nil {
		return failed(err.Error())
	}
	if _, err := c.Create("queues", payload); err != nil {
		return failed(fmt.Sprintf("Failed to create queue '%s': %s", queueName, err))
	}
	return ok(fmt.Sprintf("Queue '%s' created", queueName))
}

type queueDelete struct{}

func (queueDelete) Description() string {
	return "Delete a queue from the message VPN. Skipped if the queue does not exist."
}

func (queueDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "queueName", Type: "string", Required: true, Description: "Name of the queue to delete"},
	}
}

func (queueDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	queueName := argStr(args, "queueName", "")
	if queueName == "" {
		return failed("Missing required arg: queueName")
	}
	if err := semp.CheckNameLength("queueName", queueName); err != "" {
		return failed(err)
	}

	path := "queues/" + semp.Enc(queueName)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking queue: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("Queue '%s' does not exist", queueName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would delete queue '%s'", queueName))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to delete queue '%s': %s", queueName, err))
	}
	return ok(fmt.Sprintf("Queue '%s' deleted", queueName))
}

type queueUpdate struct{}

func (queueUpdate) Description() string {
	return "Update attributes of an existing queue. Fails if the queue does not exist."
}

func (queueUpdate) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "queueName", Type: "string", Required: true, Description: "Name of the queue to update"},
		{Name: "accessType", Type: "string", Description: "Message delivery pattern", Enum: []string{"exclusive", "non-exclusive"}},
		{Name: "owner", Type: "string", Description: "Client username that owns the queue"},
		{Name: "permission", Type: "string", Description: "Permission for non-owner clients", Enum: []string{"no-access", "read-only", "consume", "modify-topic", "delete"}},
		{Name: "deadMsgQueue", Type: "string", Description: "Name of the dead-message queue for undeliverable messages"},
		{Name: "maxMsgSpoolUsage", Type: "integer", Description: "Maximum spool usage in MB (0 = unlimited)"},
		{Name: "maxTtl", Type: "integer", Description: "Maximum time-to-live for messages in seconds. 0 disables TTL enforcement; any positive value enables it automatically."},
		{Name: "ingressEnabled", Type: "boolean", Description: "Allow clients to send messages to the queue"},
		{Name: "egressEnabled", Type: "boolean", Description: "Allow clients to consume messages from the queue"},
		{Name: "maxRedeliveryCount", Type: "integer", Description: "Maximum redelivery attempts before routing to DMQ (0 = unlimited)"},
		{Name: "rejectMsgToSenderOnDiscardBehavior", Type: "string", Description: "Action when a message is discarded", Enum: []string{"never", "when-queue-enabled", "always"}},
	}
}

func (queueUpdate) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	queueName := argStr(args, "queueName", "")
	if queueName == "" {
		return failed("Missing required arg: queueName")
	}
	if err := semp.CheckNameLength("queueName", queueName); err != "" {
		return failed(err)
	}

	path := "queues/" + semp.Enc(queueName)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking queue: %s", err))
	}
	if !exists {
		return failed(fmt.Sprintf("Queue '%s' does not exist", queueName))
	}

	payload, err := buildQueuePayload(args)
	if err != nil {
		return failed(err.Error())
	}
	delete(payload, "queueName")

	if len(payload) == 0 {
		return skipped("No fields to update")
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would update queue '%s'", queueName))
	}

	if _, err := c.Update(path, payload); err != nil {
		return failed(fmt.Sprintf("Failed to update queue '%s': %s", queueName, err))
	}
	return ok(fmt.Sprintf("Queue '%s' updated", queueName))
}
