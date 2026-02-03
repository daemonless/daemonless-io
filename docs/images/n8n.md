---
title: "n8n on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install n8n on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  N8N_PORT:
    default: "5678"
    description: n8n Host Port
---

# :simple-n8n: n8n

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/n8n/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/n8n/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/n8n?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/n8n/commits)

Workflow automation tool on FreeBSD.

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
      n8n:
        image: @REGISTRY@/n8n:latest
        container_name: n8n
        environment:
          - N8N_ENCRYPTION_KEY=your-encryption-key-here
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@N8N_CONFIG_PATH@:/config
        ports:
          - @N8N_PORT@:5678
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name n8n \
      -p @N8N_PORT@:5678 \
      -e N8N_ENCRYPTION_KEY=your-encryption-key-here \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@N8N_CONFIG_PATH@:/config \ 
      @REGISTRY@/n8n:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy n8n
      containers.podman.podman_container:
        name: n8n
        image: @REGISTRY@/n8n:latest
        state: started
        restart_policy: always
        env:
          N8N_ENCRYPTION_KEY: "your-encryption-key-here"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@N8N_PORT@:5678"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@N8N_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@N8N_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `N8N_ENCRYPTION_KEY` | `your-encryption-key-here` | Encryption key for credentials (keep safe!) |
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |


### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory (database, workflows) |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `5678` | TCP | Web UI |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://n8n.io/){ .md-button .md-button--primary }
[Source Code](https://github.com/n8n-io/n8n){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.