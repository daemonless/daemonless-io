---
title: vaultwarden - FreeBSD OCI Container
description: Vaultwarden (Bitwarden compatible backend) on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# vaultwarden

Bitwarden compatible backend server written in Rust, running natively on FreeBSD.

| | |
|---|---|
| **Port** | 80 |
| **Registry** | `ghcr.io/daemonless/vaultwarden` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/vaultwarden](https://github.com/daemonless/vaultwarden) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name vaultwarden \
      -p 80:80 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      ghcr.io/daemonless/vaultwarden:latest
    ```
    
    Access at: http://localhost

=== "Compose"

    ```yaml
    services:
      vaultwarden:
        image: ghcr.io/daemonless/vaultwarden:latest
        container_name: vaultwarden
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/vaultwarden:/config
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/vaultwarden/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/dani-garcia/vaultwarden/releases) | Latest upstream release |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration and data directory |

## Ports

| Port | Description |
|------|-------------|
| 80 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/nginx-base-image` (FreeBSD)
- **Proxy:** Includes a built-in Nginx reverse proxy to serve the Web Vault.

## Links

- [Website](https://github.com/dani-garcia/vaultwarden)
- [FreshPorts](https://www.freshports.org/security/vaultwarden/)
