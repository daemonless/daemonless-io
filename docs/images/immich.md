---
title: "Immich Stack on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Immich Stack on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  IMMICH_PORT:
    default: "2283"
    description: Immich Stack Host Port
---

# :simple-googlephotos: Immich Stack

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/immich/build.yml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/immich/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/immich?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/immich/commits)

Complete self-hosted photo and video management solution.

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
      immich:
        image: ghcr.io/daemonless/immich:latest
        container_name: immich
        environment:
          - DB_HOSTNAME=immich_postgres
          - DB_USERNAME=postgres
          - DB_PASSWORD=${DB_PASSWORD:-postgres}
          - DB_DATABASE_NAME=immich
          - REDIS_HOSTNAME=immich_redis
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@IMMICH_CONFIG_PATH@:/config
          - @DATA_PATH@:/data
        ports:
          - @IMMICH_PORT@:2283
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name immich \
      -p @IMMICH_PORT@:2283 \
      -e DB_HOSTNAME=immich_postgres \
      -e DB_USERNAME=postgres \
      -e DB_PASSWORD=${DB_PASSWORD:-postgres} \
      -e DB_DATABASE_NAME=immich \
      -e REDIS_HOSTNAME=immich_redis \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@IMMICH_CONFIG_PATH@:/config \ 
      -v @DATA_PATH@:/data \ 
      ghcr.io/daemonless/immich:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy immich
      containers.podman.podman_container:
        name: immich
        image: ghcr.io/daemonless/immich:latest
        state: started
        restart_policy: always
        env:
          DB_HOSTNAME: "immich_postgres"
          DB_USERNAME: "postgres"
          DB_PASSWORD: "${DB_PASSWORD:-postgres}"
          DB_DATABASE_NAME: "immich"
          REDIS_HOSTNAME: "immich_redis"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@IMMICH_PORT@:2283"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@IMMICH_CONFIG_PATH@:/config"
          - "@DATA_PATH@:/data"
    ```

Access the Web UI at: `http://localhost:@IMMICH_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOSTNAME` | `immich_postgres` |  |
| `DB_USERNAME` | `postgres` |  |
| `DB_PASSWORD` | `${DB_PASSWORD:-postgres}` | Postgres database password |
| `DB_DATABASE_NAME` | `immich` |  |
| `REDIS_HOSTNAME` | `immich_redis` |  |
| `PUID` | `1000` | User ID for application processes |
| `PGID` | `1000` | Group ID for application processes |
| `TZ` | `UTC` | Timezone |

### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration files |
| `/data` | Media storage (mapped to UPLOAD_LOCATION) |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `2283` | TCP | Web UI |

!!! info "Implementation Details"

    - **User:** `multiple` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://immich.app/){ .md-button .md-button--primary }
[Source Code](https://github.com/immich-app/immich){ .md-button }
