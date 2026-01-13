---
title: "Redis on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Redis on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  REDIS_PORT:
    default: "6379"
    description: Redis Host Port
---

# :simple-redis: Redis

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/redis/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/redis/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/redis?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/redis/commits)

Redis key-value store on FreeBSD.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **FreeBSD Port**. Installs from latest packages. | Most users. Matches Linux Docker behavior. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      redis:
        image: ghcr.io/daemonless/redis:latest
        container_name: redis
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@REDIS_CONFIG_PATH@:/config
        ports:
          - @REDIS_PORT@:6379
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name redis \
      -p @REDIS_PORT@:6379 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@REDIS_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/redis:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy redis
      containers.podman.podman_container:
        name: redis
        image: ghcr.io/daemonless/redis:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@REDIS_PORT@:6379"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@REDIS_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@REDIS_PORT@`

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
| `/config` | Data and configuration directory |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `6379` | TCP | Redis port |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://redis.io/){ .md-button .md-button--primary }
[Source Code](https://github.com/redis/redis){ .md-button }
[FreshPorts](https://www.freshports.org/databases/redis/){ .md-button }