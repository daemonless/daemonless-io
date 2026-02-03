---
title: "Cloudflared on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Cloudflared on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  CLOUDFLARED_PORT:
    default: "2000"
    description: Cloudflared Host Port
---

# :simple-cloudflare: Cloudflared

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/cloudflared/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/cloudflared/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/cloudflared?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/cloudflared/commits)

Cloudflare Tunnel client for exposing services securely.

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
      cloudflared:
        image: @REGISTRY@/cloudflared:latest
        container_name: cloudflared
        environment:
          - TUNNEL_TOKEN=YOUR_CLOUDFLARE_TOKEN_HERE
          - TUNNEL_METRICS=0.0.0.0:2000
        ports:
          - @CLOUDFLARED_PORT@:2000
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name cloudflared \
      -p @CLOUDFLARED_PORT@:2000 \
      -e TUNNEL_TOKEN=YOUR_CLOUDFLARE_TOKEN_HERE \
      -e TUNNEL_METRICS=0.0.0.0:2000 \
      @REGISTRY@/cloudflared:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy cloudflared
      containers.podman.podman_container:
        name: cloudflared
        image: @REGISTRY@/cloudflared:latest
        state: started
        restart_policy: always
        env:
          TUNNEL_TOKEN: "YOUR_CLOUDFLARE_TOKEN_HERE"
          TUNNEL_METRICS: "0.0.0.0:2000"
        ports:
          - "@CLOUDFLARED_PORT@:2000"
    ```

Access the Web UI at: `http://localhost:@CLOUDFLARED_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TUNNEL_TOKEN` | `YOUR_CLOUDFLARE_TOKEN_HERE` | Required: The Cloudflare Tunnel token. |
| `TUNNEL_METRICS` | `0.0.0.0:2000` | Optional: Address to bind metrics server (default: 0.0.0.0:2000) |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `2000` | TCP |  |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `root` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps){ .md-button .md-button--primary }
[Source Code](https://github.com/cloudflare/cloudflared){ .md-button }
[FreshPorts](https://www.freshports.org/net/cloudflared/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.