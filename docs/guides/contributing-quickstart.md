---
title: "Contributing Quickstart: Build Your First FreeBSD Container Image"
description: "A 10-minute guide to setting up your environment, building a daemonless container image, and submitting your first contribution."
---

# Contributing Quickstart

Welcome to Daemonless! Whether you're fixing a bug in an existing image or bringing a completely new service to the FreeBSD container ecosystem, this guide will get you set up and submitting your first Pull Request in under 10 minutes.

---

## 1. Environment Setup

Before you start building, you need to prepare your FreeBSD host.

### Prerequisites

- **FreeBSD Host** (physical machine or VM).
- A GitHub account.

### Installation

Install the required tools, the `dbuild` engine, and optionally the testing dependencies.

```bash { linenums="0" }
pkg install dbuild podman-suite ocijail jq security/trivy devel/py-pyyaml devel/git
# Optional: for screenshot-based visual regression testing
pkg install chromium www/py-selenium graphics/py-scikit-image # (1)!
```

1.  **Optional:** Only required if you intend to run screenshot-based visual regression tests locally.

### Clone the Repositories

The Daemonless project is organized into multiple repositories under the `@daemonless` organization. You'll need the main repository for scripts and documentation.

```bash { linenums="0" }
git clone https://github.com/daemonless/daemonless
cd daemonless
```

!!! tip "Clone the entire fleet"
    To clone all daemonless image repositories at once, you must first install the GitHub CLI (`pkg install gh`), then run:
    ```bash { linenums="0" }
    gh repo list daemonless --no-archived -L 1000 | awk '{print $1}' | while read repo; do git clone "https://github.com/$repo.git"; done
    ```

### Verify Setup

Ensure everything is configured correctly:

```bash { linenums="0" }
dbuild ci-test-env
```

---

## 2. Your First Contribution

Daemonless uses a standardized toolchain. Choose your path below:

=== "Create a New Image"

    1. **Scaffold the project:** Use `dbuild init` to generate the boilerplate.
    ```bash { linenums="0" }
    mkdir myapp && cd myapp
    git init
    dbuild init
    ```
    2. **Configure Metadata:** Edit `compose.yaml` to define the `x-daemonless` metadata (title, category, ports, volumes, etc.).
    3. **Edit the Containerfiles:** Define how your app installs and runs in `Containerfile` and `Containerfile.pkg`. See [Containerfile Patterns](development.md#containerfile-patterns).
    4. **Fetch Assets & Generate Docs:** Run `dbuild logo` (used in the app grid), `dbuild screenshot` (used on the website to showcase the app), and `dbuild baseline` (used for CIT visual regression tests) to pull down the app's visual assets. Then, run `dbuild generate` to auto-generate the `README.md` and inject labels into the Containerfiles.
    5. **Configure testing:** Edit `.daemonless/config.yaml` to define how the image should be tested.

=== "Update an Existing Image"

    1. **Find the repository:** Each image has its own repository (e.g., `@daemonless/radarr`).
    2. **Fork and clone:** Fork the repository on GitHub, then clone it locally.
    ```bash { linenums="0" }
    git clone https://github.com/YOUR_USERNAME/radarr
    cd radarr
    ```
    3. **Make your changes:** Edit `compose.yaml` (if modifying metadata), the `Containerfile`, or service scripts under `root/etc/services.d/`. Always run `dbuild generate` after modifying `compose.yaml`.

---

## 3. Build & Test Loop

We use **CIT** (Container Integration Testing) to ensure every image works natively on FreeBSD. 

Build your image locally:

```bash { linenums="0" }
dbuild build
```

Run the automated tests:

```bash { linenums="0" }
dbuild test
```

!!! tip "Test Modes"
    Tests are defined in `.daemonless/config.yaml`. Most web apps should use `mode: health`. For apps with complex UIs, use `mode: screenshot` to catch visual regressions. See [Quality Gates (CIT)](dbuild/cit.md) for details.

To manually verify your image, run it with Podman:

```bash { linenums="0" }
podman run -d --name test-app -p 8080:8080 localhost/YOUR_IMAGE:build-latest
```

---

## 4. Submitting Your PR

Before you open a Pull Request, run through this checklist to ensure a smooth review process:

### Pre-Flight Checklist

- [ ] **License Check:** Upstream license verified using the [SPDX identifier](https://spdx.org/licenses/). Never guess a license; if none exists, use `NOASSERTION`.
- [ ] **Metadata Sync:** `dbuild generate` has been run to sync `compose.yaml` metadata into `Containerfile`, `Containerfile.pkg`, and `README.md`.
- [ ] **Permissions:** Run scripts (`root/etc/services.d/<app>/run`) use `s6-setuidgid bsd` so the app doesn't run as root.
- [ ] **Testing:** `.daemonless/config.yaml` is configured and `dbuild test` passes locally.
- [ ] **CI Pipeline:** `.github/workflows/` is present and configured (Woodpecker is maintained as a fallback Plan B).

### How to Submit

**For existing images:** Push your branch to your fork and open a Pull Request against the `main` branch of the respective repository. Our CI will automatically run the CIT suite against your changes.

**For new images:** You cannot open a PR until a repository exists in the Daemonless organization! Please hop on our [Discord](https://discord.gg/Kb9tkhecZT) and ask us to create a new repository for your image. Once created, you can push your scaffolded project there.

---

## 5. Golden Rules & Conventions

To keep the fleet consistent, adhere to these core rules:

*   **Use `fetch`:** FreeBSD provides `fetch` in the base system. Do not install or use `curl`/`wget` unless absolutely necessary.
*   **Clean Caches:** Always clean up after installing packages: `pkg clean -ay && rm -rf /var/cache/pkg/*`.
*   **Permissions:** Use `chown -R bsd:bsd /config /app` in your Containerfile.
*   **Configuration:** Always use `/config` as the persistent volume mount point.

For the complete list of rules, labels, and architectural details, read the full **[Development Guide](development.md)**.

---

## Need Help?

Stuck on a build error or have questions about ocijail? Join us on [Discord](https://discord.gg/Kb9tkhecZT) — it's the fastest way to get help from the Daemonless community.