# SEMP Workflow Automation — Module Reference

All actions are **idempotent**: each checks current state before acting.
Result states: `changed` (action ran), `skipped` (already in desired state), `dryrun` (would change), `failed` (error).

## Contents

- [acl_profile](#acl-profile)
- [client_profile](#client-profile)
- [client_username](#client-username)
- [q_sub](#q-sub)
- [queue](#queue)
- [rdp](#rdp)
- [rdp_qb](#rdp-qb)
- [rdp_rc](#rdp-rc)

---

## acl_profile

### `acl_profile.add`

Create an ACL profile on the message VPN. Skipped if the profile already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `aclProfileName` | string | Yes | — | Name of the ACL profile |
| `clientConnectDefaultAction` | string | No | `disallow` | Default action for client connections (`allow`, `disallow`) |
| `publishTopicDefaultAction` | string | No | `disallow` | Default action for publish topic exceptions (`allow`, `disallow`) |
| `subscribeTopicDefaultAction` | string | No | `disallow` | Default action for subscribe topic exceptions (`allow`, `disallow`) |

### `acl_profile.delete`

Delete an ACL profile from the message VPN. Skipped if the profile does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `aclProfileName` | string | Yes | — | Name of the ACL profile to delete |

---

## client_profile

### `client_profile.add`

Create a client profile on the message VPN. Skipped if the profile already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clientProfileName` | string | Yes | — | Name of the client profile |
| `allowGuaranteedMsgSendEnabled` | boolean | No | — | Allow clients to send guaranteed messages |
| `allowGuaranteedMsgReceiveEnabled` | boolean | No | — | Allow clients to receive guaranteed messages |
| `allowTransactedSessionsEnabled` | boolean | No | — | Allow clients to use transacted sessions |
| `allowBridgeConnectionsEnabled` | boolean | No | — | Allow clients to use bridge connections |
| `maxConnectionCountPerClientUsername` | integer | No | — | Maximum connections per client username (0 = unlimited) |
| `maxEgressFlowCount` | integer | No | — | Maximum number of egress flows per client |
| `maxIngressFlowCount` | integer | No | — | Maximum number of ingress flows per client |
| `maxSubscriptionCount` | integer | No | — | Maximum number of subscriptions per client |

### `client_profile.delete`

Delete a client profile from the message VPN. Skipped if the profile does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clientProfileName` | string | Yes | — | Name of the client profile to delete |

---

## client_username

### `client_username.add`

Create a client username on the message VPN. Skipped if the username already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clientUsername` | string | Yes | — | The client username to create |
| `clientProfileName` | string | No | `default` | Client profile to assign to this username |
| `aclProfileName` | string | No | `default` | ACL profile to assign to this username |
| `password` | string | No | — | Password for the client username |
| `enabled` | boolean | No | `true` | Enable the client username after creation |

### `client_username.delete`

Delete a client username from the message VPN. Skipped if the username does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clientUsername` | string | Yes | — | The client username to delete |

---

## q_sub

### `q_sub.add`

Add a topic subscription to a queue. Skipped if the subscription already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `queueName` | string | Yes | — | Name of the queue to subscribe |
| `subscriptionTopic` | string | Yes | — | Topic string to subscribe to (wildcards supported, e.g. FCM/SAP/>) |

### `q_sub.delete`

Remove a topic subscription from a queue. Skipped if the subscription does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `queueName` | string | Yes | — | Name of the queue |
| `subscriptionTopic` | string | Yes | — | Topic string to unsubscribe |

---

## queue

### `queue.add`

Create a queue on the message VPN. Skipped if the queue already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `queueName` | string | Yes | — | Name of the queue to create |
| `accessType` | string | No | `exclusive` | Message delivery pattern (`exclusive`, `non-exclusive`) |
| `owner` | string | No | — | Client username that owns the queue |
| `permission` | string | No | `no-access` | Permission for non-owner clients (`no-access`, `read-only`, `consume`, `modify-topic`, `delete`) |
| `deadMsgQueue` | string | No | — | Name of the dead-message queue for undeliverable messages |
| `maxMsgSpoolUsage` | integer | No | — | Maximum spool usage in MB (0 = unlimited) |
| `maxTtl` | integer | No | — | Maximum time-to-live for messages in seconds. 0 disables TTL enforcement; any positive value enables it automatically. |
| `ingressEnabled` | boolean | No | `true` | Allow clients to send messages to the queue |
| `egressEnabled` | boolean | No | `true` | Allow clients to consume messages from the queue |
| `maxRedeliveryCount` | integer | No | — | Maximum redelivery attempts before routing to DMQ (0 = unlimited) |
| `rejectMsgToSenderOnDiscardBehavior` | string | No | — | Action when a message is discarded (`never`, `when-queue-enabled`, `always`) |

### `queue.delete`

Delete a queue from the message VPN. Skipped if the queue does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `queueName` | string | Yes | — | Name of the queue to delete |

### `queue.update`

Update attributes of an existing queue. Fails if the queue does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `queueName` | string | Yes | — | Name of the queue to update |
| `accessType` | string | No | — | Message delivery pattern (`exclusive`, `non-exclusive`) |
| `owner` | string | No | — | Client username that owns the queue |
| `permission` | string | No | — | Permission for non-owner clients (`no-access`, `read-only`, `consume`, `modify-topic`, `delete`) |
| `deadMsgQueue` | string | No | — | Name of the dead-message queue for undeliverable messages |
| `maxMsgSpoolUsage` | integer | No | — | Maximum spool usage in MB (0 = unlimited) |
| `maxTtl` | integer | No | — | Maximum time-to-live for messages in seconds. 0 disables TTL enforcement; any positive value enables it automatically. |
| `ingressEnabled` | boolean | No | — | Allow clients to send messages to the queue |
| `egressEnabled` | boolean | No | — | Allow clients to consume messages from the queue |
| `maxRedeliveryCount` | integer | No | — | Maximum redelivery attempts before routing to DMQ (0 = unlimited) |
| `rejectMsgToSenderOnDiscardBehavior` | string | No | — | Action when a message is discarded (`never`, `when-queue-enabled`, `always`) |

---

## rdp

### `rdp.add`

Create a REST Delivery Point (RDP). Skipped if the RDP already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `restDeliveryPointName` | string | Yes | — | Name of the REST Delivery Point |
| `clientProfileName` | string | No | `default` | Client profile to associate with the RDP |
| `enabled` | boolean | No | `true` | Enable the RDP after creation |

### `rdp.delete`

Delete a REST Delivery Point. Skipped if the RDP does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `restDeliveryPointName` | string | Yes | — | Name of the REST Delivery Point to delete |

### `rdp.update`

Update attributes of an existing RDP. Fails if the RDP does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `restDeliveryPointName` | string | Yes | — | Name of the REST Delivery Point to update |
| `clientProfileName` | string | No | — | Client profile to associate with the RDP |
| `enabled` | boolean | No | — | Enable or disable the RDP |

---

## rdp_qb

### `rdp_qb.add`

Bind a queue to an RDP for message delivery. Skipped if the binding already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `restDeliveryPointName` | string | Yes | — | Name of the REST Delivery Point |
| `queueBindingName` | string | Yes | — | Name of the queue to bind |
| `postRequestTarget` | string | No | — | HTTP request target path appended to the REST consumer URL |
| `gatewayReplaceTargetAuthorityEnabled` | boolean | No | — | Replace the authority in forwarded HTTP requests with the remote host |

### `rdp_qb.delete`

Remove a queue binding from an RDP. Skipped if the binding does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `restDeliveryPointName` | string | Yes | — | Name of the REST Delivery Point |
| `queueBindingName` | string | Yes | — | Name of the bound queue to remove |

---

## rdp_rc

### `rdp_rc.add`

Add a REST consumer to an RDP. Skipped if the consumer already exists.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `restConsumerName` | string | Yes | — | Name of the REST consumer |
| `remoteHost` | string | No | — | Hostname or IP address of the remote HTTP server |
| `remotePort` | integer | No | — | TCP port of the remote HTTP server (default: 8080) |
| `tlsEnabled` | boolean | No | — | Use TLS for the connection (default: false) |
| `enabled` | boolean | No | — | Enable the REST consumer after creation (default: false) |
| `httpMethod` | string | No | `post` | HTTP method for message delivery (`post`, `put`) |
| `outgoingConnectionCount` | integer | No | — | Number of simultaneous outgoing HTTP connections (default: 3) |
| `authenticationScheme` | string | No | `none` | Authentication scheme (`none`, `http-basic`, `client-certificate`, `http-header`, `oauth-client`, `oauth-jwt`, `transparent`, `aws`) |
| `authenticationHttpBasicUsername` | string | No | — | Username for HTTP Basic authentication (requires authenticationHttpBasicPassword) |
| `authenticationHttpBasicPassword` | string | No | — | Password for HTTP Basic authentication (requires authenticationHttpBasicUsername) |

### `rdp_rc.delete`

Remove a REST consumer from an RDP. Skipped if the consumer does not exist.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `restDeliveryPointName` | string | Yes | — | Name of the parent REST Delivery Point |
| `restConsumerName` | string | Yes | — | Name of the REST consumer to delete |

---
