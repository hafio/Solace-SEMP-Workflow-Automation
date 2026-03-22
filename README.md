# SEMP Workflow Automation

Ansible-style workflow automation for [Solace](https://solace.com/) brokers via the SEMP v2 REST API.

Define reusable, parameterised workflows in YAML, run them from the CLI or CI/CD pipelines, and rely on idempotent execution — every action checks broker state before acting, so re-running the same workflow is always safe.

---

## Features

- **Idempotent** — checks existence before create/delete; skips actions that are already in the desired state
- **Dry-run mode** — shows what would change without touching the broker
- **Jinja2 templating** — inputs, global variables, and defaults are all rendered with full Jinja2 support
- **15 built-in action modules** — queues, subscriptions, RDPs, REST consumers, queue bindings, ACL profiles, client profiles, client usernames
- **Fail-fast** — optionally stop on first failure across workflows or actions
- **Composable** — multiple workflows in one run, multiple templates in one file, shared `global_vars`

---

## Installation

Requires Python 3.10+.

```bash
pip install -e .
```

Verify:
```bash
semp-workflow --version
```

---

## Quick Start

**1. Create a config file** (`config.yaml`):

```yaml
semp:
  host: "https://your-broker:8943"
  username: "admin"
  password: "admin"
  msg_vpn: "default"

templates_dir: "templates"

workflows:
  - template: "my-queues.create"
    inputs:
      queue_name: "MY-APP-QUEUE"
      sub_topic:  "app/events/>"
```

**2. Create a template file** (`templates/my-queues.yaml`):

```yaml
workflow-templates:
  - name: "create"
    inputs:
      required:
        - queue_name
        - sub_topic
    actions:
      - name: "Create Queue"
        module: "queue.add"
        args:
          queueName: "{{ inputs.queue_name }}"
          accessType: exclusive
          ingressEnabled: true
          egressEnabled: true
      - name: "Add Subscription"
        module: "q_sub.add"
        args:
          queueName:         "{{ inputs.queue_name }}"
          subscriptionTopic: "{{ inputs.sub_topic }}"
```

**3. Validate, then run:**

```bash
# Check config and template references without connecting
semp-workflow validate --config config.yaml

# Preview what would change (no broker modifications)
semp-workflow run --config config.yaml --dry-run

# Execute
semp-workflow run --config config.yaml
```

---

## Config File Reference

```yaml
# ── Broker connection ──────────────────────────────────────────────────────────
semp:
  host:       "https://broker-host:8943"   # SEMP v2 base URL (required)
  username:   "admin"                       # (required)
  password:   "admin"                       # (required)
  msg_vpn:    "default"                     # Message VPN name (required)
  verify_ssl: false                         # Verify TLS certificate (default: false)
  timeout:    30                            # HTTP timeout in seconds (default: 30)

# ── Shared variables (available in all templates as {{ global_vars.X }}) ───────
global_vars:
  topic_prefix:    "myapp/events"
  default_owner:   "my-client"
  queue_ttl:       1296000              # 15 days in seconds

# ── Template directory ─────────────────────────────────────────────────────────
templates_dir: "templates"             # Path to your .yaml template files

# ── Workflows to execute (in order) ───────────────────────────────────────────
workflows:
  - template: "my-queues.create"       # "filename.template-name"
    inputs:
      queue_name: "MY-QUEUE"
      sub_topic:  "{{ global_vars.topic_prefix }}/>"

  - template: "my-queues.create"
    inputs:
      queue_name: "MY-OTHER-QUEUE"
      sub_topic:  "other/topic/>"
```

### `semp` fields

| Field | Required | Default | Description |
|---|---|---|---|
| `host` | Yes | — | Full base URL including port, e.g. `https://broker:8943` |
| `username` | Yes | — | SEMP admin username |
| `password` | Yes | — | SEMP admin password |
| `msg_vpn` | Yes | — | Message VPN to operate on |
| `verify_ssl` | No | `false` | Verify the broker's TLS certificate |
| `timeout` | No | `30` | HTTP request timeout in seconds |

---

## Template File Reference

Templates live in `.yaml` files under `templates_dir`. Each file can contain multiple named templates under the `workflow-templates` key.

Template references in the config use the format `filename.template-name` (without the `.yaml` extension).

```yaml
workflow-templates:

  - name: "create"

    # ── Input schema ────────────────────────────────────────────────────────────
    inputs:
      required:
        - queue_name               # Caller must supply this

      optional:
        # Static default
        access_type: exclusive

        # Default can reference global_vars (resolved first pass)
        owner: "{{ global_vars.default_owner }}"

        # Default can reference other inputs (resolved second pass)
        dmq_name: "DMQ/{{ inputs.queue_name }}"

    # ── Actions (executed in order) ─────────────────────────────────────────────
    actions:
      - name: "Create Queue"        # Human-readable label shown in output
        module: "queue.add"         # Module to invoke (see Module Reference below)
        args:
          queueName:   "{{ inputs.queue_name }}"
          accessType:  "{{ inputs.access_type }}"
          owner:       "{{ inputs.owner }}"
          deadMsgQueue: "{{ inputs.dmq_name }}"

      - name: "Create DMQ"
        module: "queue.add"
        args:
          queueName: "{{ inputs.dmq_name }}"
```

### Input schema

| Key | Format | Description |
|---|---|---|
| `required` | List of strings | Inputs that must be supplied by the caller |
| `optional` | Map of `name: default` | Optional inputs; default can be a literal value or a Jinja2 expression |

An optional input with `null` as its default is included in the schema but has no default value — it is omitted from the resolved context if not provided by the caller.

### Jinja2 rendering

All `args` values and input defaults are rendered through Jinja2 with `StrictUndefined`. Two passes are performed:

1. **First pass** — `global_vars` is available. Optional defaults referencing `global_vars` are resolved.
2. **Second pass** — the fully resolved `inputs` dict is available. Defaults referencing `inputs.X` (e.g. `"DMQ/{{ inputs.queue_name }}"`) are resolved.

Undefined variables raise an error immediately. Circular references between inputs are detected and reported.

### YAML anchors

YAML anchors (`&`) and aliases (`*`) are fully supported, which is useful for sharing input blocks or action lists between templates in the same file:

```yaml
workflow-templates:
  - name: "create-seq"
    inputs:
      required: &required-inputs
        - queue_name
        - sub_topic
      optional: &optional-inputs
        access_type: exclusive
    actions: &create-actions
      - name: "Create Queue"
        module: "queue.add"
        args:
          queueName: "{{ inputs.queue_name }}"

  - name: "create-non-seq"
    inputs:
      required: *required-inputs
      optional:
        <<: *optional-inputs
        access_type: non-exclusive  # override one field
    actions: *create-actions
```

---

## CLI Reference

```
semp-workflow [OPTIONS] COMMAND [ARGS]...
```

### `run` — Execute workflows

```bash
semp-workflow run --config config.yaml [OPTIONS]
```

| Option | Short | Description |
|---|---|---|
| `--config PATH` | `-c` | Config file to load (required) |
| `--templates-dir PATH` | `-t` | Override the `templates_dir` from config |
| `--dry-run` / `--check` | | Preview changes without modifying the broker |
| `--fail-fast` | `-f` | Stop on first failure (workflow or action) |
| `--verbose` | `-v` | Enable debug logging |

**Exit codes:**

| Code | Meaning |
|---|---|
| `0` | All workflows completed with no failures |
| `1` | One or more workflow actions failed |
| `2` | Configuration or template error (nothing was executed) |
| `130` | Interrupted by user (`Ctrl+C`) |

### `validate` — Check config without running

Loads the config and verifies that every template reference in `workflows` exists. No broker connection is made.

```bash
semp-workflow validate --config config.yaml [--templates-dir PATH]
```

### `list-modules` — Show available action modules

```bash
semp-workflow list-modules [--output FILE]
```

Lists all 15 registered action modules with their parameters. `--output` writes a full Markdown reference to a file.

---

## Action Result States

Every action returns one of four states, displayed in the run output:

| State | Meaning |
|---|---|
| `OK` | Action executed successfully (resource was created, updated, or deleted) |
| `SKIPPED` | No change needed — resource is already in the desired state |
| `DRYRUN` | Would have acted, but dry-run mode is enabled |
| `FAILED` | Action failed due to a SEMP error, validation error, or unexpected exception |

`SKIPPED` is the expected result when re-running the same workflow. A workflow is considered successful if it has no `FAILED` actions.

---

## Module Reference

Run `semp-workflow list-modules --output all-modules.md` to generate a full parameter reference, or see [all-modules.md](all-modules.md).

### Summary

| Module | Description |
|---|---|
| `queue.add` | Create a queue. Skipped if it already exists. |
| `queue.delete` | Delete a queue. Skipped if it does not exist. |
| `queue.update` | Update queue attributes. Fails if the queue does not exist. |
| `q_sub.add` | Add a topic subscription to a queue. Skipped if it already exists. |
| `q_sub.delete` | Remove a topic subscription from a queue. Skipped if it does not exist. |
| `rdp.add` | Create a REST Delivery Point. Skipped if it already exists. |
| `rdp.delete` | Delete a REST Delivery Point. Skipped if it does not exist. |
| `rdp.update` | Update RDP attributes. Fails if the RDP does not exist. |
| `rdp_rc.add` | Add a REST consumer to an RDP. Skipped if it already exists. |
| `rdp_rc.delete` | Remove a REST consumer from an RDP. Skipped if it does not exist. |
| `rdp_qb.add` | Bind a queue to an RDP. Skipped if the binding already exists. |
| `rdp_qb.delete` | Remove a queue binding from an RDP. Skipped if it does not exist. |
| `acl_profile.add` | Create an ACL profile. Skipped if it already exists. |
| `acl_profile.delete` | Delete an ACL profile. Skipped if it does not exist. |
| `client_profile.add` | Create a client profile. Skipped if it already exists. |
| `client_profile.delete` | Delete a client profile. Skipped if it does not exist. |
| `client_username.add` | Create a client username. Skipped if it already exists. |
| `client_username.delete` | Delete a client username. Skipped if it does not exist. |

---

## Global Variables

`global_vars` in the config are available in all templates as `{{ global_vars.X }}`. They are rendered before inputs, so defaults can reference them:

```yaml
# config.yaml
global_vars:
  topic_prefix: "myapp/events"
  queue_ttl:    1296000

# template
optional:
  sub_topic: "{{ global_vars.topic_prefix }}/>"
  ttl:       "{{ global_vars.queue_ttl }}"
```

Global variable values can themselves contain Jinja2 expressions that reference `inputs`:

```yaml
global_vars:
  queue_name_tpl: "Q-{{ inputs.domain }}-{{ inputs.system }}"
```

In this case the value is passed through as a raw string in the first pass, then resolved in the second pass once `inputs` is available.

---

## Example: Full Workflow with RDP

```yaml
# templates/app-inbound.yaml

workflow-templates:
  - name: "create"
    inputs:
      required:
        - app_name
        - backend_host
      optional:
        queue_name:   "FROM-{{ inputs.app_name }}"
        rdp_name:     "RDP-{{ inputs.app_name }}"
        rc_name:      "RC-{{ inputs.app_name }}"
        backend_port: 443
        tls_enabled:  true
        post_target:  "/api/receive"

    actions:
      - name: "Create Inbound Queue"
        module: "queue.add"
        args:
          queueName:    "{{ inputs.queue_name }}"
          accessType:   exclusive
          ingressEnabled: true
          egressEnabled:  true

      - name: "Create REST Delivery Point"
        module: "rdp.add"
        args:
          restDeliveryPointName: "{{ inputs.rdp_name }}"

      - name: "Create REST Consumer"
        module: "rdp_rc.add"
        args:
          restDeliveryPointName: "{{ inputs.rdp_name }}"
          restConsumerName:      "{{ inputs.rc_name }}"
          remoteHost:            "{{ inputs.backend_host }}"
          remotePort:            "{{ inputs.backend_port }}"
          tlsEnabled:            "{{ inputs.tls_enabled }}"
          enabled:               true

      - name: "Bind Queue to RDP"
        module: "rdp_qb.add"
        args:
          restDeliveryPointName: "{{ inputs.rdp_name }}"
          queueBindingName:      "{{ inputs.queue_name }}"
          postRequestTarget:     "{{ inputs.post_target }}"

  - name: "delete"
    inputs:
      required:
        - app_name
      optional:
        queue_name: "FROM-{{ inputs.app_name }}"
        rdp_name:   "RDP-{{ inputs.app_name }}"

    actions:
      - name: "Delete REST Delivery Point"
        module: "rdp.delete"
        args:
          restDeliveryPointName: "{{ inputs.rdp_name }}"

      - name: "Delete Inbound Queue"
        module: "queue.delete"
        args:
          queueName: "{{ inputs.queue_name }}"
```

Run it:

```yaml
# config.yaml
semp:
  host:     "https://broker:8943"
  username: "admin"
  password: "admin"
  msg_vpn:  "default"

templates_dir: "templates"

workflows:
  - template: "app-inbound.create"
    inputs:
      app_name:    "ORDER-SERVICE"
      backend_host: "orders.internal.example.com"
```

```bash
semp-workflow run --config config.yaml --dry-run
semp-workflow run --config config.yaml
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `click` | CLI framework |
| `jinja2` | Template rendering |
| `pyyaml` | Config and template parsing |
| `requests` | SEMP v2 REST API calls |
| `colorama` | Coloured terminal output |
| `urllib3` | TLS and HTTP utilities |
