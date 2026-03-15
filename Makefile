# Makefile for daemonless.io documentation

PYTHON = python3
MKDOCS = NO_MKDOCS_2_WARNING=1 mkdocs
SCRIPTS_DIR = scripts

.PHONY: all fetch generate generate-images generate-guides generate-architecture build clean serve status help

# Default target: Generate everything and build the site
all: generate build

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  fetch          Clone/update all image repositories (requires 'gh' CLI)"
	@echo "  generate       Run all documentation generators"
	@echo "  build          Build the static site using mkdocs"
	@echo "  serve          Run local mkdocs development server"
	@echo "  clean          Remove build artifacts"
	@echo "  status         Show git status of the docs repo"

# Fetch/Update all image repositories
# This ensures we have the latest compose.yaml files for generation
fetch:
	@echo "==> Fetching image repositories..."
	$(PYTHON) $(SCRIPTS_DIR)/fetch_repos.py

# Generate all dynamic documentation
generate: generate-guides generate-images generate-architecture

# Generate image documentation from compose.yaml in sub-repos
generate-images:
	@echo "==> Generating image documentation..."
	$(PYTHON) $(SCRIPTS_DIR)/generate_docs.py

# Generate dbuild guides from dbuild source using Jinja2 templates
generate-guides:
	@echo "==> Generating dbuild guides..."
	$(PYTHON) $(SCRIPTS_DIR)/dbuild_guide.py

# Generate architecture documentation
generate-architecture:
	@echo "==> Generating architecture documentation..."
	$(PYTHON) $(SCRIPTS_DIR)/generate-architecture.py

# Build the static site
build:
	@echo "==> Building site with mkdocs..."
	$(MKDOCS) build

# Local development server
serve:
	$(MKDOCS) serve -a 0.0.0.0:8888

# Cleanup
clean:
	@echo "==> Cleaning up..."
	rm -rf site/


status:
	git status
