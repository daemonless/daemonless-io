---
title: adguardhome - FreeBSD OCI Container
description: Network-wide ads & trackers blocking DNS server on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# adguardhome

Network-wide ads & trackers blocking DNS server, running natively on FreeBSD.

| | |
|---|---|
| **Port** | 3000 |
| **Registry** | `ghcr.io/daemonless/adguardhome` |
| **Tags** | `:latest`, `:pkg`, `:pkg-latest` |
| **Source** | [github.com/daemonless/adguardhome](https://github.com/daemonless/adguardhome) |

## Quick Start

=== "Podman CLI"

    ### Podman
    
    ```bash
    podman run --name adguardhome\
        --restart unless-stopped\
        -v /my/own/workdir:/opt/adguardhome/work\
        -v /my/own/confdir:/opt/adguardhome/conf\
        -p 53:53/tcp -p 53:53/udp\
        -p 67:67/udp -p 68:68/udp\
        -p 80:80/tcp -p 443:443/tcp -p 443:443/udp -p 3000:3000/tcp\
        -p 853:853/tcp\
        -p 784:784/udp -p 853:853/udp -p 8853:8853/udp\
        -p 5443:5443/tcp -p 5443:5443/udp\
        -p 6060:6060/tcp\
        -d ghcr.io/daemonless/adguardhome
    ```
    
    ### Compose
    
    ```yaml
    services:
      adguardhome:
        image: ghcr.io/daemonless/adguardhome:latest
        container_name: adguardhome
        restart: unless-stopped
        volumes:
          - /my/own/workdir:/opt/adguardhome/work
          - /my/own/confdir:/opt/adguardhome/conf
        ports:
          - "53:53/tcp"
          - "53:53/udp"
          - "67:67/udp"
          - "68:68/udp"
          - "80:80/tcp"
          - "443:443/tcp"
          - "443:443/udp"
          - "3000:3000/tcp"
          - "853:853/tcp"
          - "784:784/udp"
          - "853:853/udp"
          - "8853:8853/udp"
          - "5443:5443/tcp"
          - "5443:5443/udp"
          - "6060:6060/tcp"
    ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AGH_USER` | User to run as (`bsd` or `root`) | `bsd` |
| `TZ` | Timezone for the container | `UTC` |
| `S6_LOG_ENABLE` | Enable/Disable file logging | `1` |
| `S6_LOG_MAX_SIZE` | Max size per log file (bytes) | `1048576` |
| `S6_LOG_MAX_FILES` | Number of rotated log files to keep | `10` |

## FreeBSD Notes

On FreeBSD, binding to port 53 requires root privileges. Set `AGH_USER=root` when using privileged ports directly (e.g., with macvlan/host networking).

## First Run

1. Access the setup wizard at `http://<container-ip>:3000`
2. Configure DNS listen address and port
3. Configure web interface port
4. Set admin username and password
5. Complete the wizard

## Logging

This image uses `s6-log` for internal log rotation.
- **System Logs**: Stored at `/config/logs/daemonless/adguardhome/`
- **Application Logs**: AdGuard Home logs in `/config/work/`
- **Podman Logs**: Output is mirrored to the console, so `podman logs` still works.

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Upstream Releases](https://github.com/AdguardTeam/AdGuardHome/releases) | Latest upstream release |
| `:pkg` | FreeBSD Quarterly | FreeBSD package (quarterly branch) |
| `:pkg-latest` | FreeBSD Latest | FreeBSD package (latest branch) |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration and data directory |
| `/config/conf` | AdGuardHome.yaml configuration |
| `/config/work` | Working directory (query logs, filters) |

## Ports

| Port | Protocol | Description |
|------|----------|-------------|
| 53 | TCP/UDP | DNS queries |
| 67-68 | UDP | DHCP server |
| 80 | TCP | Web UI (HTTP) |
| 443 | TCP/UDP | Web UI (HTTPS) / DNS-over-HTTPS |
| 784 | UDP | DNS-over-QUIC |
| 853 | TCP | DNS-over-TLS |
| 853 | UDP | DNS-over-QUIC |
| 3000 | TCP | Setup wizard (initial config) |
| 5443 | TCP/UDP | DNSCrypt |
| 6060 | TCP | Debug/profiling |
| 8853 | UDP | DNS-over-QUIC (alternate) |

## Multi-Instance Sync

For redundant DNS with synchronized configuration, use [adguardhome-sync](https://github.com/bakito/adguardhome-sync).

## Notes

- **User:** Configurable via `AGH_USER` (default: `bsd`, set to `root` for port 53)
- **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD)
- **First Run:** Setup wizard configures DNS and web ports

## Links

- [Website](https://adguard.com/adguard-home.html)
- [Documentation](https://github.com/AdguardTeam/AdGuardHome/wiki)
- [FreshPorts](https://www.freshports.org/www/adguardhome/)
