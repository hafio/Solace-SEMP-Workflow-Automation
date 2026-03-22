.PHONY: install build validate clean help

TEMPLATES_DIR ?= templates
OUTPUT       ?= dist/semp-workflow.zip
CONFIG       ?= config.yaml

help:
	@echo "Usage:"
	@echo "  make install          Install in editable mode (development)"
	@echo "  make build            Build dist/semp-workflow.zip (bundles ./templates)"
	@echo "  make build TEMPLATES_DIR=./my-templates   Bundle a custom templates directory"
	@echo "  make build OUTPUT=dist/myapp.pyz          Custom output path"
	@echo "  make validate         Validate config.yaml and templates"
	@echo "  make modules          List all available modules"
	@echo "  make clean            Remove build artefacts"

install:
	pip install -e .

build:
	python scripts/build_pyz.py --templates-dir $(TEMPLATES_DIR) --output $(OUTPUT)

validate:
	semp-workflow validate --config $(CONFIG) --templates-dir $(TEMPLATES_DIR)

modules:
	semp-workflow list-modules

clean:
	rm -rf dist/ build/ src/*.egg-info
