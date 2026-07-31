#!/usr/bin/env bash
#
# dev.sh — developer / CI task runner for the Go implementation of
# SEMP Workflow Automation. Mirrors dev.ps1 exactly (same tasks, same flags).
#
# Tasks:
#   build   go build -> dist/semp-workflow            (fatal on failure)
#   release cross-compile every OS/arch -> dist/       (fatal)
#   vet     go vet ./...                               (fatal)
#   lint    golangci-lint run                          (fatal)
#   test    go test ./... (unit)                       (fatal)
#   integration  go test -tags integration ./...       (fatal; needs live broker)
#   cov     coverage profile -> func total + HTML      (fatal)
#   vuln    govulncheck ./...                          (report-only)
#   graphify  python -m graphify update .   (project root; report-only)
# Aggregates:
#   all     build vet test cov graphify
#   full    all + vuln
# (integration is opt-in — never part of all/full, so broker-free runs pass.)
#
# Runs from any cwd. Logs land in <scriptdir>/logs/<task>.log (plain text).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"          # the Go module root (= repo root)
PROJECT_ROOT="$GO_ROOT"                          # repo root (graphify graphs this)
LOG_DIR="$SCRIPT_DIR/logs"
DIST_DIR="$GO_ROOT/dist"
BIN_NAME="semp-workflow"
COVERAGE_OUT="$GO_ROOT/coverage.out"
COVERAGE_HTML="$GO_ROOT/coverage.html"

# Cross-compile matrix for `release`: OS/ARCH pairs. CGO is disabled below, so
# these build from any host with no C toolchain. Keep in sync with the build
# job in .github/workflows/go-ci.yml and the target list in
# .github/workflows/release.yml (which publishes these binaries on a release).
RELEASE_TARGETS=(
  "linux/amd64" "linux/arm64"
  "darwin/amd64" "darwin/arm64"
  "windows/amd64" "windows/arm64"
)

VERSION="${SEMP_WF_VERSION:-0.0.0-dev}"

# Tools that honor NO_COLOR emit clean text into the logs; static build by default.
export NO_COLOR=1
export CGO_ENABLED="${CGO_ENABLED:-0}"

mkdir -p "$LOG_DIR"

# ---- console helpers (colored; not captured to logs) ----------------------
c_reset=$'\033[0m'; c_blue=$'\033[1;34m'; c_green=$'\033[1;32m'
c_yellow=$'\033[1;33m'; c_red=$'\033[1;31m'
step() { printf '%s==>%s %s\n' "$c_blue" "$c_reset" "$*"; }
ok()   { printf '%s OK %s %s\n' "$c_green" "$c_reset" "$*"; }
warn() { printf '%s ! %s %s\n' "$c_yellow" "$c_reset" "$*"; }
die()  { printf '%s XX %s %s\n' "$c_red" "$c_reset" "$*" >&2; exit 1; }

# run_logged <task> <workdir> <cmd...>
# Truncates the task log with a header, then tees combined stdout+stderr while
# stripping CSI escape sequences (spinner/color) so the log stays readable.
# Returns the command's exit code (not sed/tee's), via PIPESTATUS.
run_logged() {
  local task="$1" workdir="$2"; shift 2
  local log="$LOG_DIR/$task.log"
  {
    printf '=== %s ===\n' "$task"
    printf 'dir: %s\n' "$workdir"
    printf 'cmd: %s\n\n' "$*"
  } > "$log"
  ( cd "$workdir" && "$@" 2>&1 ) \
    | sed -E $'s/\x1b\\[[0-9;?]*[a-zA-Z]//g' \
    | tee -a "$log"
  return "${PIPESTATUS[0]}"
}

# load_local_env sources the gitignored scripts/local.env — the ONLY source of the
# broker connection for the `integration` task (no environment fallback). `set -a`
# (allexport) marks every sourced assignment for export so the values reach the
# `go test` child process; a plain source would leave them as non-exported shell
# vars. The file is required: absent it we die with instructions rather than run a
# skip-only suite that looks like a pass. Because bash sources the file, values
# containing spaces or shell metacharacters must be quoted in it (prefer single).
load_local_env() {
  local file="$SCRIPT_DIR/local.env"
  [ -f "$file" ] || die "scripts/local.env not found — copy scripts/local.env.example to scripts/local.env and fill in the broker connection"
  set -a
  # shellcheck source=/dev/null
  . "$file"
  set +a
}

# ---- tasks ----------------------------------------------------------------
task_build() {
  step "build -> $DIST_DIR/$BIN_NAME"
  mkdir -p "$DIST_DIR"
  run_logged build "$GO_ROOT" \
    go build -trimpath -ldflags "-s -w -X main.version=$VERSION" \
    -o "$DIST_DIR/$BIN_NAME" ./cmd/semp-workflow \
    || die "build failed"
  ok "build"
}

