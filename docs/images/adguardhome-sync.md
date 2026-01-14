---
title: "AdGuardHome Sync on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install AdGuardHome Sync on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  ADGUARDHOME_SYNC_PORT:
    default: "8080"
    description: AdGuardHome Sync Host Port
---

# :simple-adguard: AdGuardHome Sync

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/adguardhome-sync/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/adguardhome-sync/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/adguardhome-sync?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/adguardhome-sync/commits)

Sync AdGuardHome configuration to replica instances.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **Upstream Binary**. Downloads the official release. | Most users. Matches Linux Docker behavior. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      adguardhome-sync:
        image: ghcr.io/daemonless/adguardhome-sync:latest
        container_name: adguardhome-sync
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_SYNC_CONFIG_PATH@:/config
        ports:
          - @ADGUARDHOME_SYNC_PORT@:8080
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name adguardhome-sync \
      -p @ADGUARDHOME_SYNC_PORT@:8080 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_SYNC_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/adguardhome-sync:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy adguardhome-sync
      containers.podman.podman_container:
        name: adguardhome-sync
        image: ghcr.io/daemonless/adguardhome-sync:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@ADGUARDHOME_SYNC_PORT@:8080"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@ADGUARDHOME_SYNC_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@ADGUARDHOME_SYNC_PORT@`

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
| `/config` | Configuration directory |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8080` | TCP | Metrics/API |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://github.com/bakito/adguardhome-sync){ .md-button .md-button--primary }
[Source Code](https://github.com/bakito/adguardhome-sync){ .md-button }
