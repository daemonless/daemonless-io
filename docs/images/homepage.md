---
title: "Homepage on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Homepage on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  HOMEPAGE_PORT:
    default: "3000"
    description: Homepage Host Port
---

# :material-view-dashboard: Homepage

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/homepage/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/homepage/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/homepage?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/homepage/commits)

A modern, highly customizable dashboard for your homelab.

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
      homepage:
        image: ghcr.io/daemonless/homepage:latest
        container_name: homepage
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@HOMEPAGE_CONFIG_PATH@:/config
        ports:
          - @HOMEPAGE_PORT@:3000
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name homepage \
      -p @HOMEPAGE_PORT@:3000 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@HOMEPAGE_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/homepage:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy homepage
      containers.podman.podman_container:
        name: homepage
        image: ghcr.io/daemonless/homepage:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@HOMEPAGE_PORT@:3000"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@HOMEPAGE_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@HOMEPAGE_PORT@`

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
| `/config` | Configuration directory (settings, bookmarks, services) |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3000` | TCP | Web UI |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://gethomepage.dev/){ .md-button .md-button--primary }
[Source Code](https://github.com/gethomepage/homepage){ .md-button }
[FreshPorts](https://www.freshports.org/www/homepage/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.