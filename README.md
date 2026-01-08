# daemonless.io

Documentation site for the daemonless FreeBSD container project.

Built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Local Development

### Prerequisites

```bash
pkg install py311-mkdocs py311-mkdocs-material
```

Or with pip:

```bash
pip install mkdocs-material
```

### Serve Locally

```bash
mkdocs serve -a 0.0.0.0:8000
```

Open http://localhost:8000 - changes auto-reload.

### Build Static Site

```bash
mkdocs build
```

Output is in `site/` directory.

## Deployment

The site auto-deploys to GitHub Pages on every push to `main`.

### How It Works

1. Push to `main` branch
2. GitHub Actions runs `.github/workflows/docs.yml`
3. MkDocs builds the site
4. Deploys to GitHub Pages
5. Live at https://daemonless.io

### Manual Deploy

Trigger a deploy without pushing:

```bash
gh workflow run docs.yml
```

## Adding Content

### New Image Documentation

1. Create `docs/images/<image-name>.md`:

```markdown
# Image Name

Short description.

| | |
|---|---|
| **Port** | 1234 |
| **Registry** | `ghcr.io/daemonless/<image>` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/<image>](https://github.com/daemonless/<image>) |

## Quick Start

\`\`\`bash
podman run -d --name <image> \
  -p 1234:1234 \
  -e PUID=1000 -e PGID=1000 \
  -v /data/config/<image>:/config \
  ghcr.io/daemonless/<image>:latest
\`\`\`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID |
| `PGID` | `1000` | Group ID |
| `TZ` | `UTC` | Timezone |
```

2. Add to `mkdocs.yml` nav section:

```yaml
nav:
  - Images:
    - <Category>:
      - Image Name: images/<image-name>.md
```

3. Push to `main`

### New Guide

1. Create `docs/guides/<guide-name>.md`
2. Add to `mkdocs.yml` nav under Guides
3. Push to `main`

## Site Structure

```
.
├── mkdocs.yml              # Site configuration
├── docs/
│   ├── index.md            # Homepage
│   ├── quick-start.md      # Getting started
│   ├── generator.md        # Command generator embed
│   ├── CNAME               # Custom domain
│   ├── images/             # Image documentation
│   │   ├── index.md        # Image catalog
│   │   └── <image>.md      # Per-image docs
│   └── guides/             # How-to guides
│       ├── permissions.md
│       ├── networking.md
│       └── ...
└── .github/workflows/
    └── docs.yml            # Deploy workflow
```

## Configuration

### mkdocs.yml

Key settings:

```yaml
site_name: daemonless
site_url: https://daemonless.io

theme:
  name: material
  palette:
    primary: red          # FreeBSD-inspired
  features:
    - navigation.tabs     # Top nav tabs
    - content.code.copy   # Copy button on code blocks
    - search.suggest      # Search suggestions

nav:
  - Home: index.md
  - ...                   # Define site structure here
```

### Custom Domain

The `docs/CNAME` file contains `daemonless.io`.

DNS is configured in Cloudflare with A records pointing to GitHub Pages:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

## MkDocs Features

### Admonitions (callout boxes)

```markdown
!!! note
    This is a note.

!!! warning
    This is a warning.

!!! tip
    This is a tip.
```

### Code Blocks with Copy Button

````markdown
```bash
podman run -d --name example ghcr.io/daemonless/example:latest
```
````

### Tables

```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### Icons

```markdown
:material-check:       # Checkmark
:material-close:       # X
:material-arrow-right: # Arrow
```

See [Material Icons](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/) for full list.

## Troubleshooting

### Build Fails Locally

```bash
# Check Python version
python3 --version  # Needs 3.8+

# Reinstall dependencies
pip install --upgrade mkdocs-material
```

### Deploy Fails on GitHub

1. Check Actions tab for error details
2. Ensure Pages is set to "GitHub Actions" source in repo settings
3. Verify custom domain is configured in Pages settings

### Changes Not Appearing

- GitHub Pages can cache for a few minutes
- Hard refresh: Ctrl+Shift+R
- Check workflow completed successfully in Actions tab
