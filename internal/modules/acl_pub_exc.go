package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("acl_publish_exception.add", aclPublishExceptionAdd{})
	register("acl_publish_exception.delete", aclPublishExceptionDelete{})
}

type aclPublishExceptionAdd struct{}

func (aclPublishExceptionAdd) Description() string {
	return "Add a publish topic exception to an ACL profile. Skipped if the exception already exists."
}

func (aclPublishExceptionAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "aclProfileName", Type: "string", Required: true, Description: "Name of the ACL profile"},
		{Name: "publishTopicException", Type: "string", Required: true, Description: "The topic for the exception (may include wildcards)"},
		{Name: "publishTopicExceptionSyntax", Type: "string", Description: "Syntax of the topic", Default: "smf", Enum: []string{"smf", "mqtt"}},
	}
}

func (aclPublishExceptionAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	profile := argStr(args, "aclProfileName", "")
	topic := argStr(args, "publishTopicException", "")
	syntax := argStr(args, "publishTopicExceptionSyntax", "smf")

	if profile == "" {
		return failed("Missing required arg: aclProfileName")
	}
	if topic == "" {
		return failed("Missing required arg: publishTopicException")
	}

	path := fmt.Sprintf("aclProfiles/%s/publishTopicExceptions/%s,%s", semp.Enc(profile), semp.Enc(syntax), semp.Enc(topic))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking publish topic exception: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("Publish topic exception '%s' already exists on ACL profile '%s'", topic, profile))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would add publish topic exception '%s' to ACL profile '%s'", topic, profile))
	}

	payload := map[string]any{
		"aclProfileName":              profile,
		"publishTopicException":       topic,
		"publishTopicExceptionSyntax": syntax,
	}
	if _, err := c.Create(fmt.Sprintf("aclProfiles/%s/publishTopicExceptions", semp.Enc(profile)), payload); err != nil {
		return failed(fmt.Sprintf("Failed to add publish topic exception '%s' to ACL profile '%s': %s", topic, profile, err))
	}
	return ok(fmt.Sprintf("Publish topic exception '%s' added to ACL profile '%s'", topic, profile))
}

type aclPublishExceptionDelete struct{}

func (aclPublishExceptionDelete) Description() string {
	return "Remove a publish topic exception from an ACL profile. Skipped if the exception does not exist."
}

func (aclPublishExceptionDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "aclProfileName", Type: "string", Required: true, Description: "Name of the ACL profile"},
		{Name: "publishTopicException", Type: "string", Required: true, Description: "The topic exception to remove"},
		{Name: "publishTopicExceptionSyntax", Type: "string", Description: "Syntax of the topic", Default: "smf", Enum: []string{"smf", "mqtt"}},
	}
}

func (aclPublishExceptionDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	profile := argStr(args, "aclProfileName", "")
	topic := argStr(args, "publishTopicException", "")
	syntax := argStr(args, "publishTopicExceptionSyntax", "smf")

	if profile == "" {
		return failed("Missing required arg: aclProfileName")
	}
	if topic == "" {
		return failed("Missing required arg: publishTopicException")
	}

	path := fmt.Sprintf("aclProfiles/%s/publishTopicExceptions/%s,%s", semp.Enc(profile), semp.Enc(syntax), semp.Enc(topic))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking publish topic exception: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("Publish topic exception '%s' does not exist on ACL profile '%s'", topic, profile))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would remove publish topic exception '%s' from ACL profile '%s'", topic, profile))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to remove publish topic exception '%s' from ACL profile '%s': %s", topic, profile, err))
	}
	return ok(fmt.Sprintf("Publish topic exception '%s' removed from ACL profile '%s'", topic, profile))
}
