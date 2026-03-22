# Test Documentation

## Overview

The test suite covers 100% of the source code in `src/semp_workflow/`. It is split into two tiers:

| Tier | Location | Requires broker? | Count |
|---|---|---|---|
| Unit | `tests/unit/` | No | 364 tests |
| Integration | `tests/integration/` | Yes (Solace SEMP v2) | ~50 tests |

---

## Running the Tests

### Unit Tests Only (no broker needed)

```bash
pip install -e ".[test]"
pytest tests/unit/
```

With coverage report:
```bash
pytest tests/unit/ --cov=semp_workflow --cov-report=term-missing
```

### Integration Tests (broker required)

Copy `.env.example` to `.env` in the project root and fill in your broker details:

```
SEMP_HOST=https://localhost:8943
SEMP_USERNAME=admin
SEMP_PASSWORD=admin
SEMP_MSG_VPN=default
SEMP_VERIFY_SSL=false
```

Then run:
```bash
pytest tests/integration/ -m integration -v
```

### Full Suite

```bash
pytest tests/ -v
```

### Windows Batch

```bat
:: Unit only
pytest tests\unit\

:: Integration only
pytest tests\integration\ -m integration -v

:: All
pytest tests\
```

---

## Test Structure

```
tests/
├── conftest.py                          # root: marker registration, shared mock_client fixture
├── unit/
│   ├── test_helpers.py                  # semp/helpers.py — coerce_bool, coerce_int, clean_payload, check_name_length, enc
│   ├── test_models.py                   # models.py — ActionResult, WorkflowResult, ResultStatus
│   ├── test_config.py                   # config.py — load_config, load_templates, _parse_inputs_schema, _get_bundled_templates_source
│   ├── test_templating.py               # templating.py — TemplateEngine.render, validate_inputs, _coerce_type
│   ├── test_client.py                   # semp/client.py — _request, exists, create, update, delete, test_connection
│   ├── test_engine.py                   # engine.py — _resolve_template, _run_action, _run_workflow, run, fail_fast, dry_run
│   ├── test_output.py                   # output.py — all print_* functions
│   ├── test_cli.py                      # cli.py — run, validate, list-modules, init commands; all exit codes
│   ├── test_main.py                     # __main__.py — module entry point
│   └── test_modules/
│       ├── test_queue.py                # QueueAdd, QueueDelete, QueueUpdate
│       ├── test_q_sub.py                # SubscriptionAdd, SubscriptionDelete
│       ├── test_rdp.py                  # RdpAdd, RdpDelete, RdpUpdate
│       ├── test_rdp_rc.py               # RdpRestConsumerAdd, RdpRestConsumerDelete
│       ├── test_rdp_qb.py               # QueueBindingAdd, QueueBindingDelete
│       ├── test_acl_profile.py          # AclProfileAdd, AclProfileDelete
│       ├── test_client_profile.py       # ClientProfileAdd, ClientProfileDelete
│       └── test_client_username.py      # ClientUsernameAdd, ClientUsernameDelete
└── integration/
    ├── conftest.py                      # SempClient fixture, cleanup_queues/rdps helpers, .env loader
    ├── fixtures/
    │   └── test-artifacts.yaml          # self-contained template covering all artifact types
    ├── test_semp_client.py              # SempClient connectivity, exists, create, delete
    ├── test_queue_lifecycle.py          # Queue + Subscription module lifecycle
    ├── test_rdp_lifecycle.py            # RDP + REST Consumer + Queue Binding lifecycle
    ├── test_access_control_lifecycle.py # ACL Profile + Client Profile + Client Username lifecycle
    ├── test_engine_integration.py       # Engine.run() with generic fixture template (all artifact types)
    └── test_cli_integration.py          # CLI commands against a real broker
```

---

## Unit Tests

All unit tests mock the `SempClient` using `pytest-mock`. No network calls are made.

The root `conftest.py` provides a `mock_client` fixture (a `MagicMock(spec=SempClient)`) shared by all module tests.

---

### `test_helpers.py` — SEMP Helpers

Tests `semp/helpers.py` utility functions used by all modules.

#### `TestCoerceBool`

