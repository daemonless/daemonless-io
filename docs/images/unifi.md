---
title: "UniFi Network on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install UniFi Network on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  UNIFI_PORT:
    default: "8443"
    description: UniFi Network Host Port
---

# :material-access-point-network: UniFi Network

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/unifi/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/unifi/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/unifi?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/unifi/commits)

UniFi Network Application on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **Upstream Binary**. Downloads the official release. | Most users. Matches Linux Docker behavior. |
| `pkg` | **FreeBSD Port**. Installs from Quarterly ports. | Stability. Uses system libraries. |
| `pkg-latest` | **FreeBSD Port**. Installs from Latest ports. | Bleeding edge system packages. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.
!!! warning "Memory Locking (Critical)"
    This application is built on .NET and requires memory locking enabled in the jail.
    You **must** use the `allow.mlock` annotation and have a [patched ocijail](../guides/ocijail-patch.md).

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      unifi:
        image: ghcr.io/daemonless/unifi:latest
        container_name: unifi
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@UNIFI_CONFIG_PATH@:/config
        ports:
          - @UNIFI_PORT@:8443
          - 8080:8080
          - 8843:8843
          - 8880:8880
          - 6789:6789
          - 3478:3478
          - 10001:10001
        annotations:
          org.freebsd.jail.allow.mlock: "true"
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name unifi \
      -p @UNIFI_PORT@:8443 \
      -p 8080:8080 \
      -p 8843:8843 \
      -p 8880:8880 \
      -p 6789:6789 \
      -p 3478:3478 \
      -p 10001:10001 \
      --annotation 'org.freebsd.jail.allow.mlock=true' \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@UNIFI_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/unifi:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy unifi
      containers.podman.podman_container:
        name: unifi
        image: ghcr.io/daemonless/unifi:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@UNIFI_PORT@:8443"
          - "8080:8080"
          - "8843:8843"
          - "8880:8880"
          - "6789:6789"
          - "3478:3478"
          - "10001:10001"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@UNIFI_CONFIG_PATH@:/config"
        annotation:
          org.freebsd.jail.allow.mlock: "true"
    ```

Access the Web UI at: `http://localhost:@UNIFI_PORT@`

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
| `/config` | Configuration and database directory |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8443` | TCP | Web UI (HTTPS) |
| `8080` | TCP | Device inform |
| `8843` | TCP | Guest portal HTTPS |
| `8880` | TCP | Guest portal HTTP |
| `6789` | TCP | Mobile throughput test |
| `3478` | TCP | STUN (UDP) |
| `10001` | TCP | Device discovery (UDP) |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).
    - **.NET App:** Requires `--annotation 'org.freebsd.jail.allow.mlock=true'` and a [patched ocijail](../guides/ocijail-patch.md).

[Website](https://ui.com/){ .md-button .md-button--primary }
[Source Code](https://ui.com/){ .md-button }
[FreshPorts](https://www.freshports.org/net-mgmt/unifi8/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.