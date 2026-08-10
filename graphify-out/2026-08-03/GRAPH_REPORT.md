# Graph Report - SEMP-Workflow_Automation  (2026-08-03)

## Corpus Check
- 60 files · ~50,900 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 728 nodes · 1748 edges · 41 communities (36 shown, 5 thin omitted)
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 489 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bfb1c7df`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- runCLI
- dev.sh
- dev.ps1
- newTestEngine
- subscriptionAdd
- Template: `sap-inbound`
- Template: `sap-outbound`
- queue.go
- register
- aclPublishExceptionAdd
- integrationClient
- models_test.go
- Test Documentation
- semp-workflow
- SEMP Workflow Automation — 操作指南
- SEMP Workflow Automation — How-To Guide
- capture
- SEMP Workflow Automation
- 10. 常見情境範例
- exec
- 11. 故障排除
- integrationClient
- WorkflowResult
- 7. CLI 指令
- newTestClient
- 5. 設定檔
- HOWTO.md
- test.sh
- Enc
- 6. 工作流程範本
- rdp_rc.go
- NewTemplateError
- SEMP Workflow Automation README
- ParamSpec
- NewEngine
- LoadConfig
- client_username.go
- rdp.go
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

## Communities (41 total, 5 thin omitted)

### Community 0 - "runCLI"
Cohesion: 0.18
Nodes (27): T, runCLI(), TestInitCopiesBundledTemplates(), TestListModules(), TestListModulesWritesFile(), TestMissingConfigFlagIsUsageError(), TestRunConfigError(), TestRunTemplateNotFoundExit1() (+19 more)

### Community 1 - "dev.sh"
Cohesion: 0.21
Nodes (25): CGO_ENABLED, load_local_env(), main(), NO_COLOR, _report_only(), _run(), run_logged(), dev.sh script (+17 more)

### Community 2 - "dev.ps1"
Cohesion: 0.26
Nodes (20): Get-BinPath(), Have(), Import-LocalEnv(), Invoke-Logged(), Invoke-Task(), Ok(), Step(), Task-All() (+12 more)

### Community 3 - "newTestEngine"
Cohesion: 0.09
Nodes (40): ActionSpec, AppConfig, SempConfig, WorkflowEntry, WorkflowTemplate, Engine, Engine, engineFake (+32 more)

### Community 4 - "subscriptionAdd"
Cohesion: 0.25
Nodes (3): init(), subscriptionAdd, subscriptionDelete

### Community 5 - "Template: `sap-inbound`"
Cohesion: 0.18
Nodes (11): Action Sequence, `delete` (7 actions), Delete the same resources, Dry-run then execute, Example Workflow Entry, Inputs, `new-seq` / `new-non-seq` (14 actions), Optional (with defaults) (+3 more)

### Community 6 - "Template: `sap-outbound`"
Cohesion: 0.18
Nodes (11): Action Sequence, `delete` (6 actions), Delete the same resources, Dry-run then execute, Example Workflow Entry, Inputs, `new-seq` / `new-non-seq` (11 actions), Optional (with defaults) (+3 more)

### Community 7 - "queue.go"
Cohesion: 0.18
Nodes (4): init(), queueAdd, queueDelete, queueUpdate

### Community 8 - "register"
Cohesion: 0.20
Nodes (5): init(), register(), aclProfileAdd, aclProfileDelete, Module

### Community 9 - "aclPublishExceptionAdd"
Cohesion: 0.25
Nodes (3): init(), aclPublishExceptionAdd, aclPublishExceptionDelete

### Community 10 - "integrationClient"
Cohesion: 0.64
Nodes (7): cleanupPaths(), Client, T, integrationClient(), TestIntegrationAccessControlLifecycle(), TestIntegrationQueueSubscriptionLifecycle(), TestIntegrationRdpLifecycle()

### Community 11 - "models_test.go"
Cohesion: 0.60
Nodes (4): T, TestNewActionResult(), TestWorkflowResultCounts(), TestWorkflowResultNoFailures()

### Community 15 - "SEMP Workflow Automation — 操作指南"
Cohesion: 0.17
Nodes (12): 1. 簡介, 2. 系統需求, 3. 開始使用, 4. 專案結構, 8. 內建範本說明, 9. 可用模組, sap-inbound — SAP 入站工作流程, sap-outbound — SAP 出站工作流程 (+4 more)

### Community 16 - "SEMP Workflow Automation — How-To Guide"
Cohesion: 0.05
Nodes (42): 10. Common Scenario Examples, 11. Troubleshooting, 1. Introduction, 2. Prerequisites, 3. Getting Started, 4. Project Structure, 5.1 SEMP Connection, 5.2 Global Variables (global_vars) (+34 more)

### Community 17 - "capture"
Cohesion: 0.09
Nodes (44): Buffer, Command, classifyExit(), Execute(), joinComma(), newInitCmd(), newListModulesCmd(), newRootCmd() (+36 more)

### Community 18 - "SEMP Workflow Automation"
Cohesion: 0.29
Nodes (6): Build & test (run from the repo root), Documentation rules, graphify, Project conventions, SEMP Workflow Automation, Style

### Community 19 - "10. 常見情境範例"
Cohesion: 0.29
Nodes (7): 10. 常見情境範例, 情境一：建立單一 SAP 出站佇列組合, 情境三：批次建立多個工作流程, 情境二：建立 SAP 入站流程（佇列 + RDP + REST 遞送）, 情境五：刪除資源, 情境六：循序遞送 vs 並發遞送, 情境四：使用全域變數統一管理設定

### Community 20 - "exec"
Cohesion: 0.10
Nodes (59): T, TestAclProfileDeleteBranches(), TestClientProfileDelete(), TestClientUsernameUpdateAppliesFields(), TestPublishExceptionAddBranches(), TestPublishExceptionDelete(), TestQueueBindingAddBranches(), TestQueueBindingDelete() (+51 more)

### Community 21 - "11. 故障排除"
Cohesion: 0.29
Nodes (7): 11. 故障排除, 問題：找不到範本（Template not found）, 問題：未提供必填輸入（Required input not provided）, 問題：未預期的輸入變數（Unexpected inputs）, 問題：變數未解析（Unresolved Jinja2 expression）, 問題：連線失敗（Connection error）, 試運行模式

### Community 22 - "integrationClient"
Cohesion: 0.57
Nodes (6): Client, T, integrationClient(), TestIntegrationConnection(), TestIntegrationExistsNotFound(), TestIntegrationQueueLifecycle()

### Community 24 - "7. CLI 指令"
Cohesion: 0.33
Nodes (6): 7.1 執行工作流程, 7.2 驗證設定檔, 7.3 列出所有可用模組, 7.4 匯出內建範本, 7. CLI 指令, 頂層說明

### Community 25 - "newTestClient"
Cohesion: 0.07
Nodes (49): Duration, SEMPError, HandlerFunc, asSEMPError(), backoffDelay(), Request, Response, NewClient() (+41 more)

### Community 26 - "5. 設定檔"
Cohesion: 0.40
Nodes (5): 5.1 SEMP 連線設定, 5.2 全域變數（global_vars）, 5.3 工作流程清單（workflows）, 5.4 完整設定檔範例, 5. 設定檔

### Community 29 - "Enc"
Cohesion: 0.16
Nodes (31): NewActionResult(), Client, Client, Client, argStr(), coerceBoolFields(), coerceIntFields(), dryrun() (+23 more)

### Community 30 - "6. 工作流程範本"
Cohesion: 0.40
Nodes (5): 6. 工作流程範本, YAML 錨點（Anchor）支援, 兩階段渲染說明, 變數渲染規則, 輸入結構

### Community 37 - "rdp_rc.go"
Cohesion: 0.25
Nodes (3): init(), rdpRestConsumerAdd, rdpRestConsumerDelete

### Community 43 - "NewTemplateError"
Cohesion: 0.12
Nodes (17): ConfigError, TemplateError, ValidationError, WorkflowError, TestClassifyExit(), T, TestWorkflowAndValidationErrorMessages(), IsWorkflowError() (+9 more)

### Community 48 - "SEMP Workflow Automation README"
Cohesion: 0.67
Nodes (3): SEMP Workflow Automation README, SEMP v2 REST API, Solace Broker

### Community 51 - "ParamSpec"
Cohesion: 0.22
Nodes (6): clientProfileParams(), init(), clientProfileAdd, clientProfileDelete, clientProfileUpdate, ParamSpec

### Community 57 - "NewEngine"
Cohesion: 0.17
Nodes (32): Config, CoerceBool(), T, TestRenderMalformedTemplateError(), TestRenderMapRecursionError(), TestRenderSliceRecursionError(), TestRenderUndefinedIndexBranch(), TestValidateInputsIntegerCoercionVariants() (+24 more)

### Community 59 - "LoadConfig"
Cohesion: 0.12
Nodes (37): cfgInt(), cfgStr(), LoadConfig(), LoadTemplatesFS(), T, TestLoadConfigMissingFile(), TestLoadConfigMissingSemp(), TestLoadConfigMissingSempKey() (+29 more)

### Community 62 - "client_username.go"
Cohesion: 0.18
Nodes (4): init(), clientUsernameAdd, clientUsernameDelete, clientUsernameUpdate

### Community 68 - "rdp.go"
Cohesion: 0.18
Nodes (4): init(), rdpAdd, rdpDelete, rdpUpdate

### Community 85 - "aclSubscribeExceptionAdd"
Cohesion: 0.25
Nodes (3): init(), aclSubscribeExceptionAdd, aclSubscribeExceptionDelete

### Community 87 - "queueBindingAdd"
Cohesion: 0.25
Nodes (3): init(), queueBindingAdd, queueBindingDelete

## Knowledge Gaps
- **97 isolated node(s):** `semp-workflow`, `Client`, `InputSpec`, `NO_COLOR`, `CGO_ENABLED` (+92 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Enc()` connect `Enc` to `runCLI`, `newTestEngine`, `integrationClient`, `integrationClient`, `newTestClient`, `LoadConfig`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `exec()` connect `exec` to `integrationClient`, `Enc`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `ActionResult` connect `Enc` to `capture`, `newTestEngine`, `exec`, `WorkflowResult`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `exec()` (e.g. with `TestAclProfileDeleteBranches()` and `TestClientProfileDelete()`) actually correct?**
  _`exec()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `absent()` (e.g. with `TestAclProfileDeleteBranches()` and `TestClientProfileDelete()`) actually correct?**
  _`absent()` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Enc()` (e.g. with `TestIntegrationCLIRun()` and `TestIntegrationEngineLifecycle()`) actually correct?**
  _`Enc()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **What connects `semp-workflow`, `Client`, `InputSpec` to the rest of the system?**
  _97 weakly-connected nodes found - possible documentation gaps or missing edges._