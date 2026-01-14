---
title: "Sonarr on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Sonarr on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  SONARR_PORT:
    default: "8989"
    description: Sonarr Host Port
---

# :material-television: Sonarr

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/sonarr/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/sonarr/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/sonarr?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/sonarr/commits)

Sonarr TV series management on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **Upstream Binary**. Downloads the official release. | Most users. Matches Linux Docker behavior. |
| `pkg` | **FreeBSD Port**. Installs from Quarterly ports. | Stability. Uses system libraries. |
| `pkg-latest` | **FreeBSD Port**. Installs from Latest ports. | Bleeding edge system packages. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.
!!! warning "Memory Locking (Critical)"
    This application is built on .NET and requires memory locking enabled in the jail.
    You **must** use the `allow.mlock` annotation and have a [patched ocijail](../guides/ocijail-patch.md).

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      sonarr:
        image: ghcr.io/daemonless/sonarr:latest
        container_name: sonarr
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@SONARR_CONFIG_PATH@:/config
          - @TV_PATH@:/tv # optional
          - @DOWNLOADS_PATH@:/downloads # optional
        ports:
          - @SONARR_PORT@:8989
        annotations:
          org.freebsd.jail.allow.mlock: "true"
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name sonarr \
      -p @SONARR_PORT@:8989 \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@SONARR_CONFIG_PATH@:/config \ 
      -v @TV_PATH@:/tv \  # optional
      -v @DOWNLOADS_PATH@:/downloads \  # optional
      ghcr.io/daemonless/sonarr:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy sonarr
      containers.podman.podman_container:
        name: sonarr
        image: ghcr.io/daemonless/sonarr:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@SONARR_PORT@:8989"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@SONARR_CONFIG_PATH@:/config"
          - "@TV_PATH@:/tv" # optional
          - "@DOWNLOADS_PATH@:/downloads" # optional
        annotation:
          org.freebsd.jail.allow.mlock: "true"
    ```

Access the Web UI at: `http://localhost:@SONARR_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |
| `/tv` | TV Series library (Optional) |
| `/downloads` | Download directory (Optional) |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8989` | TCP | Web UI |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).
    - **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` and a [patched ocijail](../guides/ocijail-patch.md).

[Website](https://sonarr.tv/){ .md-button .md-button--primary }
[Source Code](https://github.com/Sonarr/Sonarr){ .md-button }
[FreshPorts](https://www.freshports.org/net-p2p/sonarr/){ .md-button }