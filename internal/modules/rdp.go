package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("rdp.add", rdpAdd{})
	register("rdp.delete", rdpDelete{})
	register("rdp.update", rdpUpdate{})
}

// buildRdpPayload cleans args and coerces the enabled flag.
func buildRdpPayload(args map[string]any) map[string]any {
	payload := semp.CleanPayload(args)
	coerceBoolFields(payload, "enabled")
	return payload
}

type rdpAdd struct{}

func (rdpAdd) Description() string {
	return "Create a REST Delivery Point (RDP). Skipped if the RDP already exists."
}

func (rdpAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "restDeliveryPointName", Type: "string", Required: true, Description: "Name of the REST Delivery Point"},
		{Name: "clientProfileName", Type: "string", Description: "Client profile to associate with the RDP", Default: "default"},
		{Name: "enabled", Type: "boolean", Description: "Enable the RDP after creation", Default: "true"},
	}
}

func (rdpAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	rdpName := argStr(args, "restDeliveryPointName", "")
	if rdpName == "" {
		return failed("Missing required arg: restDeliveryPointName")
	}
	if err := semp.CheckNameLength("restDeliveryPointName", rdpName); err != "" {
		return failed(err)
	}

	path := "restDeliveryPoints/" + semp.Enc(rdpName)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking RDP: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("RDP '%s' already exists", rdpName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would create RDP '%s'", rdpName))
	}

	if _, err := c.Create("restDeliveryPoints", buildRdpPayload(args)); err != nil {
		return failed(fmt.Sprintf("Failed to create RDP '%s': %s", rdpName, err))
	}
	return ok(fmt.Sprintf("RDP '%s' created", rdpName))
}

type rdpDelete struct{}

func (rdpDelete) Description() string {
	return "Delete a REST Delivery Point. Skipped if the RDP does not exist."
}

func (rdpDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "restDeliveryPointName", Type: "string", Required: true, Description: "Name of the REST Delivery Point to delete"},
	}
}

func (rdpDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	rdpName := argStr(args, "restDeliveryPointName", "")
	if rdpName == "" {
		return failed("Missing required arg: restDeliveryPointName")
	}
	if err := semp.CheckNameLength("restDeliveryPointName", rdpName); err != "" {
		return failed(err)
	}

	path := "restDeliveryPoints/" + semp.Enc(rdpName)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking RDP: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("RDP '%s' does not exist", rdpName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would delete RDP '%s'", rdpName))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to delete RDP '%s': %s", rdpName, err))
	}
	return ok(fmt.Sprintf("RDP '%s' deleted", rdpName))
}

type rdpUpdate struct{}

func (rdpUpdate) Description() string {
	return "Update attributes of an existing RDP. Fails if the RDP does not exist."
}

func (rdpUpdate) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "restDeliveryPointName", Type: "string", Required: true, Description: "Name of the REST Delivery Point to update"},
		{Name: "clientProfileName", Type: "string", Description: "Client profile to associate with the RDP"},
		{Name: "enabled", Type: "boolean", Description: "Enable or disable the RDP"},
	}
}

func (rdpUpdate) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	rdpName := argStr(args, "restDeliveryPointName", "")
	if rdpName == "" {
		return failed("Missing required arg: restDeliveryPointName")
	}
	if err := semp.CheckNameLength("restDeliveryPointName", rdpName); err != "" {
		return failed(err)
	}

	path := "restDeliveryPoints/" + semp.Enc(rdpName)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking RDP: %s", err))
	}
	if !exists {
		return failed(fmt.Sprintf("RDP '%s' does not exist", rdpName))
	}

	payload := buildRdpPayload(args)
	delete(payload, "restDeliveryPointName")

	if len(payload) == 0 {
		return skipped("No fields to update")
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would update RDP '%s'", rdpName))
	}

	if _, err := c.Update(path, payload); err != nil {
		return failed(fmt.Sprintf("Failed to update RDP '%s': %s", rdpName, err))
	}
	return ok(fmt.Sprintf("RDP '%s' updated", rdpName))
}
