---
title: "OpenSpeedTest on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install OpenSpeedTest on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  OPENSPEEDTEST_PORT:
    default: "3005"
    description: OpenSpeedTest Host Port
---

# :material-speedometer: OpenSpeedTest

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/openspeedtest/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/openspeedtest/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/openspeedtest?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/openspeedtest/commits)

Self-hosted HTML5 Network Speed Test on FreeBSD.

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
      openspeedtest:
        image: ghcr.io/daemonless/openspeedtest:latest
        container_name: openspeedtest
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
        ports:
          - @OPENSPEEDTEST_PORT@:3005
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name openspeedtest \
      -p @OPENSPEEDTEST_PORT@:3005 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      ghcr.io/daemonless/openspeedtest:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy openspeedtest
      containers.podman.podman_container:
        name: openspeedtest
        image: ghcr.io/daemonless/openspeedtest:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@OPENSPEEDTEST_PORT@:3005"
    ```

Access the Web UI at: `http://localhost:@OPENSPEEDTEST_PORT@`

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

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3005` | TCP |  |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://openspeedtest.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/openspeedtest/Speed-Test){ .md-button }
