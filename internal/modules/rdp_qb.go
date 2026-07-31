package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("rdp_qb.add", queueBindingAdd{})
	register("rdp_qb.delete", queueBindingDelete{})
}

type queueBindingAdd struct{}

func (queueBindingAdd) Description() string {
	return "Bind a queue to an RDP for message delivery. Skipped if the binding already exists."
}

func (queueBindingAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "restDeliveryPointName", Type: "string", Required: true, Description: "Name of the REST Delivery Point"},
		{Name: "queueBindingName", Type: "string", Required: true, Description: "Name of the queue to bind"},
		{Name: "postRequestTarget", Type: "string", Description: "HTTP request target path appended to the REST consumer URL"},
		{Name: "gatewayReplaceTargetAuthorityEnabled", Type: "boolean", Description: "Replace the authority in forwarded HTTP requests with the remote host"},
	}
}

func (queueBindingAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	rdpName := argStr(args, "restDeliveryPointName", "")
	bindingName := argStr(args, "queueBindingName", "")
	if rdpName == "" || bindingName == "" {
		return failed("Missing required args: restDeliveryPointName, queueBindingName")
	}
	for _, f := range []struct{ field, value string }{
		{"restDeliveryPointName", rdpName},
		{"queueBindingName", bindingName},
	} {
		if err := semp.CheckNameLength(f.field, f.value); err != "" {
			return failed(err)
		}
	}

	path := fmt.Sprintf("restDeliveryPoints/%s/queueBindings/%s", semp.Enc(rdpName), semp.Enc(bindingName))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking queue binding: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("Queue binding '%s' already exists on RDP '%s'", bindingName, rdpName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would create queue binding '%s' on RDP '%s'", bindingName, rdpName))
	}

	payload := semp.CleanPayload(args)
	delete(payload, "restDeliveryPointName") // path param, not a body field
	coerceBoolFields(payload, "gatewayReplaceTargetAuthorityEnabled")
	if _, err := c.Create(fmt.Sprintf("restDeliveryPoints/%s/queueBindings", semp.Enc(rdpName)), payload); err != nil {
		if sempCodeOf(err) == semp.AlreadyExists {
			return skipped(fmt.Sprintf("Queue binding '%s' already exists on RDP '%s'", bindingName, rdpName))
		}
		return failed(fmt.Sprintf("Failed to create queue binding: %s", err))
	}
	return ok(fmt.Sprintf("Queue binding '%s' created on RDP '%s'", bindingName, rdpName))
}

type queueBindingDelete struct{}

func (queueBindingDelete) Description() string {
	return "Remove a queue binding from an RDP. Skipped if the binding does not exist."
}

func (queueBindingDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "restDeliveryPointName", Type: "string", Required: true, Description: "Name of the REST Delivery Point"},
		{Name: "queueBindingName", Type: "string", Required: true, Description: "Name of the bound queue to remove"},
	}
}

func (queueBindingDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	rdpName := argStr(args, "restDeliveryPointName", "")
	bindingName := argStr(args, "queueBindingName", "")
	if rdpName == "" || bindingName == "" {
		return failed("Missing required args: restDeliveryPointName, queueBindingName")
	}
	for _, f := range []struct{ field, value string }{
		{"restDeliveryPointName", rdpName},
		{"queueBindingName", bindingName},
	} {
		if err := semp.CheckNameLength(f.field, f.value); err != "" {
			return failed(err)
		}
	}

	path := fmt.Sprintf("restDeliveryPoints/%s/queueBindings/%s", semp.Enc(rdpName), semp.Enc(bindingName))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking queue binding: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("Queue binding '%s' does not exist on RDP '%s'", bindingName, rdpName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would delete queue binding '%s' from RDP '%s'", bindingName, rdpName))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to delete queue binding: %s", err))
	}
	return ok(fmt.Sprintf("Queue binding '%s' deleted from RDP '%s'", bindingName, rdpName))
}
