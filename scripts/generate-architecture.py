#!/usr/bin/env python3
"""
Generate docs/architecture.md from the image repos' Containerfile templates.

Each image's parent is the daemonless image its runtime stage (the last FROM)
starts from; builder stages don't count. WIP images are left out.

Usage:
    python3 scripts/generate-architecture.py            # writes docs/architecture.md
    python3 scripts/generate-architecture.py --stdout   # print instead
    REPOS_DIR=~/src/daemonless python3 scripts/generate-architecture.py
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
# fetch_repos.py clones the image repos next to this one
REPOS_DIR = Path(os.environ.get("REPOS_DIR", REPO_ROOT.parent)).expanduser()
OUTPUT = REPO_ROOT / "docs" / "architecture.md"

# The base layer, in the order the page describes it.
BASES = {
    "base-core": "FreeBSD userland and pkg. No init: tool images and the other bases start here.",
    "base-exec": "One process per container. `/init` runs the setup scripts, then execs the app as `bsd`. Podman, AppJail or Kubernetes restart it.",
    "base-rcd": "Several services in one container, supervised by [rcd(8)](https://github.com/bapt/freebsd-rcd).",
    "base": "The original s6 base. Kept for images built outside daemonless; new images don't use it.",
}

# Images that are mainly parents for other images.
INTERMEDIATES = {
    "arr-base": ".NET runtime for the *arr apps",
    "nginx-base": "nginx in front of an app (rcd runs both)",
    "nginx": "nginx serving static sites",
    "postgres": "PostgreSQL",
    "node": "Node.js toolchain",
    "python": "Python toolchain",
}

FROM_RE = re.compile(r"^FROM\s+(\S+)", re.MULTILINE)
DAEMONLESS_RE = re.compile(r"^ghcr\.io/daemonless/([^:@\s]+)")


def runtime_parent(repo: Path) -> str | None:
    """The daemonless image the last stage of the main template starts from."""
    for name in ("Containerfile.j2", "Containerfile.pkg.j2", "Containerfile", "Containerfile.pkg"):
        f = repo / name
        if f.is_file():
            text = f.read_text()
            break
    else:
        return None
    froms = FROM_RE.findall(text)
    if not froms:
        return None
    m = DAEMONLESS_RE.match(froms[-1])
    return m.group(1) if m else None


def is_wip(repo: Path) -> bool:
    return any(
        'io.daemonless.wip="true"' in f.read_text()
        for f in repo.glob("Containerfile*")
        if f.is_file()
    )


def discover() -> dict[str, str | None]:
    """{image: parent} for every image repo (has compose.yaml and a template)."""
    images = {}
    for repo in sorted(REPOS_DIR.iterdir()):
        if not repo.is_dir() or not (repo / "compose.yaml").is_file():
            continue
        if not any(repo.glob("Containerfile*")) or is_wip(repo):
            continue
        images[repo.name] = runtime_parent(repo)
    return images


def children(images: dict, parent: str) -> list[str]:
    return sorted(n for n, p in images.items() if p == parent and n != parent)


def link(name: str) -> str:
    # generate_docs.py writes the image pages first; not every image gets one
    if (REPO_ROOT / "docs" / "images" / f"{name}.md").is_file():
        return f"[{name}](images/{name}.md)"
    return name


def mermaid(images: dict) -> str:
    nodes = [b for b in BASES if b in images] + [i for i in INTERMEDIATES if i in images]
    lines = [
        "```mermaid",
        "flowchart LR",
    ]
    for n in nodes:
        apps = [c for c in children(images, n) if c not in BASES and c not in INTERMEDIATES]
        label = f"{n}<br/><small>{len(apps)} images</small>" if apps else n
        lines.append(f'    {n.replace("-", "_")}["{label}"]')
    for n in nodes:
        p = images.get(n)
        if p in nodes:
            lines.append(f'    {p.replace("-", "_")} --> {n.replace("-", "_")}')
    lines += [
        "    classDef baseStyle fill:#ab2b28,stroke:#333,color:#fff",
        "    classDef intermediateStyle fill:#d35400,stroke:#333,color:#fff",
        "    class " + ",".join(b.replace("-", "_") for b in BASES if b in images) + " baseStyle",
        "    class " + ",".join(i.replace("-", "_") for i in INTERMEDIATES if i in images) + " intermediateStyle",
        "```",
    ]
    return "\n".join(lines)


def generate_page(images: dict) -> str:
    base_rows = "\n".join(
        f"| **{b}** | {images.get(b) or '-'} | {desc} |" for b, desc in BASES.items() if b in images
    )
    inter_rows = "\n".join(
        f"| **{i}** | {images.get(i) or '-'} | {desc} |" for i, desc in INTERMEDIATES.items() if i in images
    )
    # apps can be parents too (opencloud-radicale is built on radicale)
    others = sorted({p for p in images.values() if p and p not in BASES and p not in INTERMEDIATES})
    groups = []
    for parent in [*BASES, *INTERMEDIATES, *others]:
        apps = [c for c in children(images, parent) if c not in BASES and c not in INTERMEDIATES]
        if apps:
            groups.append(f"### {parent} ({len(apps)})\n\n" + ", ".join(link(a) for a in apps))
    groups_md = "\n\n".join(groups)

    return f"""---
title: "Architecture: How Daemonless Container Images Are Built"
description: "The base images daemonless containers are built on: base-exec for one process per container, base-rcd for multi-service appliances, and the images that inherit from them."
---

<!-- Generated by scripts/generate-architecture.py; edit the script, not this file. -->

# Architecture

How daemonless container images are layered.

## Image Layers

{mermaid(images)}

## Base Layer

| Image | Built on | What it gives you |
|-------|----------|-------------------|
{base_rows}

**base-exec** is the default. The app is the container's command (`CMD`),
so its exit is the container's exit, and the runtime does the restarting,
stopping, health checks and logs. Appliances that bundle several services
(an app behind nginx, an app with its own database) use **base-rcd**, where
rcd starts the services in order and restarts any that crash.

Both run the same setup before the app starts: PUID/PGID remap the `bsd`
user, then the scripts in `/daemonless/init.d` and your own in
`/daemonless/custom.d`. See [Development](guides/development.md) for how an
image is put together.

## Intermediate Layers

| Image | Built on | Purpose |
|-------|----------|---------|
{inter_rows}

## Build Order

When an image changes, the images built on it are rebuilt:

1. **base-core** changes: rebuild everything
2. **base-exec** or **base-rcd** changes: rebuild the images on it
3. An intermediate image changes: rebuild its children only

## Images by Parent

{groups_md}
"""


def main():
    images = discover()
    page = generate_page(images)
    if "--stdout" in sys.argv:
        print(page)
        return
    OUTPUT.write_text(page)
    print(f"Wrote {OUTPUT} ({len(images)} images)")


if __name__ == "__main__":
    main()
