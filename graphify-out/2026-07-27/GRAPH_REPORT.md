# Graph Report - SEMP-Workflow_Automation  (2026-07-27)

## Corpus Check
- 100 files · ~52,377 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1458 nodes · 3399 edges · 97 communities (67 shown, 30 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 758 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be85a8e5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Engine & Config Core
- Payload Helpers & Coercion
- CLI Command Tests
- Jinja2 Templating Engine
- Queue & Subscription Modules
- Client Profile Module
- RDP Modules & Tests
- Client Username Module
- SEMP Client Tests
- ACL Profile Module
- CLI Commands
- Template Loading
- Config Loading
- Output Rendering Tests
- Integration Test Fixtures
- Result Models & Enums
- Workflow Execution & Output
- RDP Consumer/Binding & Client
- SEMP REST Client
- Action Result Model
- Base Module Abstraction
- Workflow Result Tests
- RDP REST Consumer Add Tests
- SEMP Error & Subscription Add
- Workflow Result Aggregation
- Queue Binding Add Tests
- Build & Packaging Script
- Input Schema Parsing
- ACL Publish Exception Module
- ACL Subscribe Exception Module
- Queue Subscription Module
- ACL Publish Exception Add Tests
- ACL Subscribe Exception Add Tests
- Bundled Templates Source
- Module Registry
- ACL Publish Exception Delete Tests
- ACL Subscribe Exception Delete Tests
- Queue Delete Tests
- Queue Binding Delete Tests
- RDP Consumer Delete Tests
- Recap Output Tests
- Subscription Delete Tests
- Workflow Header Output Tests
- Action Dispatch
- Validation Output Tests
- Project Documentation
- Shared Test Fixtures
- Module Entry Point Tests
- README & SEMP Overview
- Test Shell Script
- CI Workflow
- Package Root
- NewEngine
- check_name_length
- newTestEngine
- dev.sh
- dev.ps1
- .Execute
- clean_payload
- test_cli_integration.py
- TemplateError
- coerce_bool
- .Execute
- rdp.go
- PyStr
- coerce_int
- TestClientProfileUpdate
- TestClientUsernameUpdate
- QueueAdd
- integration/conftest.py
- WorkflowResult
- ClientProfileAdd
- TestClientProfileAdd
- TestQueueUpdate
- AclProfileAdd
- ClientUsernameAdd
- TestClientUsernameAdd
- TestRdpAdd
- TestRdpUpdate
- aclProfileAdd
- aclSubscribeExceptionAdd
- subscriptionAdd
- queueBindingAdd
- TestAclProfileDelete
- TestRdpDelete
- models_test.go
- test_queue.py
- TestPrintError
- TestPrintModuleList
- semp-workflow
- semp-workflow

## God Nodes (most connected - your core abstractions)
1. `SEMPError` - 104 edges
2. `ResultStatus` - 70 edges
3. `SempClient` - 60 edges
4. `ActionResult` - 50 edges
5. `enc()` - 44 edges
6. `BaseModule` - 41 edges
7. `TemplateError` - 40 edges
8. `exec()` - 37 edges
9. `main()` - 36 edges
10. `Engine` - 36 edges

## Surprising Connections (you probably didn't know these)
- `TestGetBundledTemplatesSource` --uses--> `AppConfig`  [INFERRED]
  tests/unit/test_config.py → src/semp_workflow/config.py
- `TestLoadConfig` --uses--> `AppConfig`  [INFERRED]
  tests/unit/test_config.py → src/semp_workflow/config.py
- `TestLoadTemplates` --uses--> `AppConfig`  [INFERRED]
  tests/unit/test_config.py → src/semp_workflow/config.py
- `TestParseInputsSchema` --uses--> `AppConfig`  [INFERRED]
  tests/unit/test_config.py → src/semp_workflow/config.py
- `TestGetBundledTemplatesSource` --uses--> `ConfigError`  [INFERRED]
  tests/unit/test_config.py → src/semp_workflow/exceptions.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Testing Infrastructure** — docs_tests, github_workflows_ci, tests_integration_fixtures_test_artifacts [EXTRACTED 0.90]

## Communities (97 total, 30 thin omitted)

### Community 0 - "Engine & Config Core"
Cohesion: 0.07
Nodes (40): AppConfig, SEMP connection details., A single workflow invocation from the config file., Top-level application configuration., SempConfig, WorkflowEntry, Engine, Loads templates, resolves variables, and executes workflows. (+32 more)

### Community 1 - "Payload Helpers & Coercion"
Cohesion: 0.14
Nodes (8): ActionResult, _build_queue_payload(), ActionResult, Build a SEMP queue payload with proper type coercion., ActionResult, enc(), URL-encode a SEMP path segment., TestEnc

### Community 2 - "CLI Command Tests"
Cohesion: 0.09
Nodes (16): Exception, main(), SEMP Workflow Automation - Ansible-like playbooks for Solace SEMP., ConfigError, Input validation failure., Base exception for all workflow errors., Invalid or missing configuration., ValidationError (+8 more)

### Community 3 - "Jinja2 Templating Engine"
Cohesion: 0.07
Nodes (16): _coerce_type(), Any, Coerce a value to the expected type., Resolves Jinja2 expressions in workflow action args.      Context is a dict with, Recursively render Jinja2 expressions in a data structure.          - Strings ar, Render a single string through Jinja2., Validate and fill defaults for workflow inputs against a schema.      Args:, TemplateEngine (+8 more)

### Community 5 - "Client Profile Module"
Cohesion: 0.15
Nodes (5): add_module(), delete_module(), Unit tests for modules/client_profile.py., TestClientProfileDelete, update_module()

### Community 6 - "RDP Modules & Tests"
Cohesion: 0.12
Nodes (21): ABC, BaseModule, Abstract base for all SEMP action modules.      Every module implements idempote, _build_rdp_payload(), ActionResult, QueueBindingAdd, QueueBindingDelete, RDP module - rdp.add, rdp.delete, rdp.update. (+13 more)

### Community 7 - "Client Username Module"
Cohesion: 0.15
Nodes (5): add_module(), delete_module(), Unit tests for modules/client_username.py., TestClientUsernameDelete, update_module()

### Community 8 - "SEMP Client Tests"
Cohesion: 0.07
Nodes (13): Verify connectivity to the broker by fetching the VPN., Base URL for VPN-scoped SEMP config endpoints., URL-encode a path segment (handles /, #, *, > etc.)., client(), _make_response(), Unit tests for semp/client.py (mocked requests.Session)., SempClient with a mocked requests.Session.      We create a real SempClient (s, TestConnectionMethod (+5 more)

### Community 9 - "ACL Profile Module"
Cohesion: 0.17
Nodes (4): add_module(), delete_module(), Unit tests for modules/acl_profile.py., TestAclProfileAdd

### Community 10 - "CLI Commands"
Cohesion: 0.12
Nodes (21): init_cmd(), list_modules_cmd(), CLI entry point using Click., Validate config and templates without executing., List all available action modules., Copy bundled workflow templates to a local directory.      Useful after receivin, Execute workflows defined in a config file., run() (+13 more)

### Community 11 - "Template Loading"
Cohesion: 0.21
Nodes (4): load_templates(), Load all workflow templates from a filesystem directory or a Traversable.      A, load_templates works with a mock Traversable (simulating importlib.resources)., TestLoadTemplates

### Community 12 - "Config Loading"
Cohesion: 0.18
Nodes (5): load_config(), Path, Load and validate the main config YAML file., When templates_dir doesn't exist and bundled source is available, use_bundled=Tr, TestLoadConfig

### Community 13 - "Output Rendering Tests"
Cohesion: 0.14
Nodes (4): SEMP Workflow Automation - Ansible-like playbooks for Solace SEMP., Unit tests for output.py., TestPrintDryRunBanner, TestRenderModuleDocsMd

### Community 14 - "Integration Test Fixtures"
Cohesion: 0.22
Nodes (3): Integration tests for SempClient against a real Solace broker., TestConnectivity, TestExistence

### Community 15 - "Result Models & Enums"
Cohesion: 0.12
Nodes (21): Enum, Exception hierarchy for SEMP Workflow Automation., Data models for SEMP Workflow Automation., Result of an idempotent action., ResultStatus, ACL Profile module - acl_profile.add, acl_profile.delete., ACL Publish Topic Exception module - acl_publish_exception.add, acl_publish_exce, ACL Subscribe Topic Exception module - acl_subscribe_exception.add, acl_subscrib (+13 more)

### Community 16 - "Workflow Execution & Output"
Cohesion: 0.13
Nodes (18): ActionResult, Any, WorkflowEntry, WorkflowResult, Workflow execution engine - orchestrates template resolution, variable rendering, Execute a single workflow entry., Resolve args and execute a single action module., Execute all workflows defined in the config.          Returns list of WorkflowRe (+10 more)

### Community 17 - "RDP Consumer/Binding & Client"
Cohesion: 0.06
Nodes (71): Buffer, Command, ActionSpec, AppConfig, SempConfig, WorkflowEntry, WorkflowTemplate, Engine (+63 more)

### Community 18 - "SEMP REST Client"
Cohesion: 0.10
Nodes (15): ActionResult, AclSubscribeExceptionAdd, AclSubscribeExceptionDelete, ActionResult, ActionResult, Execute the module action idempotently., Check if a resource exists. Returns (exists, data_or_None)., POST to create a resource. (+7 more)

### Community 19 - "Action Result Model"
Cohesion: 0.27
Nodes (4): ActionResult, Result of a single task execution., TestActionResult, TestPrintTaskResult

### Community 20 - "Base Module Abstraction"
Cohesion: 0.11
Nodes (49): absent(), existing(), sempErr(), exec(), ActionResult, Client, T, TestAclProfileAddDelete() (+41 more)

### Community 23 - "SEMP Error & Subscription Add"
Cohesion: 0.12
Nodes (4): Error returned by the Solace SEMP API., SEMPError, TestSubscriptionAdd, TestQueueBindingAdd

### Community 24 - "Workflow Result Aggregation"
Cohesion: 0.18
Nodes (3): Aggregated result of a complete workflow execution., WorkflowResult, TestPrintBanner

### Community 25 - "Queue Binding Add Tests"
Cohesion: 0.09
Nodes (37): Duration, asSEMPError(), backoffDelay(), NewClient(), Client, T, newTestClient(), TestConnectionFailed() (+29 more)

### Community 26 - "Build & Packaging Script"
Cohesion: 0.33
Nodes (9): build(), _clean_project(), _clean_stage(), main(), Path, Pick the templates directory to bundle, with sensible fallbacks., Remove build artifacts that inflate the archive unnecessarily., Remove setuptools build cache so renamed/deleted files don't bleed into the zip. (+1 more)

### Community 27 - "Input Schema Parsing"
Cohesion: 0.31
Nodes (4): _parse_inputs_schema(), Any, Parse a template inputs block into a flat schema dict.      Format:         inpu, TestParseInputsSchema

### Community 28 - "ACL Publish Exception Module"
Cohesion: 0.25
Nodes (6): AclPublishExceptionAdd, AclPublishExceptionDelete, ActionResult, add_module(), delete_module(), Unit tests for modules/acl_pub_exc.py.

### Community 29 - "ACL Subscribe Exception Module"
Cohesion: 0.18
Nodes (25): NewActionResult(), ActionResult, Client, ActionResult, Client, argStr(), dryrun(), failed() (+17 more)

### Community 30 - "Queue Subscription Module"
Cohesion: 0.29
Nodes (6): SubscriptionAdd, SubscriptionDelete, TestSubscriptionLifecycle, add_module(), delete_module(), Unit tests for modules/q_sub.py.

### Community 33 - "Bundled Templates Source"
Cohesion: 0.24
Nodes (5): _get_bundled_templates_source(), Return an importlib.resources Traversable for bundled templates, or None.      W, AppConfig, Unit tests for config.py., TestGetBundledTemplatesSource

### Community 34 - "Module Registry"
Cohesion: 0.29
Nodes (7): _autodiscover(), get_module(), Module registry - auto-discovers and registers all SEMP action modules., Register a module action under the given 'object.verb' name., Look up a registered module by 'object.verb' name., Import all sibling modules to trigger their MODULES registration., register()

### Community 43 - "Action Dispatch"
Cohesion: 0.09
Nodes (29): ConfigError, SEMPError, TemplateError, ValidationError, WorkflowError, T, runCLI(), TestClassifyExit() (+21 more)

### Community 45 - "Project Documentation"
Cohesion: 0.50
Nodes (4): Module Reference, Release Process, Test Documentation, Test Artifacts Template

### Community 47 - "Module Entry Point Tests"
Cohesion: 0.50
Nodes (3): Unit tests for __main__.py - python -m semp_workflow entry point., Running as __main__ calls the CLI main() function., test_main_module_calls_cli()

### Community 48 - "README & SEMP Overview"
Cohesion: 0.67
Nodes (3): SEMP Workflow Automation README, SEMP v2 REST API, Solace Broker

### Community 51 - "Package Root"
Cohesion: 0.07
Nodes (22): coerceBoolFields(), coerceIntFields(), sempCodeOf(), buildProfilePayload(), clientProfileParams(), init(), buildUsernamePayload(), init() (+14 more)

### Community 57 - "NewEngine"
Cohesion: 0.22
Nodes (23): Config, coerceType(), isUndefinedErr(), NewEngine(), pyInt(), ctx(), T, TestRenderDefaultFilter() (+15 more)

### Community 58 - "check_name_length"
Cohesion: 0.14
Nodes (10): _build_profile_payload(), ClientProfileUpdate, ActionResult, Client Profile module - client_profile.add, client_profile.delete, client_profil, _build_username_payload(), ClientUsernameUpdate, ActionResult, check_name_length() (+2 more)

### Community 59 - "newTestEngine"
Cohesion: 0.21
Nodes (17): Engine, engineFake, Client, T, WorkflowTemplate, newTestEngine(), queueTemplate(), silence() (+9 more)

### Community 60 - "dev.sh"
Cohesion: 0.35
Nodes (19): CGO_ENABLED, main(), NO_COLOR, run_logged(), dev.sh script, die(), ok(), step() (+11 more)

### Community 61 - "dev.ps1"
Cohesion: 0.40
Nodes (15): Have(), Invoke-Logged(), Die(), Ok(), Step(), Task-All(), Task-Build(), Task-Cov() (+7 more)

### Community 62 - ".Execute"
Cohesion: 0.16
Nodes (7): buildQueuePayload(), ActionResult, Client, init(), queueAdd, queueDelete, queueUpdate

### Community 63 - "clean_payload"
Cohesion: 0.20
Nodes (5): _build_consumer_payload(), ActionResult, clean_payload(), Return a copy of args with None and empty-string values removed., TestCleanPayload

### Community 64 - "test_cli_integration.py"
Cohesion: 0.15
Nodes (6): config_file(), Integration: CLI commands against a real Solace broker., TestListModulesCommand, TestRunCommand, TestValidateCommand, _write_config()

### Community 65 - "TemplateError"
Cohesion: 0.16
Nodes (10): ActionSpec, Configuration and template loading., A single action step within a workflow template., A parsed workflow template., WorkflowTemplate, WorkflowTemplate, Resolve a 'filename.TemplateName' reference to a WorkflowTemplate., Error loading or resolving a workflow template. (+2 more)

### Community 66 - "coerce_bool"
Cohesion: 0.25
Nodes (3): coerce_bool(), Coerce a value to bool (handles YAML bools and Jinja2 string output)., TestCoerceBool

### Community 67 - ".Execute"
Cohesion: 0.20
Nodes (5): ActionResult, Client, init(), aclPublishExceptionAdd, aclPublishExceptionDelete

### Community 68 - "rdp.go"
Cohesion: 0.17
Nodes (5): buildRdpPayload(), init(), rdpAdd, rdpDelete, rdpUpdate

### Community 69 - "PyStr"
Cohesion: 0.27
Nodes (10): CoerceInt(), isUnreserved(), PyStr(), T, TestCheckNameLength(), TestCleanPayload(), TestCoerceBool(), TestCoerceInt() (+2 more)

### Community 70 - "coerce_int"
Cohesion: 0.26
Nodes (4): coerce_int(), Coerce a value to int., Unit tests for semp/helpers.py., TestCoerceInt

### Community 73 - "QueueAdd"
Cohesion: 0.36
Nodes (5): QueueAdd, QueueDelete, QueueUpdate, TestQueueLifecycle, update_module()

### Community 74 - "integration/conftest.py"
Cohesion: 0.20
Nodes (8): cleanup_queues(), cleanup_rdps(), _missing_vars(), Integration test fixtures.  Connection settings are loaded from a .env file at, Yield a list to register queue names for deletion after the test., Yield a list to register RDP names for deletion after the test., semp_client(), Integration: ACL profile, client profile, and client username lifecycle.

### Community 75 - "WorkflowResult"
Cohesion: 0.38
Nodes (3): ActionResult, ResultStatus, WorkflowResult

### Community 76 - "ClientProfileAdd"
Cohesion: 0.42
Nodes (3): ClientProfileAdd, ClientProfileDelete, TestClientProfileLifecycle

### Community 79 - "AclProfileAdd"
Cohesion: 0.47
Nodes (3): AclProfileAdd, AclProfileDelete, TestAclProfileLifecycle

### Community 80 - "ClientUsernameAdd"
Cohesion: 0.47
Nodes (3): ClientUsernameAdd, ClientUsernameDelete, TestClientUsernameLifecycle

### Community 84 - "aclProfileAdd"
Cohesion: 0.25
Nodes (3): init(), aclProfileAdd, aclProfileDelete

### Community 85 - "aclSubscribeExceptionAdd"
Cohesion: 0.25
Nodes (3): init(), aclSubscribeExceptionAdd, aclSubscribeExceptionDelete

### Community 86 - "subscriptionAdd"
Cohesion: 0.25
Nodes (3): init(), subscriptionAdd, subscriptionDelete

### Community 87 - "queueBindingAdd"
Cohesion: 0.25
Nodes (3): init(), queueBindingAdd, queueBindingDelete

### Community 90 - "models_test.go"
Cohesion: 0.60
Nodes (4): T, TestNewActionResult(), TestWorkflowResultCounts(), TestWorkflowResultNoFailures()

### Community 91 - "test_queue.py"
Cohesion: 0.50
Nodes (3): add_module(), delete_module(), Unit tests for modules/queue.py.

## Knowledge Gaps
- **12 isolated node(s):** `semp-workflow`, `Client`, `InputSpec`, `NO_COLOR`, `CGO_ENABLED` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SEMPError` connect `SEMP Error & Subscription Add` to `Engine & Config Core`, `CLI Command Tests`, `Queue & Subscription Modules`, `Client Profile Module`, `RDP Modules & Tests`, `Client Username Module`, `SEMP Client Tests`, `ACL Profile Module`, `Result Models & Enums`, `SEMP REST Client`, `RDP REST Consumer Add Tests`, `ACL Publish Exception Add Tests`, `ACL Subscribe Exception Add Tests`, `ACL Publish Exception Delete Tests`, `ACL Subscribe Exception Delete Tests`, `Queue Delete Tests`, `Queue Binding Delete Tests`, `RDP Consumer Delete Tests`, `Subscription Delete Tests`, `check_name_length`, `TestClientProfileUpdate`, `TestClientUsernameUpdate`, `TestClientProfileAdd`, `TestQueueUpdate`, `TestClientUsernameAdd`, `TestRdpAdd`, `TestRdpUpdate`, `TestAclProfileDelete`, `TestRdpDelete`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `ResultStatus` connect `Result Models & Enums` to `Engine & Config Core`, `CLI Command Tests`, `Queue & Subscription Modules`, `Client Profile Module`, `RDP Modules & Tests`, `Client Username Module`, `ACL Profile Module`, `Output Rendering Tests`, `Workflow Execution & Output`, `Action Result Model`, `Workflow Result Tests`, `RDP REST Consumer Add Tests`, `SEMP Error & Subscription Add`, `Workflow Result Aggregation`, `Queue Subscription Module`, `ACL Publish Exception Add Tests`, `ACL Subscribe Exception Add Tests`, `ACL Publish Exception Delete Tests`, `ACL Subscribe Exception Delete Tests`, `Queue Delete Tests`, `Queue Binding Delete Tests`, `RDP Consumer Delete Tests`, `Recap Output Tests`, `Subscription Delete Tests`, `Workflow Header Output Tests`, `Validation Output Tests`, `check_name_length`, `TestClientProfileUpdate`, `TestClientUsernameUpdate`, `QueueAdd`, `ClientProfileAdd`, `TestClientProfileAdd`, `TestQueueUpdate`, `AclProfileAdd`, `ClientUsernameAdd`, `TestClientUsernameAdd`, `TestRdpAdd`, `TestRdpUpdate`, `TestAclProfileDelete`, `TestRdpDelete`, `TestPrintError`, `TestPrintModuleList`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `SempClient` connect `SEMP REST Client` to `Bundled Templates Source`, `Payload Helpers & Coercion`, `RDP Modules & Tests`, `SEMP Client Tests`, `integration/conftest.py`, `Integration Test Fixtures`, `Result Models & Enums`, `Workflow Execution & Output`, `check_name_length`, `ACL Publish Exception Module`, `clean_payload`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `SEMPError` (e.g. with `TestConnectionMethod` and `TestCrudMethods`) actually correct?**
  _`SEMPError` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `ResultStatus` (e.g. with `Engine` and `TestAclProfileLifecycle`) actually correct?**
  _`ResultStatus` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `SempClient` (e.g. with `TestConnectivity` and `TestExistence`) actually correct?**
  _`SempClient` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `ActionResult` (e.g. with `Engine` and `TestInitCommand`) actually correct?**
  _`ActionResult` has 23 INFERRED edges - model-reasoned connections that need verification._