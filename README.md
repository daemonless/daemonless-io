# daemonless.io

Documentation and catalog site for the [daemonless](https://github.com/daemonless/daemonless) FreeBSD container project.

Built with [Zensical](https://zensical.org/).

## Local Development

Documentation for both image repositories and the `dbuild` toolchain is generated from repository metadata and source templates.

### Prerequisites

```bash
pip install -r requirements.txt
```

### Build Workflow

```bash
# 1. Clone or update all image repositories (as siblings of daemonless-io/)
make fetch

# 2. Generate dynamic documentation (image pages, catalog, status, dbuild guides, architecture)
make generate

# 3. Build the static site and validate rendered HTML
make build

# Or run generation + build together:
make all
```

### Preview Locally

```bash
make serve
```

Serves `site/` at `http://localhost:8001`.

## Automated Documentation

1. **Image Catalog & Pages**: `scripts/generate_docs.py` reads `compose.yaml` (`x-daemonless`) and `.daemonless/config.yaml` from each image repository via `dbuild` to render `docs/images/*.md`, `docs/images/index.md`, `docs/status.md`, and `zensical.toml`.
2. **dbuild Guides**: `scripts/dbuild_guide.py` renders CLI and configuration references from `dbuild` into `docs/guides/dbuild/`.
3. **Architecture**: `scripts/generate-architecture.py` builds the base-layer inheritance diagram and parent tree in `docs/architecture.md`.
4. **Render Gate**: `scripts/check-rendered.py` fails `make build` if unrendered shortcodes, admonitions, frontmatter, or placeholders reach `site/`.

## Deployment

GitHub Actions (`.github/workflows/deploy.yaml`) generates and deploys the site to GitHub Pages on pushes to `main` and scheduled version checks.

## Site Structure

```text
.
├── Makefile                      # Build, generate, and preview entry point
├── requirements.txt              # Python dependencies (Zensical, Jinja2, Pillow)
├── docs/
│   ├── guides/                   # Operations, appliances, and porting guides
│   ├── reverse-proxy/            # Reverse Proxy appliance documentation
│   ├── pkg-cache/                # Package Cache appliance documentation
│   ├── javascripts/              # Catalog filtering, choices, and customizer JS
│   └── stylesheets/              # Custom theme styles
├── scripts/
│   ├── templates/                # Jinja2 templates (zensical.toml.j2, status, home)
│   ├── generate_docs.py          # Catalog and image page generator
│   ├── dbuild_guide.py           # dbuild reference generator
│   └── check-rendered.py         # Post-build HTML verification gate
└── overrides/                    # Zensical theme overrides and custom icons
```

## Links

- **Website**: [daemonless.io](https://daemonless.io)
- **Status**: [daemonless.io/status/](https://daemonless.io/status/)
- **fjord**: [fjord.daemonless.io](https://fjord.daemonless.io)
- **GitHub**: [github.com/daemonless](https://github.com/daemonless)
- **Discord**: [discord.com/invite/Kb9tkhecZT](https://discord.com/invite/Kb9tkhecZT)
