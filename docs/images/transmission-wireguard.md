---
title: "Transmission with WireGuard on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Transmission with WireGuard on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  TRANSMISSION_WIREGUARD_PORT:
    default: "9091"
    description: Transmission with WireGuard Host Port
---

# :simple-wireguard: Transmission with WireGuard

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/transmission-wireguard/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/transmission-wireguard/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/transmission-wireguard?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/transmission-wireguard/commits)

Transmission BitTorrent client with built-in WireGuard VPN support.

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
      transmission-wireguard:
        image: ghcr.io/daemonless/transmission-wireguard:latest
        container_name: transmission-wireguard
        environment:
          - WG_ENABLE=true
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_CONFIG_PATH@:/config
          - @DOWNLOADS_PATH@:/downloads
          - @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_WATCH_PATH@:/watch
        ports:
          - @TRANSMISSION_WIREGUARD_PORT@:9091
          - 51413:51413
          - 51413:51413
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name transmission-wireguard \
      -p @TRANSMISSION_WIREGUARD_PORT@:9091 \
      -p 51413:51413 \
      -p 51413:51413 \
      -e WG_ENABLE=true \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_CONFIG_PATH@:/config \ 
      -v @DOWNLOADS_PATH@:/downloads \ 
      -v @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_WATCH_PATH@:/watch \ 
      ghcr.io/daemonless/transmission-wireguard:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy transmission-wireguard
      containers.podman.podman_container:
        name: transmission-wireguard
        image: ghcr.io/daemonless/transmission-wireguard:latest
        state: started
        restart_policy: always
        env:
          WG_ENABLE: "true"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@TRANSMISSION_WIREGUARD_PORT@:9091"
          - "51413:51413"
          - "51413:51413"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_CONFIG_PATH@:/config"
          - "@DOWNLOADS_PATH@:/downloads"
          - "@CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_WATCH_PATH@:/watch"
    ```

Access the Web UI at: `http://localhost:@TRANSMISSION_WIREGUARD_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WG_ENABLE` | `true` | Enable WireGuard (true/false) |
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory (settings.json, WireGuard configs) |
| `/downloads` | Download directory |
| `/watch` | Watch directory for torrent files |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `9091` | TCP | Web UI |
| `51413` | TCP | Torrent traffic (TCP/UDP) |
| `51413` | TCP | Torrent traffic (TCP/UDP) |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://transmissionbt.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/transmission/transmission){ .md-button }
[FreshPorts](https://www.freshports.org/net-p2p/transmission-daemon/){ .md-button }