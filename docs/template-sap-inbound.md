# Template: `sap-inbound`

**File:** [examples/templates/sap-inbound.yaml](../examples/templates/sap-inbound.yaml)

**Message direction:** SAP -> Solace -> backend REST service (broker receives messages from SAP and delivers them to a backend HTTP endpoint via an RDP).

**Use case:** Provision the broker resources needed to receive messages on a topic and forward them to a backend REST service — including access control, queue set, and the full RDP delivery pipeline (REST consumer + queue binding).

---

## Template Variants

| Template reference | Purpose | Key differences |
|---|---|---|
| `sap-inbound.new-seq` | Create the full inbound stack with **sequential** delivery | `service_queue_max_redelivery: 0` (retry forever) |
| `sap-inbound.new-non-seq` | Create the full inbound stack with **concurrent/retry** delivery | `service_queue_max_redelivery: 5` (route to DMQ after 5 retries) |
| `sap-inbound.delete` | Tear down all inbound resources for a topic | Removes RDP first (cascades consumers/bindings), then queues, then access control |

`new-seq` and `new-non-seq` share the same action list via a YAML anchor — the only difference is the `service_queue_max_redelivery` default.

---

## Inputs

### Required

| Input | Description | Example |
|---|---|---|
| `domain` | Business domain identifier | `HQ` |
| `system` | Source system name | `SAP` |
| `system_topic` | Business topic identifier | `GCM.FIANA.LOT-TURNKEY-COST` |
| `non_service_queue_owner` | Client username that owns the mirror queue and DMQ | `ADMIN-USER` |
| `aem_client_username` | Client username to create for this topic | `SAP-AIF-CLIENT` |

### Optional (with defaults)

**Access control:**

| Input | Default | Notes |
|---|---|---|
| `client_profile_name` | `"cp-it-user"` | Shared client profile used by all SAP workflows |
| `acl_profile_name` | `"acl-it-user-{{ inputs.aem_client_username }}"` | Per-user ACL profile |

**Topics and naming:**

| Input | Default |
|---|---|
| `service_queue_name` | `"FROM-{{ domain }}-{{ system }}-{{ system_topic }}"` |
| `service_queue_subscription` | `"{{ domain }}/{{ system }}/{{ system_topic }}"` |
| `mirror_queue_name` | `"MIRROR/FROM-{{ domain }}-{{ system }}-{{ system_topic }}"` |
| `mirror_queue_subscription` | `"{{ domain }}/{{ system }}/{{ system_topic }}"` |
| `dmq_name` | `"DMQ/FROM-{{ domain }}-{{ system }}-{{ system_topic }}"` |

**Service queue behaviour:**

| Input | Default | Notes |
|---|---|---|
| `service_queue_owner` | `"#rdp/RDP/FROM-..."` | Owned by the RDP so it can consume |
| `service_queue_dmq` | `"DMQ/FROM-..."` | Dead-message queue target |
| `service_queue_permission` | `"no-access"` | |
| `service_queue_access` | `exclusive` | |
| `service_queue_reject_msg_sender` | `"always"` | |
| `service_queue_ttl` | `0` | 0 = no TTL |
| `service_queue_max_redelivery` | `0` (seq) / `5` (non-seq) | -1 = disabled, 0 = forever |
| `service_queue_max_spool` | `5000` | MB |
| `service_queue_enabled` | `false` | |

**Mirror queue behaviour:**

| Input | Default |
|---|---|
| `mirror_queue_owner` | `"{{ non_service_queue_owner }}"` |
| `mirror_queue_dmq` | `"#DEAD_MSG_QUEUE"` |
| `mirror_queue_permission` | `"no-access"` |
| `mirror_queue_access` | `exclusive` |
| `mirror_queue_reject_msg_sender` | `"when-queue-enabled"` |
| `mirror_queue_ttl` | `1296000` (15 days) |
| `mirror_queue_max_spool` | `5000` |
| `mirror_queue_enabled` | `false` |

**DMQ behaviour:**

| Input | Default |
|---|---|
| `dmq_owner` | `"{{ non_service_queue_owner }}"` |
| `dmq_dmq` | `"#DEAD_MSG_QUEUE"` |
| `dmq_permission` | `"no-access"` |
| `dmq_access` | `exclusive` |
| `dmq_ttl` | `7776000` (90 days) |
| `dmq_max_spool` | `5000` |
| `dmq_enabled` | `false` |

**REST Delivery Point (RDP):**

| Input | Default |
|---|---|
| `rdp_name` | `"RDP/FROM-{{ domain }}-{{ system }}-{{ system_topic }}"` |
| `rdp_client_profile` | `"cp-vip"` |
| `rdp_enabled` | `true` |

**REST Consumer (the HTTP endpoint):**

| Input | Default | Notes |
|---|---|---|
| `rc_name` | `"RC-SAP-REST"` | |
| `rc_remote_host` | `"sapslbs4uat.tsmc.com"` | Override per environment |
| `rc_remote_port` | `80` | |
| `rc_tls_enabled` | `false` | Set `true` for HTTPS |
| `rc_http_method` | `"post"` | |
| `rc_outgoing_connection_count` | `1` | |
| `rc_auth_scheme` | `"http-basic"` | |
| `rc_auth_username` | `"**************"` | Override |
| `rc_auth_password` | `"**************"` | Override |
| `rc_enabled` | `true` | |

