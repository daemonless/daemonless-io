---
title: "AdGuard Home on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install AdGuard Home on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  ADGUARDHOME_PORT:
    default: "53"
    description: AdGuard Home Host Port
---

# :simple-adguard: AdGuard Home

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/adguardhome/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/adguardhome/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/adguardhome?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/adguardhome/commits)

Network-wide ads & trackers blocking DNS server on FreeBSD.

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
      adguardhome:
        image: ghcr.io/daemonless/adguardhome:latest
        container_name: adguardhome
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_OPT_ADGUARDHOME_CONF_PATH@:/opt/adguardhome/conf
          - @CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_OPT_ADGUARDHOME_WORK_PATH@:/opt/adguardhome/work
        ports:
          - @ADGUARDHOME_PORT@:53
          - 53:53
          - 67:67
          - 68:68
          - 80:80
          - 443:443
          - 443:443
          - 784:784
          - 853:853
          - 853:853
          - 3000:3000
          - 5443:5443
          - 5443:5443
          - 6060:6060
          - 8853:8853
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name adguardhome \
      -p @ADGUARDHOME_PORT@:53 \
      -p 53:53 \
      -p 67:67 \
      -p 68:68 \
      -p 80:80 \
      -p 443:443 \
      -p 443:443 \
      -p 784:784 \
      -p 853:853 \
      -p 853:853 \
      -p 3000:3000 \
      -p 5443:5443 \
      -p 5443:5443 \
      -p 6060:6060 \
      -p 8853:8853 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_OPT_ADGUARDHOME_CONF_PATH@:/opt/adguardhome/conf \ 
      -v @CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_OPT_ADGUARDHOME_WORK_PATH@:/opt/adguardhome/work \ 
      ghcr.io/daemonless/adguardhome:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy adguardhome
      containers.podman.podman_container:
        name: adguardhome
        image: ghcr.io/daemonless/adguardhome:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@ADGUARDHOME_PORT@:53"
          - "53:53"
          - "67:67"
          - "68:68"
          - "80:80"
          - "443:443"
          - "443:443"
          - "784:784"
          - "853:853"
          - "853:853"
          - "3000:3000"
          - "5443:5443"
          - "5443:5443"
          - "6060:6060"
          - "8853:8853"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_OPT_ADGUARDHOME_CONF_PATH@:/opt/adguardhome/conf"
          - "@CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_OPT_ADGUARDHOME_WORK_PATH@:/opt/adguardhome/work"
    ```

Access the Web UI at: `http://localhost:@ADGUARDHOME_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |

### Volumes

| Path | Description |
|------|-------------|
| `/opt/adguardhome/conf` | Configuration files |
| `/opt/adguardhome/work` | Work directory (database, logs, data) |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `53` | TCP | DNS (TCP/UDP) |
| `53` | TCP | DNS (TCP/UDP) |
| `67` | TCP |  |
| `68` | TCP |  |
| `80` | TCP | HTTP |
| `443` | TCP | HTTPS / DNS-over-HTTPS (TCP/UDP) |
| `443` | TCP | HTTPS / DNS-over-HTTPS (TCP/UDP) |
| `784` | TCP |  |
| `853` | TCP | DNS-over-TLS (TCP/UDP) |
| `853` | TCP | DNS-over-TLS (TCP/UDP) |
| `3000` | TCP | Web UI (Setup/Admin) |
| `5443` | TCP | DNS-over-HTTPS (TCP/UDP) |
| `5443` | TCP | DNS-over-HTTPS (TCP/UDP) |
| `6060` | TCP | Admin API |
| `8853` | TCP |  |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://adguard.com/adguard-home.html){ .md-button .md-button--primary }
[Source Code](https://github.com/AdguardTeam/AdGuardHome){ .md-button }
[FreshPorts](https://www.freshports.org/net-mgmt/adguardhome/){ .md-button }