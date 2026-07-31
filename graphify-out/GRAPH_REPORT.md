# Graph Report - SEMP-Workflow_Automation  (2026-07-31)

## Corpus Check
- 60 files · ~47,525 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 717 nodes · 1754 edges · 42 communities (38 shown, 4 thin omitted)
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 489 edges (avg confidence: 0.8)
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
- Output Rendering Tests
- Integration Test Fixtures
- SEMP Workflow Automation — 操作指南
- SEMP Workflow Automation — How-To Guide
- RDP Consumer/Binding & Client
- SEMP Workflow Automation
- 10. Common Scenario Examples
- Base Module Abstraction
- 11. Troubleshooting
- integrationClient
- 7. CLI Commands
- 5. Configuration File
- Queue Binding Add Tests
- 6. Workflow Templates
- test.sh
- ACL Subscribe Exception Module
- Queue Delete Tests
- Action Dispatch
- Project Documentation
- README & SEMP Overview
- Package Root
- NewEngine
- newTestEngine
- .Execute
- rdp.go
- WorkflowResult
- aclSubscribeExceptionAdd
- queueBindingAdd

## God Nodes (most connected - your core abstractions)
1. `exec()` - 54 edges
2. `absent()` - 37 edges
3. `ActionResult` - 35 edges
4. `Enc()` - 35 edges
5. `ParamSpec` - 27 edges
6. `failed()` - 27 edges
7. `ok()` - 27 edges
8. `skipped()` - 27 edges
9. `dryrun()` - 27 edges
10. `argStr()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `NewEngine()` --calls--> `FS()`  [INFERRED]
  internal/engine/engine.go → templates/embed.go
- `newValidateCmd()` --calls--> `FS()`  [INFERRED]
  internal/cli/cli.go → templates/embed.go
- `newInitCmd()` --calls--> `FS()`  [INFERRED]
  internal/cli/cli.go → templates/embed.go
- `LoadTemplatesFS()` --references--> `FS()`  [EXTRACTED]
  internal/config/config.go → templates/embed.go
- `init()` --calls--> `register()`  [INFERRED]
  internal/modules/acl_pub_exc.go → internal/modules/registry.go

## Import Cycles
- None detected.

## Communities (42 total, 4 thin omitted)

### Community 0 - "Engine & Config Core"
Cohesion: 0.18
Nodes (27): T, runCLI(), TestInitCopiesBundledTemplates(), TestListModules(), TestListModulesWritesFile(), TestMissingConfigFlagIsUsageError(), TestRunConfigError(), TestRunTemplateNotFoundExit1() (+19 more)

### Community 1 - "Payload Helpers & Coercion"
Cohesion: 0.32
Nodes (22): CGO_ENABLED, load_local_env(), main(), NO_COLOR, run_logged(), dev.sh script, die(), ok() (+14 more)

### Community 2 - "CLI Command Tests"
Cohesion: 0.36
Nodes (18): Have(), Import-LocalEnv(), Invoke-Logged(), Die(), Ok(), Step(), Task-All(), Task-Build() (+10 more)

### Community 3 - "Jinja2 Templating Engine"
Cohesion: 0.21
Nodes (13): cfgInt(), TestCoerceBoolDefaultBranch(), CoerceBool(), CoerceInt(), isUnreserved(), Stringify(), T, TestCheckNameLength() (+5 more)

### Community 4 - "Queue & Subscription Modules"
Cohesion: 0.25
Nodes (3): init(), subscriptionAdd, subscriptionDelete

### Community 5 - "Client Profile Module"
Cohesion: 0.18
Nodes (11): Action Sequence, `delete` (7 actions), Delete the same resources, Dry-run then execute, Example Workflow Entry, Inputs, `new-seq` / `new-non-seq` (14 actions), Optional (with defaults) (+3 more)

### Community 6 - "RDP Modules & Tests"
Cohesion: 0.18
Nodes (11): Action Sequence, `delete` (6 actions), Delete the same resources, Dry-run then execute, Example Workflow Entry, Inputs, `new-seq` / `new-non-seq` (11 actions), Optional (with defaults) (+3 more)

### Community 7 - "Client Username Module"
Cohesion: 0.18
Nodes (4): init(), queueAdd, queueDelete, queueUpdate

### Community 8 - "SEMP Client Tests"
Cohesion: 0.20
Nodes (5): init(), register(), aclProfileAdd, aclProfileDelete, Module

### Community 9 - "ACL Profile Module"
Cohesion: 0.25
Nodes (3): init(), aclPublishExceptionAdd, aclPublishExceptionDelete

### Community 10 - "CLI Commands"
Cohesion: 0.64
Nodes (7): cleanupPaths(), Client, T, integrationClient(), TestIntegrationAccessControlLifecycle(), TestIntegrationQueueSubscriptionLifecycle(), TestIntegrationRdpLifecycle()

### Community 11 - "Template Loading"
Cohesion: 0.60
Nodes (4): T, TestNewActionResult(), TestWorkflowResultCounts(), TestWorkflowResultNoFailures()

### Community 15 - "SEMP Workflow Automation — 操作指南"
Cohesion: 0.05
Nodes (40): 10. 常見情境範例, 11. 故障排除, 1. 簡介, 2. 系統需求, 3. 開始使用, 4. 專案結構, 5.1 SEMP 連線設定, 5.2 全域變數（global_vars） (+32 more)

### Community 16 - "SEMP Workflow Automation — How-To Guide"
Cohesion: 0.20
Nodes (10): 1. Introduction, 2. Prerequisites, 3. Getting Started, 4. Project Structure, 8. Built-in Template Reference, 9. Available Modules, sap-inbound — SAP Inbound Workflows, sap-outbound — SAP Outbound Workflows (+2 more)

### Community 17 - "RDP Consumer/Binding & Client"
Cohesion: 0.09
Nodes (44): Buffer, Command, classifyExit(), Execute(), joinComma(), newInitCmd(), newListModulesCmd(), newRootCmd() (+36 more)

### Community 18 - "SEMP Workflow Automation"
Cohesion: 0.29
Nodes (6): Build & test (run from the repo root), Documentation rules, graphify, Project conventions, SEMP Workflow Automation, Style

### Community 19 - "10. Common Scenario Examples"
Cohesion: 0.29
Nodes (7): 10. Common Scenario Examples, Scenario 1: Create a single SAP outbound queue set, Scenario 2: Create a SAP inbound flow (queue + RDP + REST delivery), Scenario 3: Batch-create multiple workflows, Scenario 4: Centralise settings in global_vars, Scenario 5: Delete resources, Scenario 6: Sequential vs non-sequential delivery

### Community 20 - "Base Module Abstraction"
Cohesion: 0.10
Nodes (59): T, TestAclProfileDeleteBranches(), TestClientProfileDelete(), TestClientUsernameUpdateAppliesFields(), TestPublishExceptionAddBranches(), TestPublishExceptionDelete(), TestQueueBindingAddBranches(), TestQueueBindingDelete() (+51 more)

### Community 21 - "11. Troubleshooting"
Cohesion: 0.29
Nodes (7): 11. Troubleshooting, Dry-run best practice, Issue: Connection error, Issue: Required input not provided, Issue: Template not found, Issue: Unexpected inputs, Issue: Unresolved Jinja2 expression

### Community 22 - "integrationClient"
Cohesion: 0.57
Nodes (6): Client, T, integrationClient(), TestIntegrationConnection(), TestIntegrationExistsNotFound(), TestIntegrationQueueLifecycle()

### Community 23 - "7. CLI Commands"
Cohesion: 0.33
Nodes (6): 7.1 Run Workflows, 7.2 Validate Configuration, 7.3 List Available Modules, 7.4 Export Bundled Templates, 7. CLI Commands, Top-Level Help

### Community 24 - "5. Configuration File"
Cohesion: 0.40
Nodes (5): 5.1 SEMP Connection, 5.2 Global Variables (global_vars), 5.3 Workflow List (workflows), 5.4 Full Config Example, 5. Configuration File

### Community 25 - "Queue Binding Add Tests"
Cohesion: 0.07
Nodes (48): Duration, SEMPError, HandlerFunc, asSEMPError(), backoffDelay(), Request, Response, NewClient() (+40 more)

### Community 26 - "6. Workflow Templates"
Cohesion: 0.40
Nodes (5): 6. Workflow Templates, Input Schema, Two-Pass Rendering, Variable Rendering Rules, YAML Anchor Support

### Community 29 - "ACL Subscribe Exception Module"
Cohesion: 0.17
Nodes (30): NewActionResult(), Client, Client, Client, argStr(), coerceBoolFields(), coerceIntFields(), dryrun() (+22 more)

### Community 37 - "Queue Delete Tests"
Cohesion: 0.25
Nodes (3): init(), rdpRestConsumerAdd, rdpRestConsumerDelete

### Community 43 - "Action Dispatch"
Cohesion: 0.12
Nodes (17): ConfigError, TemplateError, ValidationError, WorkflowError, TestClassifyExit(), T, TestWorkflowAndValidationErrorMessages(), IsWorkflowError() (+9 more)

### Community 48 - "README & SEMP Overview"
Cohesion: 0.67
Nodes (3): SEMP Workflow Automation README, SEMP v2 REST API, Solace Broker

### Community 51 - "Package Root"
Cohesion: 0.22
Nodes (6): clientProfileParams(), init(), clientProfileAdd, clientProfileDelete, clientProfileUpdate, ParamSpec

### Community 57 - "NewEngine"
Cohesion: 0.17
Nodes (32): Config, T, TestRenderMalformedTemplateError(), TestRenderMapRecursionError(), TestRenderSliceRecursionError(), TestRenderUndefinedIndexBranch(), TestValidateInputsIntegerCoercionVariants(), TestValidateInputsOptionalSkipped() (+24 more)

### Community 59 - "newTestEngine"
Cohesion: 0.16
Nodes (24): Engine, engineFake, T, TestNewEngineBundledTemplates(), TestNewEngineMissingTemplatesDir(), TestResolveTemplateNotFoundListsAvailable(), TestRunFailFastStopsAfterFailedWorkflow(), TestRunFailFastStopsOnTemplateError() (+16 more)

### Community 62 - ".Execute"
Cohesion: 0.18
Nodes (4): init(), clientUsernameAdd, clientUsernameDelete, clientUsernameUpdate

### Community 68 - "rdp.go"
Cohesion: 0.18
Nodes (4): init(), rdpAdd, rdpDelete, rdpUpdate

### Community 75 - "WorkflowResult"
Cohesion: 0.09
Nodes (43): ActionSpec, AppConfig, SempConfig, WorkflowEntry, WorkflowTemplate, Engine, cfgBool(), cfgStr() (+35 more)

### Community 85 - "aclSubscribeExceptionAdd"
Cohesion: 0.25
Nodes (3): init(), aclSubscribeExceptionAdd, aclSubscribeExceptionDelete

### Community 87 - "queueBindingAdd"
Cohesion: 0.25
Nodes (3): init(), queueBindingAdd, queueBindingDelete

## Knowledge Gaps
- **96 isolated node(s):** `semp-workflow`, `Client`, `InputSpec`, `NO_COLOR`, `CGO_ENABLED` (+91 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Enc()` connect `ACL Subscribe Exception Module` to `Engine & Config Core`, `Jinja2 Templating Engine`, `CLI Commands`, `WorkflowResult`, `integrationClient`, `Queue Binding Add Tests`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `exec()` connect `Base Module Abstraction` to `CLI Commands`, `ACL Subscribe Exception Module`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `ActionResult` connect `ACL Subscribe Exception Module` to `RDP Consumer/Binding & Client`, `WorkflowResult`, `Base Module Abstraction`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `exec()` (e.g. with `TestAclProfileDeleteBranches()` and `TestClientProfileDelete()`) actually correct?**
  _`exec()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `absent()` (e.g. with `TestAclProfileDeleteBranches()` and `TestClientProfileDelete()`) actually correct?**
  _`absent()` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Enc()` (e.g. with `TestIntegrationCLIRun()` and `TestIntegrationEngineLifecycle()`) actually correct?**
  _`Enc()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `semp-workflow`, `Client`, `InputSpec` to the rest of the system?**
  _96 weakly-connected nodes found - possible documentation gaps or missing edges._