| Test | Input | Expected |
|---|---|---|
| `test_true_passthrough` | `True` | `True` |
| `test_false_passthrough` | `False` | `False` |
| `test_string_true` | `"true"` | `True` |
| `test_string_True` | `"True"` | `True` |
| `test_string_yes` | `"yes"` | `True` |
| `test_string_1` | `"1"` | `True` |
| `test_string_false` | `"false"` | `False` |
| `test_string_no` | `"no"` | `False` |
| `test_string_0` | `"0"` | `False` |
| `test_string_empty` | `""` | `False` |
| `test_int_nonzero` | `1` | `True` |
| `test_int_zero` | `0` | `False` |

#### `TestCoerceInt`

| Test | Input | Expected |
|---|---|---|
| `test_int_passthrough` | `42` | `42` |
| `test_zero` | `0` | `0` |
| `test_negative` | `-1` | `-1` |
| `test_string_int` | `"42"` | `42` |
| `test_bool_true_raises` | `True` | raises `ValueError`/`TypeError` |
| `test_string_abc_raises` | `"abc"` | raises |

#### `TestCheckNameLength`

Field-specific length limits enforced before any SEMP call:

| Field | Max length |
|---|---|
| `queueName` | 200 |
| `restConsumerName` | 32 |
| `aclProfileName` | 32 |
| unknown field | unlimited (returns `None`) |

#### `TestCleanPayload`

Strips `None`, empty string `""`, and whitespace-only strings from a dict before sending to SEMP. Keeps `0` and `False`.

```python
clean_payload({"a": None, "b": "", "c": "  ", "d": 0, "e": False, "f": "ok"})
# → {"d": 0, "e": False, "f": "ok"}
```

#### `TestEnc`

URL-encodes special characters in path segments:

```python
enc("MIRROR/TOPIC")    # → "MIRROR%2FTOPIC"
enc("#DEAD_MSG_QUEUE") # → "%23DEAD_MSG_QUEUE"
enc("a*b")             # → "a%2Ab"
enc("a>b")             # → "a%3Eb"
enc("abc123")          # → "abc123"  (unchanged)
```

---

### `test_models.py` — Data Models

Tests `models.py` data structures.

#### `TestActionResult`

```python
ActionResult(status=ResultStatus.OK, message="done")
# .module == ""  (default)
# .task_name == ""  (default)
```

#### `TestWorkflowResult`

`WorkflowResult.has_failures` is `True` only if any task has `FAILED` status:

| Task statuses | `has_failures` |
|---|---|
| `[OK, FAILED]` | `True` |
| `[OK, OK]` | `False` |
| `[SKIPPED, SKIPPED]` | `False` |
| `[DRYRUN]` | `False` |

Also verifies `ok_count`, `skipped_count`, `failed_count`, `dryrun_count`.

---

### `test_config.py` — Configuration Loading

Tests `config.py` YAML loading and validation.

#### `TestLoadConfig`

Example valid config used in tests:

```yaml
semp:
  host: "https://broker:943"
  username: "admin"
  password: "secret"
  msg_vpn: "default"
workflows: []
```

What is tested:

| Test | Scenario | Expected |
|---|---|---|
| `test_valid_minimal` | Valid minimal config | `AppConfig` with correct fields |
| `test_semp_defaults` | No `verify_ssl`/`timeout` | `verify_ssl=False`, `timeout=30` |
| `test_semp_custom_values` | `verify_ssl: true`, `timeout: 60` | correctly parsed |
| `test_missing_file_raises` | File doesn't exist | `ConfigError("not found")` |
| `test_missing_semp_section_raises` | No `semp:` key | `ConfigError("semp")` |
| `test_missing_semp_host_raises` | No `host` under `semp` | `ConfigError("host")` |
| `test_global_vars_loaded` | `global_vars: {prefix: FCM}` | `cfg.global_vars == {"prefix": "FCM"}` |
| `test_workflows_not_list_raises` | `workflows: bad` | `ConfigError("list")` |
| `test_workflow_entry_missing_template_raises` | Entry with no `template` key | `ConfigError("template")` |
| `test_non_dict_yaml_raises` | YAML list at root | `ConfigError("YAML mapping")` |
| `test_bundled_fallback_when_templates_dir_missing` | Dir missing, bundled source available | `use_bundled_templates=True` |

#### `TestParseInputsSchema`

Parses the `inputs:` section of a template:

```yaml
inputs:
  required:
    - domain
    - system
  optional:
    owner: "admin"
    ttl: null        # no default
```

