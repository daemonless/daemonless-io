---
title: "Organizr on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Organizr on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  ORGANIZR_PORT:
    default: "8083"
    description: Organizr Host Port
---

# :material-view-dashboard: Organizr

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/organizr/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/organizr/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/organizr?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/organizr/commits)

HTPC/Homelab Services Organizer on FreeBSD.

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
      organizr:
        image: ghcr.io/daemonless/organizr:latest
        container_name: organizr
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@ORGANIZR_CONFIG_PATH@:/config
        ports:
          - @ORGANIZR_PORT@:8083
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name organizr \
      -p @ORGANIZR_PORT@:8083 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@ORGANIZR_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/organizr:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy organizr
      containers.podman.podman_container:
        name: organizr
        image: ghcr.io/daemonless/organizr:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@ORGANIZR_PORT@:8083"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@ORGANIZR_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@ORGANIZR_PORT@`

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
| `/config` | Configuration directory (database, logos) |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8083` | TCP |  |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://organizr.app/){ .md-button .md-button--primary }
[Source Code](https://github.com/causefx/Organizr){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.