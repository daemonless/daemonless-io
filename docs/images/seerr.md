---
title: "Seerr on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Seerr on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  SEERR_PORT:
    default: "5055"
    description: Seerr Host Port
---

# :material-eye: Seerr

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/seerr/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/seerr/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/seerr?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/seerr/commits)

Unified media request management (Plex, Jellyfin, Emby) on FreeBSD.

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
      seerr:
        image: @REGISTRY@/seerr:latest
        container_name: seerr
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@SEERR_CONFIG_PATH@:/config
        ports:
          - @SEERR_PORT@:5055
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name seerr \
      -p @SEERR_PORT@:5055 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@SEERR_CONFIG_PATH@:/config \ 
      @REGISTRY@/seerr:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy seerr
      containers.podman.podman_container:
        name: seerr
        image: @REGISTRY@/seerr:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@SEERR_PORT@:5055"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@SEERR_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@SEERR_PORT@`

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
| `/config` | Configuration and database directory |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `5055` | TCP | Web UI |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://seerr.io/){ .md-button .md-button--primary }
[Source Code](https://github.com/seerr-team/seerr){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/Kb9tkhecZT) community.