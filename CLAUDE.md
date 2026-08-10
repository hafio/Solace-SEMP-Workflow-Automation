# SEMP Workflow Automation

The implementation lives at the repository root (module `semp-workflow`). Run all
Go commands from the repo root.

## Project conventions

- Each action implements the `modules.Module` interface (`Execute`/`Description`/`Params`) and follows the idempotent pattern (check state -> skip/dryrun/act).
- Every module file registers its actions via `init()` calling `register("object.verb", ...)` in `internal/modules`.
- New modules need: table-driven unit tests in the same package (`internal/modules/*_test.go`, using the shared `fakeClient`), and an entry in `docs/HOWTO*.md` module tables.
- After adding/removing modules: update counts in README.md, docs/HOWTO*.md, docs/TESTS.md, and the `TestRegistryCompleteness` expected list.
- After param changes: regenerate `docs/all-modules.md` with `semp-workflow list-modules --output docs/all-modules.md` (or `go run ./cmd/semp-workflow list-modules --output docs/all-modules.md`).

## Build & test (run from the repo root)

- Build: `./scripts/dev.sh build` (`.\scripts\dev.ps1 build` on Windows) -> `dist/semp-workflow-<os>-<arch>[.exe]` (host os/arch unless `TARGET_OS`/`TARGET_ARCH` are set)
- Tests: `go test ./...` (or `./scripts/dev.sh test`)
- Coverage: `./scripts/dev.sh cov` -> printed total + `coverage.html`
- Security scan: `./scripts/dev.sh scan` -> `go tool govulncheck ./...` (govulncheck pinned as a go.mod `tool` directive; the `toolchain` directive pins Go, so it resolves through the module -- never `go run pkg@version`). Fatal on a fixable CVE.
- Integration tests (need a live broker): `go test -tags integration ./...` with `SEMP_HOST/SEMP_USERNAME/SEMP_PASSWORD/SEMP_MSG_VPN` set
- Validate examples: `semp-workflow validate -c examples/config.yaml -t examples/templates`
- Version is stamped at build time via `-ldflags "-X main.version=..."` -- no reinstall step.

## Documentation rules

- README.md: brief overview only, no technical details
- docs/HOWTO.md, docs/HOWTO-zh.md: full technical guide, use the `semp-workflow` binary exclusively
- Keep English and Chinese HOWTO files in sync
- docs/template-*.md: capture template workflow details, inputs, step by step workflow, and example usage.

## Style

- Don't add backwards-compat shims or unused-var renames
- Prefer editing existing files over creating new ones

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
