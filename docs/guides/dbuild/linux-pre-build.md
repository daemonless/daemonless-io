---
title: "Linux Pre-Build Artifacts for FreeBSD Images"
description: "How to build Linux-only toolchain artifacts (e.g. SWC/pnpm frontends) on a Linux runner and inject them into a FreeBSD container build."
---

# Linux Pre-Build Artifacts

Some applications embed assets that must be compiled with toolchains unavailable on FreeBSD.
The most common case is a **JavaScript/TypeScript frontend** that uses [SWC](https://swc.rs/) —
a Rust-based JS compiler that ships prebuilt binaries only for Linux and macOS.

Rather than committing built assets to the repository, Daemonless builds them on a Linux
GitHub Actions runner and passes them to the FreeBSD build as an artifact.

Critically, **the built assets don't need to run on Linux** — they are static files (HTML,
CSS, JS bundles) or data embedded into a native FreeBSD binary at compile time. The Linux
toolchain is only needed to produce those assets; the final container image contains only
the FreeBSD binary that embeds them.

## When You Need This

You need a Linux pre-build step when your container build requires assets that depend on:

- **SWC / Next.js** — no FreeBSD binary, WASM fallback unreliable in some versions
- **pnpm / npm** with native addons that only target Linux
- Any other tool that explicitly does not support FreeBSD

If the asset can be built on FreeBSD (e.g. plain Go, Rust, or Python), you don't need this pattern.

## How It Works

GitHub Actions artifacts are scoped to the **workflow run ID**. When a caller workflow
invokes a reusable workflow (`daemonless-build.yaml`), both run under the same run ID.
This means a job in the caller can upload an artifact, and a job inside the reusable
workflow can download it by name — no URLs, no cross-repo magic.

```
build-web (ubuntu-latest)          build (FreeBSD VM)
─────────────────────────          ──────────────────────────────────────
pnpm install && pnpm build   →  artifact store (run-scoped)
upload-artifact: web-dist          download-artifact: web-dist → web/dist/
                                   vmactions/freebsd-vm syncs web/dist/
                                   cargo build (embeds web/dist at compile time)
```

## Implementation

### 1. Add a `build-web` job to your `build.yaml`

```yaml
jobs:
  build-web:
    runs-on: ubuntu-latest
    steps:
      - name: Get latest upstream tag
        id: tag
        run: |
          TAG=$(git ls-remote --tags --sort="v:refname" \
            https://github.com/upstream/myapp.git | \
            grep -v '\^{}' | tail -n1 | sed 's/.*\///')
          echo "tag=${TAG}" >> $GITHUB_OUTPUT

      - uses: actions/checkout@v4
        with:
          repository: upstream/myapp
          ref: ${{ steps.tag.outputs.tag }}

      - uses: pnpm/action-setup@v4
        with:
          version: 9          # pin to match upstream lockfile version

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Build frontend
        run: cd web && pnpm install && pnpm run build

      - name: Upload web/dist
        uses: actions/upload-artifact@v4
        with:
          name: web-dist
          path: web/dist/
```

### 2. Pass the artifact into the reusable build

```yaml
  build:
    needs: build-web
    uses: daemonless/dbuild/.github/workflows/daemonless-build.yaml@main
    with:
      image_name: myapp
      pre_artifact_name: web-dist
      pre_artifact_path: web/dist/
    secrets: inherit
```

The reusable workflow downloads the artifact into `web/dist/` on the Linux runner
**before** `vmactions/freebsd-vm` runs. Because vmactions syncs the entire workspace
into the FreeBSD VM, `web/dist/` is available to `podman build` / `buildah` just like
any other checked-out file.

### 3. Reference the artifact in your `Containerfile.j2`

```dockerfile
# Note: web/dist is built on Linux (build-web CI job) and passed as an
# artifact. SWC is not available on FreeBSD.
# This directory is embedded into the binary at compile time.
COPY web/dist /build/web/dist
```

### 4. Exclude `web/dist` from the repository

Since assets are now built in CI, they should not be committed:

```gitignore
# web/dist is built by CI (build-web job) and passed as an artifact
web/dist/
```

Remove any previously committed assets:

```bash
git rm -r --cached web/dist
git commit -m "Remove committed web/dist - now built by CI"
```

## pnpm Version

`pnpm/action-setup@v4` requires an explicit version if the upstream repository does not
set `packageManager` in `package.json`. Check the upstream lockfile header:

```bash
head -1 web/pnpm-lock.yaml
# lockfileVersion: '9.0'  →  use pnpm version 9
```

## Determining the lockfile version → pnpm version

| lockfileVersion | pnpm version |
|-----------------|--------------|
| `'6.0'`         | pnpm 6       |
| `'7.0'`         | pnpm 7       |
| `'8.0'` / `9.0` was backported | pnpm 8 |
| `'9.0'`         | pnpm 9       |

## Real Example

[bichon](https://github.com/daemonless/bichon) embeds a React frontend that is compiled
with SWC. The `build-web` job checks out the upstream `rustmailer/bichon` repository at
its latest tag, builds with pnpm, and uploads `web/dist/` as an artifact. The FreeBSD
build then compiles the Rust binary with the frontend embedded via `include_dir!()`.
