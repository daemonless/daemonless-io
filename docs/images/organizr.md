---
title: organizr - FreeBSD OCI Container
description: HTPC/Homelab Services Organizer on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# organizr

HTPC/Homelab Services Organizer - dashboard for all your self-hosted services.

| | |
|---|---|
| **Port** | 80 |
| **Registry** | `ghcr.io/daemonless/organizr` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/organizr](https://github.com/daemonless/organizr) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name organizr \
      -p 80:80 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      ghcr.io/daemonless/organizr:latest
    ```
    
    Access at: http://localhost

=== "Compose"

    ```yaml
    services:
      organizr:
        image: ghcr.io/daemonless/organizr:latest
        container_name: organizr
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
          - BRANCH=v2-master
        volumes:
          - /data/config/organizr:/config
        ports:
          - 80:80
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/organizr/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/causefx/Organizr) | Latest from git |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |
| `BRANCH` | v2-master | Git branch (v2-master or v2-develop) |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory (includes nginx/php configs) |

## Ports

| Port | Description |
|------|-------------|
| 80 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/nginx-base-image` (FreeBSD)

## Links

- [Website](https://organizr.app/)
- [GitHub](https://github.com/causefx/Organizr)
