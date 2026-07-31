package modules

import (
	"fmt"

	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

func init() {
	register("rdp_rc.add", rdpRestConsumerAdd{})
	register("rdp_rc.delete", rdpRestConsumerDelete{})
}

// buildConsumerPayload cleans args, drops the path-only restDeliveryPointName,
// and coerces the consumer's bool and int fields.
func buildConsumerPayload(args map[string]any) (map[string]any, error) {
	payload := semp.CleanPayload(args)
	delete(payload, "restDeliveryPointName") // path param, not a body field
	coerceBoolFields(payload, "tlsEnabled", "enabled")
	if err := coerceIntFields(payload, "remotePort", "outgoingConnectionCount"); err != nil {
		return nil, err
	}
	return payload, nil
}

type rdpRestConsumerAdd struct{}

func (rdpRestConsumerAdd) Description() string {
	return "Add a REST consumer to an RDP. Skipped if the consumer already exists."
}

func (rdpRestConsumerAdd) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "restConsumerName", Type: "string", Required: true, Description: "Name of the REST consumer"},
		{Name: "remoteHost", Type: "string", Description: "Hostname or IP address of the remote HTTP server"},
		{Name: "remotePort", Type: "integer", Description: "TCP port of the remote HTTP server (default: 8080)"},
		{Name: "tlsEnabled", Type: "boolean", Description: "Use TLS for the connection (default: false)"},
		{Name: "enabled", Type: "boolean", Description: "Enable the REST consumer after creation (default: false)"},
		{Name: "httpMethod", Type: "string", Description: "HTTP method for message delivery", Default: "post", Enum: []string{"post", "put"}},
		{Name: "outgoingConnectionCount", Type: "integer", Description: "Number of simultaneous outgoing HTTP connections (default: 3)"},
		{Name: "authenticationScheme", Type: "string", Description: "Authentication scheme", Default: "none", Enum: []string{"none", "http-basic", "client-certificate", "http-header", "oauth-client", "oauth-jwt", "transparent", "aws"}},
		{Name: "authenticationHttpBasicUsername", Type: "string", Description: "Username for HTTP Basic authentication (requires authenticationHttpBasicPassword)"},
		{Name: "authenticationHttpBasicPassword", Type: "string", Description: "Password for HTTP Basic authentication (requires authenticationHttpBasicUsername)"},
	}
}

func (rdpRestConsumerAdd) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	rdpName := argStr(args, "restDeliveryPointName", "")
	consumerName := argStr(args, "restConsumerName", "")
	if rdpName == "" || consumerName == "" {
		return failed("Missing required args: restDeliveryPointName, restConsumerName")
	}
	for _, f := range []struct{ field, value string }{
		{"restDeliveryPointName", rdpName},
		{"restConsumerName", consumerName},
	} {
		if err := semp.CheckNameLength(f.field, f.value); err != "" {
			return failed(err)
		}
	}

	path := fmt.Sprintf("restDeliveryPoints/%s/restConsumers/%s", semp.Enc(rdpName), semp.Enc(consumerName))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking REST consumer: %s", err))
	}
	if exists {
		return skipped(fmt.Sprintf("REST consumer '%s' already exists on RDP '%s'", consumerName, rdpName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would create REST consumer '%s' on RDP '%s'", consumerName, rdpName))
	}

	payload, err := buildConsumerPayload(args)
	if err != nil {
		return failed(err.Error())
	}
	if _, err := c.Create(fmt.Sprintf("restDeliveryPoints/%s/restConsumers", semp.Enc(rdpName)), payload); err != nil {
		return failed(fmt.Sprintf("Failed to create REST consumer: %s", err))
	}
	return ok(fmt.Sprintf("REST consumer '%s' created on RDP '%s'", consumerName, rdpName))
}

type rdpRestConsumerDelete struct{}

func (rdpRestConsumerDelete) Description() string {
	return "Remove a REST consumer from an RDP. Skipped if the consumer does not exist."
}

func (rdpRestConsumerDelete) Params() []ParamSpec {
	return []ParamSpec{
		{Name: "restDeliveryPointName", Type: "string", Required: true, Description: "Name of the parent REST Delivery Point"},
		{Name: "restConsumerName", Type: "string", Required: true, Description: "Name of the REST consumer to delete"},
	}
}

func (rdpRestConsumerDelete) Execute(c Client, args map[string]any, dryRun bool) models.ActionResult {
	rdpName := argStr(args, "restDeliveryPointName", "")
	consumerName := argStr(args, "restConsumerName", "")
	if rdpName == "" || consumerName == "" {
		return failed("Missing required args: restDeliveryPointName, restConsumerName")
	}
	for _, f := range []struct{ field, value string }{
		{"restDeliveryPointName", rdpName},
		{"restConsumerName", consumerName},
	} {
		if err := semp.CheckNameLength(f.field, f.value); err != "" {
			return failed(err)
		}
	}

	path := fmt.Sprintf("restDeliveryPoints/%s/restConsumers/%s", semp.Enc(rdpName), semp.Enc(consumerName))

	exists, _, err := c.Exists(path)
	if err != nil {
		return failed(fmt.Sprintf("Error checking REST consumer: %s", err))
	}
	if !exists {
		return skipped(fmt.Sprintf("REST consumer '%s' does not exist on RDP '%s'", consumerName, rdpName))
	}
	if dryRun {
		return dryrun(fmt.Sprintf("Would delete REST consumer '%s' from RDP '%s'", consumerName, rdpName))
	}

	if err := c.Delete(path); err != nil {
		return failed(fmt.Sprintf("Failed to delete REST consumer: %s", err))
	}
	return ok(fmt.Sprintf("REST consumer '%s' deleted from RDP '%s'", consumerName, rdpName))
}
