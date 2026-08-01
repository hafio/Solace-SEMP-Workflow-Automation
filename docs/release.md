# Release Process

How to cut a new release of `semp-workflow` (Go implementation).

---

## Versioning Scheme

The version is **not** stored in a source file — it is stamped into the binary
at build time via linker flags:

```bash
go build -ldflags "-X main.version=0.4.0+20260520" ./cmd/semp-workflow
```

`main.version` defaults to `0.0.0-dev` for unversioned `go run` / plain builds.
The dev scripts read the version from the `SEMP_WF_VERSION` environment variable
(default `0.0.0-dev`).

Format: `MAJOR.MINOR.PATCH+YYYYMMDD`

- `MAJOR.MINOR.PATCH` follows [Semantic Versioning](https://semver.org/):
  - **MAJOR** — breaking changes to config/template format or CLI
  - **MINOR** — new modules, templates, or backwards-compatible features
  - **PATCH** — bug fixes, documentation
- `+YYYYMMDD` is the build date. Bump it on any re-build, even without a version bump.

Git tags use the format `vMAJOR.MINOR.PATCH` (no date, no `+` suffix):

```
v0.2.1
v0.2.2
v0.3.0
```

---

## Release Checklist

All commands run from the repo root unless noted.

### 1. Run the test suite

```bash
go test ./...
# or: ./scripts/dev.sh test
```

All tests must pass. If a broker is available, also run the integration suite:

```bash
SEMP_HOST=... SEMP_USERNAME=... SEMP_PASSWORD=... SEMP_MSG_VPN=... \
  go test -tags integration ./...
```

### 2. Run vet, lint, and the vulnerability scan

```bash
./scripts/dev.sh vet lint vuln
```

### 3. Regenerate documentation

If any modules or parameters changed, regenerate the module reference from the
binary:

```bash
go run ./cmd/semp-workflow list-modules --output docs/all-modules.md
```

Also update counts in:
- [README.md](../README.md) -- "All N built-in modules"
- [docs/HOWTO.md](HOWTO.md) + [docs/HOWTO-zh.md](HOWTO-zh.md) — module tables
- [docs/TESTS.md](TESTS.md) — test count, module count, registry table

### 4. Build the release binary

```bash
SEMP_WF_VERSION="0.4.0+20260520" ./scripts/dev.sh build
# -> dist/semp-workflow   (Windows: .\scripts\dev.ps1 build -> dist\semp-workflow.exe)
```

Smoke-test the binary:

```bash
./dist/semp-workflow --version
# semp-workflow, version 0.4.0+20260520
./dist/semp-workflow list-modules
```

### 5. Commit the release

```bash
git add docs/all-modules.md README.md docs/HOWTO.md docs/HOWTO-zh.md docs/TESTS.md
git commit -m "Release v0.4.0"
```

### 6. Tag the release

```bash
git tag -a v0.4.0 -m "Release v0.4.0"
git push origin main
git push origin v0.4.0
```

### 7. Create the GitHub release (binaries publish automatically)

Create the tag and the GitHub Release -- do NOT attach binaries by hand.
Publishing the release triggers
[.github/workflows/release.yml](../.github/workflows/release.yml) -- the
repository's sole CI workflow. It first runs the full gate on the tagged source
(`go vet`, the test suite with coverage, `golangci-lint`, and a `govulncheck`
scan), then cross-compiles all six targets, writes a `SHA256SUMS` file, and
uploads the seven assets to that release. The publish is all-or-nothing: any
gate failure -- a failing test, vet, or lint, or a known, reachable
vulnerability in the tagged source -- blocks the build and upload entirely:

```bash
git tag -a v0.4.0 -m "Release v0.4.0"
git push origin v0.4.0

# Create + publish the release for the tag (the GitHub UI works too). No files
# are needed -- the workflow attaches them on `release: published`.
gh release create v0.4.0 --title "v0.4.0" --notes "Summary of changes..."
```

The workflow stamps `main.version` from the tag name verbatim, so a released
binary reports its version as e.g. `v0.4.0` -- distinct from the local
`SEMP_WF_VERSION` `MAJOR.MINOR.PATCH+YYYYMMDD` convention above, which applies
only to hand-built binaries. Downloaders verify integrity with
`sha256sum -c SHA256SUMS`.

To build the same six binaries locally -- offline, or to sanity-check before
tagging -- use the `release` task. It does NOT upload anything:

```bash
SEMP_WF_VERSION="0.4.0+20260520" ./scripts/dev.sh release   # Windows: .\scripts\dev.ps1 release
# -> dist/semp-workflow_{linux,darwin,windows}_{amd64,arm64}[.exe]   (6 binaries)
```

To reproduce the release gate locally before tagging, run `./scripts/dev.sh full`
(build vet test cov vuln) and `./scripts/dev.sh lint` -- the same commands the
workflow runs on the tagged source.

---

## Tag Naming Conventions

- Correct: `v0.4.0`
- Incorrect: `0.4.0`, `v.0.4.0`, `release-0.4.0`

One past tag (`v.0.2.2`) uses an unusual `v.` prefix — leave it as-is for historical continuity, but use `v0.X.Y` going forward.

---

## Common Commands

| Purpose | Command |
|---|---|
| List all tags | `git tag --list` |
| Show tag details | `git show v0.4.0` |
| Delete a local tag (mistyped) | `git tag -d v0.4.0` |
| Delete a remote tag | `git push origin --delete v0.4.0` |
| Check built version | `./dist/semp-workflow --version` |
| Rebuild | `SEMP_WF_VERSION="0.4.0+20260520" ./scripts/dev.sh build` |
| Cross-compile all platforms | `SEMP_WF_VERSION="0.4.0+20260520" ./scripts/dev.sh release` |
