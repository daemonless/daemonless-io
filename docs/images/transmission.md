---
title: "Transmission on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Transmission on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  TRANSMISSION_PORT:
    default: "9091"
    description: Transmission Host Port
---

# :simple-transmission: Transmission

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/transmission/build.yml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/transmission/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/transmission?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/transmission/commits)

Transmission BitTorrent client on FreeBSD.

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
      transmission:
        image: ghcr.io/daemonless/transmission:latest
        container_name: transmission
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - USER=
          - PASS=<PASS>
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_CONFIG_PATH@:/config
          - @DOWNLOADS_PATH@:/downloads
          - @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WATCH_PATH@:/watch
        ports:
          - @TRANSMISSION_PORT@:9091
          - 51413:51413
          - 51413:51413
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name transmission \
      -p @TRANSMISSION_PORT@:9091 \
      -p 51413:51413 \
      -p 51413:51413 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e USER= \
      -e PASS=<PASS> \
      -v @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_CONFIG_PATH@:/config \ 
      -v @DOWNLOADS_PATH@:/downloads \ 
      -v @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WATCH_PATH@:/watch \ 
      ghcr.io/daemonless/transmission:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy transmission
      containers.podman.podman_container:
        name: transmission
        image: ghcr.io/daemonless/transmission:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          USER: ""
          PASS: "<PASS>"
        ports:
          - "@TRANSMISSION_PORT@:9091"
          - "51413:51413"
          - "51413:51413"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@TRANSMISSION_CONFIG_PATH@:/config"
          - "@DOWNLOADS_PATH@:/downloads"
          - "@CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WATCH_PATH@:/watch"
    ```

Access the Web UI at: `http://localhost:@TRANSMISSION_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `USER` | `` | Optional: Web UI Username |
| `PASS` | `<PASS>` | Optional: Web UI Password |

### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |
| `/downloads` | Download directory |
| `/watch` | Watch directory for .torrent files |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `9091` | TCP | Web UI |
| `51413` | TCP | Torrent peer port |
| `51413` | TCP | Torrent peer port |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://transmissionbt.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/transmission/transmission){ .md-button }
[FreshPorts](https://www.freshports.org/net-p2p/transmission-daemon/){ .md-button }