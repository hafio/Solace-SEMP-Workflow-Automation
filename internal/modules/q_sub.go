package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("q_sub.add", subscriptionAdd{})
	register("q_sub.delete", subscriptionDelete{})
}

type subscriptionAdd struct{}

func (subscriptionAdd) Description() string {
	return "Add a topic subscription to a queue. Skipped if the subscription already exists."
}

func (subscriptionAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "queueName", Type: "string", Required: true, Description: "Name of the queue to subscribe"},
		{Name: "subscriptionTopic", Type: "string", Required: true, Description: "Topic string to subscribe to (wildcards supported, e.g. SITEA/SAP/>)"},
	}
}

func (subscriptionAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	queueName := argStr(args, "queueName", "")
	topic := argStr(args, "subscriptionTopic", "")
	if queueName == "" || topic == "" {
		return failed("Missing required args: queueName, subscriptionTopic")
	}

	if dryRun {
		path := fmt.Sprintf("queues/%s/subscriptions/%s", semp.Enc(queueName), semp.Enc(topic))
		exists, _, err := c.Exists(path)
		if err != nil {
			exists = false
		}
		if exists {
			return skipped("Subscription already exists")
		}
		return dryrun(fmt.Sprintf("Would add subscription '%s' to queue '%s'", topic, queueName))
	}

	payload := map[string]any{
		"queueName":         queueName,
		"subscriptionTopic": topic,
	}
	if _, err := c.Create(fmt.Sprintf("queues/%s/subscriptions", semp.Enc(queueName)), payload); err != nil {
		if sempCodeOf(err) == semp.AlreadyExists {
			return skipped(fmt.Sprintf("Subscription '%s' already exists on queue '%s'", topic, queueName))
		}
		return failed(fmt.Sprintf("Failed to add subscription: %s", err))
	}
	return ok(fmt.Sprintf("Subscription '%s' added to queue '%s'", topic, queueName))
}

type subscriptionDelete struct{}

func (subscriptionDelete) Description() string {
	return "Remove a topic subscription from a queue. Skipped if the subscription does not exist."
}

func (subscriptionDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "queueName", Type: "string", Required: true, Description: "Name of the queue"},
		{Name: "subscriptionTopic", Type: "string", Required: true, Description: "Topic string to unsubscribe"},
	}
}

func (subscriptionDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	queueName := argStr(args, "queueName", "")
	topic := argStr(args, "subscriptionTopic", "")
	if queueName == "" || topic == "" {
		return failed("Missing required args: queueName, subscriptionTopic")
	}

	path := fmt.Sprintf("queues/%s/subscriptions/%s", semp.Enc(queueName), semp.Enc(topic))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking subscription: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("Subscription '%s' does not exist on queue '%s'", topic, queueName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would remove subscription '%s' from queue '%s'", topic, queueName))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to remove subscription: %s", err))
	}
	return ok(fmt.Sprintf("Subscription '%s' removed from queue '%s'", topic, queueName))
}
