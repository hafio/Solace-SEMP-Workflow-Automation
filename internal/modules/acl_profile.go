package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("acl_profile.add", aclProfileAdd{})
	register("acl_profile.delete", aclProfileDelete{})
}

type aclProfileAdd struct{}

func (aclProfileAdd) Description() string {
	return "Create an ACL profile on the message VPN. Skipped if the profile already exists."
}

func (aclProfileAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "aclProfileName", Type: "string", Required: true, Description: "Name of the ACL profile"},
		{Name: "clientConnectDefaultAction", Type: "string", Description: "Default action for client connections", Default: "disallow", Enum: []string{"allow", "disallow"}},
		{Name: "publishTopicDefaultAction", Type: "string", Description: "Default action for publish topic exceptions", Default: "disallow", Enum: []string{"allow", "disallow"}},
		{Name: "subscribeTopicDefaultAction", Type: "string", Description: "Default action for subscribe topic exceptions", Default: "disallow", Enum: []string{"allow", "disallow"}},
	}
}

func (aclProfileAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	name := argStr(args, "aclProfileName", "")
	if name == "" {
		return failed("Missing required arg: aclProfileName")
	}
	if err := semp.CheckNameLength("aclProfileName", name); err != "" {
		return failed(err)
	}

	path := "aclProfiles/" + semp.Enc(name)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking ACL profile: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("ACL profile '%s' already exists", name))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would create ACL profile '%s'", name))
	}

	if _, err := c.Create("aclProfiles", semp.CleanPayload(args)); err != nil {
		return failed(fmt.Sprintf("Failed to create ACL profile '%s': %s", name, err))
	}
	return ok(fmt.Sprintf("ACL profile '%s' created", name))
}

type aclProfileDelete struct{}

func (aclProfileDelete) Description() string {
	return "Delete an ACL profile from the message VPN. Skipped if the profile does not exist."
}

func (aclProfileDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "aclProfileName", Type: "string", Required: true, Description: "Name of the ACL profile to delete"},
	}
}

func (aclProfileDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	name := argStr(args, "aclProfileName", "")
	if name == "" {
		return failed("Missing required arg: aclProfileName")
	}
	if err := semp.CheckNameLength("aclProfileName", name); err != "" {
		return failed(err)
	}

	path := "aclProfiles/" + semp.Enc(name)

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking ACL profile: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("ACL profile '%s' does not exist", name))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would delete ACL profile '%s'", name))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to delete ACL profile '%s': %s", name, err))
	}
	return ok(fmt.Sprintf("ACL profile '%s' deleted", name))
}
