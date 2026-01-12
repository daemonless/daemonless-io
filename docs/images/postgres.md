---
title: "PostgreSQL on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install PostgreSQL on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  POSTGRES_PORT:
    default: "5432"
    description: PostgreSQL Host Port
---

# :simple-postgresql: PostgreSQL

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/postgres/build.yml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/postgres/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/postgres?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/postgres/commits)

The World's Most Advanced Open Source Relational Database on FreeBSD.

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
      postgres:
        image: ghcr.io/daemonless/postgres:latest
        container_name: postgres
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=postgres
          - POSTGRES_DB=postgres
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@POSTGRES_VAR_LIB_POSTGRESQL_DATA_PATH@:/var/lib/postgresql/data
        ports:
          - @POSTGRES_PORT@:5432
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name postgres \
      -p @POSTGRES_PORT@:5432 \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=postgres \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@POSTGRES_VAR_LIB_POSTGRESQL_DATA_PATH@:/var/lib/postgresql/data \ 
      ghcr.io/daemonless/postgres:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy postgres
      containers.podman.podman_container:
        name: postgres
        image: ghcr.io/daemonless/postgres:latest
        state: started
        restart_policy: always
        env:
          POSTGRES_USER: "postgres"
          POSTGRES_PASSWORD: "postgres"
          POSTGRES_DB: "postgres"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@POSTGRES_PORT@:5432"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@POSTGRES_VAR_LIB_POSTGRESQL_DATA_PATH@:/var/lib/postgresql/data"
    ```

Access the Web UI at: `http://localhost:@POSTGRES_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | Database superuser name (default: postgres) |
| `POSTGRES_PASSWORD` | `postgres` | Database superuser password |
| `POSTGRES_DB` | `postgres` | Default database to create (default: same as user) |
| `PUID` | `1000` |  |
| `PGID` | `1000` |  |
| `TZ` | `UTC` |  |

### Volumes

| Path | Description |
|------|-------------|
| `/var/lib/postgresql/data` | Database data directory |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `5432` | TCP | PostgreSQL port |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://www.postgresql.org/){ .md-button .md-button--primary }
[Source Code](https://www.postgresql.org/){ .md-button }
[FreshPorts](https://www.freshports.org/databases/postgresql17-server/){ .md-button }