Produces:
```python
{
    "domain": {"required": True},
    "system": {"required": True},
    "owner":  {"required": False, "default": "admin"},
    "ttl":    {"required": False},   # null → no "default" key
}
```

#### `TestLoadTemplates`

| Test | Scenario |
|---|---|
| `test_loads_single_template` | One YAML, one template → registered as `"filename.template-name"` |
| `test_multiple_templates_in_one_file` | Two entries → both registered |
| `test_nonexistent_path_raises` | Path doesn't exist → `TemplateError` |
| `test_file_without_workflow_templates_key_skipped` | Unknown top-level key → silently skipped |
| `test_non_mapping_yaml_skipped` | YAML list file → skipped |
| `test_workflow_templates_not_list_skipped` | `workflow-templates: not-a-list` → skipped |
| `test_template_without_name_skipped` | Entry without `name:` → skipped |
| `test_non_dict_action_skipped` | Action is a string not a dict → skipped, template still registered |
| `test_traversable_source_loads_templates` | Mock `importlib.resources` Traversable → loads templates |
| `test_yaml_anchors_resolved` | Real `examples/templates/` with YAML anchors → all templates loaded |

---

### `test_templating.py` — Jinja2 Engine

Tests `templating.py` Jinja2 rendering with `StrictUndefined`.

#### `TestTemplateEngineRender`

```python
engine = TemplateEngine()

engine.render("hello world", {})
# → "hello world"  (fast path: no {{ in string)

engine.render("{{ inputs.x }}", {"inputs": {"x": "foo"}})
# → "foo"

engine.render({"key": "{{ inputs.v }}"}, {"inputs": {"v": "val"}})
# → {"key": "val"}

engine.render(["{{ inputs.a }}", "{{ inputs.b }}"], {"inputs": {"a": "1", "b": "2"}})
# → ["1", "2"]

engine.render(42, {})    # → 42   (passthrough)
engine.render(True, {})  # → True (passthrough)
engine.render(None, {})  # → None (passthrough)

engine.render("{{ inputs.missing }}", {"inputs": {}})
# → raises TemplateError("Undefined variable")

engine.render("{{ 1 / 0 }}", {})
# → raises TemplateError("Template rendering error")
```

#### `TestValidateInputs`

Validates user-supplied inputs against a template's input schema:

```python
# Required field provided
validate_inputs({"domain": "HQ"}, {"domain": {"required": True}}, engine, {})
# → {"domain": "HQ"}

# Required field missing
validate_inputs({}, {"domain": {"required": True}}, engine, {})
# → raises TemplateError("domain")

# Optional with Jinja2 default
schema = {"name": {"required": False, "default": "{{ global_vars.prefix }}"}}
validate_inputs({}, schema, engine, {"global_vars": {"prefix": "FCM"}})
# → {"name": "FCM"}

# Unexpected input
validate_inputs({"domain": "HQ", "typo_var": "x"}, {"domain": {"required": True}}, engine, {})
# → raises TemplateError("typo_var")
```

#### `TestCoerceType`

Post-render type coercion applied to validated inputs:

```python
_coerce_type("field", "42",    "integer")  # → 42
_coerce_type("field", "abc",   "integer")  # → raises TemplateError
_coerce_type("field", "true",  "boolean")  # → True
_coerce_type("field", False,   "boolean")  # → False
_coerce_type("field", 42,      "string")   # → "42"
_coerce_type("field", "x",     "unknown")  # → "x"  (passthrough)
```

---

### `test_client.py` — SEMP REST Client

Tests `semp/client.py` with a mocked `requests.Session`. No network calls made.

#### `TestVpnUrl`

```python
SempClient("https://broker:943", "admin", "pass", "default").vpn_url
# → "https://broker:943/SEMP/v2/config/msgVpns/default"

SempClient("https://b", "u", "p", "my/vpn").vpn_url
# → contains "my%2Fvpn"
```

#### `TestRequest`

| Test | Mock response | Expected |
|---|---|---|
| `test_success_returns_data` | `200`, `{"data": {"key": "val"}}` | returns `{"key": "val"}` |
| `test_empty_body_returns_none` | `200`, empty body | `None` or `{}` |
| `test_semp_error_raises` | `400`, error body with `code: 99` | raises `SEMPError(semp_code=99)` |
| `test_connection_error_raises_semp_error` | `ConnectionError` | raises `SEMPError(status_code=0)` |
| `test_timeout_raises_semp_error` | `Timeout` | raises `SEMPError(status_code=0)` |

