---
title: "Bichon on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Bichon on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  BICHON_PORT:
    default: "15630"
    description: Bichon Host Port
---

# :material-email: Bichon

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/bichon/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/bichon/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/bichon?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/bichon/commits)

High-performance email archiver and search tool on FreeBSD.

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
      bichon:
        image: @REGISTRY@/bichon:latest
        container_name: bichon
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - BICHON_ENCRYPT_PASSWORD=changeme
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@BICHON_PATH@:/data
        ports:
          - @BICHON_PORT@:15630
        healthcheck:
          test: ["CMD", "{'port': 15630, 'path': '/'}"]
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name bichon \
      -p @BICHON_PORT@:15630 \
      --health-cmd {'port': 15630, 'path': '/'} \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e BICHON_ENCRYPT_PASSWORD=changeme \
      -v @CONTAINER_CONFIG_ROOT@/@BICHON_PATH@:/data \ 
      @REGISTRY@/bichon:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy bichon
      containers.podman.podman_container:
        name: bichon
        image: @REGISTRY@/bichon:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          BICHON_ENCRYPT_PASSWORD: "changeme"
        ports:
          - "@BICHON_PORT@:15630"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@BICHON_PATH@:/data"
    ```

Access the Web UI at: `http://localhost:@BICHON_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `BICHON_ENCRYPT_PASSWORD` | `changeme` | Encryption password for core database |


### Volumes

| Path | Description |
|------|-------------|
| `/data` | Core data and search indices |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `15630` | TCP | Web UI / API |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://github.com/rustmailer/bichon){ .md-button .md-button--primary }
[Source Code](https://github.com/rustmailer/bichon){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/Kb9tkhecZT) community.