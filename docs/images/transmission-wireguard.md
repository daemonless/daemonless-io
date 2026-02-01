---
title: "Transmission with WireGuard on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Transmission with WireGuard on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  TRANSMISSION_WIREGUARD_PORT:
    default: "9091"
    description: Transmission with WireGuard Host Port
---

# :simple-wireguard: Transmission with WireGuard

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/transmission-wireguard/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/transmission-wireguard/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/transmission-wireguard?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/transmission-wireguard/commits)

Transmission BitTorrent client with built-in WireGuard VPN support.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **FreeBSD Port**. Installs from latest packages. | Most users. Matches Linux Docker behavior. |
| `pkg` | **FreeBSD Port**. Installs from Quarterly ports. | Stability. Uses system libraries. |
| `pkg-latest` | **FreeBSD Port**. Installs from Latest ports. | Bleeding edge system packages. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      transmission-wireguard:
        image: ghcr.io/daemonless/transmission-wireguard:latest
        container_name: transmission-wireguard
        environment:
          - WG_PRIVATE_KEY=your-private-key
          - WG_PEER_PUBLIC_KEY=vpn-server-public-key
          - WG_ENDPOINT=vpn.example.com:51820
          - WG_ADDRESS=10.5.0.2/32
          - WG_DNS=1.1.1.1
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_CONFIG_PATH@:/config
          - @DOWNLOADS_PATH@:/downloads
          - @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_WATCH_PATH@:/watch
        ports:
          - @TRANSMISSION_WIREGUARD_PORT@:9091
          - 51413:51413
          - 51413:51413
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name transmission-wireguard \
      -p @TRANSMISSION_WIREGUARD_PORT@:9091 \
      -p 51413:51413 \
      -p 51413:51413 \
      -e WG_PRIVATE_KEY=your-private-key \
      -e WG_PEER_PUBLIC_KEY=vpn-server-public-key \
      -e WG_ENDPOINT=vpn.example.com:51820 \
      -e WG_ADDRESS=10.5.0.2/32 \
      -e WG_DNS=1.1.1.1 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_CONFIG_PATH@:/config \ 
      -v @DOWNLOADS_PATH@:/downloads \ 
      -v @CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_WATCH_PATH@:/watch \ 
      ghcr.io/daemonless/transmission-wireguard:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy transmission-wireguard
      containers.podman.podman_container:
        name: transmission-wireguard
        image: ghcr.io/daemonless/transmission-wireguard:latest
        state: started
        restart_policy: always
        env:
          WG_PRIVATE_KEY: "your-private-key"
          WG_PEER_PUBLIC_KEY: "vpn-server-public-key"
          WG_ENDPOINT: "vpn.example.com:51820"
          WG_ADDRESS: "10.5.0.2/32"
          WG_DNS: "1.1.1.1"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@TRANSMISSION_WIREGUARD_PORT@:9091"
          - "51413:51413"
          - "51413:51413"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_CONFIG_PATH@:/config"
          - "@DOWNLOADS_PATH@:/downloads"
          - "@CONTAINER_CONFIG_ROOT@/@TRANSMISSION_WIREGUARD_WATCH_PATH@:/watch"
    ```

Access the Web UI at: `http://localhost:@TRANSMISSION_WIREGUARD_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WG_PRIVATE_KEY` | `your-private-key` | Your WireGuard private key |
| `WG_PEER_PUBLIC_KEY` | `vpn-server-public-key` | VPN server's public key |
| `WG_ENDPOINT` | `vpn.example.com:51820` | VPN server address (host:port) |
| `WG_ADDRESS` | `10.5.0.2/32` | Your tunnel IP address (default: 10.5.0.2/32) |
| `WG_DNS` | `1.1.1.1` | DNS server to use (default: 1.1.1.1) |
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |


### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory (settings.json, WireGuard configs) |
| `/downloads` | Download directory |
| `/watch` | Watch directory for torrent files |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `9091` | TCP | Web UI |
| `51413` | TCP | Torrent traffic (TCP/UDP) |
| `51413` | TCP | Torrent traffic (TCP/UDP) |


## WireGuard Setup

### Host Requirements

Load the WireGuard kernel module on the host:
```bash
kldload if_wg
echo 'if_wg_load="YES"' >> /boot/loader.conf
```

### VNET Required

This container requires its own network stack. Add the annotation:
```
--annotation 'org.freebsd.jail.vnet=new'
```

### Getting VPN Credentials

From your VPN provider (Mullvad, PIA, ProtonVPN, etc.), get:
- **Private Key** - Your client private key
- **Public Key** - The VPN server's public key
- **Endpoint** - Server address like `vpn.example.com:51820`
- **Address** - Your assigned tunnel IP

### Kill Switch

Traffic is routed through the VPN interface. If the VPN connection drops, Transmission loses connectivity - no IP leaks.

### Verifying VPN

Check your public IP from inside the container:
```bash
podman exec transmission-wireguard fetch -qo - https://ifconfig.me
```


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://transmissionbt.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/transmission/transmission){ .md-button }
[FreshPorts](https://www.freshports.org/net-p2p/transmission-daemon/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.