#### `TestExists`

| Test | Mock | Expected |
|---|---|---|
| `test_found_returns_true_and_data` | `200` with data | `(True, data)` |
| `test_not_found_semp_code_returns_false` | SEMP `NOT_FOUND` code | `(False, None)` |
| `test_404_status_returns_false` | HTTP `404` | `(False, None)` |
| `test_other_error_reraises` | `500` server error | re-raises `SEMPError` |

#### `TestConnectionMethod`

```python
client.test_connection()  # → True on 200, False on 401, False on ConnectionError
```

#### `TestCrudMethods`

Verifies HTTP method delegation:
- `client.create("queues", {...})` → `POST`
- `client.update("queues/q", {...})` → `PATCH`
- `client.delete("queues/q")` → `DELETE`

---

### `test_modules/` — Module Tests

All eight module files follow the same idempotency pattern. Each action is tested for:

| Scenario | Status |
|---|---|
| Resource already exists (add) | `SKIPPED` |
| Resource does not exist (add) + `dry_run=True` | `DRYRUN` |
| Resource does not exist (add) | `OK` |
| `SEMPError` on `exists` check | `FAILED` |
| `SEMPError` on `create`/`delete`/`update` | `FAILED` |
| Empty required name | `FAILED` |
| Name exceeds field limit | `FAILED` |
| Resource exists (delete) | `OK` |
| Resource does not exist (delete) | `SKIPPED` |
| Resource exists (delete) + `dry_run=True` | `DRYRUN` |

#### `test_queue.py` — Queue-specific payload logic

Beyond the standard pattern, `QueueAdd` has additional payload transformation tests:

| Input | Payload result |
|---|---|
| `maxTtl=0` | `respectTtlEnabled=False` |
| `maxTtl=300` | `respectTtlEnabled=True` |
| `maxRedeliveryCount=-1` | `maxRedeliveryCount=0`, `redeliveryEnabled=False` |
| `maxRedeliveryCount=5` | `maxRedeliveryCount=5`, `redeliveryEnabled=True` |
| `ingressEnabled="true"` (string) | `ingressEnabled=True` (bool coerced) |

`QueueUpdate`:

| Input | Expected |
|---|---|
| Queue exists, `maxMsgSpoolUsage=1024` | `OK`, `PATCH` called |
| Queue does not exist | `FAILED` (cannot update nonexistent) |
| Only `queueName` provided, nothing else | `SKIPPED` (empty payload) |
| `queueName` removed from PATCH payload | `queueName` not in payload sent to broker |

#### `test_q_sub.py` — Subscription idempotency

`SubscriptionAdd` handles SEMP `ALREADY_EXISTS` code (10) from `create` as `SKIPPED` rather than `FAILED` — the subscription was added by a concurrent process.

#### `test_rdp.py`, `test_rdp_rc.py`, `test_rdp_qb.py`

Standard add/delete/update pattern. `RdpUpdate` tested with empty payload → `SKIPPED`.

#### `test_acl_profile.py`, `test_client_profile.py`, `test_client_username.py`

Standard add/delete pattern. No update operation for these resource types.

---

### `test_engine.py` — Workflow Engine

Tests `engine.py` with a mocked `SempClient` and real template YAML files written to `tmp_path`.

The SIMPLE_TEMPLATE used in most tests:

```yaml
workflow-templates:
  - name: "simple"
    inputs:
      required:
        - domain
      optional:
        queue_name: "{{ global_vars.q_name_tpl }}"
    actions:
      - name: "Create Queue"
        module: "queue.add"
        args:
          queueName: "{{ inputs.queue_name }}"
```

The engine is configured with `global_vars: {"q_name_tpl": "Q-{{ inputs.domain }}"}` which exercises the two-pass rendering system.

#### `TestResolveTemplate`

| Test | Input | Expected |
|---|---|---|
| `test_found` | `"wf.simple"` | returns template object |
| `test_not_found_raises` | `"wf.missing"` | raises `TemplateError("not found")` |

#### `TestRunAction`

