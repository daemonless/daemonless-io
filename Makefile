# Makefile for daemonless.io documentation

PYTHON = python3
MKDOCS = NO_MKDOCS_2_WARNING=1 mkdocs
SCRIPTS_DIR = scripts

# Zensical (trial, parallel to the MkDocs build — uses zensical.toml)
ZENSICAL = zensical
ZEN_CONFIG = zensical.toml
# Zensical 0.0.30 opens many files via pygments; raise the fd limit first
ZEN_ULIMIT = ulimit -n 200000;

.PHONY: all fetch generate generate-images generate-guides generate-architecture build build-zen clean clean-zen serve serve-zen status help

# Default target: Generate everything and build the site
all: generate build

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  fetch          Clone/update all image repositories (requires 'gh' CLI)"
	@echo "  generate       Run all documentation generators"
	@echo "  build          Build the static site using mkdocs"
	@echo "  build-zen      Build the static site using zensical (-> site-zen/)"
	@echo "  serve          Run local mkdocs development server (:8888)"
	@echo "  serve-zen      Run local zensical development server (:8001)"
	@echo "  clean          Remove mkdocs build artifacts"
	@echo "  clean-zen      Remove zensical build artifacts"
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
	@curl -sL https://raw.githubusercontent.com/daemonless/daemonless/main/daemonless-versions.json \
		-o daemonless-versions.json 2>/dev/null || true
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

# Build the static site with Zensical (trial)
build-zen:
	@echo "==> Building site with Zensical..."
	$(ZEN_ULIMIT) $(ZENSICAL) build -f $(ZEN_CONFIG)

# Local development server
serve:
	$(MKDOCS) serve -a 0.0.0.0:8888

# Local development server (Zensical trial)
serve-zen:
	$(ZEN_ULIMIT) $(ZENSICAL) serve -f $(ZEN_CONFIG) -a 0.0.0.0:8001

# Cleanup
clean:
	@echo "==> Cleaning up..."
	rm -rf site/

# Cleanup (Zensical trial)
clean-zen:
	@echo "==> Cleaning up Zensical build..."
	rm -rf site-zen/


status:
	git status
