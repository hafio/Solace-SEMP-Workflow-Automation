package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("client_profile.add", clientProfileAdd{})
	register("client_profile.delete", clientProfileDelete{})
	register("client_profile.update", clientProfileUpdate{})
}

var clientProfileBoolFields = []string{
	"allowGuaranteedMsgSendEnabled",
	"allowGuaranteedMsgReceiveEnabled",
	"allowTransactedSessionsEnabled",
	"allowBridgeConnectionsEnabled",
	"compressionEnabled",
}

var clientProfileIntFields = []string{
	"maxConnectionCountPerClientUsername",
	"maxEgressFlowCount",
	"maxIngressFlowCount",
	"maxSubscriptionCount",
}

func buildProfilePayload(args map[string]any) (map[string]any, error) {
	payload := semp.CleanPayload(args)
	coerceBoolFields(payload, clientProfileBoolFields...)
	if err := coerceIntFields(payload, clientProfileIntFields...); err != nil {
		return nil, err
	}
	return payload, nil
}

func clientProfileParams(nameDesc string) []ParamSpec {
	return []ParamSpec{
		{Name: "clientProfileName", Type: "string", Required: true, Description: nameDesc},
		{Name: "allowGuaranteedMsgSendEnabled", Type: "boolean", Description: "Allow clients to send guaranteed messages"},
		{Name: "allowGuaranteedMsgReceiveEnabled", Type: "boolean", Description: "Allow clients to receive guaranteed messages"},
		{Name: "allowTransactedSessionsEnabled", Type: "boolean", Description: "Allow clients to use transacted sessions"},
		{Name: "allowBridgeConnectionsEnabled", Type: "boolean", Description: "Allow clients to use bridge connections"},
		{Name: "compressionEnabled", Type: "boolean", Description: "Enable message compression for clients using this profile"},
		{Name: "maxConnectionCountPerClientUsername", Type: "integer", Description: "Maximum connections per client username (0 = unlimited)"},
		{Name: "maxEgressFlowCount", Type: "integer", Description: "Maximum number of egress flows per client"},
		{Name: "maxIngressFlowCount", Type: "integer", Description: "Maximum number of ingress flows per client"},
		{Name: "maxSubscriptionCount", Type: "integer", Description: "Maximum number of subscriptions per client"},
	}
}

type clientProfileAdd struct{}

func (clientProfileAdd) Description() string {
	return "Create a client profile on the message VPN. Skipped if the profile already exists."
}

func (clientProfileAdd) Params() []ParamSpec {
	return clientProfileParams("Name of the client profile")
}

func (clientProfileAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	name := argStr(args, "clientProfileName", "")
	if name == "" {
		return failed("Missing required arg: clientProfileName")
	}
	if err := semp.CheckNameLength("clientProfileName", name); err != "" {
		return failed(err)
	}

	path := "clientProfiles/" + semp.Enc(name)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking client profile: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("Client profile '%s' already exists", name))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would create client profile '%s'", name))
	}

	payload, err := buildProfilePayload(args)
	if err != nil {
		return failed(err.Error())
	}
	if _, err := c.Create("clientProfiles", payload); err != nil {
		return failed(fmt.Sprintf("Failed to create client profile '%s': %s", name, err))
	}
	return ok(fmt.Sprintf("Client profile '%s' created", name))
}

type clientProfileDelete struct{}

func (clientProfileDelete) Description() string {
	return "Delete a client profile from the message VPN. Skipped if the profile does not exist."
}

func (clientProfileDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "clientProfileName", Type: "string", Required: true, Description: "Name of the client profile to delete"},
	}
}

func (clientProfileDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	name := argStr(args, "clientProfileName", "")
	if name == "" {
		return failed("Missing required arg: clientProfileName")
	}
	if err := semp.CheckNameLength("clientProfileName", name); err != "" {
		return failed(err)
	}

	path := "clientProfiles/" + semp.Enc(name)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking client profile: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("Client profile '%s' does not exist", name))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would delete client profile '%s'", name))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to delete client profile '%s': %s", name, err))
	}
	return ok(fmt.Sprintf("Client profile '%s' deleted", name))
}

type clientProfileUpdate struct{}

func (clientProfileUpdate) Description() string {
	return "Update attributes of an existing client profile. Fails if the profile does not exist."
}

func (clientProfileUpdate) Params() []ParamSpec {
	return clientProfileParams("Name of the client profile to update")
}

func (clientProfileUpdate) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	name := argStr(args, "clientProfileName", "")
	if name == "" {
		return failed("Missing required arg: clientProfileName")
	}
	if err := semp.CheckNameLength("clientProfileName", name); err != "" {
		return failed(err)
	}

	path := "clientProfiles/" + semp.Enc(name)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking client profile: %s", err))
	}
	if !exists {
		return failed(fmt.Sprintf("Client profile '%s' does not exist", name))
	}

	payload, err := buildProfilePayload(args)
	if err != nil {
		return failed(err.Error())
	}
	delete(payload, "clientProfileName")

	if len(payload) == 0 {
		return skipped("No fields to update")
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would update client profile '%s'", name))
	}

	if _, err := c.Update(path, payload); err != nil {
		return failed(fmt.Sprintf("Failed to update client profile '%s': %s", name, err))
	}
	return ok(fmt.Sprintf("Client profile '%s' updated", name))
}
