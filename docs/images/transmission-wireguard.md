---
title: transmission-wireguard - FreeBSD OCI Container
description: Transmission BitTorrent client with WireGuard VPN on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# transmission-wireguard

Transmission BitTorrent client running through a WireGuard VPN tunnel on FreeBSD.

| | |
|---|---|
| **Port** | 9091 |
| **Registry** | `ghcr.io/daemonless/transmission-wireguard` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/transmission-wireguard](https://github.com/daemonless/transmission-wireguard) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name transmission-vpn \
      --annotation 'org.freebsd.jail.vnet=new' \
      -e WG_PRIVATE_KEY="your-private-key" \
      -e WG_PEER_PUBLIC_KEY="vpn-server-public-key" \
      -e WG_ENDPOINT="vpn.example.com:51820" \
      -e PUID=1000 -e PGID=1000 \
      -v /path/to/config:/config \
      -v /path/to/downloads:/downloads \
      ghcr.io/daemonless/transmission-wireguard:latest
    ```
    
    **Access:** Check IP with `podman inspect transmission-vpn --format '{{.NetworkSettings.IPAddress}}'` then go to `http://<IP>:9091`.

=== "Compose"

    ```yaml
    services:
      transmission-vpn:
        image: ghcr.io/daemonless/transmission-wireguard:latest
        container_name: transmission-vpn
        environment:
          - WG_PRIVATE_KEY=your-private-key
          - WG_PEER_PUBLIC_KEY=vpn-server-public-key
          - WG_ENDPOINT=vpn.example.com:51820
          - WG_ADDRESS=10.5.0.2/32
          - WG_DNS=1.1.1.1
          - PUID=1000
          - PGID=1000
          - TZ=America/New_York
        volumes:
          - /data/config/transmission-vpn:/config
          - /data/downloads:/downloads
          - /data/watch:/watch
        annotations:
          org.freebsd.jail.vnet: "new"
        restart: unless-stopped
    ```

## Environment Variables (Standard)

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
- **System Logs**: Captured from console and stored at `/config/logs/daemonless/transmission-wireguard/`.
- **Application Logs**: Managed by the app and typically found in `/config/logs/`.
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://transmissionbt.com/) | Latest upstream release |

## WireGuard Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WG_PRIVATE_KEY` | Yes | - | Your WireGuard private key |
| `WG_PEER_PUBLIC_KEY` | Yes | - | VPN server's public key |
| `WG_ENDPOINT` | Yes | - | VPN server address (host:port) |
| `WG_ADDRESS` | No | `10.5.0.2/32` | Your tunnel IP address |
| `WG_DNS` | No | `1.1.1.1` | DNS server to use |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |
| `/downloads` | Download directory |
| `/watch` | Watch directory |

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 9091 | TCP | Web UI / RPC |
| 51413 | TCP/UDP | BitTorrent peer connections |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)

### Specific Requirements
- **VNET Required:** Must use `--annotation 'org.freebsd.jail.vnet=new'`
- **Kernel Module:** Host must have `if_wg` loaded (`kldload if_wg`)

### Kill Switch
Traffic is routed through the VPN interface. If the VPN drops, Transmission loses connectivity.

## Links

- [Website](https://transmissionbt.com/)
- [FreshPorts](https://www.freshports.org/net-p2p/transmission-daemon/)
