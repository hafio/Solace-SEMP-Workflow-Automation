#!/usr/bin/env python3
"""Build script: packages semp-workflow into a self-contained .pyz archive.

The .pyz bundles:
  - The semp_workflow Python package
  - All third-party dependencies (click, jinja2, requests, colorama, ...)
  - Workflow templates stored as package data in semp_workflow/bundled_templates/
    (read via importlib.resources — no temp dir extraction at runtime)

Template precedence when running the pyz:
  1. --templates-dir PATH  (CLI flag, highest priority)
  2. templates_dir: in config.yaml (if the directory exists on disk)
  3. Bundled templates (fallback, read directly from the zip via importlib.resources)

Configuration (the config.yaml) is intentionally NOT bundled.

Usage:
    python scripts/build_pyz.py
    python scripts/build_pyz.py --templates-dir ./templates
    python scripts/build_pyz.py --templates-dir ./templates --output dist/myapp.pyz

Running the built pyz:
    python dist/semp-workflow.zip run --config config.yaml
    python dist/semp-workflow.zip list-modules
    python dist/semp-workflow.zip init --output-dir ./templates
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import zipapp
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
DEFAULT_TEMPLATES = ROOT / "templates"
FALLBACK_TEMPLATES = ROOT / "examples" / "templates"


# ---------------------------------------------------------------------------
# Bootstrapper embedded as __main__.py inside the .pyz
# ---------------------------------------------------------------------------
# Templates are stored as package data in semp_workflow/bundled_templates/ and
# read via importlib.resources — no extraction or temp dirs needed.

_BOOTSTRAPPER = '''\
from semp_workflow.cli import main
main()
'''


# ---------------------------------------------------------------------------
# Build logic
# ---------------------------------------------------------------------------

def _clean_stage(stage: Path) -> None:
    """Remove build artifacts that inflate the archive unnecessarily."""
    for pattern in ("*.dist-info", "*.data"):
        for p in stage.glob(pattern):
            if p.is_dir():
                shutil.rmtree(p)
    for p in stage.rglob("__pycache__"):
        shutil.rmtree(p)
    # Remove test directories bundled by some packages
    for p in stage.rglob("tests"):
        if p.is_dir():
            shutil.rmtree(p)


def _clean_project() -> None:
    """Remove setuptools build cache so renamed/deleted files don't bleed into the zip."""
    for path in (ROOT / "build", ROOT / "dist"):
        if path.exists():
            shutil.rmtree(path)
    for path in ROOT.glob("src/*.egg-info"):
        shutil.rmtree(path)


def build(templates_dir: Path, output: Path) -> None:
    print(f"Building {output.name} ...")
    print(f"  Source:    {ROOT}")
    print(f"  Templates: {templates_dir}")
    print(f"  Output:    {output}")
    print()

    print("  [0/5] Cleaning project build cache ...")
    _clean_project()

    with tempfile.TemporaryDirectory(prefix="semp-wf-build-") as tmpdir:
        stage = Path(tmpdir) / "stage"
        stage.mkdir()

        # 1. Install the package + all dependencies into the staging dir
        print("  [1/5] Installing package and dependencies ...")
        subprocess.run(
            [
                sys.executable, "-m", "pip", "install",
                "--target", str(stage),
                "--no-compile",
                "--no-cache-dir",
                "--quiet",
                str(ROOT),
            ],
            check=True,
        )

        # 2. Strip build artifacts to keep the archive small
        print("  [2/5] Cleaning build artifacts ...")
        _clean_stage(stage)

        # 3. Bundle workflow templates as package data inside semp_workflow/bundled_templates/.
        #    importlib.resources.files("semp_workflow.bundled_templates") reads them
        #    directly from the zip at runtime — no temp dir, no extraction.
        bundled_dir = stage / "semp_workflow" / "bundled_templates"
        bundled_dir.mkdir(parents=True, exist_ok=True)
        (bundled_dir / "__init__.py").write_text("")  # mark as Python package

        if templates_dir.exists():
            yaml_files = list(templates_dir.glob("*.yaml"))
            for tmpl in yaml_files:
                shutil.copy2(tmpl, bundled_dir / tmpl.name)
            print(f"  [3/5] Bundled {len(yaml_files)} template(s) from {templates_dir.name}/")
        else:
            print(f"  [3/5] Warning: templates dir not found: {templates_dir}")
            print("         Pyz will have no bundled templates.")

        # 4. Write the bootstrapper as the root __main__.py
        print("  [4/5] Writing bootstrapper ...")
        (stage / "__main__.py").write_text(_BOOTSTRAPPER)

        # 5. Create the .zip archive
        print("  [5/5] Creating .zip archive ...")
        output.parent.mkdir(parents=True, exist_ok=True)
        zipapp.create_archive(
            stage,
            output,
            interpreter="/usr/bin/env python3",
            compressed=True,
        )

    size_kb = output.stat().st_size // 1024
    print()
    print(f"  Done! {output}  ({size_kb} KB)")
    print()
    print("  Usage:")
    print(f"    python {output.name} --help")
    print(f"    python {output.name} list-modules")
    print(f"    python {output.name} run --config config.yaml")
    print(f"    python {output.name} init --output-dir ./templates")


def _resolve_templates_dir(given: Path | None) -> Path:
    """Pick the templates directory to bundle, with sensible fallbacks."""
    if given is not None:
        return given
    if DEFAULT_TEMPLATES.exists():
        return DEFAULT_TEMPLATES
    return FALLBACK_TEMPLATES


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Workflow templates directory to bundle into the pyz. "
            f"Defaults to ./templates, falling back to ./examples/templates."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DIST / "semp-workflow.zip",
        metavar="PATH",
        help="Output file path (default: dist/semp-workflow.zip)",
    )
    args = parser.parse_args()

    templates_dir = _resolve_templates_dir(args.templates_dir)
    build(templates_dir, args.output)


if __name__ == "__main__":
    main()
