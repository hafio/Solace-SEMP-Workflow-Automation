<#
.SYNOPSIS
  dev.ps1 -- developer / CI task runner for the Go implementation of
  SEMP Workflow Automation. Mirrors dev.sh exactly (same tasks, same flags).

.DESCRIPTION
  Tasks:
    build   go build -> dist/semp-workflow.exe        (fatal on failure)
    release cross-compile every OS/arch -> dist/       (fatal)
    vet     go vet ./...                               (fatal)
    lint    golangci-lint run                          (fatal)
    test    go test ./... (unit)                       (fatal)
    integration  go test -tags integration ./...       (fatal; needs live broker)
    cov     coverage profile -> func total + HTML      (fatal)
    vuln    govulncheck ./...                          (report-only)
    graphify  python -m graphify update .   (project root; report-only)
  Aggregates:
    all     build vet test cov graphify
    full    all + vuln
  (integration is opt-in -- never part of all/full, so broker-free runs pass.)

  Runs from any cwd. Logs land in <scriptdir>\logs\<task>.log (plain text).
#>
[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments = $true)] [string[]] $Tasks)

# NB: do NOT set this to "Stop". In Windows PowerShell 5.1, `2>&1` on a native
# command (go/govulncheck) wraps each stderr line in a NativeCommandError; with
# "Stop" the first such record becomes a terminating error and aborts the script
# before $LASTEXITCODE is read -- e.g. `go vet` writing diagnostics to stderr would
# kill the run with no log written. "Continue" mirrors dev.sh (set -uo pipefail,
# no -e): every task gates explicitly on its captured exit code instead.
$ErrorActionPreference = "Continue"

$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$GoRoot       = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$ProjectRoot  = $GoRoot
$LogDir       = Join-Path $ScriptDir "logs"
$DistDir      = Join-Path $GoRoot "dist"
$BinName      = "semp-workflow.exe"
$CoverageOut  = Join-Path $GoRoot "coverage.out"
$CoverageHtml = Join-Path $GoRoot "coverage.html"

$Version = if ($env:SEMP_WF_VERSION) { $env:SEMP_WF_VERSION } else { "0.0.0-dev" }

# Cross-compile matrix for `release`: OS/ARCH pairs. CGO is disabled below, so
# these build from any host with no C toolchain. Keep in sync with the build
# job in .github\workflows\go-ci.yml and the target list in
# .github\workflows\release.yml (which publishes these binaries on a release).
$ReleaseTargets = @(
    "linux/amd64", "linux/arm64",
    "darwin/amd64", "darwin/arm64",
    "windows/amd64", "windows/arm64"
)

# Tools that honor NO_COLOR emit clean text into the logs; static build by default.
$env:NO_COLOR = "1"
if (-not $env:CGO_ENABLED) { $env:CGO_ENABLED = "0" }

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

