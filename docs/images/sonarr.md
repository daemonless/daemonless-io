---
title: sonarr - FreeBSD OCI Container
description: Sonarr TV show management on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# sonarr

TV show collection manager for Usenet and BitTorrent users.

| | |
|---|---|
| **Port** | 8989 |
| **Registry** | `ghcr.io/daemonless/sonarr` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/sonarr](https://github.com/daemonless/sonarr) |

!!! warning "Requires patched ocijail"
    This application requires the `allow.mlock` annotation.
    See [ocijail patch](../guides/ocijail-patch.md).

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name sonarr \
      -p 8989:8989 \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/tv:/tv \
      -v /path/to/downloads:/downloads \
      ghcr.io/daemonless/sonarr:latest
    ```
    
    Access at: http://localhost:8989

=== "Compose"

    ```yaml
    services:
      sonarr:
        image: ghcr.io/daemonless/sonarr:latest
        container_name: sonarr
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/sonarr:/config
          - /data/media/tv:/tv
          - /data/downloads:/downloads
        ports:
          - 8989:8989
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/sonarr/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://services.sonarr.tv/v1/releases) | Latest upstream release |
| `:pkg` | `net-p2p/sonarr` | FreeBSD quarterly packages |
| `:pkg-latest` | `net-p2p/sonarr` | FreeBSD latest packages |

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
| `/tv` | TV show library |
| `/downloads` | Download directory |

## Ports

| Port | Description |
|------|-------------|
| 8989 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

### Specific Requirements
- **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` (Requires [patched ocijail](https://github.com/daemonless/daemonless#ocijail-patch))

## Links

- [Website](https://sonarr.tv/)
- [FreshPorts](https://www.freshports.org/net-p2p/sonarr/)
