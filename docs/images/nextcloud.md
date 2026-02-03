---
title: "Nextcloud on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Nextcloud on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  NEXTCLOUD_PORT:
    default: "8082"
    description: Nextcloud Host Port
---

# :simple-nextcloud: Nextcloud

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/nextcloud/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/nextcloud/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/nextcloud?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/nextcloud/commits)

Nextcloud self-hosted cloud on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **FreeBSD Port**. Installs from latest packages. | Most users. Matches Linux Docker behavior. |
| `pkg` | **FreeBSD Port**. Installs from Quarterly ports. | Stability. Uses system libraries. |
| `pkg-latest` | **FreeBSD Port**. Installs from Latest ports. | Bleeding edge system packages. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      nextcloud:
        image: @REGISTRY@/nextcloud:latest
        container_name: nextcloud
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@NEXTCLOUD_CONFIG_PATH@:/config
          - @CONTAINER_CONFIG_ROOT@/@NEXTCLOUD_DATA_PATH@:/data
        ports:
          - @NEXTCLOUD_PORT@:8082
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name nextcloud \
      -p @NEXTCLOUD_PORT@:8082 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@NEXTCLOUD_CONFIG_PATH@:/config \ 
      -v @CONTAINER_CONFIG_ROOT@/@NEXTCLOUD_DATA_PATH@:/data \ 
      @REGISTRY@/nextcloud:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy nextcloud
      containers.podman.podman_container:
        name: nextcloud
        image: @REGISTRY@/nextcloud:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@NEXTCLOUD_PORT@:8082"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@NEXTCLOUD_CONFIG_PATH@:/config"
          - "@CONTAINER_CONFIG_ROOT@/@NEXTCLOUD_DATA_PATH@:/data"
    ```

Access the Web UI at: `http://localhost:@NEXTCLOUD_PORT@`

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
| `/config` | Configuration and application files |
| `/data` | User data storage |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8082` | TCP |  |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://nextcloud.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/nextcloud/server){ .md-button }
[FreshPorts](https://www.freshports.org/www/nextcloud/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.