| Test | Scenario | Expected |
|---|---|---|
| `test_success` | Valid args, mock returns OK | `ResultStatus.OK` |
| `test_unknown_module_fails` | Module `"nonexistent.module"` | `ResultStatus.FAILED` |
| `test_template_error_fails` | Undefined var in args | `ResultStatus.FAILED` |
| `test_module_and_task_name_set` | Successful action | `result.task_name` and `result.module` populated |
| `test_unexpected_exception_returns_failed` | `module.execute` raises `RuntimeError` | `FAILED`, message contains "Unexpected error" |

#### `TestRunWorkflow`

| Test | Scenario | Expected |
|---|---|---|
| `test_valid_inputs_runs_actions` | `domain="HQ"` provided | result has no failures |
| `test_required_input_missing_produces_failed_result` | `domain` missing | `has_failures=True`, message contains "domain" |
| `test_unexpected_input_produces_failed_result` | Extra `typo` key in inputs | `has_failures=True` |
| `test_second_pass_renders_input_default` | `queue_name` default uses `{{ inputs.domain }}` | `create()` called with `queueName="Q-HQ"` |
| `test_circular_reference_produces_failed_result` | Inputs `a → b → a` | `has_failures=True` |

#### `TestRunOptions`

| Test | Scenario | Expected |
|---|---|---|
| `test_dry_run_produces_dryrun_results` | `dry_run=True` | all `DRYRUN`, `create` never called |
| `test_fail_fast_stops_after_first_failure` | Two workflows, first fails, `fail_fast=True` | only 1 result returned |
| `test_multiple_workflows_all_run_without_fail_fast` | Two workflows, no `fail_fast` | 2 results |
| `test_fail_fast_stops_within_workflow` | Two actions, first fails, `fail_fast=True` | only 1 task result |
| `test_second_pass_template_error_produces_failed` | Default references undefined input | `has_failures=True` |
| `test_circular_detection_via_global_vars_produces_failed` | Circular via global_vars expansion | `has_failures=True` |

#### `TestBundledTemplates`

`Engine` loads templates from `importlib.resources` when `use_bundled_templates=True` and the templates directory doesn't exist on disk.

---

### `test_cli.py` — CLI Commands

Tests all CLI commands via `click.testing.CliRunner`. The `Engine` is mocked so no broker is needed.

#### `run` Command Exit Codes

| Scenario | Exit code |
|---|---|
| Success (no failures) | `0` |
| Workflow has failures | `1` |
| `WorkflowError` raised | `1` |
| `ConfigError` or `TemplateError` | `2` |
| `KeyboardInterrupt` | `130` |

#### `validate` Command

| Test | Scenario | Exit code |
|---|---|---|
| Valid config + valid template ref | `0` |
| `ConfigError` | `2` |
| `TemplateError` | `2` |
| Unknown template ref in workflows | `2` |
| `--templates-dir` override | `0` |
| Bundled templates used when no dir configured | `0` |

#### `list-modules` Command

- Exits `0`
- Output contains `"queue"` (and all 15 registered module names)
- `--output <file>` writes a Markdown file and echoes the path

#### `init` Command

| Test | Scenario | Expected |
|---|---|---|
| No bundled templates | exits `2` |
| Normal run | copies bundled YAML files to `--output-dir` |
| File already exists, no `--force` | original preserved |
| File already exists, `--force` | overwritten |
| Summary printed | `"1 file(s) written, 0 skipped"` in output |

---

## Integration Tests

Integration tests hit a real Solace broker. All resource names use the prefix `TEST-SEMP-WF-` to avoid collisions. Every test class has an `autouse` fixture that deletes resources after each test.

### Prerequisites

Set these in `.env` (project root) or as real environment variables:

```
SEMP_HOST=https://<broker-host>:8943
SEMP_USERNAME=admin
SEMP_PASSWORD=admin
SEMP_MSG_VPN=default
SEMP_VERIFY_SSL=false
```

If any are missing, all integration tests are skipped automatically.

---

### `test_semp_client.py` — SEMP Client Connectivity

Directly tests `SempClient` against the broker (no modules layer).

| Test | What it does |
|---|---|
| `test_connection_returns_true` | `client.test_connection()` returns `True` |
| `test_nonexistent_queue_returns_false` | `exists("queues/...")` → `(False, None)` |
| `test_created_queue_returns_true` | `create(...)` then `exists(...)` → `(True, data)` |
| `test_deleted_queue_returns_false` | `create(...)`, `delete(...)`, `exists(...)` → `(False, None)` |