# ---- console helpers (colored; not captured to logs) ----------------------
function Step($m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host " OK  $m" -ForegroundColor Green }
function Warn($m) { Write-Host " !   $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host " XX  $m" -ForegroundColor Red; exit 1 }

# Invoke-Logged: run a native command in $WorkDir, capture combined output once
# (PS 5.1-safe: flatten ErrorRecords, no Tee-Object), strip CSI escapes, write a
# UTF-8 log, echo to console, and return the native exit code ($LASTEXITCODE).
function Invoke-Logged {
    param([string]$Task, [string]$WorkDir, [string]$Exe, [string[]]$CmdArgs)
    $log = Join-Path $LogDir "$Task.log"
    Push-Location $WorkDir
    try {
        $out  = (& $Exe @CmdArgs 2>&1 | ForEach-Object { "$_" } | Out-String -Width 4096)
        $code = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    $out = $out -replace "\x1b\[[0-9;?]*[a-zA-Z]", ""
    $header = "=== $Task ===`r`ndir: $WorkDir`r`ncmd: $Exe $($CmdArgs -join ' ')`r`n`r`n"
    Set-Content -Path $log -Value ($header + $out) -Encoding utf8
    if ($out) { Write-Host $out }
    return $code
}

function Have($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

# Import-LocalEnv loads KEY=VALUE lines from a gitignored scripts\local.env -- the
# ONLY source of the broker connection for the `integration` task (no environment
# fallback). Each key is set as a process env var so the `go test` child sees it;
# blank lines and `#` comments are skipped, and surrounding single or double
# quotes are stripped (matching what bash's `source` of the same file yields).
# The file is required: absent it we throw with instructions rather than run a
# skip-only suite that looks like a pass.
function Import-LocalEnv {
    $file = Join-Path $ScriptDir "local.env"
    if (-not (Test-Path $file)) {
        Die "scripts\local.env not found -- copy scripts\local.env.example to scripts\local.env and fill in the broker connection"
    }
    foreach ($line in Get-Content -LiteralPath $file) {
        $t = $line.Trim()
        if ($t -eq "" -or $t.StartsWith("#")) { continue }
        $idx = $t.IndexOf("=")
        if ($idx -lt 1) { continue }
        $key = $t.Substring(0, $idx).Trim()
        $val = $t.Substring($idx + 1).Trim().Trim('"', "'")
        Set-Item -Path "Env:$key" -Value $val
    }
}

# ---- tasks ----------------------------------------------------------------
function Task-Build {
    Step "build -> $DistDir\$BinName"
    if (-not (Test-Path $DistDir)) { New-Item -ItemType Directory -Path $DistDir | Out-Null }
    $code = Invoke-Logged "build" $GoRoot "go" @(
        "build", "-trimpath", "-ldflags", "-s -w -X main.version=$Version",
        "-o", (Join-Path $DistDir $BinName), "./cmd/semp-workflow")
    if ($code -ne 0) { Die "build failed" }
    Ok "build"
}

# Task-Release cross-compiles the CLI for every pair in $ReleaseTargets into
# dist\semp-workflow_<os>_<arch>[.exe]. Combined output is captured once per
# target (PS 5.1-safe), CSI-stripped, and appended to logs\release.log (sec. 8.1);
# GOOS/GOARCH are restored afterward. Any target failure fails the task.
function Task-Release {
    Step "release (cross-compile $($ReleaseTargets.Count) targets -> $DistDir)"
    if (-not (Test-Path $DistDir)) { New-Item -ItemType Directory -Path $DistDir | Out-Null }
    $binBase = $BinName -replace '\.exe$', ''
    $log = Join-Path $LogDir "release.log"
    $header = "=== release ===`r`ndir: $GoRoot`r`nversion: $Version`r`ntargets: $($ReleaseTargets -join ' ')`r`n`r`n"
    Set-Content -Path $log -Value $header -Encoding utf8
    $failed = 0
    $prevGoos = $env:GOOS; $prevGoarch = $env:GOARCH
    Push-Location $GoRoot
    try {
        foreach ($target in $ReleaseTargets) {
            $parts = $target -split "/"
            $os = $parts[0]; $arch = $parts[1]
            $out = Join-Path $DistDir "${binBase}_${os}_${arch}"
            if ($os -eq "windows") { $out = "$out.exe" }
            Step "  $os/$arch -> $(Split-Path -Leaf $out)"
            $env:GOOS = $os; $env:GOARCH = $arch
            $bout = (& go build -trimpath -ldflags "-s -w -X main.version=$Version" -o $out ./cmd/semp-workflow 2>&1 |
                ForEach-Object { "$_" } | Out-String -Width 4096)
            $code = $LASTEXITCODE
            $bout = $bout -replace "\x1b\[[0-9;?]*[a-zA-Z]", ""
            Add-Content -Path $log -Value ("--- $os/$arch ---`r`n" + $bout) -Encoding utf8
            if ($bout) { Write-Host $bout }
            if ($code -ne 0) { Warn "  $os/$arch failed"; $failed = 1 } else { Ok "  $os/$arch" }
        }
    } finally {
        if ($null -eq $prevGoos)   { Remove-Item Env:GOOS   -ErrorAction SilentlyContinue } else { $env:GOOS = $prevGoos }
        if ($null -eq $prevGoarch) { Remove-Item Env:GOARCH -ErrorAction SilentlyContinue } else { $env:GOARCH = $prevGoarch }
        Pop-Location
    }
    if ($failed -ne 0) { Die "release: one or more targets failed" }
    Ok "release -> $DistDir"
}

function Task-Vet {
    Step "vet"
    $code = Invoke-Logged "vet" $GoRoot "go" @("vet", "./...")
    if ($code -ne 0) { Die "vet failed" }
    Ok "vet"
}

function Task-Lint {
    Step "lint (golangci-lint)"
    if (-not (Have "golangci-lint")) { Warn "golangci-lint not installed; skipping"; return }
    $code = Invoke-Logged "lint" $GoRoot "golangci-lint" @("run", "--no-color", "./...")
    if ($code -ne 0) { Die "lint failed" }
    Ok "lint"
}

function Task-Test {
    Step "test (unit)"
    # -count=1 disables Go's test result cache so every run re-executes the whole
    # suite -- a cached PASS can otherwise hide a regression or stale coverage.
    $code = Invoke-Logged "test" $GoRoot "go" @("test", "-count=1", "./...")
    if ($code -ne 0) { Die "tests failed" }
    Ok "test"
}

# Task-Integration runs the `//go:build integration` suites (module/engine/cli
# lifecycles) against a live broker. Connection values come solely from the
# gitignored scripts\local.env, which Import-LocalEnv loads (and requires -- it
# throws if the file is absent). Building with the tag always compiles the
# integration files, so this catches compile errors even against an unreachable
# broker.
function Task-Integration {
    Step "integration (-tags integration; live broker)"
    Import-LocalEnv
    # -count=1: never cache. -tags integration compiles+runs the broker-gated suites.
    $code = Invoke-Logged "integration" $GoRoot "go" @("test", "-count=1", "-tags", "integration", "./...")
    if ($code -ne 0) { Die "integration tests failed" }
    Ok "integration"
}

function Task-Cov {
    Step "cov"
    # -count=1: never cache -- coverage must reflect a real run of every package.
    $code = Invoke-Logged "cov" $GoRoot "go" @(
        "test", "-count=1", "-covermode=atomic", "-coverprofile=$CoverageOut", "./...")
    if ($code -ne 0) { Die "coverage run failed" }
    Push-Location $GoRoot
    try {
        $funcOut = (& go tool cover -func="$CoverageOut" 2>&1 | ForEach-Object { "$_" } | Out-String -Width 4096)
        Add-Content -Path (Join-Path $LogDir "cov.log") -Value $funcOut -Encoding utf8
        $total = ($funcOut -split "`n" | Where-Object { $_ -match "total:" } | Select-Object -Last 1)
        if ($total) { Write-Host $total.Trim() }
        & go tool cover -html="$CoverageOut" -o "$CoverageHtml"
    } finally {
        Pop-Location
    }
    Ok "cov -> $CoverageHtml"
}

function Task-Vuln {
    Step "vuln (govulncheck)"
    if (-not (Have "govulncheck")) { Warn "govulncheck not installed; skipping"; return }
    $code = Invoke-Logged "vuln" $GoRoot "govulncheck" @("./...")
    if ($code -ne 0) { Warn "govulncheck reported findings (see logs\vuln.log)" }
    Ok "vuln"
}

function Task-Graphify {
    Step "graphify (update graph at $ProjectRoot)"
    $py = if (Have "python") { "python" } elseif (Have "python3") { "python3" } else { $null }
    if (-not $py) { Warn "python not found; skipping graphify"; return }
    $code = Invoke-Logged "graphify" $ProjectRoot $py @("-m", "graphify", "update", ".")
    if ($code -ne 0) { Warn "graphify update failed (see logs\graphify.log)" }
    Ok "graphify"
}

function Task-All  { Task-Build; Task-Vet; Task-Test; Task-Cov; Task-Graphify }
function Task-Full { Task-All; Task-Vuln }

function Show-Usage {
    Write-Host @"
Usage: dev.ps1 <task> [task...]

Tasks:
  build     Compile the CLI to dist\semp-workflow.exe
  release   Cross-compile every OS/arch to dist\semp-workflow_<os>_<arch>[.exe]
  vet       go vet ./...
  lint      golangci-lint run
  test      go test ./... (unit)
  integration  go test -tags integration ./...  (needs a live broker; requires scripts\local.env)
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
  scripts\local.env (copy scripts\local.env.example) -- SEMP_HOST, SEMP_USERNAME,
  SEMP_PASSWORD, SEMP_MSG_VPN, and optional SEMP_VERIFY_SSL (TLS cert verify,
  default false). The task fails if the file is missing.
"@
}

if (-not $Tasks -or $Tasks.Count -eq 0) { Show-Usage; exit 0 }

foreach ($t in $Tasks) {
    switch ($t) {
        { $_ -in @("-h", "--help", "help") } { Show-Usage; exit 0 }
        "build"    { Task-Build }
        "release"  { Task-Release }
        "vet"      { Task-Vet }
        "lint"     { Task-Lint }
        "test"     { Task-Test }
        "integration" { Task-Integration }
        "cov"      { Task-Cov }
        "vuln"     { Task-Vuln }
        "graphify" { Task-Graphify }
        "all"      { Task-All }
        "full"     { Task-Full }
        default    { Die "unknown task: $t (run 'dev.ps1 help')" }
    }
}
