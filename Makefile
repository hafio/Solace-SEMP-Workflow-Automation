.PHONY: install test test-all build validate clean help

TEMPLATES_DIR ?= templates
OUTPUT       ?= dist/semp-workflow.zip
CONFIG       ?= config.yaml

help:
	@echo "Usage:"
	@echo "  make install          Install in editable mode (development)"
	@echo "  make test             Run unit tests"
	@echo "  make test-all         Run all tests (unit + integration, requires live broker)"
	@echo "  make build            Build dist/semp-workflow.zip (bundles ./templates)"
	@echo "  make build TEMPLATES_DIR=./my-templates   Bundle a custom templates directory"
	@echo "  make build OUTPUT=dist/myapp.pyz          Custom output path"
	@echo "  make validate         Validate config.yaml and templates"
	@echo "  make modules          List all available modules"
	@echo "  make clean            Remove build artefacts"

install:
	pip install -e ".[test]"

test:
	pytest tests/unit -v

test-all:
	pytest tests/ -v

build:
	python scripts/build.py --templates-dir $(TEMPLATES_DIR) --output $(OUTPUT)

validate:
	semp-workflow validate --config $(CONFIG) --templates-dir $(TEMPLATES_DIR)

modules:
	semp-workflow list-modules

clean:
	rm -rf dist/ build/ src/*.egg-info
