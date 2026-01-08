---
title: radarr - FreeBSD OCI Container
description: Radarr movie management on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# radarr

Movie collection manager for Usenet and BitTorrent users.

| | |
|---|---|
| **Port** | 7878 |
| **Registry** | `ghcr.io/daemonless/radarr` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/radarr](https://github.com/daemonless/radarr) |

!!! warning "Requires patched ocijail"
    This application requires the `allow.mlock` annotation.
    See [ocijail patch](../guides/ocijail-patch.md).

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name radarr \
      -p 7878:7878 \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/movies:/movies \
      -v /path/to/downloads:/downloads \
      ghcr.io/daemonless/radarr:latest
    ```
    
    Access at: http://localhost:7878

=== "Compose"

    ```yaml
    services:
      radarr:
        image: ghcr.io/daemonless/radarr:latest
        container_name: radarr
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/radarr:/config
          - /data/media/movies:/movies
          - /data/downloads:/downloads
        ports:
          - 7878:7878
        annotations:
          org.freebsd.jail.allow.mlock: "true"
        restart: unless-stopped
    ```

=== "Ansible"

    ```yaml
    - name: Deploy Radarr
      containers.podman.podman_container:
        name: radarr
        image: ghcr.io/daemonless/radarr:latest
        state: started
        restart_policy: unless-stopped
        env:
          PUID: "1000"
          PGID: "1000"
          TZ: "America/New_York"
        ports:
          - "7878:7878"
        volumes:
          - /data/config/radarr:/config
          - /data/media/movies:/movies
          - /data/downloads:/downloads
        annotation:
          org.freebsd.jail.allow.mlock: "true"
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/radarr/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://radarr.servarr.com/) | Latest upstream release |
| `:pkg` | `net-p2p/radarr` | FreeBSD quarterly packages |
| `:pkg-latest` | `net-p2p/radarr` | FreeBSD latest packages |

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
| `/movies` | Movie library |
| `/downloads` | Download directory |

## Ports

| Port | Description |
|------|-------------|
| 7878 | Web UI |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

### Specific Requirements
- **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` (Requires [patched ocijail](https://github.com/daemonless/daemonless#ocijail-patch))

## Links

- [Website](https://radarr.video/)
- [FreshPorts](https://www.freshports.org/net-p2p/radarr/)
