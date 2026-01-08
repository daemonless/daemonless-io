---
title: jellyfin - FreeBSD OCI Container
description: The Free Software Media System on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# jellyfin

The Free Software Media System

| | |
|---|---|
| **Port** | 8096 |
| **Registry** | `ghcr.io/daemonless/jellyfin` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/jellyfin](https://github.com/daemonless/jellyfin) |

!!! warning "Requires patched ocijail"
    This application requires the `allow.mlock` annotation.
    See [ocijail patch](../guides/ocijail-patch.md).

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name jellyfin \
      -p 8096:8096 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/cache:/cache \
      -v /path/to/media:/media \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      ghcr.io/daemonless/jellyfin:latest
    ```
    
    Access at: http://localhost:8096

=== "Compose"

    ```yaml
    services:
      jellyfin:
        image: ghcr.io/daemonless/jellyfin:latest
        container_name: jellyfin
        annotations:
          org.freebsd.jail.allow.mlock: "true"
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/jellyfin:/config
          - /data/cache/jellyfin:/cache
          - /data/media:/media
        ports:
          - 8096:8096
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/jellyfin/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/jellyfin/jellyfin) | Latest upstream release |
| `:pkg` | `jellyfin` | FreeBSD quarterly packages |
| `:pkg-latest` | `jellyfin` | FreeBSD latest packages |

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
| `/cache` | Cache directory |
| `/media` | Media directory |

## Ports

| Port | Description |
|------|-------------|
| 8096 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Healthcheck:** `--health-cmd /healthz`
- **Base:** Built on `ghcr.io/daemonless/arr-base` (FreeBSD)

### Specific Requirements
- **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` (Requires [patched ocijail](https://github.com/daemonless/daemonless#ocijail-patch))

## Links

- [Website](https://jellyfin.org/)
- [FreshPorts](https://www.freshports.org/multimedia/jellyfin/)
