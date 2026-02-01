---
title: "Overseerr on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Overseerr on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  OVERSEERR_PORT:
    default: "5055"
    description: Overseerr Host Port
---

# :material-eye: Overseerr

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/overseerr/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/overseerr/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/overseerr?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/overseerr/commits)

Overseerr media request management on FreeBSD.

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
      overseerr:
        image: @REGISTRY@/overseerr:latest
        container_name: overseerr
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@OVERSEERR_CONFIG_PATH@:/config
        ports:
          - @OVERSEERR_PORT@:5055
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name overseerr \
      -p @OVERSEERR_PORT@:5055 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@OVERSEERR_CONFIG_PATH@:/config \ 
      @REGISTRY@/overseerr:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy overseerr
      containers.podman.podman_container:
        name: overseerr
        image: @REGISTRY@/overseerr:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@OVERSEERR_PORT@:5055"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@OVERSEERR_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@OVERSEERR_PORT@`

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


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `5055` | TCP | Web UI |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://overseerr.dev/){ .md-button .md-button--primary }
[Source Code](https://github.com/sct/overseerr){ .md-button }
[FreshPorts](https://www.freshports.org/www/overseerr/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.