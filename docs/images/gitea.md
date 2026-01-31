---
title: "Gitea on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Gitea on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  GITEA_PORT:
    default: "3000"
    description: Gitea Host Port
---

# :simple-gitea: Gitea

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/gitea/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/gitea/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/gitea?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/gitea/commits)

Gitea self-hosted Git service on FreeBSD.

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
      gitea:
        image: ghcr.io/daemonless/gitea:latest
        container_name: gitea
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@GITEA_CONFIG_PATH@:/config
        ports:
          - @GITEA_PORT@:3000
          - 2222:2222
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name gitea \
      -p @GITEA_PORT@:3000 \
      -p 2222:2222 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@GITEA_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/gitea:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy gitea
      containers.podman.podman_container:
        name: gitea
        image: ghcr.io/daemonless/gitea:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@GITEA_PORT@:3000"
          - "2222:2222"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@GITEA_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@GITEA_PORT@`

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
| `/config` | Configuration, repositories, and data directory |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3000` | TCP | Web UI |
| `2222` | TCP |  |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://about.gitea.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/go-gitea/gitea){ .md-button }
[FreshPorts](https://www.freshports.org/www/gitea/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.