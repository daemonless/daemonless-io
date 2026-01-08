---
title: adguardhome-sync - FreeBSD OCI Container
description: Sync AdGuardHome config to replica instances  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# adguardhome-sync

Sync AdGuardHome configuration from an origin instance to replica instances, running natively on FreeBSD.

| | |
|---|---|
| **Port** | 8080 |
| **Registry** | `ghcr.io/daemonless/adguardhome-sync` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/adguardhome-sync](https://github.com/daemonless/adguardhome-sync) |

## Quick Start

=== "Podman CLI"

    ### Podman
    
    ```bash
    podman run --name adguardhome-sync\
        --restart unless-stopped\
        -v /my/own/config:/config\
        -p 8080:8080/tcp\
        -d ghcr.io/daemonless/adguardhome-sync
    ```
    
    ### Compose
    
    ```yaml
    services:
      adguardhome-sync:
        image: ghcr.io/daemonless/adguardhome-sync:latest
        container_name: adguardhome-sync
        restart: unless-stopped
        volumes:
          - /my/own/config:/config
        ports:
          - "8080:8080/tcp"
    ```

## Configuration

Create `/config/adguardhome-sync.yaml`:

```yaml
# cron expression for sync schedule
cron: "*/5 * * * *"

# run sync on startup
runOnStart: true

    # Primary instance
    url: http://<primary-ip>:3000
    username: admin
    password: password
    # Secondary instances to sync to
    replica:
      - url: http://<replica-ip>:3000
        username: admin

# API server
api:
  port: 8080
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PUID` | User ID | `1000` |
| `PGID` | Group ID | `1000` |
| `TZ` | Timezone | `UTC` |

## What Gets Synced

- General settings
- DNS configuration (rewrites, access lists, server config)
- Filters
- Client settings
- DHCP settings (optional)
- Services
- Query log config
- Statistics config

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 8080 | TCP | Web API / metrics |

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/bakito/adguardhome-sync/releases) | Latest upstream release |

## Links

- [Upstream Repository](https://github.com/bakito/adguardhome-sync)
- [Configuration Reference](https://github.com/bakito/adguardhome-sync#config-file)
