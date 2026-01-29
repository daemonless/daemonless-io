---
title: "BookLore on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install BookLore on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  BOOKLORE_PORT:
    default: "6060"
    description: BookLore Host Port
---

# :material-book-open-page-variant: BookLore

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/booklore/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/booklore/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/booklore?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/booklore/commits)

Self-hosted digital library with smart shelves, metadata, OPDS support, and built-in reader.

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
      booklore:
        image: ghcr.io/daemonless/booklore:latest
        container_name: booklore
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - SPRING_DATASOURCE_URL=jdbc:mariadb://mariadb:3306/booklore
          - SPRING_DATASOURCE_USERNAME=booklore
          - SPRING_DATASOURCE_PASSWORD=changeme
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@BOOKLORE_APP_DATA_PATH@:/app/data
          - @BOOKS_PATH@:/books
          - @CONTAINER_CONFIG_ROOT@/@BOOKLORE_BOOKDROP_PATH@:/bookdrop
        ports:
          - @BOOKLORE_PORT@:6060
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name booklore \
      -p @BOOKLORE_PORT@:6060 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e SPRING_DATASOURCE_URL=jdbc:mariadb://mariadb:3306/booklore \
      -e SPRING_DATASOURCE_USERNAME=booklore \
      -e SPRING_DATASOURCE_PASSWORD=changeme \
      -v @CONTAINER_CONFIG_ROOT@/@BOOKLORE_APP_DATA_PATH@:/app/data \ 
      -v @BOOKS_PATH@:/books \ 
      -v @CONTAINER_CONFIG_ROOT@/@BOOKLORE_BOOKDROP_PATH@:/bookdrop \ 
      ghcr.io/daemonless/booklore:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy booklore
      containers.podman.podman_container:
        name: booklore
        image: ghcr.io/daemonless/booklore:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          SPRING_DATASOURCE_URL: "jdbc:mariadb://mariadb:3306/booklore"
          SPRING_DATASOURCE_USERNAME: "booklore"
          SPRING_DATASOURCE_PASSWORD: "changeme"
        ports:
          - "@BOOKLORE_PORT@:6060"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@BOOKLORE_APP_DATA_PATH@:/app/data"
          - "@BOOKS_PATH@:/books"
          - "@CONTAINER_CONFIG_ROOT@/@BOOKLORE_BOOKDROP_PATH@:/bookdrop"
    ```

Access the Web UI at: `http://localhost:@BOOKLORE_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` |  |
| `PGID` | `1000` |  |
| `TZ` | `Etc/UTC` |  |
| `SPRING_DATASOURCE_URL` | `jdbc:mariadb://mariadb:3306/booklore` | MariaDB JDBC URL (e.g., jdbc:mariadb://mariadb:3306/booklore) |
| `SPRING_DATASOURCE_USERNAME` | `booklore` | Database username |
| `SPRING_DATASOURCE_PASSWORD` | `changeme` | Database password |
### Volumes

| Path | Description |
|------|-------------|
| `/app/data` | Configuration and application data |
| `/books` | Book library directory |
| `/bookdrop` | Drop folder for automatic imports |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `6060` | TCP | Web interface |

## Migration from Official Image

This image uses `/app/data` for application data, matching the official `ghcr.io/booklore-app/booklore` image. You can migrate from Linux to FreeBSD:

1. Stop containers on source host
2. Copy `/containers/booklore/` (data + mariadb) to destination
3. Start containers on destination

The MariaDB data format is compatible between Linux and FreeBSD.


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://booklore.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/booklore-app/booklore){ .md-button }