**Queue Binding (connects queue to RDP):**

| Input | Default |
|---|---|
| `qb_post_request_target` | `"/sap/bc/aem2aif"` |
| `qb_gateway_replace_target_authority` | `false` |

---

## Action Sequence

### `new-seq` / `new-non-seq` (14 actions)

| # | Action name | Module | Purpose |
|---|---|---|---|
| 1 | Create Client Profile | `client_profile.add` | Create `cp-it-user`. Skipped if exists. |
| 2 | Update Client Profile | `client_profile.update` | Enable guaranteed send + receive. Always runs. |
| 3 | Create ACL Profile | `acl_profile.add` | Create `acl-it-user-{aem_client_username}` (allow connect, disallow pub/sub). Skipped if exists. |
| 4 | Create Client Username | `client_username.add` | Create `{aem_client_username}` linked to both profiles. Skipped if exists. |
| 5 | Update Client Username Association | `client_username.update` | Ensures profile links are correct even if the username pre-existed with wrong associations. |
| 6 | Add ACL Publish Topic Exception | `acl_publish_exception.add` | Add publish exception for the subscription topic. |
| 7 | Create Service Queue | `queue.add` | Create `FROM-{domain}-{system}-{system_topic}`, owned by the RDP. |
| 8 | Create Mirror Queue | `queue.add` | Create `MIRROR/FROM-{domain}-{system}-{system_topic}`. |
| 9 | Create DMQ | `queue.add` | Create `DMQ/FROM-{domain}-{system}-{system_topic}`. |
| 10 | Add Service Queue Subscription | `q_sub.add` | Subscribe service queue to `{domain}/{system}/{system_topic}`. |
| 11 | Add Mirror Queue Subscription | `q_sub.add` | Subscribe mirror queue to the same topic. |
| 12 | Create REST Delivery Point | `rdp.add` | Create the RDP. |
| 13 | Create REST Consumer | `rdp_rc.add` | Create the REST consumer pointing at the backend HTTP endpoint. |
| 14 | Create Queue Binding | `rdp_qb.add` | Bind the service queue to the RDP with the POST target path. |

**End-to-end pipeline:** Message arrives on topic -> service queue (via subscription) -> RDP picks up via queue binding -> REST consumer delivers as HTTP POST to the backend.

All actions are idempotent. Re-running produces `SKIPPED` for everything (except the two update actions, which always run).

### `delete` (8 actions)

| # | Action name | Module | Purpose |
|---|---|---|---|
| 1 | Delete REST Delivery Point | `rdp.delete` | Removes RDP (cascades the REST consumer and queue binding). |
| 2 | Delete Service Queue | `queue.delete` | Remove service queue. |
| 3 | Delete Mirror Queue | `queue.delete` | Remove mirror queue. |
| 4 | Delete DMQ | `queue.delete` | Remove dead-message queue. |
| 5 | Remove ACL Publish Topic Exception | `acl_publish_exception.delete` | Remove publish exception. |
| 6 | Delete Client Username | `client_username.delete` | Remove the per-topic client username. |
| 7 | Delete ACL Profile | `acl_profile.delete` | Remove the per-user ACL profile. |

**Deletion order matters:** RDP first (because the queue binding references the queue), then queues, then access control (because the username references the ACL profile).

> **Note:** The shared `cp-it-user` client profile is **not** deleted — it's reused by all SAP workflows.

---

## Example Workflow Entry

```yaml
workflows:
  - template: "sap-inbound.new-seq"
    inputs:
      domain: "HQ"
      system: "SAP"
      system_topic: "GCM.FIANA.LOT-TURNKEY-COST"
      non_service_queue_owner: "ADMIN-USER"
      aem_client_username: "SAP-AIF-CLIENT"
      rc_remote_host: "sap-backend.internal"
      rc_remote_port: 443
      rc_tls_enabled: true
      rc_auth_username: "aem-bot"
      rc_auth_password: "s3cret"
```

With the defaults above, this creates:

| Resource | Name |
|---|---|
| Client profile | `cp-it-user` |
| ACL profile | `acl-it-user-SAP-AIF-CLIENT` |
| Client username | `SAP-AIF-CLIENT` |
| Publish topic exception | `HQ/SAP/GCM.FIANA.LOT-TURNKEY-COST` |
| Service queue | `FROM-HQ-SAP-GCM.FIANA.LOT-TURNKEY-COST` |
| Mirror queue | `MIRROR/FROM-HQ-SAP-GCM.FIANA.LOT-TURNKEY-COST` |
| DMQ | `DMQ/FROM-HQ-SAP-GCM.FIANA.LOT-TURNKEY-COST` |
| REST Delivery Point | `RDP/FROM-HQ-SAP-GCM.FIANA.LOT-TURNKEY-COST` |
| REST Consumer | `RC-SAP-REST` -> `https://sap-backend.internal:443/sap/bc/aem2aif` |
| Queue binding | service queue -> RDP |

### Dry-run then execute

```bash
python semp-workflow.zip run -c config.yaml --dry-run
python semp-workflow.zip run -c config.yaml
```

### Delete the same resources

```yaml
workflows:
  - template: "sap-inbound.delete"
    inputs:
      domain: "HQ"
      system: "SAP"
      system_topic: "GCM.FIANA.LOT-TURNKEY-COST"
      aem_client_username: "SAP-AIF-CLIENT"
```
