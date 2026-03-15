# daemonless.io

Documentation site for the [daemonless](https://github.com/daemonless/daemonless) FreeBSD container project.

Built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Local Development

The documentation for both image repositories and the `dbuild` tool is dynamically generated from source code and metadata.

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Build Workflow

A `Makefile` is provided to manage the generation and build process:

```bash
# 1. Fetch/Update all image repositories (clones to sibling directories)
# Requires GitHub CLI (gh)
make fetch

# 2. Generate all dynamic documentation
# Runs image doc generators and dbuild guide templates
make generate

# 3. Build the static site
make build

# Or do everything at once:
make all
```

### Serve Locally

To run the development server with auto-reload:

```bash
make serve
```

The site will be available at `http://localhost:8888` (or `http://saturn:8888`).

## Automated Documentation

The site structure is partially automated:

1.  **Image Docs**: `scripts/generate_docs.py` reads `compose.yaml` and `x-daemonless` metadata from each image repository to generate `docs/images/*.md`.
2.  **dbuild Guides**: `scripts/dbuild_guide.py` uses Jinja2 templates in `scripts/templates/` to generate the command reference and configuration guides directly from the `dbuild` source code.
3.  **Architecture**: `scripts/generate-architecture.py` generates the Mermaid-based architecture diagrams.

## Deployment

The site auto-deploys to GitHub Pages on every push to `main` via Woodpecker CI.

## Site Structure

```
.
├── Makefile                # Unified build entry point
├── mkdocs.yaml             # MkDocs configuration
├── requirements.txt        # Python dependencies
├── docs/
│   ├── index.md            # Homepage
│   ├── images/             # Generated image documentation
│   ├── guides/             # Manual and generated guides
│   │   └── dbuild/         # Generated dbuild engine guides
│   └── assets/             # Images, logos, and favicons
├── scripts/                # Documentation generators
│   ├── templates/          # Jinja2 templates for guides
│   ├── generate_docs.py    # Image doc generator
│   └── dbuild_guide.py     # dbuild guide generator
└── overrides/              # Material for MkDocs theme overrides
```

## Community

- **GitHub**: [github.com/daemonless](https://github.com/daemonless)
- **Discord**: [Join our Community](https://discord.com/invite/Kb9tkhecZT)
- **CI Status**: [ci.daemonless.io](https://ci.daemonless.io)
