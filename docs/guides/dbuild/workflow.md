---
title: "Building Your First Image: A Complete Workflow"
description: "A step-by-step walkthrough of creating a FreeBSD container image with dbuild, using Traefik as a real-world example with upstream binary, pkg, and pkg-latest variants."
---

# Building Your First Image: A Complete Workflow

This guide walks through the full lifecycle of creating a new **daemonless** container image, from initialization to GitHub Actions CI/CD.

## Why use `dbuild`?

If you're building FreeBSD container images, `dbuild` provides a standardized, high-trust workflow that bridges the gap between local development and CI/CD:

*   **Jinja2 Power:** Use templates (`.j2`) to keep your `Containerfile` DRY across multiple variants (e.g., `:latest` vs `:pkg`).
*   **Integrated Testing (CIT):** Automatically verify that your container actually *works* (port checks, health endpoints, even screenshots) before pushing.
*   **GitHub-First:** Seamlessly integrates with GitHub Actions and GHCR.io with zero-config reusable workflows.
*   **Local/CI Parity:** The exact same `dbuild build` and `dbuild test` commands run on your laptop and in the cloud.

---

## 1. Prerequisites

- **FreeBSD 14+ or 15+**
- `dbuild` and Podman installed:

```bash
pkg install sysutils/py-dbuild
```
- A **GitHub account** (for pushing images via `ghcr.io`)
- **Optional:** A Woodpecker CI instance for self-hosted builds.

---

## 2. Initialize the Project

Create an empty directory for your image and run `dbuild init`. We'll use **Traefik** as our example:

```bash
mkdir traefik && cd traefik
dbuild init \
  --freebsd-port net/traefik \
  --port 8080 \
  --variants latest,pkg,pkg-latest \
  --github
```

### What just happened?
`dbuild` scaffolded a complete project structure for you:

```text
traefik/
├── .daemonless/
│   └── config.yaml             # Build variants and CIT test config
├── .github/workflows/build.yaml # GitHub Actions CI pipeline
├── compose.yaml                # Image metadata + deployment example
├── Containerfile.j2            # Template for :latest (upstream binary)
├── Containerfile.pkg.j2        # Template for :pkg and :pkg-latest
└── root/
    ├── etc/services.d/traefik/run # s6 service supervisor script
    └── healthz                 # Optional health check script
```

---

## 3. The "Single Source of Truth": `compose.yaml`

In the daemonless ecosystem, `compose.yaml` isn't just for deployment—it's the **source of truth** for your image's metadata and documentation.

Open `compose.yaml` and refine the `x-daemonless` section:

```yaml
name: traefik

x-daemonless:
  title: "Traefik"
  icon: ":material-server-network:"        # Browse icons at pictogrammers.com
  category: "Infrastructure"               # See config reference for categories
  description: "Modern HTTP reverse proxy and load balancer for FreeBSD."
  upstream_url: "https://github.com/traefik/traefik" # Must be the SOURCE repo
  web_url: "https://traefik.io/"
  freshports_url: "https://www.freshports.org/net/traefik/"
  upstream_binary: true                    # Tells dbuild :latest uses binaries
  user: "bsd"

  docs:
    env:
      PUID: "User ID for the application process"
      PGID: "Group ID for the application process"
    volumes:
      /config: "Traefik configuration directory"
    ports:
      80: "HTTP"
      443: "HTTPS"
      8080: "Dashboard / API"

services:
  traefik:
    image: ghcr.io/daemonless/traefik:latest
    # ... rest of deployment config ...
```

---

## 4. Crafting the Templates (`.j2`)

`dbuild` uses Jinja2 templates to generate standard `Containerfile`s. This allows you to inject dynamic labels and reuse logic.

### Edit `Containerfile.j2` (:latest variant)
Replace the placeholder download logic with Traefik's real GitHub releases:

