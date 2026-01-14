---
title: "SmokePing on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install SmokePing on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  SMOKEPING_PORT:
    default: "8081"
    description: SmokePing Host Port
---

# :material-pulse: SmokePing

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/smokeping/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/smokeping/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/smokeping?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/smokeping/commits)

SmokePing network latency monitor on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **FreeBSD Port**. Installs from latest packages. | Most users. Matches Linux Docker behavior. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      smokeping:
        image: ghcr.io/daemonless/smokeping:latest
        container_name: smokeping
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@SMOKEPING_CONFIG_PATH@:/config
          - @CONTAINER_CONFIG_ROOT@/@SMOKEPING_DATA_PATH@:/data
        ports:
          - @SMOKEPING_PORT@:8081
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name smokeping \
      -p @SMOKEPING_PORT@:8081 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@SMOKEPING_CONFIG_PATH@:/config \ 
      -v @CONTAINER_CONFIG_ROOT@/@SMOKEPING_DATA_PATH@:/data \ 
      ghcr.io/daemonless/smokeping:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy smokeping
      containers.podman.podman_container:
        name: smokeping
        image: ghcr.io/daemonless/smokeping:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@SMOKEPING_PORT@:8081"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@SMOKEPING_CONFIG_PATH@:/config"
          - "@CONTAINER_CONFIG_ROOT@/@SMOKEPING_DATA_PATH@:/data"
    ```

Access the Web UI at: `http://localhost:@SMOKEPING_PORT@`

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
| `/config` | Configuration directory (Probes, Targets, etc.) |
| `/data` | Data directory (RRD database files) |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8081` | TCP |  |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://oss.oetiker.ch/smokeping/){ .md-button .md-button--primary }
[Source Code](https://github.com/oetiker/smokeping){ .md-button }
[FreshPorts](https://www.freshports.org/net-mgmt/smokeping/){ .md-button }