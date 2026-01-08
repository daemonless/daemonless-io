---
title: smokeping - FreeBSD OCI Container
description: SmokePing network latency monitor on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# smokeping

Deluxe latency measurement tool.

| | |
|---|---|
| **Port** | 80 |
| **Registry** | `ghcr.io/daemonless/smokeping` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/smokeping](https://github.com/daemonless/smokeping) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name smokeping \
      --network=host \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      ghcr.io/daemonless/smokeping:latest
    ```
    
    Access at: http://localhost:80/smokeping/smokeping.cgi

=== "Compose"

    ```yaml
    services:
      smokeping:
        image: ghcr.io/daemonless/smokeping:latest
        container_name: smokeping
        network_mode: host
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/smokeping:/config
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/smokeping/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/oetiker/SmokePing) | Built from source |
| `:pkg` | `net-mgmt/smokeping` | FreeBSD quarterly packages |
| `:pkg-latest` | `net-mgmt/smokeping` | FreeBSD latest packages |

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
| 80 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/nginx-base-image` (FreeBSD)

## Links

- [Website](https://oss.oetiker.ch/smokeping/)
- [FreshPorts](https://www.freshports.org/net-mgmt/smokeping/)
