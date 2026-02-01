---
title: "Tautulli on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Tautulli on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  TAUTULLI_PORT:
    default: "8181"
    description: Tautulli Host Port
---

# :simple-plex: Tautulli

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/tautulli/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/tautulli/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/tautulli?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/tautulli/commits)

Tautulli Plex monitoring on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **Upstream Binary**. Downloads the official release. | Most users. Matches Linux Docker behavior. |
| `pkg` | **FreeBSD Port**. Installs from Quarterly ports. | Stability. Uses system libraries. |
| `pkg-latest` | **FreeBSD Port**. Installs from Latest ports. | Bleeding edge system packages. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      tautulli:
        image: @REGISTRY@/tautulli:latest
        container_name: tautulli
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - TAUTULLI_DOCKER=True
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@TAUTULLI_CONFIG_PATH@:/config
        ports:
          - @TAUTULLI_PORT@:8181
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name tautulli \
      -p @TAUTULLI_PORT@:8181 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e TAUTULLI_DOCKER=True \
      -v @CONTAINER_CONFIG_ROOT@/@TAUTULLI_CONFIG_PATH@:/config \ 
      @REGISTRY@/tautulli:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy tautulli
      containers.podman.podman_container:
        name: tautulli
        image: @REGISTRY@/tautulli:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          TAUTULLI_DOCKER: "True"
        ports:
          - "@TAUTULLI_PORT@:8181"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@TAUTULLI_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@TAUTULLI_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `TAUTULLI_DOCKER` | `True` | Disable internal updater (True/False) |


### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8181` | TCP | Web UI |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://tautulli.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/Tautulli/Tautulli){ .md-button }
[FreshPorts](https://www.freshports.org/multimedia/tautulli/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.