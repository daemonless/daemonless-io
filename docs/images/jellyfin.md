---
title: "Jellyfin on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Jellyfin on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  JELLYFIN_PORT:
    default: "8096"
    description: Jellyfin Host Port
---

# :simple-jellyfin: Jellyfin

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/jellyfin/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/jellyfin/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/jellyfin?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/jellyfin/commits)

The Free Software Media System on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **FreeBSD Port**. Installs from latest packages. | Most users. Matches Linux Docker behavior. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.
!!! warning "Memory Locking (Critical)"
    This application is built on .NET and requires memory locking enabled in the jail.
    You **must** use the `allow.mlock` annotation and have a [patched ocijail](../guides/ocijail-patch.md).

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      jellyfin:
        image: ghcr.io/daemonless/jellyfin:latest
        container_name: jellyfin
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@JELLYFIN_CONFIG_PATH@:/config
          - @CONTAINER_CONFIG_ROOT@/@JELLYFIN_CACHE_PATH@:/cache # optional
          - @TV_PATH@:/tv # optional
          - @MOVIES_PATH@:/movies # optional
        ports:
          - @JELLYFIN_PORT@:8096
        annotations:
          org.freebsd.jail.allow.mlock: "true"
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name jellyfin \
      -p @JELLYFIN_PORT@:8096 \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@JELLYFIN_CONFIG_PATH@:/config \ 
      -v @CONTAINER_CONFIG_ROOT@/@JELLYFIN_CACHE_PATH@:/cache \  # optional
      -v @TV_PATH@:/tv \  # optional
      -v @MOVIES_PATH@:/movies \  # optional
      ghcr.io/daemonless/jellyfin:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy jellyfin
      containers.podman.podman_container:
        name: jellyfin
        image: ghcr.io/daemonless/jellyfin:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@JELLYFIN_PORT@:8096"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@JELLYFIN_CONFIG_PATH@:/config"
          - "@CONTAINER_CONFIG_ROOT@/@JELLYFIN_CACHE_PATH@:/cache" # optional
          - "@TV_PATH@:/tv" # optional
          - "@MOVIES_PATH@:/movies" # optional
        annotation:
          org.freebsd.jail.allow.mlock: "true"
    ```

Access the Web UI at: `http://localhost:@JELLYFIN_PORT@`

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
| `/cache` | Cache directory (Optional) |
| `/tv` | TV Series library (Optional) |
| `/movies` | Movie library (Optional) |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8096` | TCP | Web UI |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).
    - **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` and a [patched ocijail](../guides/ocijail-patch.md).

[Website](https://jellyfin.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/jellyfin/jellyfin){ .md-button }
[FreshPorts](https://www.freshports.org/multimedia/jellyfin/){ .md-button }