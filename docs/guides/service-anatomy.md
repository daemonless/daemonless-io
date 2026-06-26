---
title: "Service Source Files"
description: "What compose.yaml, .daemonless/config.yaml, Containerfile templates, and root files are for in a Daemonless service repository."
---

# Service Source Files

## What Each File Is For

**`compose.yaml` is the public service definition.** It names the image, describes it, documents the ports/volumes/env vars, and provides the deployment example users copy from the README and website.

**`.daemonless/config.yaml` is the `dbuild` control file.** It tells automation which variants to build and how CIT should test the image.

**`Containerfile*.j2` is the image recipe.** It says which base image to use, which packages to install, how upstream bits are fetched, and what labels or build-time values the generated `Containerfile` needs.

**`root/` is the filesystem overlay.** Files here are copied into the image, including s6 service scripts, init scripts, default configs, and helper scripts.

Generated files such as `Containerfile`, `Containerfile.pkg`, and `README.md` are outputs from `dbuild generate`. Change the source file, then regenerate.

## `compose.yaml`

Use this for the service contract people see and run:

- `name`
- `x-daemonless.title`, `description`, `category`, `icon`, and project links
- documented ports, volumes, and environment variables
- the example service definition
- production annotations and AppJail settings

If it appears in the README, image index, generated labels, or deployment example, it belongs here. Do not duplicate this metadata in `.daemonless/config.yaml`.

## `.daemonless/config.yaml`

Use this for `dbuild` automation:

- build variants such as `latest`, `pkg`, and `pkg-latest`
- variant template targets and architectures
- CIT mode, probe port, health path, ready timeout, and screenshots
- test-only annotations or compose-stack settings

This file should explain how CI builds and proves the image. It should not become a second metadata file for title, category, icon, or user docs.

## `Containerfile*.j2`

Use templates for image assembly:

- base image selection
- package installation
- upstream fetch and version extraction logic
- generated build args and labels
- copy steps for files under `root/`

The generated `Containerfile` should get standard labels from `dbuild generate`; avoid hardcoding labels that are already derived from `compose.yaml`.

## `root/`

Use this for files that need to exist inside the image:

- `etc/services.d/<service>/run` scripts
- `etc/cont-init.d/` initialization scripts
- default config files
- healthcheck helpers
- permission or ownership setup scripts

If changing the file changes what is inside the built image at runtime, it belongs in `root/` or in the template instructions that copy it.

## Common Boundaries

**Ports:** put public ports in `compose.yaml`. Set `cit.port` only when the test target differs from the public port.

**Health checks:** put the runtime healthcheck in `compose.yaml`. Set `cit.health` only when tests need a different endpoint.

**Jail settings:** put production jail/AppJail settings in `compose.yaml`. Use `cit.annotations` only for test-only permissions.

**Upstream URLs:** put human-facing website, source, and FreshPorts links in `compose.yaml`. Put machine-facing version endpoints and filters in `Containerfile*.j2`.

**Package versions:** preserve the version reported by `pkg`; do not strip FreeBSD revision suffixes such as `_1` from generated version labels.

See also: [Development Guide](development.md), [Building Your First Image](dbuild/workflow.md), and [Configuration Reference](dbuild/config.md).
