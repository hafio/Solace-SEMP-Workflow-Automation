# Graph Report - SEMP-Workflow_Automation  (2026-07-31)

## Corpus Check
- 57 files · ~41,611 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 628 nodes · 1664 edges · 32 communities (28 shown, 4 thin omitted)
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 489 edges (avg confidence: 0.8)
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
- RDP Consumer/Binding & Client
- Base Module Abstraction
- Queue Binding Add Tests
- ACL Subscribe Exception Module
- Queue Delete Tests
- Action Dispatch
- Project Documentation
- README & SEMP Overview
- Test Shell Script
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

## Communities (32 total, 4 thin omitted)

### Community 0 - "Engine & Config Core"
Cohesion: 0.17
Nodes (28): T, runCLI(), TestClassifyExit(), TestInitCopiesBundledTemplates(), TestListModules(), TestListModulesWritesFile(), TestMissingConfigFlagIsUsageError(), TestRunConfigError() (+20 more)

### Community 1 - "Payload Helpers & Coercion"
Cohesion: 0.32
Nodes (22): CGO_ENABLED, load_local_env(), main(), NO_COLOR, run_logged(), dev.sh script, die(), ok() (+14 more)

### Community 2 - "CLI Command Tests"
Cohesion: 0.36
Nodes (18): Have(), Import-LocalEnv(), Invoke-Logged(), Die(), Ok(), Step(), Task-All(), Task-Build() (+10 more)

### Community 3 - "Jinja2 Templating Engine"
Cohesion: 0.24
Nodes (11): cfgInt(), CoerceInt(), isUnreserved(), Stringify(), T, TestCheckNameLength(), TestCleanPayload(), TestCoerceBool() (+3 more)

### Community 4 - "Queue & Subscription Modules"
Cohesion: 0.25
Nodes (3): init(), subscriptionAdd, subscriptionDelete

### Community 5 - "Client Profile Module"
Cohesion: 0.17
Nodes (11): Action Sequence, `delete` (7 actions), Delete the same resources, Dry-run then execute, Example Workflow Entry, Inputs, `new-seq` / `new-non-seq` (14 actions), Optional (with defaults) (+3 more)

### Community 6 - "RDP Modules & Tests"
Cohesion: 0.17
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

### Community 17 - "RDP Consumer/Binding & Client"
Cohesion: 0.09
Nodes (44): Buffer, Command, classifyExit(), Execute(), joinComma(), newInitCmd(), newListModulesCmd(), newRootCmd() (+36 more)

### Community 20 - "Base Module Abstraction"
Cohesion: 0.10
Nodes (59): T, TestAclProfileDeleteBranches(), TestClientProfileDelete(), TestClientUsernameUpdateAppliesFields(), TestPublishExceptionAddBranches(), TestPublishExceptionDelete(), TestQueueBindingAddBranches(), TestQueueBindingDelete() (+51 more)

### Community 25 - "Queue Binding Add Tests"
Cohesion: 0.07
Nodes (54): Duration, HandlerFunc, asSEMPError(), backoffDelay(), Request, Response, NewClient(), Client (+46 more)

### Community 29 - "ACL Subscribe Exception Module"
Cohesion: 0.17
Nodes (30): NewActionResult(), Client, Client, Client, argStr(), coerceBoolFields(), coerceIntFields(), dryrun() (+22 more)

### Community 37 - "Queue Delete Tests"
Cohesion: 0.25
Nodes (3): init(), rdpRestConsumerAdd, rdpRestConsumerDelete

### Community 43 - "Action Dispatch"
Cohesion: 0.11
Nodes (17): ConfigError, SEMPError, TemplateError, ValidationError, WorkflowError, T, TestWorkflowAndValidationErrorMessages(), IsWorkflowError() (+9 more)

### Community 48 - "README & SEMP Overview"
Cohesion: 0.67
Nodes (3): SEMP Workflow Automation README, SEMP v2 REST API, Solace Broker

### Community 51 - "Package Root"
Cohesion: 0.22
Nodes (6): clientProfileParams(), init(), clientProfileAdd, clientProfileDelete, clientProfileUpdate, ParamSpec

### Community 57 - "NewEngine"
Cohesion: 0.17
Nodes (32): Config, CoerceBool(), T, TestRenderMalformedTemplateError(), TestRenderMapRecursionError(), TestRenderSliceRecursionError(), TestRenderUndefinedIndexBranch(), TestValidateInputsIntegerCoercionVariants() (+24 more)

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
Nodes (44): ActionSpec, AppConfig, SempConfig, WorkflowEntry, WorkflowTemplate, Engine, cfgBool(), cfgStr() (+36 more)

### Community 85 - "aclSubscribeExceptionAdd"
Cohesion: 0.25
Nodes (3): init(), aclSubscribeExceptionAdd, aclSubscribeExceptionDelete

### Community 87 - "queueBindingAdd"
Cohesion: 0.25
Nodes (3): init(), queueBindingAdd, queueBindingDelete

## Knowledge Gaps
- **25 isolated node(s):** `semp-workflow`, `Client`, `InputSpec`, `NO_COLOR`, `CGO_ENABLED` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Enc()` connect `ACL Subscribe Exception Module` to `Engine & Config Core`, `Jinja2 Templating Engine`, `CLI Commands`, `WorkflowResult`, `Queue Binding Add Tests`?**
  _High betweenness centrality (0.177) - this node is a cross-community bridge._
- **Why does `exec()` connect `Base Module Abstraction` to `CLI Commands`, `ACL Subscribe Exception Module`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Why does `ActionResult` connect `ACL Subscribe Exception Module` to `RDP Consumer/Binding & Client`, `WorkflowResult`, `Base Module Abstraction`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `exec()` (e.g. with `TestAclProfileDeleteBranches()` and `TestClientProfileDelete()`) actually correct?**
  _`exec()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `absent()` (e.g. with `TestAclProfileDeleteBranches()` and `TestClientProfileDelete()`) actually correct?**
  _`absent()` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Enc()` (e.g. with `TestIntegrationCLIRun()` and `TestIntegrationEngineLifecycle()`) actually correct?**
  _`Enc()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `semp-workflow`, `Client`, `InputSpec` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._