Example SEMP payload sent:
```python
client.create("queues", {"queueName": "TEST-SEMP-WF-CLIENT-TEST", "accessType": "exclusive"})
```

---

### `test_queue_lifecycle.py` — Queue + Subscription

Tests `QueueAdd`, `QueueDelete`, `QueueUpdate`, `SubscriptionAdd`, `SubscriptionDelete` directly against the broker.

#### `TestQueueLifecycle`

| Test | Steps | Assert |
|---|---|---|
| `test_add_creates_queue` | `QueueAdd({"queueName": "TEST-SEMP-WF-QUEUE-LIFECYCLE"})` | `OK` |
| `test_add_again_skipped` | Add twice | second call → `SKIPPED` |
| `test_update_changes_queue` | Add, then `QueueUpdate({"maxMsgSpoolUsage": 512})` | `OK` |
| `test_delete_removes_queue` | Add, then `QueueDelete` | `OK` |
| `test_delete_again_skipped` | Add, Delete, Delete again | second Delete → `SKIPPED` |
| `test_update_nonexistent_fails` | `QueueUpdate` on non-existent queue | `FAILED` |

#### `TestSubscriptionLifecycle`

Queue name: `TEST-SEMP-WF-QUEUE-LIFECYCLE`
Topic: `TEST-SEMP-WF-TEST/TOPIC`

| Test | Steps | Assert |
|---|---|---|
| `test_add_subscription` | Add queue, `SubscriptionAdd` | `OK` |
| `test_add_subscription_again_skipped` | Add sub twice | second → `SKIPPED` |
| `test_delete_subscription` | Add queue + sub, `SubscriptionDelete` | `OK` |
| `test_delete_subscription_again_skipped` | `SubscriptionDelete` with no sub | `SKIPPED` |

---

### `test_rdp_lifecycle.py` — RDP + REST Consumer + Queue Binding

Tests `RdpAdd`, `RdpDelete`, `RdpRestConsumerAdd`, `RdpRestConsumerDelete`, `QueueBindingAdd`, `QueueBindingDelete`.

Resource names:
- RDP: `TEST-SEMP-WF-RDP-LIFECYCLE`
- REST Consumer: `TEST-SEMP-WF-RC`
- Queue: `TEST-SEMP-WF-QUEUE-RDP`

#### `TestRdpLifecycle`

| Test | Steps | Assert |
|---|---|---|
| `test_rdp_add` | `RdpAdd({"restDeliveryPointName": "..."})` | `OK` |
| `test_rdp_add_skipped` | Add twice | second → `SKIPPED` |
| `test_rest_consumer_add` | Add RDP, `RdpRestConsumerAdd(...)` | `OK` |
| `test_queue_binding_add` | Add RDP + Queue, `QueueBindingAdd(...)` | `OK` |
| `test_full_teardown` | Create full stack, delete in reverse order | all → `OK` |

Example REST Consumer payload:
```python
{
    "restDeliveryPointName": "TEST-SEMP-WF-RDP-LIFECYCLE",
    "restConsumerName": "TEST-SEMP-WF-RC",
    "remoteHost": "backend.example.com",
    "remotePort": 443,
    "tlsEnabled": True,
}
```

Example Queue Binding payload:
```python
{
    "restDeliveryPointName": "TEST-SEMP-WF-RDP-LIFECYCLE",
    "queueBindingName": "TEST-SEMP-WF-QUEUE-RDP",
    "postRequestTarget": "/api/receive",
}
```

---

### `test_access_control_lifecycle.py` — ACL Profile + Client Profile + Client Username

Tests access control modules in order of their dependency (username depends on profile and ACL).

Resource names:
- ACL Profile: `TEST-SEMP-WF-ACL`
- Client Profile: `TEST-SEMP-WF-CLIENT-PROFILE`
- Client Username: `TEST-SEMP-WF-CLIENT-USER`

Cleanup deletes in reverse dependency order: username → client profile → ACL profile.

#### `TestAclProfileLifecycle`

