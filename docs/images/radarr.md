---
title: "Radarr on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Radarr on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  RADARR_PORT:
    default: "7878"
    description: Radarr Host Port
---

# :material-movie: Radarr

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/radarr/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/radarr/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/radarr?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/radarr/commits)

Radarr movie management on FreeBSD.

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
      radarr:
        image: @REGISTRY@/radarr:latest
        container_name: radarr
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@RADARR_CONFIG_PATH@:/config
          - @MOVIES_PATH@:/movies # optional
          - @DOWNLOADS_PATH@:/downloads # optional
        ports:
          - @RADARR_PORT@:7878
        annotations:
          org.freebsd.jail.allow.mlock: "true"
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name radarr \
      -p @RADARR_PORT@:7878 \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@RADARR_CONFIG_PATH@:/config \ 
      -v @MOVIES_PATH@:/movies \  # optional
      -v @DOWNLOADS_PATH@:/downloads \  # optional
      @REGISTRY@/radarr:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy radarr
      containers.podman.podman_container:
        name: radarr
        image: @REGISTRY@/radarr:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@RADARR_PORT@:7878"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@RADARR_CONFIG_PATH@:/config"
          - "@MOVIES_PATH@:/movies" # optional
          - "@DOWNLOADS_PATH@:/downloads" # optional
        annotation:
          org.freebsd.jail.allow.mlock: "true"
    ```

Access the Web UI at: `http://localhost:@RADARR_PORT@`

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
| `/movies` | Movie library (Optional) |
| `/downloads` | Download directory (Optional) |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `7878` | TCP | Web UI |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).
    - **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` and a [patched ocijail](../guides/ocijail-patch.md).

[Website](https://radarr.video/){ .md-button .md-button--primary }
[Source Code](https://github.com/Radarr/Radarr){ .md-button }
[FreshPorts](https://www.freshports.org/net-p2p/radarr/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.