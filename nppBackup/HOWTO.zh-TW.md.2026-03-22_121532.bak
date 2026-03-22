# SEMP Workflow Automation — 操作指南

> 版本：0.2.0
> 適用平台：Solace PubSub+（SEMP v2）

---

## 目錄

1. [簡介](#1-簡介)
2. [系統需求](#2-系統需求)
3. [安裝](#3-安裝)
4. [專案結構](#4-專案結構)
5. [設定檔](#5-設定檔)
6. [工作流程範本](#6-工作流程範本)
7. [CLI 指令](#7-cli-指令)
8. [內建範本說明](#8-內建範本說明)
9. [可用模組](#9-可用模組)
10. [常見情境範例](#10-常見情境範例)
11. [故障排除](#11-故障排除)

---

## 1. 簡介

SEMP Workflow Automation 是一套類似 Ansible Playbook 的命令列工具，專為 Solace PubSub+ 訊息代理人（Message Broker）設計。透過宣告式 YAML 設定檔，您可以批次建立、刪除或更新佇列（Queue）、REST 遞送點（RDP）及其他 SEMP v2 資源，無需手動操作管理介面。

**主要特色：**
- 冪等操作（Idempotent）：每次執行前先檢查資源是否存在，避免重複建立
- Jinja2 變數渲染：支援動態命名與跨變數參考
- 試運行模式（Dry-run）：可預覽變更內容而不實際執行
- 模組化設計：每種 SEMP 資源對應獨立模組，易於擴充

---

## 2. 系統需求

| 需求項目 | 版本要求 |
|---|---|
| Python | 3.10 以上 |
| Solace PubSub+ Broker | 支援 SEMP v2 API 的版本 |
| 網路連線 | 可存取 Broker 的 SEMP 管理埠（預設 `8080` / `1943`） |

---

## 3. 安裝

**使用獨立執行檔（.zip）**

若收到 `semp-workflow.zip` 打包檔，其中已內建所有 Python 套件（`click`、`jinja2`、`requests`、`colorama` 等），目標機器只需有 Python 3.10 以上的直譯器，無需執行 `pip install`。
```bash
python semp-workflow.zip --help
```

初次使用時，可將內建範本匯出至本機目錄供自訂修改：
```bash
python semp-workflow.zip init --output-dir workflow-templates
```

---

## 4. 專案結構

```
專案目錄/
├── config.yaml               # 主設定檔（連線資訊 + 工作流程清單）
└── workflow-templates/       # 工作流程範本目錄
    ├── sap-inbound.yaml      # SAP 入站工作流程範本
    └── sap-outbound.yaml     # SAP 出站工作流程範本
```

- **`config.yaml`**：定義 SEMP 連線、全域變數（`global_vars`）及要執行的工作流程清單
- **`workflow-templates/`**：每個 YAML 檔包含一或多個具名範本，每個範本定義輸入變數與動作序列

---

## 5. 設定檔

`config.yaml` 分為三個主要區塊：

### 5.1 SEMP 連線設定

```yaml
semp:
  host: "https://broker.example.com:1943"
  username: "admin"
  password: "admin"
  msg_vpn: "default"
  verify_ssl: false   # 自簽憑證環境設為 false
  timeout: 30         # 秒
```

### 5.2 全域變數（global_vars）

全域變數可在所有工作流程的輸入欄位中透過 `{{ global_vars.變數名稱 }}` 引用，方便統一管理重複設定值。

```yaml
global_vars:
  topic_prefix: "FCM/SAP/AIF"
  default_queue_owner: "SAP_AIF_CLIENT"
  default_rc_remote_host: "my-backend.example.com"
```

### 5.3 工作流程清單（workflows）

每個工作流程條目指定要套用的範本以及輸入變數：

```yaml
workflows:
  - template: "sap-outbound.new-seq"    # 格式：檔名.範本名稱
    inputs:
      domain: "HQ"                       # 必填輸入
      system: "NATS"
      system_topic: "GCM.FIANA.LOT"
      # 選填輸入（移除 # 號可覆蓋範本預設值）：
      #service_queue_owner: "{{ global_vars.default_queue_owner }}"
```

> **注意**：範本參照格式為 `檔名.範本名稱`，例如 `sap-outbound.new-seq` 代表 `sap-outbound.yaml` 中名為 `new-seq` 的範本。

---

## 6. 工作流程範本

範本檔案定義可重複使用的工作流程，結構如下：

```yaml
workflow-templates:
  - name: "my-template"

    inputs:
      required:           # 必填輸入（未提供時報錯）
      - domain
      - system

      optional:           # 選填輸入（提供預設值）
        queue_name: "Q-{{ inputs.domain }}-{{ inputs.system }}"
        queue_owner: ""

    actions:
    - name: "建立佇列"
      module: "queue.add"
      args:
        queueName: "{{ inputs.queue_name }}"
        owner: "{{ inputs.queue_owner }}"
```

### 變數渲染規則

| 語法 | 用途 |
|---|---|
| `{{ inputs.變數名稱 }}` | 引用輸入變數 |
| `{{ global_vars.變數名稱 }}` | 引用全域變數（僅在預設值中使用） |
| `{{ inputs.a }}-{{ inputs.b }}` | 組合多個變數 |

### YAML 錨點（Anchor）支援

範本支援 YAML 錨點與別名，可共用輸入定義或動作清單：

```yaml
inputs:
  required: &required-vars
  - domain
  - system

# 另一個範本可重用：
inputs:
  required: *required-vars
```

---

## 7. CLI 指令

### 7.1 執行工作流程

```bash
semp-workflow run --config config.yaml
```

| 選項 | 簡寫 | 說明 |
|---|---|---|
| `--config` | `-c` | 設定檔路徑（必填） |
| `--templates-dir` | `-t` | 覆蓋範本目錄路徑 |
| `--dry-run` / `--check` | | 試運行：顯示將執行的操作，不實際變更 |
| `--fail-fast` | `-f` | 遇到第一個失敗即停止執行 |
| `--verbose` | `-v` | 顯示除錯日誌 |

**範例：**
```bash
# 試運行（不實際執行）
semp-workflow run -c config.yaml --dry-run

# 遇錯即停，並顯示詳細日誌
semp-workflow run -c config.yaml --fail-fast --verbose

# 使用自訂範本目錄
semp-workflow run -c config.yaml --templates-dir ./my-templates
```

### 7.2 驗證設定檔

驗證設定檔與範本的格式正確性，不執行任何操作：

```bash
semp-workflow validate --config config.yaml
```

### 7.3 列出所有可用模組

```bash
semp-workflow list-modules

# 匯出模組文件為 Markdown 檔案
semp-workflow list-modules --output all-modules.md
```

### 7.4 匯出內建範本

（僅在使用 `.zip` 打包檔時可用）

```bash
python semp-workflow.zip init --output-dir workflow-templates

# 強制覆蓋已存在的檔案
python semp-workflow.zip init --output-dir workflow-templates --force
```

---

## 8. 內建範本說明

### sap-outbound — SAP 出站工作流程

訊息流向：Solace → SAP（Broker 接收訊息後轉送至下游）

| 範本 | 說明 |
|---|---|
| `sap-outbound.new-seq` | 建立循序遞送佇列組合（Service Queue + Mirror Queue + DMQ + 訂閱） |
| `sap-outbound.new-non-seq` | 建立並發遞送佇列組合（與 new-seq 相同結構，預設重遞送次數不同） |
| `sap-outbound.delete` | 刪除出站佇列組合 |

**必填輸入：**

| 變數 | 說明 | 範例 |
|---|---|---|
| `domain` | 業務領域 | `HQ` |
| `system` | 系統名稱 | `NATS` |
| `system_topic` | 主題識別碼 | `GCM.FIANA.LOT-COST` |

---

### sap-inbound — SAP 入站工作流程

訊息流向：SAP → Solace → 後端 REST 服務

| 範本 | 說明 |
|---|---|
| `sap-inbound.new-seq` | 建立循序入站流程（佇列組合 + RDP + REST Consumer + Queue Binding），訂閱主題格式：`domain/system/topic` |
| `sap-inbound.new-non-seq` | 建立並發入站流程，訂閱主題格式：`topic_prefix/topic` |
| `sap-inbound.delete` | 刪除入站資源（先刪 RDP，再刪佇列） |

**必填輸入：**

| 變數 | 說明 | 範例 |
|---|---|---|
| `domain` | 業務領域 | `HQ` |
| `system` | 系統名稱 | `SAP` |
| `system_topic` | 主題識別碼 | `GCM.FIANA.LOT-COST` |

> 所有選填輸入均有預設值，可在 `config.yaml` 工作流程條目中覆蓋。完整選填參數清單請參閱範本檔案中的 `optional:` 區塊。

---

## 9. 可用模組

所有操作均為**冪等**（Idempotent）：執行前先檢查資源狀態，若已是目標狀態則跳過（`skipped`）。

| 模組 | 說明 |
|---|---|
| `queue.add` | 建立佇列 |
| `queue.delete` | 刪除佇列 |
| `queue.update` | 更新佇列屬性 |
| `q_sub.add` | 新增佇列訂閱主題 |
| `q_sub.delete` | 移除佇列訂閱主題 |
| `rdp.add` | 建立 REST Delivery Point |
| `rdp.delete` | 刪除 REST Delivery Point |
| `rdp.update` | 更新 REST Delivery Point |
| `rdp_rc.add` | 新增 REST Consumer 至 RDP |
| `rdp_rc.delete` | 移除 RDP 的 REST Consumer |
| `rdp_qb.add` | 建立佇列與 RDP 的繫結（Queue Binding） |
| `rdp_qb.delete` | 移除佇列繫結 |
| `acl_profile.add` | 建立 ACL Profile |
| `acl_profile.delete` | 刪除 ACL Profile |
| `client_profile.add` | 建立 Client Profile |
| `client_profile.delete` | 刪除 Client Profile |
| `client_username.add` | 建立 Client Username |
| `client_username.delete` | 刪除 Client Username |

**執行結果狀態：**

| 狀態 | 說明 |
|---|---|
| `changed` | 資源已成功建立／變更 |
| `skipped` | 資源已存在，無需變更 |
| `dryrun` | 試運行模式，顯示將執行的操作 |
| `failed` | 操作失敗 |

完整參數說明請執行 `semp-workflow list-modules` 或參閱 `all-modules.md`。

---

## 10. 常見情境範例

### 情境一：建立單一 SAP 出站佇列組合

```yaml
# config.yaml
semp:
  host: "https://broker.example.com:1943"
  username: "admin"
  password: "admin"
  msg_vpn: "default"
  verify_ssl: false

global_vars:
  topic_prefix: "FCM/SAP/AIF"

workflows:
  - template: "sap-outbound.new-seq"
    inputs:
      domain: "HQ"
      system: "NATS"
      system_topic: "GCM.FIANA.LOT-TURNKEY-COST"
```

```bash
# 試運行確認
semp-workflow run -c config.yaml --dry-run

# 確認無誤後正式執行
semp-workflow run -c config.yaml
```

---

### 情境二：批次建立多個工作流程

在 `config.yaml` 的 `workflows` 清單中加入多個條目即可批次執行：

```yaml
workflows:
  - template: "sap-outbound.new-seq"
    inputs:
      domain: "HQ"
      system: "NATS"
      system_topic: "ORDER.CREATE"

  - template: "sap-outbound.new-seq"
    inputs:
      domain: "HQ"
      system: "NATS"
      system_topic: "ORDER.UPDATE"

  - template: "sap-inbound.new-non-seq"
    inputs:
      domain: "HQ"
      system: "SAP"
      system_topic: "ORDER.CONFIRM"
      rc_remote_host: "sap-backend.internal"
      rc_remote_port: 443
      rc_tls_enabled: true
```

---

### 情境三：使用全域變數統一管理後端連線

```yaml
global_vars:
  default_rc_remote_host: "sap-backend.internal"
  default_rc_remote_port: 443
  default_rc_tls_enabled: true
  default_queue_owner: "SAP_AIF_CLIENT"

workflows:
  - template: "sap-inbound.new-non-seq"
    inputs:
      domain: "HQ"
      system: "SAP"
      system_topic: "GCM.FIANA.LOT-COST"
      rc_remote_host: "{{ global_vars.default_rc_remote_host }}"
      rc_remote_port: "{{ global_vars.default_rc_remote_port }}"
      rc_tls_enabled: "{{ global_vars.default_rc_tls_enabled }}"
      service_queue_owner: "{{ global_vars.default_queue_owner }}"
```

---

### 情境四：刪除資源

```yaml
workflows:
  - template: "sap-inbound.delete"
    inputs:
      domain: "HQ"
      system: "SAP"
      system_topic: "GCM.FIANA.LOT-COST"
```

> **注意**：入站刪除範本會先刪除 RDP，再刪除佇列，順序正確避免資源殘留。

---

## 11. 故障排除

### 問題：找不到範本（Template not found）

```
TemplateError: Template 'sap-outbound.new-seq' not found.
```

**原因與解決方式：**
- 確認 `config.yaml` 中的 `templates_dir` 路徑正確（相對於 config.yaml 所在目錄）
- 確認範本目錄中確實存在 `sap-outbound.yaml`
- 若使用 `.zip` 打包檔且無外部範本目錄，請執行 `python semp-workflow.zip init` 匯出內建範本

---

### 問題：未提供必填輸入（Required input not provided）

```
TemplateError: Required input 'domain' not provided
```

**解決方式：** 在 `config.yaml` 工作流程的 `inputs:` 區塊中補上缺少的必填變數。

---

### 問題：未預期的輸入變數（Unexpected inputs）

```
TemplateError: Unexpected inputs: my_typo_var
```

**解決方式：** 確認輸入變數名稱拼寫正確，需與範本 `optional:` 區塊中定義的名稱完全相符。

---

### 問題：連線失敗（Connection error）

```
SEMPError: Connection refused / SSL error
```

**解決方式：**
- 確認 `semp.host` URL 格式正確（含通訊協定 `https://` 及正確埠號）
- 自簽憑證環境請設定 `verify_ssl: false`
- 確認帳號密碼正確，且有 Message VPN 的管理權限

---

### 問題：變數未解析（Unresolved Jinja2 expression）

```
WorkflowError: Input 'queue_name' still contains an unresolved Jinja2 expression
```

**解決方式：**
- 確認引用的輸入變數已存在（無誤字）
- 避免循環引用（如 A 的預設值引用 B，B 的預設值又引用 A）

---

### 試運行模式

在執行任何變更前，強烈建議先使用試運行模式確認操作內容：

```bash
semp-workflow run -c config.yaml --dry-run --verbose
```
