#!/usr/bin/env python3
"""
Generate Mermaid diagram from Containerfile analysis.

Usage:
    python3 scripts/generate-architecture.py > docs/architecture.md
    python3 scripts/generate-architecture.py --mermaid-only  # Just the diagram
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
REPOS_DIR = REPO_ROOT.parent

# Base images (not app images)
BASE_IMAGES = {"base", "arr-base", "nginx-base"}


def parse_containerfile(containerfile: Path) -> dict:
    """Parse FROM and labels from a Containerfile."""
    result = {"parent": "base", "base_label": None}

    if not containerfile.exists():
        return result

    content = containerfile.read_text()

    # Find FROM ghcr.io/daemonless/<parent>
    from_match = re.search(r"FROM\s+ghcr\.io/daemonless/([^:\s]+)", content)
    if from_match:
        result["parent"] = from_match.group(1)

    # Find io.daemonless.base label (e.g., base="nginx")
    base_match = re.search(r'io\.daemonless\.base="([^"]+)"', content)
    if base_match:
        result["base_label"] = base_match.group(1)

    # Find io.daemonless.wip label
    if re.search(r'io\.daemonless\.wip="true"', content):
        result["wip"] = True

    return result


def discover_images() -> dict:
    """Scan repos and determine parent relationships."""
    images = {}

    if not REPOS_DIR.exists():
        return images

    for repo_path in sorted(REPOS_DIR.iterdir()):
        if not repo_path.is_dir():
            continue

        name = repo_path.name
        containerfile = repo_path / "Containerfile"

        if not containerfile.exists():
            continue

        info = parse_containerfile(containerfile)

        # Skip WIP images
        if info.get("wip"):
            continue

        # Determine effective parent
        parent = info["parent"]

        # If base_label is "nginx", it means nginx-base
        if info["base_label"] == "nginx":
            parent = "nginx-base"

        # arr-base children are detected by FROM line
        # nginx-base children are detected by base label or FROM line

        images[name] = {"parent": parent}

    return images


def generate_mermaid(images: dict) -> str:
    """Generate Mermaid flowchart from image relationships."""
    lines = [
        "```mermaid",
        "%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px' }}}%%",
        "flowchart LR",
        "    subgraph base_layer[\"Base Layer\"]",
        '        base["base<br/>s6, execline"]',
        "    end",
        "",
        "    subgraph intermediate[\"Intermediate Layers\"]",
        '        arr-base["arr-base<br/><small>sqlite3, icu, .NET</small>"]',
        '        nginx-base["nginx-base<br/><small>nginx</small>"]',
        "    end",
        "",
    ]

    # Group apps by parent
    arr_apps = []
    nginx_apps = []
    base_apps = []

    for name, info in images.items():
        if name in BASE_IMAGES:
            continue
        parent = info.get("parent", "base")
        if parent == "arr-base":
            arr_apps.append(name)
        elif parent == "nginx-base":
            nginx_apps.append(name)
        else:
            base_apps.append(name)

    # Arr apps subgraph
    if arr_apps:
        lines.append('    subgraph arr_apps[".NET Apps"]')
        for app in sorted(arr_apps):
            lines.append(f'        {app}["{app}"]')
        lines.append("    end")
        lines.append("")

    # Nginx apps subgraph
    if nginx_apps:
        lines.append('    subgraph nginx_apps["Nginx Apps"]')
        for app in sorted(nginx_apps):
            lines.append(f'        {app}["{app}"]')
        lines.append("    end")
        lines.append("")

    # Base apps subgraph
    if base_apps:
        lines.append('    subgraph base_apps["Direct Apps"]')
        for app in sorted(base_apps):
            lines.append(f'        {app}["{app}"]')
        lines.append("    end")
        lines.append("")

    # Connections
    lines.append("    %% Connections")
    lines.append("    base --> arr-base")
    lines.append("    base --> nginx-base")

    for app in arr_apps:
        lines.append(f"    arr-base --> {app}")
        lines.append(f'    click {app} "../images/{app}/" "View {app} Docs"')

    for app in nginx_apps:
        lines.append(f"    nginx-base --> {app}")
        lines.append(f'    click {app} "../images/{app}/" "View {app} Docs"')

    for app in base_apps:
        lines.append(f"    base --> {app}")
        lines.append(f'    click {app} "../images/{app}/" "View {app} Docs"')

    # Styling
    lines.append("")
    lines.append("    %% Styling")
    lines.append("    classDef baseStyle fill:#ab2b28,stroke:#333,color:#fff")
    lines.append("    classDef intermediateStyle fill:#d35400,stroke:#333,color:#fff")
    lines.append("    classDef appStyle fill:#2980b9,stroke:#333,color:#fff")
    lines.append("    class base baseStyle")
    lines.append("    class arr-base,nginx-base intermediateStyle")

    all_apps = arr_apps + nginx_apps + base_apps
    if all_apps:
        lines.append(f"    class {','.join(all_apps)} appStyle")

    lines.append("```")

    return "\n".join(lines)


def generate_page(images: dict) -> str:
    """Generate full architecture page with mermaid diagram."""
    mermaid = generate_mermaid(images)

    # Build dynamic inheritance tree
    arr_apps = []
    nginx_apps = []
    base_apps = []

    for name, info in images.items():
        if name in BASE_IMAGES:
            continue
        parent = info.get("parent", "base")
        if parent == "arr-base":
            arr_apps.append(name)
        elif parent == "nginx-base":
            nginx_apps.append(name)
        else:
            base_apps.append(name)

    arr_tree = "\n".join(f"    │   ├── {app}" for app in sorted(arr_apps)[:-1])
    if arr_apps:
        arr_tree += f"\n    │   └── {sorted(arr_apps)[-1]}"

    nginx_tree = "\n".join(f"    │   ├── {app}" for app in sorted(nginx_apps)[:-1])
    if nginx_apps:
        nginx_tree += f"\n    │   └── {sorted(nginx_apps)[-1]}"

    base_tree = "\n".join(f"    ├── {app}" for app in sorted(base_apps)[:-1])
    if base_apps:
        base_tree += f"\n    └── {sorted(base_apps)[-1]}"

    page = f"""# Architecture

