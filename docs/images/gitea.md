---
title: gitea - FreeBSD OCI Container
description: Gitea self-hosted Git service on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# gitea

Self-hosted Git service.

| | |
|---|---|
| **Port** | 3000 |
| **Registry** | `ghcr.io/daemonless/gitea` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/gitea](https://github.com/daemonless/gitea) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name gitea \
      -p 3000:3000 -p 2222:22 \
      -e PUID=1000 -e PGID=1000 \
      -v /data/gitea:/gitea \
      ghcr.io/daemonless/gitea:latest
    ```
    
    Access at: http://localhost:3000

=== "Compose"

    ```yaml
    services:
      gitea:
        image: ghcr.io/daemonless/gitea:latest
        container_name: gitea
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/gitea:/gitea
        ports:
          - 3000:3000
          - 2222:22
        restart: unless-stopped
    ```

=== "Ansible"

    ```yaml
    - name: Deploy Gitea
      containers.podman.podman_container:
        name: gitea
        image: ghcr.io/daemonless/gitea:latest
        state: started
        restart_policy: unless-stopped
        env:
          PUID: "1000"
          PGID: "1000"
          TZ: "America/New_York"
        ports:
          - "3000:3000"
          - "2222:22"
        volumes:
          - /data/gitea:/gitea
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/gitea/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Advanced: VNET Networking

For full isolation, you can use VNET. This gives the jail its own network stack, but requires manual IP configuration or a custom bridge setup.

```bash
podman run -d --name gitea \
  --network none \
  --annotation 'org.freebsd.jail.vnet=new' \
  -v /containers/gitea:/gitea \
  ghcr.io/daemonless/gitea:latest
```

**Note**: With `network=none` and `vnet=new`, the container will not have network connectivity until you assign an interface (epair) and IP address to it manually via `ifconfig` from the host.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | `devel/gitea` | FreeBSD packages (latest branch) |
| `:pkg` | `devel/gitea` | FreeBSD quarterly packages |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |

## Volumes

| Path | Description |
|------|-------------|
| `/gitea` | Configuration, repositories, and data |

### Directory Structure
- `/gitea/custom/conf/app.ini` - Configuration
- `/gitea/repos` - Git repositories
- `/gitea/data` - Data (avatars, etc.)
- `/gitea/log` - Logs

## Ports

| Port | Description |
|------|-------------|
| 3000 | Web UI |
| 22 | SSH |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

### Specific Requirements
- **VNET Optional:** Can use `--annotation 'org.freebsd.jail.vnet=new'` for isolation, but standard bridge networking works out of the box.

## Links

- [Website](https://about.gitea.com/)
- [FreshPorts](https://www.freshports.org/devel/gitea/)
