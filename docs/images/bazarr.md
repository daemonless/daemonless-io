---
title: "Bazarr on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Bazarr on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  BAZARR_PORT:
    default: "6767"
    description: Bazarr Host Port
---

# :material-subtitle: Bazarr

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/bazarr/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/bazarr/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/bazarr?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/bazarr/commits)

Bazarr is a companion application to Sonarr and Radarr. It can manage and download subtitles based on your requirements. You define your preferences by TV show or movie and Bazarr takes care of everything for you.

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
      bazarr:
        image: @REGISTRY@/bazarr:latest
        container_name: bazarr
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@BAZARR_CONFIG_PATH@:/config
          - @MOVIES_PATH@:/movies # optional
          - @TV_PATH@:/tv # optional
        ports:
          - @BAZARR_PORT@:6767
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name bazarr \
      -p @BAZARR_PORT@:6767 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@BAZARR_CONFIG_PATH@:/config \ 
      -v @MOVIES_PATH@:/movies \  # optional
      -v @TV_PATH@:/tv \  # optional
      @REGISTRY@/bazarr:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy bazarr
      containers.podman.podman_container:
        name: bazarr
        image: @REGISTRY@/bazarr:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@BAZARR_PORT@:6767"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@BAZARR_CONFIG_PATH@:/config"
          - "@MOVIES_PATH@:/movies" # optional
          - "@TV_PATH@:/tv" # optional
    ```

Access the Web UI at: `http://localhost:@BAZARR_PORT@`

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
| `/movies` | Movie library (should match Radarr) (Optional) |
| `/tv` | TV library (should match Sonarr) (Optional) |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `6767` | TCP | Web UI |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://www.bazarr.media/){ .md-button .md-button--primary }
[Source Code](https://github.com/morpheus65535/bazarr){ .md-button }
[FreshPorts](https://www.freshports.org/net-p2p/bazarr/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/Kb9tkhecZT) community.