How daemonless container images are structured and built.

## Image Layers

{mermaid}

## Layer Descriptions

### Base Layer

The `base` image provides the foundation for all daemonless containers:

- **FreeBSD 15** (or 14) minimal base
- **s6** - Process supervision
- **execline** - Scripting language for s6
- **FreeBSD-utilities** - Core utilities

### Intermediate Layers

| Image | Purpose | Key Packages |
|-------|---------|--------------|
| **arr-base** | .NET runtime for *arr apps | sqlite3, icu, libunwind, .NET compat |
| **nginx-base** | Web server base | nginx |

### Application Layer

Final images that users run. Each inherits from either:

- `base` - Direct apps (Python, Go, Node.js apps)
- `arr-base` - .NET applications (Radarr, Sonarr, etc.)
- `nginx-base` - PHP/web applications (Nextcloud, Organizr, etc.)

## Build Order

When a base image changes, dependent images must be rebuilt:

1. **base** changes → rebuild everything
2. **arr-base** changes → rebuild *arr apps only
3. **nginx-base** changes → rebuild nginx apps only

## Image Inheritance

```
FreeBSD 15 Base
└── base (s6, execline)
    ├── arr-base (sqlite3, icu, .NET compat)
{arr_tree}
    ├── nginx-base (nginx)
{nginx_tree}
{base_tree}
```
"""
    return page


def main():
    mermaid_only = "--mermaid-only" in sys.argv

    images = discover_images()

    if not images:
        print("No images found. Run fetch_repos.py first.", file=sys.stderr)
        sys.exit(1)

    if mermaid_only:
        print(generate_mermaid(images))
    else:
        print(generate_page(images))


if __name__ == "__main__":
    main()
