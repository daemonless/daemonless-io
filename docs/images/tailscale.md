---
title: "Tailscale on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Tailscale on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
---

# :simple-tailscale: Tailscale

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/tailscale/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/tailscale/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/tailscale?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/tailscale/commits)

Tailscale mesh VPN on FreeBSD.

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
      tailscale:
        image: @REGISTRY@/tailscale:latest
        container_name: tailscale
        environment:
          - TS_AUTHKEY=tskey-auth-xxxx
          - TS_EXTRA_ARGS=--advertise-exit-node
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@TAILSCALE_CONFIG_PATH@:/config
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name tailscale \
      -e TS_AUTHKEY=tskey-auth-xxxx \
      -e TS_EXTRA_ARGS=--advertise-exit-node \
      -v @CONTAINER_CONFIG_ROOT@/@TAILSCALE_CONFIG_PATH@:/config \ 
      @REGISTRY@/tailscale:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy tailscale
      containers.podman.podman_container:
        name: tailscale
        image: @REGISTRY@/tailscale:latest
        state: started
        restart_policy: always
        env:
          TS_AUTHKEY: "tskey-auth-xxxx"
          TS_EXTRA_ARGS: "--advertise-exit-node"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@TAILSCALE_CONFIG_PATH@:/config"
    ```

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TS_AUTHKEY` | `tskey-auth-xxxx` | Optional: Tailscale Auth Key for automatic login |
| `TS_EXTRA_ARGS` | `--advertise-exit-node` | Optional: Additional arguments for tailscale up |


### Volumes

| Path | Description |
|------|-------------|
| `/config` | State directory (tailscaled.state) |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `root` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://tailscale.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/tailscale/tailscale){ .md-button }
[FreshPorts](https://www.freshports.org/security/tailscale/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.