# task_release cross-compiles $BIN_NAME for every pair in RELEASE_TARGETS into
# dist/$BIN_NAME_<os>_<arch>[.exe]. Output is streamed to logs/release.log with
# CSI stripped (§8.1); a failure in any target fails the whole task.
task_release() {
  step "release (cross-compile ${#RELEASE_TARGETS[@]} targets -> $DIST_DIR)"
  mkdir -p "$DIST_DIR"
  local log="$LOG_DIR/release.log"
  {
    printf '=== release ===\n'
    printf 'dir: %s\n' "$GO_ROOT"
    printf 'version: %s\n' "$VERSION"
    printf 'targets: %s\n\n' "${RELEASE_TARGETS[*]}"
  } > "$log"
  local failed=0 target os arch out
  for target in "${RELEASE_TARGETS[@]}"; do
    os="${target%/*}"; arch="${target#*/}"
    out="$DIST_DIR/${BIN_NAME}_${os}_${arch}"
    [ "$os" = "windows" ] && out="$out.exe"
    step "  $os/$arch -> $(basename "$out")"
    ( cd "$GO_ROOT" && GOOS="$os" GOARCH="$arch" \
        go build -trimpath -ldflags "-s -w -X main.version=$VERSION" \
        -o "$out" ./cmd/semp-workflow 2>&1 ) \
      | sed -E $'s/\x1b\\[[0-9;?]*[a-zA-Z]//g' | tee -a "$log"
    if [ "${PIPESTATUS[0]}" -ne 0 ]; then
      warn "  $os/$arch failed"; failed=1
    else
      ok "  $os/$arch"
    fi
  done
  [ "$failed" -eq 0 ] || die "release: one or more targets failed"
  ok "release -> $DIST_DIR"
}

task_vet() {
  step "vet"
  run_logged vet "$GO_ROOT" go vet ./... || die "vet failed"
  ok "vet"
}

task_lint() {
  step "lint (golangci-lint)"
  if ! command -v golangci-lint >/dev/null 2>&1; then
    warn "golangci-lint not installed; skipping (install: https://golangci-lint.run)"
    return 0
  fi
  run_logged lint "$GO_ROOT" golangci-lint run --no-color ./... || die "lint failed"
  ok "lint"
}

task_test() {
  step "test (unit)"
  # -count=1 disables Go's test result cache so every run re-executes the whole
  # suite — a cached PASS can otherwise hide a regression or stale coverage.
  run_logged test "$GO_ROOT" go test -count=1 ./... || die "tests failed"
  ok "test"
}

# task_integration runs the //go:build integration suites (module/engine/cli
# lifecycles) against a live broker. Connection values come solely from the
# gitignored scripts/local.env, which load_local_env sources (and requires —
# it dies if the file is absent). Building with the tag always compiles the
# integration files, so this catches compile errors even against an unreachable
# broker.
task_integration() {
  step "integration (-tags integration; live broker)"
  load_local_env
  # -count=1: never cache. -tags integration compiles+runs the broker-gated suites.
  run_logged integration "$GO_ROOT" go test -count=1 -tags integration ./... || die "integration tests failed"
  ok "integration"
}

task_cov() {
  step "cov"
  # -count=1: never cache — coverage must reflect a real run of every package.
  run_logged cov "$GO_ROOT" \
    go test -count=1 -covermode=atomic -coverprofile="$COVERAGE_OUT" ./... || die "coverage run failed"
  ( cd "$GO_ROOT" && go tool cover -func="$COVERAGE_OUT" | tee -a "$LOG_DIR/cov.log" | tail -1 )
  ( cd "$GO_ROOT" && go tool cover -html="$COVERAGE_OUT" -o "$COVERAGE_HTML" )
  ok "cov -> $COVERAGE_HTML"
}

task_vuln() {
  step "vuln (govulncheck)"
  if ! command -v govulncheck >/dev/null 2>&1; then
    warn "govulncheck not installed; skipping (go install golang.org/x/vuln/cmd/govulncheck@latest)"
    return 0
  fi
  run_logged vuln "$GO_ROOT" govulncheck ./... || warn "govulncheck reported findings (see logs/vuln.log)"
  ok "vuln"
}

task_graphify() {
  step "graphify (update graph at $PROJECT_ROOT)"
  if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    warn "python not found; skipping graphify"
    return 0
  fi
  local py; py="$(command -v python || command -v python3)"
  run_logged graphify "$PROJECT_ROOT" "$py" -m graphify update . \
    || warn "graphify update failed (see logs/graphify.log)"
  ok "graphify"
}

task_all()  { task_build; task_vet; task_test; task_cov; task_graphify; }
task_full() { task_all; task_vuln; }

usage() {
  cat <<'EOF'
Usage: dev.sh <task> [task...]

Tasks:
  build     Compile the CLI to dist/semp-workflow
  release   Cross-compile every OS/arch to dist/semp-workflow_<os>_<arch>[.exe]
  vet       go vet ./...
  lint      golangci-lint run
  test      go test ./... (unit)
  integration  go test -tags integration ./...  (needs a live broker; requires scripts/local.env)
  cov       Coverage profile -> printed total + coverage.html
  vuln      govulncheck ./...                 (report-only)
  graphify  python -m graphify update .        (report-only)

Aggregates:
  all       build vet test cov graphify
  full      all + vuln
  (integration is opt-in and never part of all/full)

Env:
  SEMP_WF_VERSION   version stamped into the binary (default 0.0.0-dev)

  The 'integration' task reads the broker connection ONLY from a gitignored
  scripts/local.env (copy scripts/local.env.example) — SEMP_HOST, SEMP_USERNAME,
  SEMP_PASSWORD, SEMP_MSG_VPN, and optional SEMP_VERIFY_SSL (TLS cert verify,
  default false). The task fails if the file is missing.
EOF
}

main() {
  [ "$#" -eq 0 ] && { usage; exit 0; }
  for arg in "$@"; do
    case "$arg" in
      -h|--help|help) usage; exit 0 ;;
      build)    task_build ;;
      release)  task_release ;;
      vet)      task_vet ;;
      lint)     task_lint ;;
      test)     task_test ;;
      integration) task_integration ;;
      cov)      task_cov ;;
      vuln)     task_vuln ;;
      graphify) task_graphify ;;
      all)      task_all ;;
      full)     task_full ;;
      *) die "unknown task: $arg (run 'dev.sh help')" ;;
    esac
  done
}

main "$@"
