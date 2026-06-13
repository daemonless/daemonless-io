# Makefile for daemonless.io documentation

PYTHON = python3
SCRIPTS_DIR = scripts

# Zensical SSG
ZENSICAL = zensical
ZEN_CONFIG = zensical.toml
# Zensical 0.0.30 opens many files via pygments; raise the fd limit to the max
# the host allows. Soft->hard works locally and on CI runners (where a fixed
# 200000 exceeds the hard limit and errors). Never fail the recipe over it.
ZEN_ULIMIT = ulimit -n $$(ulimit -Hn) 2>/dev/null || true;

.PHONY: all fetch generate generate-images generate-guides generate-architecture build clean serve status help

# Default target: Generate everything and build the site
all: generate build

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  fetch          Clone/update all image repositories (requires 'gh' CLI)"
	@echo "  generate       Run all documentation generators"
	@echo "  build          Build the static site using Zensical"
	@echo "  serve          Preview the build at :8001 (post-processed)"
	@echo "  clean          Remove all build artifacts"
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

# Build the static site with Zensical
build:
	@echo "==> Building site with Zensical..."
	$(ZEN_ULIMIT) $(ZENSICAL) build -f $(ZEN_CONFIG)
	@echo "==> Injecting interactive placeholders (Zensical doesn't run the MkDocs plugin)..."
	@# --phase both: mark @VAR@ -> convert in ONE process (shared unique id).
	markdown-placeholder-standalone site/ --phase both --placeholder-config placeholder-plugin.yaml

# Preview the Zensical build. Serves the post-processed static output so
# placeholders work. NOTE: not `zensical serve` — that rebuilds without the
# placeholder post-process (leaving raw @VAR@) and there's no live reload here.
serve: build
	@echo "==> Serving post-processed site/ at http://0.0.0.0:8001 (placeholders work; no live-reload)"
	python3 -m http.server -d site --bind 0.0.0.0 8001

# Cleanup
clean:
	@echo "==> Cleaning up..."
	rm -rf site/


status:
	git status
