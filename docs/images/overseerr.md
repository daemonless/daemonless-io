---
title: overseerr - FreeBSD OCI Container
description: Overseerr media request management on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# overseerr

Request management and media discovery tool for Plex.

| | |
|---|---|
| **Port** | 5055 |
| **Registry** | `ghcr.io/daemonless/overseerr` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/overseerr](https://github.com/daemonless/overseerr) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name overseerr \
      -p 5055:5055 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      ghcr.io/daemonless/overseerr:latest
    ```
    
    Access at: http://localhost:5055

=== "Compose"

    ```yaml
    services:
      overseerr:
        image: ghcr.io/daemonless/overseerr:latest
        container_name: overseerr
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/overseerr:/config
        ports:
          - 5055:5055
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/overseerr/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/sct/overseerr) | Latest development build |

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

## Ports

| Port | Description |
|------|-------------|
| 5055 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)
- **Build:** Built from source (Node.js)

## Links

- [Website](https://overseerr.dev/)
- [GitHub](https://github.com/sct/overseerr)