| Test | Steps | Assert |
|---|---|---|
| `test_add_creates_profile` | `AclProfileAdd({"aclProfileName": "..."})` | `OK` |
| `test_add_again_skipped` | Add twice | `SKIPPED` |
| `test_dryrun_not_exists` | `dry_run=True`, verify not created | `DRYRUN`, `exists()` → `False` |
| `test_delete_removes_profile` | Add, Delete | `OK` |
| `test_delete_again_skipped` | Add, Delete, Delete | `SKIPPED` |
| `test_dryrun_delete_exists` | Add, `dry_run=True` Delete | `DRYRUN`, still exists on broker |

#### `TestClientProfileLifecycle`

Same six tests plus:

| Test | Steps | Assert |
|---|---|---|
| `test_add_with_options` | Add with `allowGuaranteedMsgSendEnabled=True`, `maxSubscriptionCount=100` | `OK` |

Example payload with options:
```python
{
    "clientProfileName": "TEST-SEMP-WF-CLIENT-PROFILE",
    "allowGuaranteedMsgSendEnabled": True,
    "allowGuaranteedMsgReceiveEnabled": True,
    "maxSubscriptionCount": 100,
}
```

#### `TestClientUsernameLifecycle`

Same six tests as ACL Profile:

```python
ClientUsernameAdd().execute(client, {"clientUsername": "TEST-SEMP-WF-CLIENT-USER"})
```

---

### `test_engine_integration.py` — Engine End-to-End (All Artifact Types)

Uses the self-contained fixture template at `tests/integration/fixtures/test-artifacts.yaml`. The template covers every supported broker artifact type in a single workflow.

#### Fixture Template: `test-artifacts.yaml`

**`test-artifacts.create`** — provisions in dependency order:

| Step | Module | Key args |
|---|---|---|
| 1 | `acl_profile.add` | `aclProfileName`, `clientConnectDefaultAction: allow` |
| 2 | `client_profile.add` | `clientProfileName`, `allowGuaranteedMsgSendEnabled: true` |
| 3 | `client_username.add` | `clientUsername`, `clientProfileName`, `aclProfileName` |
| 4 | `queue.add` | `queueName`, `accessType: exclusive`, `maxTtl: 0`, `maxRedeliveryCount: -1` |
| 5 | `q_sub.add` | `queueName`, `subscriptionTopic: TEST/<prefix>/>` |
| 6 | `rdp.add` | `restDeliveryPointName` |
| 7 | `rdp_rc.add` | `restDeliveryPointName`, `restConsumerName`, `remoteHost`, `remotePort`, `tlsEnabled` |
| 8 | `rdp_qb.add` | `restDeliveryPointName`, `queueBindingName`, `postRequestTarget: /api/test` |

**`test-artifacts.delete`** — removes in reverse dependency order:

| Step | Module |
|---|---|
| 1 | `rdp_qb.delete` |
| 2 | `rdp_rc.delete` |
| 3 | `rdp.delete` |
| 4 | `queue.delete` |
| 5 | `client_username.delete` |
| 6 | `client_profile.delete` |
| 7 | `acl_profile.delete` |

Inputs are derived from a single `prefix` parameter:
```python
INPUTS = {"prefix": "TEST-SEMP-WF-ENG"}
```

Resulting resource names:
| Resource | Name |
|---|---|
| ACL Profile | `TEST-SEMP-WF-ENG-ACL` |
| Client Profile | `TEST-SEMP-WF-ENG-CP` |
| Client Username | `TEST-SEMP-WF-ENG-USER` |
| Queue | `TEST-SEMP-WF-ENG-QUEUE` |
| Subscription topic | `TEST/TEST-SEMP-WF-ENG/>` |
| RDP | `TEST-SEMP-WF-ENG-RDP` |
| REST Consumer | `TEST-SEMP-WF-ENG-RC` |

#### `TestDryRun`

| Test | Assert |
|---|---|
| `test_all_results_are_dryrun` | All 8 task results have `status == DRYRUN` |
| `test_no_broker_objects_created` | Queue, RDP, ACL Profile all `exists()` → `False` |

#### `TestCreateAndDelete`

