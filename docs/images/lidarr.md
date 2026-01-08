---
title: lidarr - FreeBSD OCI Container
description: Lidarr music management on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# lidarr

Music collection manager for Usenet and BitTorrent users.

| | |
|---|---|
| **Port** | 8686 |
| **Registry** | `ghcr.io/daemonless/lidarr` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/lidarr](https://github.com/daemonless/lidarr) |

!!! warning "Requires patched ocijail"
    This application requires the `allow.mlock` annotation.
    See [ocijail patch](../guides/ocijail-patch.md).

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name lidarr \
      -p 8686:8686 \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/music:/music \
      -v /path/to/downloads:/downloads \
      ghcr.io/daemonless/lidarr:latest
    ```
    
    Access at: http://localhost:8686

=== "Compose"

    ```yaml
    services:
      lidarr:
        image: ghcr.io/daemonless/lidarr:latest
        container_name: lidarr
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/lidarr:/config
          - /data/media/music:/music
          - /data/downloads:/downloads
        ports:
          - 8686:8686
        annotations:
          org.freebsd.jail.allow.mlock: "true"
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/lidarr/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://lidarr.servarr.com/) | Latest upstream release |
| `:pkg` | `net-p2p/lidarr` | FreeBSD quarterly packages |
| `:pkg-latest` | `net-p2p/lidarr` | FreeBSD latest packages |

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
| `/music` | Music library |
| `/downloads` | Download directory |

## Ports

| Port | Description |
|------|-------------|
| 8686 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

### Specific Requirements
- **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` (Requires [patched ocijail](https://github.com/daemonless/daemonless#ocijail-patch))

## Links

- [Website](https://lidarr.audio/)
- [FreshPorts](https://www.freshports.org/net-p2p/lidarr/)
