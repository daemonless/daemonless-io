---
title: "Immich Machine Learning on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Immich Machine Learning on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  IMMICH_ML_PORT:
    default: "3003"
    description: Immich Machine Learning Host Port
---

# :material-brain: Immich Machine Learning

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/immich-ml/build.yml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/immich-ml/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/immich-ml?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/immich-ml/commits)

Immich Machine Learning service (Python/ONNX) on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **Upstream Binary**. Downloads the official release. | Most users. Matches Linux Docker behavior. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      immich-ml:
        image: ghcr.io/daemonless/immich-ml:latest
        container_name: immich-ml
        environment:
          - MACHINE_LEARNING_HOST=0.0.0.0
          - MACHINE_LEARNING_PORT=3003
          - MACHINE_LEARNING_CACHE_FOLDER=/cache
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@IMMICH_ML_CACHE_PATH@:/cache
          - @CONTAINER_CONFIG_ROOT@/@IMMICH_ML_CONFIG_PATH@:/config
        ports:
          - @IMMICH_ML_PORT@:3003
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name immich-ml \
      -p @IMMICH_ML_PORT@:3003 \
      -e MACHINE_LEARNING_HOST=0.0.0.0 \
      -e MACHINE_LEARNING_PORT=3003 \
      -e MACHINE_LEARNING_CACHE_FOLDER=/cache \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@IMMICH_ML_CACHE_PATH@:/cache \ 
      -v @CONTAINER_CONFIG_ROOT@/@IMMICH_ML_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/immich-ml:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy immich-ml
      containers.podman.podman_container:
        name: immich-ml
        image: ghcr.io/daemonless/immich-ml:latest
        state: started
        restart_policy: always
        env:
          MACHINE_LEARNING_HOST: "0.0.0.0"
          MACHINE_LEARNING_PORT: "3003"
          MACHINE_LEARNING_CACHE_FOLDER: "/cache"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@IMMICH_ML_PORT@:3003"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@IMMICH_ML_CACHE_PATH@:/cache"
          - "@CONTAINER_CONFIG_ROOT@/@IMMICH_ML_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@IMMICH_ML_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MACHINE_LEARNING_HOST` | `0.0.0.0` | Host to bind to (0.0.0.0) |
| `MACHINE_LEARNING_PORT` | `3003` | Port to bind to (3003) |
| `MACHINE_LEARNING_CACHE_FOLDER` | `/cache` | Path to cache folder (/cache) |
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |

### Volumes

| Path | Description |
|------|-------------|
| `/cache` | Model cache directory (HuggingFace) |
| `/config` | Configuration directory (unused but mounted) |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3003` | TCP | ML API |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://immich.app/){ .md-button .md-button--primary }
[Source Code](https://github.com/immich-app/immich){ .md-button }