| Test | Steps | Assert |
|---|---|---|
| `test_create_all_artifacts_ok` | Run `create` once | all `OK` or `SKIPPED`, no failures |
| `test_rerun_all_skipped` | Run `create` twice | second run all `SKIPPED` |
| `test_all_artifacts_exist_after_create` | Run `create`, check broker | ACL, CP, CU, Queue, RDP all `exists()` → `True` |
| `test_delete_after_create` | Run `create` then `delete` | all `OK` or `SKIPPED` |
| `test_delete_again_all_skipped` | Run `delete` twice | second run all `SKIPPED` |
| `test_no_artifacts_remain_after_delete` | Full create→delete cycle | ACL, CP, CU, Queue, RDP all `exists()` → `False` |

---

### `test_cli_integration.py` — CLI Against Real Broker

Uses `click.testing.CliRunner` with a real config file pointing to the live broker and the `tests/integration/fixtures/test-artifacts.yaml` template.

Config file written to `tmp_path`:
```yaml
semp:
  host: "https://<host>:8943"
  username: "admin"
  password: "admin"
  msg_vpn: "default"
  verify_ssl: false
  timeout: 30
templates_dir: "tests/integration/fixtures"
workflows:
  - template: "test-artifacts.create"
    inputs:
      prefix: "TEST-SEMP-WF-CLI"
```

#### `TestValidateCommand`

| Test | Scenario | Exit code |
|---|---|---|
| `test_valid_config_exits_zero` | Valid config + valid template ref | `0` |
| `test_invalid_template_ref_exits_nonzero` | `bad.nonexistent` template | non-zero |

#### `TestListModulesCommand`

| Test | Assert |
|---|---|
| `test_exits_zero` | exit code `0` |
| `test_output_contains_queue_add` | `"queue.add"` in output |
| `test_output_contains_all_module_types` | All 15 registered module names present in output |

The 15 modules verified:
`acl_profile.add/delete`, `client_profile.add/delete`, `client_username.add/delete`,
`queue.add/delete/update`, `q_sub.add/delete`, `rdp.add/delete`,
`rdp_rc.add/delete`, `rdp_qb.add/delete`

#### `TestRunCommand`

| Test | Scenario | Assert |
|---|---|---|
| `test_dry_run_exits_zero` | `run --dry-run` | exit code `0` |
| `test_run_creates_resources` | `run` (no dry-run) | exit `0`, Queue and RDP `exists()` → `True` on broker |

---

## Result Status Reference

All module `execute()` methods return an `ActionResult` with one of these statuses:

| Status | Meaning |
|---|---|
| `OK` | Action was performed and succeeded (resource was created/deleted/updated) |
| `SKIPPED` | No action needed — resource was already in the desired state (idempotent) |
| `DRYRUN` | Dry-run mode: action would have been performed but was not |
| `FAILED` | Action failed due to a SEMP error, validation error, or unexpected exception |

`WorkflowResult.has_failures` is `True` only when at least one task has `FAILED` status.

---

## Module Registry

All 15 actions registered and their SEMP resource paths:

| Module | HTTP method | SEMP path |
|---|---|---|
| `queue.add` | `POST` | `queues` |
| `queue.delete` | `DELETE` | `queues/<name>` |
| `queue.update` | `PATCH` | `queues/<name>` |
| `q_sub.add` | `POST` | `queues/<queue>/subscriptions` |
| `q_sub.delete` | `DELETE` | `queues/<queue>/subscriptions/<topic>` |
| `rdp.add` | `POST` | `restDeliveryPoints` |
| `rdp.delete` | `DELETE` | `restDeliveryPoints/<name>` |
| `rdp.update` | `PATCH` | `restDeliveryPoints/<name>` |
| `rdp_rc.add` | `POST` | `restDeliveryPoints/<rdp>/restConsumers` |
| `rdp_rc.delete` | `DELETE` | `restDeliveryPoints/<rdp>/restConsumers/<rc>` |
| `rdp_qb.add` | `POST` | `restDeliveryPoints/<rdp>/queueBindings` |
| `rdp_qb.delete` | `DELETE` | `restDeliveryPoints/<rdp>/queueBindings/<queue>` |
| `acl_profile.add` | `POST` | `aclProfiles` |
| `acl_profile.delete` | `DELETE` | `aclProfiles/<name>` |
| `client_profile.add` | `POST` | `clientProfiles` |
| `client_profile.delete` | `DELETE` | `clientProfiles/<name>` |
| `client_username.add` | `POST` | `clientUsernames` |
| `client_username.delete` | `DELETE` | `clientUsernames/<name>` |
