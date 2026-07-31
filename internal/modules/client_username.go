package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("client_username.add", clientUsernameAdd{})
	register("client_username.delete", clientUsernameDelete{})
	register("client_username.update", clientUsernameUpdate{})
}

// buildUsernamePayload cleans args and coerces the enabled flag.
func buildUsernamePayload(args map[string]any) map[string]any {
	payload := semp.CleanPayload(args)
	coerceBoolFields(payload, "enabled")
	return payload
}

type clientUsernameAdd struct{}

func (clientUsernameAdd) Description() string {
	return "Create a client username on the message VPN. Skipped if the username already exists."
}

func (clientUsernameAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "clientUsername", Type: "string", Required: true, Description: "The client username to create"},
		{Name: "clientProfileName", Type: "string", Description: "Client profile to assign to this username", Default: "default"},
		{Name: "aclProfileName", Type: "string", Description: "ACL profile to assign to this username", Default: "default"},
		{Name: "password", Type: "string", Description: "Password for the client username"},
		{Name: "enabled", Type: "boolean", Description: "Enable the client username after creation", Default: "true"},
	}
}

func (clientUsernameAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	username := argStr(args, "clientUsername", "")
	if username == "" {
		return failed("Missing required arg: clientUsername")
	}
	if err := semp.CheckNameLength("clientUsername", username); err != "" {
		return failed(err)
	}

	path := "clientUsernames/" + semp.Enc(username)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking client username: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("Client username '%s' already exists", username))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would create client username '%s'", username))
	}

	if _, err := c.Create("clientUsernames", buildUsernamePayload(args)); err != nil {
		return failed(fmt.Sprintf("Failed to create client username '%s': %s", username, err))
	}
	return ok(fmt.Sprintf("Client username '%s' created", username))
}

type clientUsernameDelete struct{}

func (clientUsernameDelete) Description() string {
	return "Delete a client username from the message VPN. Skipped if the username does not exist."
}

func (clientUsernameDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "clientUsername", Type: "string", Required: true, Description: "The client username to delete"},
	}
}

func (clientUsernameDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	username := argStr(args, "clientUsername", "")
	if username == "" {
		return failed("Missing required arg: clientUsername")
	}
	if err := semp.CheckNameLength("clientUsername", username); err != "" {
		return failed(err)
	}

	path := "clientUsernames/" + semp.Enc(username)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking client username: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("Client username '%s' does not exist", username))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would delete client username '%s'", username))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to delete client username '%s': %s", username, err))
	}
	return ok(fmt.Sprintf("Client username '%s' deleted", username))
}

type clientUsernameUpdate struct{}

func (clientUsernameUpdate) Description() string {
	return "Update attributes of an existing client username. Fails if the username does not exist."
}

func (clientUsernameUpdate) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "clientUsername", Type: "string", Required: true, Description: "The client username to update"},
		{Name: "clientProfileName", Type: "string", Description: "Client profile to assign"},
		{Name: "aclProfileName", Type: "string", Description: "ACL profile to assign"},
		{Name: "password", Type: "string", Description: "Password for the client username"},
		{Name: "enabled", Type: "boolean", Description: "Enable or disable the client username"},
	}
}

func (clientUsernameUpdate) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	username := argStr(args, "clientUsername", "")
	if username == "" {
		return failed("Missing required arg: clientUsername")
	}
	if err := semp.CheckNameLength("clientUsername", username); err != "" {
		return failed(err)
	}

	path := "clientUsernames/" + semp.Enc(username)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking client username: %s", err))
	}
	if !exists {
		return failed(fmt.Sprintf("Client username '%s' does not exist", username))
	}

	payload := buildUsernamePayload(args)
	delete(payload, "clientUsername")

	if len(payload) == 0 {
		return skipped("No fields to update")
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would update client username '%s'", username))
	}

	if _, err := c.Update(path, payload); err != nil {
		return failed(fmt.Sprintf("Failed to update client username '%s': %s", username, err))
	}
	return ok(fmt.Sprintf("Client username '%s' updated", username))
}