```dockerfile
ARG BASE_VERSION=15
FROM ghcr.io/daemonless/base:${BASE_VERSION}

ARG UPSTREAM_URL="https://api.github.com/repos/traefik/traefik/releases/latest"
ARG UPSTREAM_JQ=".tag_name"

# [dbuild] labels will be automatically injected here

RUN pkg update && pkg install -y ca_root_nss jq && pkg clean -ay

# Fetch version and binary using 'fetch' (FreeBSD native)
RUN TRAEFIK_VERSION=$(fetch -qo - "${UPSTREAM_URL}" | jq -r "${UPSTREAM_JQ}") && \
    fetch -qo /tmp/traefik.tar.gz \
      "https://github.com/traefik/traefik/releases/download/${TRAEFIK_VERSION}/traefik_${TRAEFIK_VERSION}_freebsd_amd64.tar.gz" && \
    tar xzf /tmp/traefik.tar.gz -C /usr/local/bin traefik && \
    chmod +x /usr/local/bin/traefik && \
    mkdir -p /app && echo "${TRAEFIK_VERSION}" > /app/version && \
    rm /tmp/traefik.tar.gz

RUN mkdir -p /config && chown -R bsd:bsd /config

COPY root/ /
```

---

## 5. Generate and Build

The core `dbuild` loop is **Generate → Build → Test**.

### Step A: Generate
Turn your templates and `compose.yaml` into real files:
```bash
dbuild generate
```
*   Updates `Containerfile` and `Containerfile.pkg`
*   Generates a standardized `README.md` from your `compose.yaml`

### Step B: Build Locally
```bash
# Build the default variant
dbuild build

# Build all variants defined in .daemonless/config.yaml
dbuild build --variant latest --variant pkg --variant pkg-latest

# Build all variants in parallel
dbuild build -p

# Limit to 2 concurrent builds
dbuild build -p 2
```

---

## 6. Test with CIT (Container Integration Test)

Don't just assume it works. `dbuild test` spins up the container and runs the checks defined in `.daemonless/config.yaml`:

```yaml
cit:
  mode: health
  port: 8080
  health: /ping
  ready: "Configuration loaded" # Watch logs for this string
```

Run the test:
```bash
dbuild test
```
If the app doesn't bind to port 8080 or the `/ping` endpoint fails, the build is considered "failed".

---

## 7. GitHub Integration: `dbuild + github`

This is where `dbuild` shines. The `.github/workflows/build.yaml` file generated by `dbuild init --github` uses a **reusable workflow**.

### The Workflow File
```yaml
name: Build FreeBSD Container

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    # This delegates EVERYTHING to the shared daemonless engine
    uses: daemonless/dbuild/.github/workflows/daemonless-build.yaml@main
    with:
      image_name: traefik
    secrets: inherit
```

### Why use the Reusable Workflow?
1.  **Managed FreeBSD Runners:** It automatically handles spinning up FreeBSD VMs on GitHub Actions.
2.  **Automatic Matrix:** It calls `dbuild detect` to build all your variants in parallel.
3.  **GHCR.io Auth:** It uses your `GITHUB_TOKEN` to automatically push to `ghcr.io/your-user/traefik`.
4.  **SBOM Generation:** Automatically generates and attaches CycloneDX Software Bill of Materials.

### GitHub "Pro Tips"
*   **Registry:** By default, it pushes to `ghcr.io/{github_actor}/{image_name}`.
*   **Commit Directives:** Control CI behavior directly from your commit messages:
    *   `[skip test]` — Skip CIT (useful for docs-only changes).
    *   `[skip push]` — Build and test, but don't push to the registry.

---

## 8. Summary of Commands

| Command | Description |
|---------|-------------|
| `dbuild init` | Scaffold a new project |
| `dbuild generate` | Update Containerfiles from templates |
| `dbuild build` | Build the container image(s) |
| `dbuild test` | Run Integration Tests (CIT) |
| `dbuild push` | Push to registry (GHCR/DockerHub) |
| `dbuild info` | Show detected variants and config |

---

## Next Steps

*   Learn more about [Quality Gates (CIT)](cit.md).
*   Explore [Multi-Arch Builds](multiarch.md) for amd64 and aarch64.
*   Check the [Config Reference](config.md) for advanced `.daemonless/config.yaml` options.
