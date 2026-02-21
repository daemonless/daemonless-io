---
title: "Contributing Quickstart: Build Your First FreeBSD Container Image"
description: "A 10-minute guide to setting up your environment, building a daemonless container image, and submitting your first contribution."
---

# Contributing Quickstart

A 10-minute guide to building and testing your first FreeBSD container image.

## Prerequisites

- **FreeBSD** (physical host or VM with Podman access)
- **Python 3.11+** and **git**
- **Podman** with **ocijail** runtime
- A GitHub account (for forking and PRs)

!!! tip "Check your environment"
    After installing dbuild, run `dbuild ci-test-env` to verify all required tools, networking, and jail support are in place.

## Setup (~5 minutes)

### 1. Clone the repos

```bash
# The main project (scripts, docs, version tracking)
git clone https://github.com/daemonless/daemonless

# The build tool
git clone https://github.com/daemonless/dbuild

# An image repo to use as a reference
git clone https://github.com/daemonless/tautulli
```

### 2. Install dependencies

```bash
# Core build tools
pkg install podman buildah skopeo jq trivy py311-pyyaml

# Optional: for screenshot-based visual regression testing
pkg install chromium py311-selenium py311-scikit-image
```

### 3. Install dbuild

```bash
cd dbuild
make install
```

Or manually:

```bash
pkg install py311-pyyaml
export PYTHONPATH=/path/to/dbuild
alias dbuild='python3 -m dbuild'
```

!!! tip "Alternative: pip install"
    You can also install dbuild via pip if you prefer:
    ```bash
    cd dbuild
    pip install .
    ```

### 3. Verify your environment

```bash
dbuild ci-test-env
```

All required checks should pass. Optional tools (like podman-compose) are only needed for multi-service stacks.

## Your First Image (~5 minutes)

### 1. Scaffold a new image

```bash
mkdir myapp && cd myapp
git init
dbuild init
```

This creates:

```
myapp/
├── Containerfile           # Build from upstream binaries (:latest tag)
├── Containerfile.pkg       # Build from FreeBSD packages (:pkg tag)
├── .daemonless/
│   └── config.yaml         # Build + test configuration
├── .woodpecker.yaml        # CI/CD pipeline (or .github/workflows/)
└── root/                   # Files copied into container
    └── etc/
        ├── cont-init.d/    # Initialization scripts
        └── services.d/     # s6 service definitions
            └── myapp/
                └── run     # Service start script
```

!!! info "Repository structure"
    Each image is a standalone git repo with this layout. See the [Development Guide](development.md#repository-structure) for a detailed walkthrough.

### 2. Build it

```bash
dbuild build
```

### 3. Test it

```bash
dbuild test
```

### 4. Run it manually

```bash
podman run -d --name myapp \
  -p 8080:8080 \
  -e PUID=1000 -e PGID=1000 \
  -v /tmp/myapp-config:/config \
  localhost/myapp:build-latest
```

## Contribution Types

| Type | Description | Where |
|------|-------------|-------|
| **New images** | Package a new application as a FreeBSD container | New repo under `daemonless/` |
| **Image fixes** | Bug fixes or improvements to existing images | The image's repo |
| **Tooling** | Improvements to dbuild or CIT | `daemonless/dbuild` |
| **Documentation** | Guides, corrections, image docs | `daemonless/daemonless-io` |

## Image Checklist

Before submitting a new image, verify:

- [x] `Containerfile` with required labels (`io.daemonless.port`, `io.daemonless.category`, `io.daemonless.packages`)
- [x] `Containerfile.pkg` with matching labels (keep both in sync)
- [x] `root/etc/services.d/<app>/run` — s6 service script using `s6-setuidgid bsd`
- [x] `.daemonless/config.yaml` with CIT test configuration
- [x] CI pipeline configured (`.woodpecker.yaml` or `.github/workflows/`)
- [x] Upstream license verified — check the [SPDX identifier](https://spdx.org/licenses/)
- [x] `dbuild build && dbuild test` passes locally

!!! warning "Never guess a license"
    Always check the upstream repository's LICENSE file and verify the SPDX identifier. Common licenses: MIT, Apache-2.0, GPL-3.0, AGPL-3.0, BSD-3-Clause.

## Conventions

### Containerfile rules

- Use `fetch`, not `curl` — FreeBSD base includes `fetch`
- Clean the pkg cache: `pkg clean -ay && rm -rf /var/cache/pkg/*`
- Set ownership: `chown -R bsd:bsd /config /app`
- Use `ARG` for `BASE_VERSION`, `PACKAGES`, and `VERSION`
- Use `.j2` templates — run `dbuild generate` after changes

!!! note "Containerfile patterns"
    Daemonless uses three Containerfile patterns: **standard** (upstream binaries), **package** (FreeBSD packages), and **multi-stage** (compiled apps). See the [Development Guide](development.md#containerfile-patterns) for templates of each.

### Runtime conventions

- Run services as `bsd` user via `s6-setuidgid bsd`
- Support `PUID`, `PGID`, and `TZ` environment variables
- Use `/config` as the configuration volume
- Use `exec` in run scripts for proper signal handling

### Labels

Every image needs at minimum:

```dockerfile
LABEL io.daemonless.port="8080"
LABEL io.daemonless.category="Utilities"
LABEL io.daemonless.packages="${PACKAGES}"
```

See the [Labels Reference](development.md#labels-reference) for the full list of `io.daemonless.*` and OCI labels.

## Testing

All images must pass CIT (Container Integration Testing) before push. CIT has four cumulative modes:

| Mode | Checks | Use case |
|------|--------|----------|
| `shell` | Container starts, exec works | Base images, CLI tools |
| `port` | Shell + TCP port listening | Network services |
| `health` | Port + HTTP endpoint responds | Web apps |
| `screenshot` | Health + visual regression | Web UIs |

Configure your test mode in `.daemonless/config.yaml`:

```yaml
cit:
  mode: health
  port: 8080
  health: /api/health
```

Run tests locally:

```bash
dbuild build && dbuild test
```

!!! tip "Choosing a test mode"
    Most web applications should use `health` mode. Use `screenshot` mode for apps with a web UI where visual regressions matter. See the [Quality Gates (CIT)](cit.md) guide for the full configuration reference.

## Submitting Changes

1. **Fork** the image repo on GitHub
2. **Branch** from `main`
3. **Build and test** locally with `dbuild build && dbuild test`
4. **Open a PR** — CI runs CIT automatically
5. All CIT gates must pass before merge

## Get Help

Stuck on something? Join us on [Discord](https://discord.gg/PTg5DJ2y) — it's the fastest way to get help from the community.

## Further Reading

- [Development Guide](development.md) — Full architecture, labels reference, Containerfile patterns
- [dbuild](dbuild.md) — Complete build engine documentation
- [Quality Gates (CIT)](cit.md) — Test modes, configuration, visual regression
- [CI/CD Pipeline](ci-cd.md) — CI integration and pipeline details
- [Image Tagging](tagging.md) — Tag conventions and version strategy
- [OCI Compliance](oci-compliance.md) — Label standards and SBOM
