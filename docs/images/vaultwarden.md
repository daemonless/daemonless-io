---
title: "Vaultwarden on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Vaultwarden on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  VAULTWARDEN_PORT:
    default: "8080"
    description: Vaultwarden Host Port
---

# :simple-bitwarden: Vaultwarden

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/vaultwarden/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/vaultwarden/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/vaultwarden?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/vaultwarden/commits)

Vaultwarden (Bitwarden compatible backend) on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **Upstream Binary**. Downloads the official release. | Most users. Matches Linux Docker behavior. |
| `pkg` | **FreeBSD Port**. Installs from Quarterly ports. | Stability. Uses system libraries. |
| `pkg-latest` | **FreeBSD Port**. Installs from Latest ports. | Bleeding edge system packages. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      vaultwarden:
        image: @REGISTRY@/vaultwarden:latest
        container_name: vaultwarden
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - SIGNUPS_ALLOWED=true
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@VAULTWARDEN_CONFIG_PATH@:/config
        ports:
          - @VAULTWARDEN_PORT@:8080
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name vaultwarden \
      -p @VAULTWARDEN_PORT@:8080 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e SIGNUPS_ALLOWED=true \
      -v @CONTAINER_CONFIG_ROOT@/@VAULTWARDEN_CONFIG_PATH@:/config \ 
      @REGISTRY@/vaultwarden:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy vaultwarden
      containers.podman.podman_container:
        name: vaultwarden
        image: @REGISTRY@/vaultwarden:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          SIGNUPS_ALLOWED: "true"
        ports:
          - "@VAULTWARDEN_PORT@:8080"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@VAULTWARDEN_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@VAULTWARDEN_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `SIGNUPS_ALLOWED` | `true` | Enable/disable user registration (true/false) |


### Volumes

| Path | Description |
|------|-------------|
| `/config` | Data directory (database, attachments, icons) |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8080` | TCP |  |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://github.com/dani-garcia/vaultwarden){ .md-button .md-button--primary }
[Source Code](https://github.com/dani-garcia/vaultwarden){ .md-button }
[FreshPorts](https://www.freshports.org/security/vaultwarden/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.