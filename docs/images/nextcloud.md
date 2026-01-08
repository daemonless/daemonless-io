---
title: nextcloud - FreeBSD OCI Container
description: Nextcloud self-hosted cloud on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# nextcloud

Self-hosted productivity platform (file sync, share, collaboration).

| | |
|---|---|
| **Port** | 80 |
| **Registry** | `ghcr.io/daemonless/nextcloud` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/nextcloud](https://github.com/daemonless/nextcloud) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name nextcloud \
      --network=host \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/data:/data \
      ghcr.io/daemonless/nextcloud:latest
    ```
    
    Access at: http://localhost:80

=== "Compose"

    ```yaml
    services:
      nextcloud:
        image: ghcr.io/daemonless/nextcloud:latest
        container_name: nextcloud
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/nextcloud:/config
          - /data/nextcloud:/data
        network_mode: host
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/nextcloud/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | `www/nextcloud` | FreeBSD packages (latest branch) |
| `:pkg` | `www/nextcloud` | FreeBSD quarterly packages |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration (nginx.conf, config.php) |
| `/data` | User data files |

## Ports

| Port | Description |
|------|-------------|
| 80 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/nginx-base-image` (FreeBSD)

### Initial Setup
Run the wizard at http://localhost:80. Select Database (SQLite, MySQL, or PostgreSQL).

### Performance
Includes APCu and OPcache. To use Redis, configure `config.php` to point to a Redis host.

## Links

- [Website](https://nextcloud.com/)
- [FreshPorts](https://www.freshports.org/www/nextcloud/)
