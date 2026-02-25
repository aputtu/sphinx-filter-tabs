VENV    := venv
PYTHON  := $(VENV)/bin/python
SCRIPTS := scripts

.DEFAULT_GOAL := help

# Ensure the venv exists and the package is installed before running dev commands
$(PYTHON):
	@echo "No virtual environment found. Run 'make setup' first."
	@exit 1

.PHONY: help setup export test html pdf docs all clean clean-all watch

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Setup"
	@echo "  setup        Create venv, install dependencies, build docs"
	@echo ""
	@echo "Development"
	@echo "  test         Run tests"
	@echo "  html         Build HTML documentation"
	@echo "  pdf          Build PDF documentation"
	@echo "  docs         Build HTML and PDF documentation"
	@echo "  all          Run tests and build all documentation"
	@echo "  watch        Watch for changes and auto-rebuild HTML"
	@echo ""
	@echo "Maintenance"
	@echo "  clean        Remove build artifacts"
	@echo "  clean-all    Clean, then rebuild everything"
	@echo "  export       Export project to a single text file"

setup:
	@bash $(SCRIPTS)/setup_dev.sh

export:
	@bash $(SCRIPTS)/export-project.sh

test: $(PYTHON)
	@bash $(SCRIPTS)/dev.sh test

html: $(PYTHON)
	@bash $(SCRIPTS)/dev.sh html

pdf: $(PYTHON)
	@bash $(SCRIPTS)/dev.sh pdf

docs: $(PYTHON)
	@bash $(SCRIPTS)/dev.sh docs

all: $(PYTHON)
	@bash $(SCRIPTS)/dev.sh all

clean:
	@bash $(SCRIPTS)/dev.sh clean

clean-all: $(PYTHON)
	@bash $(SCRIPTS)/dev.sh clean-all

watch: $(PYTHON)
	@bash $(SCRIPTS)/dev.sh watch
