---
title: Uptime Kuma - FreeBSD OCI Container
description: A fancy self-hosted monitoring tool on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# Uptime Kuma

A fancy self-hosted monitoring tool, running natively on FreeBSD.

| | |
|---|---|
| **Port** | 3001 |
| **Registry** | `ghcr.io/daemonless/uptime-kuma` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/uptime-kuma](https://github.com/daemonless/uptime-kuma) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name uptime-kuma \
      --annotation 'org.freebsd.jail.allow.raw_sockets=true' \
      -v /containers/uptime-kuma:/config \
      -p 3001:3001 \
      ghcr.io/daemonless/uptime-kuma:latest
    ```
    
    Access the web UI at `http://localhost:3001`

## Features

- Monitoring uptime for HTTP(s), TCP, Ping, DNS, and more
- Fancy, reactive, fast UI/UX
- Notifications via Telegram, Discord, Slack, Email, and 90+ services
- Multi-language support
- Status pages
- Browser Engine monitoring (with Chromium)

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | 1000 | User ID |
| `PGID` | 1000 | Group ID |
| `DATA_DIR` | /config | Data directory |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Database and configuration |

## Ports

| Port | Description |
|------|-------------|
| 3001 | Web UI |

## Notes

- **Ping monitoring** requires `allow.raw_sockets` jail annotation
- **Browser Engine monitoring** uses FreeBSD's Chromium package
- Image is larger than typical due to Chromium dependency

## Links

- [Uptime Kuma](https://uptime.kuma.pet/)
- [Documentation](https://github.com/louislam/uptime-kuma/wiki)
- [Daemonless](https://daemonless.io)
