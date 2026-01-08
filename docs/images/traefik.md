---
title: traefik - FreeBSD OCI Container
description: Traefik reverse proxy on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# traefik

Modern HTTP reverse proxy and load balancer.

| | |
|---|---|
| **Port** | 80 |
| **Registry** | `ghcr.io/daemonless/traefik` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/traefik](https://github.com/daemonless/traefik) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name traefik \
      -p 80:80 -p 443:443 -p 8080:8080 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      --health-cmd /healthz \
      ghcr.io/daemonless/traefik:latest
    ```
    
    Access dashboard at: http://localhost:8080/dashboard/

=== "Compose"

    ```yaml
    services:
      traefik:
        image: ghcr.io/daemonless/traefik:latest
        container_name: traefik
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/traefik:/config
        ports:
          - 80:80
          - 443:443
          - 8080:8080
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/traefik/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/traefik/traefik/releases) | Latest upstream release |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory (traefik.yml, dynamic/, letsencrypt/) |

## Ports

| Port | Description |
|------|-------------|
| 80 | HTTP |
| 443 | HTTPS |
| 8080 | Dashboard/API |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Healthcheck:** `--health-cmd /healthz`
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

## Links

- [Website](https://traefik.io/)
- [GitHub](https://github.com/traefik/traefik)
