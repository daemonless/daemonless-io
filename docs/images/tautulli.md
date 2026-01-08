---
title: tautulli - FreeBSD OCI Container
description: Tautulli Plex monitoring on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# tautulli

Monitoring, analytics, and notifications for Plex Media Server.

| | |
|---|---|
| **Port** | 8181 |
| **Registry** | `ghcr.io/daemonless/tautulli` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/tautulli](https://github.com/daemonless/tautulli) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name tautulli \
      -p 8181:8181 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      --health-cmd /healthz \
      ghcr.io/daemonless/tautulli:latest
    ```
    
    Access at: http://localhost:8181

=== "Compose"

    ```yaml
    services:
      tautulli:
        image: ghcr.io/daemonless/tautulli:latest
        container_name: tautulli
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/tautulli:/config
        ports:
          - 8181:8181
        healthcheck:
          test: ["CMD", "/healthz"]
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/tautulli/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/Tautulli/Tautulli/releases) | Latest upstream release |
| `:pkg` | `multimedia/tautulli` | FreeBSD quarterly packages |
| `:pkg-latest` | `multimedia/tautulli` | FreeBSD latest packages |

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
| 8181 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Healthcheck:** `--health-cmd /healthz`
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

## Links

- [Website](https://tautulli.com/)
- [FreshPorts](https://www.freshports.org/multimedia/tautulli/)
