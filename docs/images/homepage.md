---
title: Homepage - FreeBSD OCI Container
description: Homepage - A modern dashboard for your homelab  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# Homepage

A modern, fully static, fast, secure fully proxied, highly customizable application dashboard for your homelab.

| | |
|---|---|
| **Port** | 3000 |
| **Registry** | `ghcr.io/daemonless/homepage` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/homepage](https://github.com/daemonless/homepage) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name homepage \
      -p 3000:3000 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      ghcr.io/daemonless/homepage:latest
    ```
    
    Access at: http://localhost:3000

=== "Compose"

    ```yaml
    services:
      homepage:
        image: ghcr.io/daemonless/homepage:latest
        container_name: homepage
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/homepage:/config
        ports:
          - 3000:3000
        restart: unless-stopped
    ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PUID` | User ID for the application process | `1000` |
| `PGID` | Group ID for the application process | `1000` |
| `TZ` | Timezone for the container | `UTC` |
| `PORT` | Web UI port | `3000` |
| `HOMEPAGE_ALLOWED_HOSTS` | Allowed host headers | `*` |
| `S6_LOG_ENABLE` | Enable/Disable file logging | `1` |
| `S6_LOG_MAX_SIZE` | Max size per log file (bytes) | `1048576` |
| `S6_LOG_MAX_FILES` | Number of rotated log files to keep | `10` |

## Logging

This image uses `s6-log` for internal log rotation.
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/homepage/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [GitHub Releases](https://github.com/gethomepage/homepage/releases) | Latest upstream release |
| `:pkg` | `homepage` | FreeBSD quarterly packages |
| `:pkg-latest` | `homepage` | FreeBSD latest packages |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory (settings.yaml, services.yaml, etc.) |

## Ports

| Port | Description |
|------|-------------|
| 3000 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Healthcheck:** `--health-cmd /healthz`
- **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD)

## Links

- [Website](https://gethomepage.dev/)
- [Documentation](https://gethomepage.dev/configs/)
- [FreshPorts](https://www.freshports.org/www/homepage/)
