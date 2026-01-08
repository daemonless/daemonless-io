---
title: unifi - FreeBSD OCI Container
description: UniFi Network Application on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# unifi

UniFi Network Application for managing Ubiquiti network devices.

| | |
|---|---|
| **Port** | 8443 |
| **Registry** | `ghcr.io/daemonless/unifi` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/unifi](https://github.com/daemonless/unifi) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name unifi \
      --network host \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      ghcr.io/daemonless/unifi:latest
    ```
    
    Access at: https://localhost:8443

=== "Compose"

    ```yaml
    services:
      unifi:
        image: ghcr.io/daemonless/unifi:latest
        container_name: unifi
        network_mode: host
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/unifi:/config
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/unifi/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Ubiquiti Downloads](https://ui.com/download/releases/network-server) | Latest UniFi release |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |
| `SYSTEM_IP` | - | Host IP for device inform (enables bridge networking) |

## Volumes

| Path | Description |
|------|-------------|--|
| `/config` | Configuration, database, and logs |

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 8443 | TCP | Web UI (HTTPS) |
| 8080 | TCP | Device inform URL |
| 8843 | TCP | Guest portal HTTPS |
| 8880 | TCP | Guest portal HTTP |
| 6789 | TCP | Mobile throughput test |
| 3478 | UDP | STUN |
| 10001 | UDP | Device discovery |

## Networking

### Host Networking (Recommended)
Uses host network stack. L2 discovery works automatically.

### Bridge Networking
Requires `SYSTEM_IP` env var so devices know where to connect. L2 discovery won't work (requires manual `set-inform` or DNS).

## Notes

- **User:** `unifi` (MongoDB runs as root due to restrictions)
- **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD)

## Links

- [Website](https://ui.com/)
- [FreshPorts](https://www.freshports.org/net-mgmt/unifi9/)
