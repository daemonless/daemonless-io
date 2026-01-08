---
title: sabnzbd - FreeBSD OCI Container
description: SABnzbd Usenet downloader on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# sabnzbd

Binary newsreader for Usenet with NZB support.

| | |
|---|---|
| **Port** | 8080 |
| **Registry** | `ghcr.io/daemonless/sabnzbd` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/sabnzbd](https://github.com/daemonless/sabnzbd) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name sabnzbd \
      -p 8080:8080 \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/downloads:/downloads \
      ghcr.io/daemonless/sabnzbd:latest
    ```
    
    Access at: http://localhost:8080

=== "Compose"

    ```yaml
    services:
      sabnzbd:
        image: ghcr.io/daemonless/sabnzbd:latest
        container_name: sabnzbd
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
          - HOST_WHITELIST=myserver,myserver.local
        volumes:
          - /data/config/sabnzbd:/config
          - /data/downloads:/downloads
        ports:
          - 8080:8080
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/sabnzbd/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/sabnzbd/sabnzbd/releases) | Latest upstream release |
| `:pkg` | `news/sabnzbd` | FreeBSD quarterly packages |
| `:pkg-latest` | `news/sabnzbd` | FreeBSD latest packages |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |
| `HOST_WHITELIST` | | Hostnames for initial config |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |
| `/downloads` | Download directory |

## Ports

| Port | Description |
|------|-------------|
| 8080 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)
- **Tools:** Includes par2, unrar, and 7-zip

### Hostname Verification
If you see "Access denied - Hostname verification failed", set `HOST_WHITELIST` environment variable or edit config.

## Links

- [Website](https://sabnzbd.org/)
- [FreshPorts](https://www.freshports.org/news/sabnzbd/)
