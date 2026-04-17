# SEMP Workflow Automation

Ansible-style workflow automation for [Solace](https://solace.com/) brokers via the SEMP v2 REST API.

Define reusable, parameterised workflows in YAML and run them against your broker — every action is idempotent, so re-running the same workflow is always safe.

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
3. You run the tool — it connects to the broker, checks current state, and only makes the changes needed

All 24 built-in modules are idempotent: if a resource already exists, the action is skipped. If it doesn't exist, it's created. Re-running is always safe.

---

## Quick Start

Requires Python 3.10+. The `.zip` bundle is self-contained — no `pip install` needed.

```bash
# See available commands
python semp-workflow.zip --help

# Export bundled templates for customisation
python semp-workflow.zip init --output-dir templates

# Validate config without connecting to the broker
python semp-workflow.zip validate --config config.yaml

# Preview what would change
python semp-workflow.zip run --config config.yaml --dry-run

# Execute
python semp-workflow.zip run --config config.yaml
```

---

## Documentation

For full technical details — configuration reference, template authoring, module parameters, examples, and troubleshooting — see the **[How-To Guide](docs/HOWTO.md)**.

| Document | Contents |
|---|---|
| [docs/HOWTO.md](docs/HOWTO.md) | Complete technical guide (English) |
| [docs/HOWTO-zh.md](docs/HOWTO-zh.md) | Complete technical guide (Chinese) |
| [docs/all-modules.md](docs/all-modules.md) | Auto-generated module parameter reference |
