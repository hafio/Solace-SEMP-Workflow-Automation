# SEMP Workflow Automation

Ansible-style workflow automation for [Solace](https://solace.com/) brokers via the SEMP v2 REST API.

Define reusable, parameterised workflows in YAML and run them against your broker -- every action is idempotent, so re-running the same workflow is always safe.

---

## What It Does

- Batch-create, update, or delete queues, REST Delivery Points, subscriptions, ACL profiles, client profiles, and client usernames
- Preview changes with dry-run mode before touching the broker
- Use Jinja2 templates and global variables to build dynamic, reusable workflows
- Run multiple workflows in a single execution with shared configuration

---

## How It Works

1. You write a **config file** (`config.yaml`) with your broker connection and a list of workflows
2. You write **template files** (`.yaml`) that describe what actions to perform (create queue, add subscription, etc.)
3. You run the tool -- it connects to the broker, checks current state, and only makes the changes needed

All 24 built-in modules are idempotent: if a resource already exists, the action is skipped. If it doesn't exist, it's created. Re-running is always safe.

---

## Quick Start

A single self-contained binary -- the workflow templates are embedded, so there are no runtime dependencies.

Build it (requires Go 1.24+):

```bash
./scripts/dev.sh build        # -> dist/semp-workflow   (Windows: .\scripts\dev.ps1 build)
```

Then run it:

```bash
# See available commands
semp-workflow --help

# Export bundled templates for customisation
semp-workflow init --output-dir templates

# Validate config without connecting to the broker
semp-workflow validate --config config.yaml

# Preview what would change
semp-workflow run --config config.yaml --dry-run

# Execute
semp-workflow run --config config.yaml
```

---

## Documentation

For full technical details -- configuration reference, template authoring, module parameters, examples, and troubleshooting -- see the **[How-To Guide](docs/HOWTO.md)**.

| Document | Contents |
|---|---|
| [docs/HOWTO.md](docs/HOWTO.md) | Full technical guide: configuration, templates, modules, and troubleshooting |
| [docs/HOWTO-zh.md](docs/HOWTO-zh.md) | Chinese translation of the How-To guide |
| [docs/all-modules.md](docs/all-modules.md) | Auto-generated module parameter reference |
| [docs/TESTS.md](docs/TESTS.md) | Test suite overview, layout, and module registry |
| [docs/template-sap-inbound.md](docs/template-sap-inbound.md) | `sap-inbound` template: inputs, action sequence, examples |
| [docs/template-sap-outbound.md](docs/template-sap-outbound.md) | `sap-outbound` template: inputs, action sequence, examples |
| [docs/release.md](docs/release.md) | Release process and versioning scheme |
