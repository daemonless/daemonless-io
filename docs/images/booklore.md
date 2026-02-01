---
title: "BookLore on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install BookLore on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
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
        image: @REGISTRY@/booklore:latest
        container_name: booklore
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - SPRING_DATASOURCE_URL=jdbc:mariadb://127.0.0.1:3306/booklore
          - SPRING_DATASOURCE_USERNAME=booklore
          - SPRING_DATASOURCE_PASSWORD=changeme
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@BOOKLORE_APP_DATA_PATH@:/app/data
          - @BOOKS_PATH@:/books
          - @CONTAINER_CONFIG_ROOT@/@BOOKLORE_BOOKDROP_PATH@:/bookdrop
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name booklore \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e SPRING_DATASOURCE_URL=jdbc:mariadb://127.0.0.1:3306/booklore \
      -e SPRING_DATASOURCE_USERNAME=booklore \
      -e SPRING_DATASOURCE_PASSWORD=changeme \
      -v @CONTAINER_CONFIG_ROOT@/@BOOKLORE_APP_DATA_PATH@:/app/data \ 
      -v @BOOKS_PATH@:/books \ 
      -v @CONTAINER_CONFIG_ROOT@/@BOOKLORE_BOOKDROP_PATH@:/bookdrop \ 
      @REGISTRY@/booklore:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy booklore
      containers.podman.podman_container:
        name: booklore
        image: @REGISTRY@/booklore:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          SPRING_DATASOURCE_URL: "jdbc:mariadb://127.0.0.1:3306/booklore"
          SPRING_DATASOURCE_USERNAME: "booklore"
          SPRING_DATASOURCE_PASSWORD: "changeme"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@BOOKLORE_APP_DATA_PATH@:/app/data"
          - "@BOOKS_PATH@:/books"
          - "@CONTAINER_CONFIG_ROOT@/@BOOKLORE_BOOKDROP_PATH@:/bookdrop"
    ```

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` |  |
| `PGID` | `1000` |  |
| `TZ` | `Etc/UTC` |  |
| `SPRING_DATASOURCE_URL` | `jdbc:mariadb://127.0.0.1:3306/booklore` | MariaDB JDBC URL (e.g., jdbc:mariadb://mariadb:3306/booklore) |
| `SPRING_DATASOURCE_USERNAME` | `booklore` | Database username |
| `SPRING_DATASOURCE_PASSWORD` | `changeme` | Database password |


### Volumes

| Path | Description |
|------|-------------|
| `/app/data` | Configuration and application data |
| `/books` | Book library directory |
| `/bookdrop` | Drop folder for automatic imports |


## Networking

This compose uses `network_mode: host` so services communicate via `127.0.0.1`.

For isolated networking (multiple stacks, no port conflicts), use bridge mode with the [dnsname CNI plugin](https://github.com/containers/dnsname):

```yaml
services:
  booklore:
    # remove network_mode: host, add ports
    ports:
      - "6060:6060"
    environment:
      SPRING_DATASOURCE_URL: "jdbc:mariadb://mariadb:3306/booklore"

  mariadb:
    # remove network_mode: host
    # container name becomes DNS hostname
```

## Migration from Official Image

This image uses `/app/data` for application data, matching the official `ghcr.io/booklore-app/booklore` image. You can migrate from Linux to FreeBSD:

1. Stop containers on source host
2. Copy `/containers/booklore/` (data + mariadb) to destination
3. Start containers on destination

The MariaDB data format is compatible between Linux and FreeBSD.


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://booklore.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/booklore-app/booklore){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.