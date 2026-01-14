---
title: "Uptime Kuma on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Uptime Kuma on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  UPTIME_KUMA_PORT:
    default: "3001"
    description: Uptime Kuma Host Port
---

# :material-chart-line: Uptime Kuma

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/uptime-kuma/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/uptime-kuma/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/uptime-kuma?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/uptime-kuma/commits)

A fancy self-hosted monitoring tool on FreeBSD.

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
      uptime-kuma:
        image: ghcr.io/daemonless/uptime-kuma:latest
        container_name: uptime-kuma
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - UPTIME_KUMA_IS_CONTAINER=1
          - UPTIME_KUMA_ALLOW_ALL_CHROME_EXEC=1
          - PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
          - DATA_DIR=/config
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@UPTIME_KUMA_CONFIG_PATH@:/config
        ports:
          - @UPTIME_KUMA_PORT@:3001
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name uptime-kuma \
      -p @UPTIME_KUMA_PORT@:3001 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e UPTIME_KUMA_IS_CONTAINER=1 \
      -e UPTIME_KUMA_ALLOW_ALL_CHROME_EXEC=1 \
      -e PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
      -e DATA_DIR=/config \
      -v @CONTAINER_CONFIG_ROOT@/@UPTIME_KUMA_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/uptime-kuma:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy uptime-kuma
      containers.podman.podman_container:
        name: uptime-kuma
        image: ghcr.io/daemonless/uptime-kuma:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          UPTIME_KUMA_IS_CONTAINER: "1"
          UPTIME_KUMA_ALLOW_ALL_CHROME_EXEC: "1"
          PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: "1"
          DATA_DIR: "/config"
        ports:
          - "@UPTIME_KUMA_PORT@:3001"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@UPTIME_KUMA_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@UPTIME_KUMA_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `UPTIME_KUMA_IS_CONTAINER` | `1` |  |
| `UPTIME_KUMA_ALLOW_ALL_CHROME_EXEC` | `1` |  |
| `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` | `1` |  |
| `DATA_DIR` | `/config` |  |
### Volumes

| Path | Description |
|------|-------------|
| `/config` | Data directory (database, settings) |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3001` | TCP | Web UI |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://uptime.kuma.pet/){ .md-button .md-button--primary }
[Source Code](https://github.com/louislam/uptime-kuma){ .md-button }
[FreshPorts](https://www.freshports.org/net-mgmt/uptime-kuma/){ .md-button }