---
title: openspeedtest - FreeBSD OCI Container
description: HTML5 Network Speed Test on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# openspeedtest

Free and open-source HTML5 network speed test.

| | |
|---|---|
| **Port** | 3000 |
| **Registry** | `ghcr.io/daemonless/openspeedtest` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/openspeedtest](https://github.com/daemonless/openspeedtest) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name openspeedtest \
      -p 3000:3000 \
      ghcr.io/daemonless/openspeedtest:latest
    ```
    
    Access at: http://localhost:3000

=== "Compose"

    ```yaml
    services:
      openspeedtest:
        image: ghcr.io/daemonless/openspeedtest:latest
        container_name: openspeedtest
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
| `S6_LOG_ENABLE` | Enable/Disable file logging | `1` |
| `S6_LOG_MAX_SIZE` | Max size per log file (bytes) | `1048576` |
| `S6_LOG_MAX_FILES` | Number of rotated log files to keep | `10` |

## Logging

This image uses `s6-log` for internal log rotation.
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/openspeedtest/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/openspeedtest/Speed-Test) | Latest from git |

## Ports

| Port | Description |
|------|-------------|
| 3000 | Web UI |

## Notes

- **Base:** Built on `ghcr.io/daemonless/nginx-base-image` (FreeBSD)
- **Storage:** No persistent storage required (client-side only)

## Links

- [Website](https://openspeedtest.com/)
- [GitHub](https://github.com/openspeedtest/Speed-Test)
