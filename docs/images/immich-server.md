---
title: "Immich Server on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Immich Server on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  IMMICH_SERVER_PORT:
    default: "2283"
    description: Immich Server Host Port
---

# :material-server: Immich Server

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/immich-server/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/immich-server/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/immich-server?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/immich-server/commits)

Immich photo management server on FreeBSD.

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
      immich-server:
        image: ghcr.io/daemonless/immich-server:latest
        container_name: immich-server
        environment:
          - DB_HOSTNAME=immich-postgres
          - DB_USERNAME=postgres
          - DB_PASSWORD=postgres
          - DB_DATABASE_NAME=immich
          - REDIS_HOSTNAME=immich-redis
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@IMMICH_SERVER_CONFIG_PATH@:/config
          - @DATA_PATH@:/data
        ports:
          - @IMMICH_SERVER_PORT@:2283
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name immich-server \
      -p @IMMICH_SERVER_PORT@:2283 \
      -e DB_HOSTNAME=immich-postgres \
      -e DB_USERNAME=postgres \
      -e DB_PASSWORD=postgres \
      -e DB_DATABASE_NAME=immich \
      -e REDIS_HOSTNAME=immich-redis \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@IMMICH_SERVER_CONFIG_PATH@:/config \ 
      -v @DATA_PATH@:/data \ 
      ghcr.io/daemonless/immich-server:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy immich-server
      containers.podman.podman_container:
        name: immich-server
        image: ghcr.io/daemonless/immich-server:latest
        state: started
        restart_policy: always
        env:
          DB_HOSTNAME: "immich-postgres"
          DB_USERNAME: "postgres"
          DB_PASSWORD: "postgres"
          DB_DATABASE_NAME: "immich"
          REDIS_HOSTNAME: "immich-redis"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@IMMICH_SERVER_PORT@:2283"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@IMMICH_SERVER_CONFIG_PATH@:/config"
          - "@DATA_PATH@:/data"
    ```

Access the Web UI at: `http://localhost:@IMMICH_SERVER_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOSTNAME` | `immich-postgres` | Postgres database hostname |
| `DB_USERNAME` | `postgres` | Postgres database user |
| `DB_PASSWORD` | `postgres` | Postgres database password |
| `DB_DATABASE_NAME` | `immich` | Postgres database name |
| `REDIS_HOSTNAME` | `immich-redis` | Redis hostname |
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |

### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory (unused but mounted) |
| `/data` | Media storage (photos, videos, thumbnails) |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `2283` | TCP | Web UI/API |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://immich.app/){ .md-button .md-button--primary }
[Source Code](https://github.com/immich-app/immich){ .md-button }
