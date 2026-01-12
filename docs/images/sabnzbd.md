---
title: "SABnzbd on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install SABnzbd on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  SABNZBD_PORT:
    default: "8080"
    description: SABnzbd Host Port
---

# :material-download-network: SABnzbd

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/sabnzbd/build.yml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/sabnzbd/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/sabnzbd?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/sabnzbd/commits)

SABnzbd Usenet downloader on FreeBSD.

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
      sabnzbd:
        image: ghcr.io/daemonless/sabnzbd:latest
        container_name: sabnzbd
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@SABNZBD_CONFIG_PATH@:/config
          - @DOWNLOADS_PATH@:/downloads
        ports:
          - @SABNZBD_PORT@:8080
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name sabnzbd \
      -p @SABNZBD_PORT@:8080 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@SABNZBD_CONFIG_PATH@:/config \ 
      -v @DOWNLOADS_PATH@:/downloads \ 
      ghcr.io/daemonless/sabnzbd:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy sabnzbd
      containers.podman.podman_container:
        name: sabnzbd
        image: ghcr.io/daemonless/sabnzbd:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@SABNZBD_PORT@:8080"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@SABNZBD_CONFIG_PATH@:/config"
          - "@DOWNLOADS_PATH@:/downloads"
    ```

Access the Web UI at: `http://localhost:@SABNZBD_PORT@`

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
| `/downloads` | Download directory |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8080` | TCP | Web UI |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://sabnzbd.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/sabnzbd/sabnzbd){ .md-button }
[FreshPorts](https://www.freshports.org/news/sabnzbd/){ .md-button }