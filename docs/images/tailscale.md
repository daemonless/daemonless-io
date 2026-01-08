---
title: tailscale - FreeBSD OCI Container
description: Tailscale mesh VPN on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# tailscale

Mesh VPN container.

| | |
|---|---|
| **Registry** | `ghcr.io/daemonless/tailscale` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/tailscale](https://github.com/daemonless/tailscale) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name tailscale \
      --network host \
      -v /containers/tailscale:/var/db/tailscale \
      --restart unless-stopped \
      ghcr.io/daemonless/tailscale:latest
    ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `S6_LOG_ENABLE` | Enable/Disable file logging | `1` |
| `S6_LOG_MAX_SIZE` | Max size per log file (bytes) | `1048576` |
| `S6_LOG_MAX_FILES` | Number of rotated log files to keep | `10` |

## Logging

This image uses `s6-log` for internal log rotation.
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/tailscale/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Configuration

**First Run:**
Authenticate the node:
```bash
podman exec tailscale tailscale up
```
Visit the printed URL to authorize.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | `security/tailscale` | FreeBSD packages |

## Volumes

| Path | Description |
|------|-------------|
| `/var/db/tailscale` | State directory (identity, auth) |

## Networking

### Userspace Networking
Runs in userspace networking mode.
- **SOCKS5 Proxy:** `localhost:1055`
- **HTTP Proxy:** `localhost:1055`

### Subnet Router
To expose local network:
```bash

## Usage

### Advertize Subnet Routes

```bash
podman exec tailscale tailscale up --advertise-routes=<your-subnet>/24
```

### Authentication with Auth Key
```

## Notes

- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

### Specific Requirements
- **Host Network Required:** Must use `--network host`

## Links

- [Website](https://tailscale.com/)
- [FreshPorts](https://www.freshports.org/security/tailscale/)
