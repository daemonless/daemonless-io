---
title: woodpecker - FreeBSD OCI Container
description: Woodpecker CI server and agent  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# woodpecker

Continuous Integration (CI) server and agent.

| | |
|---|---|
| **Port** | 8000 |
| **Registry** | `ghcr.io/daemonless/woodpecker` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/woodpecker](https://github.com/daemonless/woodpecker) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name woodpecker-server \
      -p 8000:8000 -p 9000:9000 \
      -e PUID=1000 -e PGID=1000 \
      -e WOODPECKER_SERVER_ENABLE=true \
      -e WOODPECKER_GITEA=true \
      -e WOODPECKER_GITEA_URL=https://gitea.example.com \
      -e WOODPECKER_GITEA_CLIENT=your_client_id \
      -e WOODPECKER_GITEA_SECRET=your_client_secret \
      -e WOODPECKER_AGENT_SECRET=shared_secret \
      -v /path/to/data:/var/lib/woodpecker \
      ghcr.io/daemonless/woodpecker:latest
    ```
    
    Access at: http://localhost:8000

=== "Compose"

    ```yaml
    services:
      woodpecker-server:
        image: ghcr.io/daemonless/woodpecker:latest
        container_name: woodpecker-server
        environment:
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
          - WOODPECKER_SERVER_ENABLE=true
          - WOODPECKER_GITEA=true
          - WOODPECKER_GITEA_URL=https://gitea.example.com
          - WOODPECKER_AGENT_SECRET=changeme
        volumes:
          - /data/woodpecker:/var/lib/woodpecker
        ports:
          - 8000:8000
          - 9000:9000
        restart: unless-stopped
    
      woodpecker-agent:
        image: ghcr.io/daemonless/woodpecker:latest
        container_name: woodpecker-agent
        environment:
          - PUID=1000
          - PGID=1000
          - WOODPECKER_AGENT_ENABLE=true
          - WOODPECKER_SERVER=woodpecker-server:9000
          - WOODPECKER_AGENT_SECRET=changeme
        volumes:
          - /var/run/podman/podman.sock:/var/run/podman.sock
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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/woodpecker/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Quick Start (Agent)

```bash
podman run -d --name woodpecker-agent \
  -e PUID=1000 -e PGID=1000 \
  -e WOODPECKER_AGENT_ENABLE=true \
  -e WOODPECKER_SERVER=woodpecker-server:9000 \
  -e WOODPECKER_AGENT_SECRET=shared_secret \
  -v /var/run/podman/podman.sock:/var/run/podman.sock \
  ghcr.io/daemonless/woodpecker:latest
```

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/woodpecker-ci/woodpecker) | Built from source |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID for app |
| `PGID` | 1000 | Group ID for app |
| `TZ` | UTC | Timezone |
| `WOODPECKER_SERVER_ENABLE` | false | Enable server mode |
| `WOODPECKER_AGENT_ENABLE` | false | Enable agent mode |

See [Woodpecker Docs](https://woodpecker-ci.org/docs/administration/server-config) for all configuration options.

## Volumes

| Path | Description |
|------|-------------|
| `/var/lib/woodpecker` | Server database and data |

## Ports

| Port | Description |
|------|-------------|
| 8000 | Web UI (Server) |
| 9000 | gRPC Agent communication (Server) |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)
- **Dual Mode:** This image contains both Server and Agent binaries. Enable one or both via env vars.

## Building

This image is built via **Woodpecker CI** only. GitHub Actions is disabled because the Go compilation (3 binaries from source) exceeds GitHub's runner time limits.

## Links

- [Website](https://woodpecker-ci.org/)
- [GitHub](https://github.com/woodpecker-ci/woodpecker)
