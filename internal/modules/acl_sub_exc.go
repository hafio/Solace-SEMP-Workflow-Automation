package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("acl_subscribe_exception.add", aclSubscribeExceptionAdd{})
	register("acl_subscribe_exception.delete", aclSubscribeExceptionDelete{})
}

type aclSubscribeExceptionAdd struct{}

func (aclSubscribeExceptionAdd) Description() string {
	return "Add a subscribe topic exception to an ACL profile. Skipped if the exception already exists."
}

func (aclSubscribeExceptionAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "aclProfileName", Type: "string", Required: true, Description: "Name of the ACL profile"},
		{Name: "subscribeTopicException", Type: "string", Required: true, Description: "The topic for the exception (may include wildcards)"},
		{Name: "subscribeTopicExceptionSyntax", Type: "string", Description: "Syntax of the topic", Default: "smf", Enum: []string{"smf", "mqtt"}},
	}
}

func (aclSubscribeExceptionAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	profile := argStr(args, "aclProfileName", "")
	topic := argStr(args, "subscribeTopicException", "")
	syntax := argStr(args, "subscribeTopicExceptionSyntax", "smf")

	if profile == "" {
		return failed("Missing required arg: aclProfileName")
	}
	if topic == "" {
		return failed("Missing required arg: subscribeTopicException")
	}

	path := fmt.Sprintf("aclProfiles/%s/subscribeTopicExceptions/%s,%s", semp.Enc(profile), semp.Enc(syntax), semp.Enc(topic))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking subscribe topic exception: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("Subscribe topic exception '%s' already exists on ACL profile '%s'", topic, profile))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would add subscribe topic exception '%s' to ACL profile '%s'", topic, profile))
	}

	payload := map[string]any{
		"aclProfileName":                profile,
		"subscribeTopicException":       topic,
		"subscribeTopicExceptionSyntax": syntax,
	}
	if _, err := c.Create(fmt.Sprintf("aclProfiles/%s/subscribeTopicExceptions", semp.Enc(profile)), payload); err != nil {
		return failed(fmt.Sprintf("Failed to add subscribe topic exception '%s' to ACL profile '%s': %s", topic, profile, err))
	}
	return ok(fmt.Sprintf("Subscribe topic exception '%s' added to ACL profile '%s'", topic, profile))
}

type aclSubscribeExceptionDelete struct{}

func (aclSubscribeExceptionDelete) Description() string {
	return "Remove a subscribe topic exception from an ACL profile. Skipped if the exception does not exist."
}

func (aclSubscribeExceptionDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "aclProfileName", Type: "string", Required: true, Description: "Name of the ACL profile"},
		{Name: "subscribeTopicException", Type: "string", Required: true, Description: "The topic exception to remove"},
		{Name: "subscribeTopicExceptionSyntax", Type: "string", Description: "Syntax of the topic", Default: "smf", Enum: []string{"smf", "mqtt"}},
	}
}

func (aclSubscribeExceptionDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	profile := argStr(args, "aclProfileName", "")
	topic := argStr(args, "subscribeTopicException", "")
	syntax := argStr(args, "subscribeTopicExceptionSyntax", "smf")

	if profile == "" {
		return failed("Missing required arg: aclProfileName")
	}
	if topic == "" {
		return failed("Missing required arg: subscribeTopicException")
	}

	path := fmt.Sprintf("aclProfiles/%s/subscribeTopicExceptions/%s,%s", semp.Enc(profile), semp.Enc(syntax), semp.Enc(topic))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking subscribe topic exception: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("Subscribe topic exception '%s' does not exist on ACL profile '%s'", topic, profile))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would remove subscribe topic exception '%s' from ACL profile '%s'", topic, profile))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to remove subscribe topic exception '%s' from ACL profile '%s': %s", topic, profile, err))
	}
	return ok(fmt.Sprintf("Subscribe topic exception '%s' removed from ACL profile '%s'", topic, profile))
}
