---
title: transmission - FreeBSD OCI Container
description: Transmission BitTorrent client on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# transmission

Lightweight BitTorrent client with web interface.

| | |
|---|---|
| **Port** | 9091 |
| **Registry** | `ghcr.io/daemonless/transmission` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/transmission](https://github.com/daemonless/transmission) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name transmission \
      -p 9091:9091 \
      -p 51413:51413 \
      -p 51413:51413/udp \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/downloads:/downloads \
      -v /path/to/watch:/watch \
      ghcr.io/daemonless/transmission:latest
    ```
    
    Access at: http://localhost:9091

=== "Compose"

    ```yaml
    services:
      transmission:
        image: ghcr.io/daemonless/transmission:latest
        container_name: transmission
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/transmission:/config
          - /data/downloads:/downloads
          - /data/watch:/watch
        ports:
          - 9091:9091
          - 51413:51413
          - 51413:51413/udp
        restart: unless-stopped
    ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PUID` | User ID for the application process | `1000` |
| `PGID` | Group ID for the application process | `1000` |
| `TZ` | Timezone for the container | `UTC` |
| `S6_LOG_ENABLE` | Enable/Disable file logging | `1` |
| `S6_LOG_MAX_SIZE` | Max size per log file (bytes) | `1048576` |
| `S6_LOG_MAX_FILES` | Number of rotated log files to keep | `10` |

## Logging

This image uses `s6-log` for internal log rotation.
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/transmission/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://transmissionbt.com/) | Latest upstream release |
| `:pkg` | `net-p2p/transmission-daemon` | FreeBSD quarterly packages |
| `:pkg-latest` | `net-p2p/transmission-daemon` | FreeBSD latest packages |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |
| `/downloads` | Download directory |
| `/watch` | Watch directory for .torrent files |

## Ports

| Port | Description |
|------|-------------|
| 9091 | Web UI |
| 51413 | Peer listening port (TCP/UDP) |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

## Links

- [Website](https://transmissionbt.com/)
- [FreshPorts](https://www.freshports.org/net-p2p/transmission-daemon/)
