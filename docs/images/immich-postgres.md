---
title: "Immich PostgreSQL on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Immich PostgreSQL on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  IMMICH_POSTGRES_PORT:
    default: "5432"
    description: Immich PostgreSQL Host Port
---

# :simple-postgresql: Immich PostgreSQL

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/immich-postgres/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/immich-postgres/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/immich-postgres?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/immich-postgres/commits)

PostgreSQL 14 with pgvector/pgvecto.rs extensions for Immich.

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
      immich-postgres:
        image: ghcr.io/daemonless/immich-postgres:latest
        container_name: immich-postgres
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=postgres
          - POSTGRES_DB=immich
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@IMMICH_POSTGRES_PATH@:/var/lib/postgresql/data
        ports:
          - @IMMICH_POSTGRES_PORT@:5432
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name immich-postgres \
      -p @IMMICH_POSTGRES_PORT@:5432 \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=immich \
      -v @CONTAINER_CONFIG_ROOT@/@IMMICH_POSTGRES_PATH@:/var/lib/postgresql/data \ 
      ghcr.io/daemonless/immich-postgres:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy immich-postgres
      containers.podman.podman_container:
        name: immich-postgres
        image: ghcr.io/daemonless/immich-postgres:latest
        state: started
        restart_policy: always
        env:
          POSTGRES_USER: "postgres"
          POSTGRES_PASSWORD: "postgres"
          POSTGRES_DB: "immich"
        ports:
          - "@IMMICH_POSTGRES_PORT@:5432"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@IMMICH_POSTGRES_PATH@:/var/lib/postgresql/data"
    ```

Access the Web UI at: `http://localhost:@IMMICH_POSTGRES_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | Database superuser (default: postgres) |
| `POSTGRES_PASSWORD` | `postgres` | Database password (default: postgres) |
| `POSTGRES_DB` | `immich` | Database name (default: immich) |
### Volumes

| Path | Description |
|------|-------------|
| `/var/lib/postgresql/data` | Database data directory |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `5432` | TCP | PostgreSQL Port |

This image is part of the [Immich Stack](https://daemonless.io/images/immich).

!!! info "Implementation Details"

    - **User:** `postgres` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://immich.app/){ .md-button .md-button--primary }
[Source Code](https://github.com/immich-app/immich){ .md-button }
[FreshPorts](https://www.freshports.org/databases/postgresql14-server/){ .md-button }