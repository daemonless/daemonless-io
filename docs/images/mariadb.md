---
title: "MariaDB on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install MariaDB on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  MARIADB_PORT:
    default: "3306"
    description: MariaDB Host Port
---

# :simple-mariadb: MariaDB

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/mariadb/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/mariadb/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/mariadb?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/mariadb/commits)

MariaDB database server for FreeBSD.

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
      mariadb:
        image: @REGISTRY@/mariadb:latest
        container_name: mariadb
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - MYSQL_ROOT_PASSWORD=changeme
          - MYSQL_DATABASE=mydb
          - MYSQL_USER=myuser
          - MYSQL_PASSWORD=mypassword
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@MARIADB_CONFIG_PATH@:/config
        ports:
          - @MARIADB_PORT@:3306
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name mariadb \
      -p @MARIADB_PORT@:3306 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e MYSQL_ROOT_PASSWORD=changeme \
      -e MYSQL_DATABASE=mydb \
      -e MYSQL_USER=myuser \
      -e MYSQL_PASSWORD=mypassword \
      -v @CONTAINER_CONFIG_ROOT@/@MARIADB_CONFIG_PATH@:/config \ 
      @REGISTRY@/mariadb:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy mariadb
      containers.podman.podman_container:
        name: mariadb
        image: @REGISTRY@/mariadb:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          MYSQL_ROOT_PASSWORD: "changeme"
          MYSQL_DATABASE: "mydb"
          MYSQL_USER: "myuser"
          MYSQL_PASSWORD: "mypassword"
        ports:
          - "@MARIADB_PORT@:3306"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@MARIADB_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@MARIADB_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` |  |
| `PGID` | `1000` |  |
| `TZ` | `Etc/UTC` |  |
| `MYSQL_ROOT_PASSWORD` | `changeme` | Root password (required on first run) |
| `MYSQL_DATABASE` | `mydb` | Database to create on first run |
| `MYSQL_USER` | `myuser` | User to create on first run |
| `MYSQL_PASSWORD` | `mypassword` | Password for MYSQL_USER |


### Volumes

| Path | Description |
|------|-------------|
| `/config` | MariaDB configuration and data |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3306` | TCP | MariaDB port |


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://mariadb.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/MariaDB/server){ .md-button }
[FreshPorts](https://www.freshports.org/databases/mariadb114-server/){ .md-button }

---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.