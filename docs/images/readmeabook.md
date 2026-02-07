---
title: "ReadMeABook on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install ReadMeABook on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  READMEABOOK_PORT:
    default: "3030"
    description: ReadMeABook Host Port
---

# :material-book-music: ReadMeABook

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/readmeabook/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/readmeabook/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/readmeabook?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/readmeabook/commits)

Audiobook request and management platform with AI recommendations.

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
      readmeabook:
        image: @REGISTRY@/readmeabook:latest
        container_name: readmeabook
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - LOG_LEVEL=info
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@READMEABOOK_CONFIG_PATH@:/app/config
          - @CONTAINER_CONFIG_ROOT@/@READMEABOOK_CACHE_PATH@:/app/cache
          - @CONTAINER_CONFIG_ROOT@/@READMEABOOK_POSTGRES_PATH@:/var/lib/postgresql/data
          - @CONTAINER_CONFIG_ROOT@/@READMEABOOK_REDIS_PATH@:/var/lib/redis
          - @DOWNLOADS_PATH@:/downloads
          - @MEDIA_PATH@:/media
        ports:
          - @READMEABOOK_PORT@:3030
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name readmeabook \
      -p @READMEABOOK_PORT@:3030 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e LOG_LEVEL=info \
      -v @CONTAINER_CONFIG_ROOT@/@READMEABOOK_CONFIG_PATH@:/app/config \ 
      -v @CONTAINER_CONFIG_ROOT@/@READMEABOOK_CACHE_PATH@:/app/cache \ 
      -v @CONTAINER_CONFIG_ROOT@/@READMEABOOK_POSTGRES_PATH@:/var/lib/postgresql/data \ 
      -v @CONTAINER_CONFIG_ROOT@/@READMEABOOK_REDIS_PATH@:/var/lib/redis \ 
      -v @DOWNLOADS_PATH@:/downloads \ 
      -v @MEDIA_PATH@:/media \ 
      @REGISTRY@/readmeabook:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy readmeabook
      containers.podman.podman_container:
        name: readmeabook
        image: @REGISTRY@/readmeabook:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          LOG_LEVEL: "info"
        ports:
          - "@READMEABOOK_PORT@:3030"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@READMEABOOK_CONFIG_PATH@:/app/config"
          - "@CONTAINER_CONFIG_ROOT@/@READMEABOOK_CACHE_PATH@:/app/cache"
          - "@CONTAINER_CONFIG_ROOT@/@READMEABOOK_POSTGRES_PATH@:/var/lib/postgresql/data"
          - "@CONTAINER_CONFIG_ROOT@/@READMEABOOK_REDIS_PATH@:/var/lib/redis"
          - "@DOWNLOADS_PATH@:/downloads"
          - "@MEDIA_PATH@:/media"
    ```

Access the Web UI at: `http://localhost:@READMEABOOK_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `LOG_LEVEL` | `info` | Logging level (default: info) |


### Volumes

| Path | Description |
|------|-------------|
| `/app/config` | Application configuration and secrets |
| `/app/cache` | Thumbnail and metadata cache |
| `/var/lib/postgresql/data` | PostgreSQL database storage |
| `/var/lib/redis` | Redis data persistence |
| `/downloads` | Download client path |
| `/media` | Audiobook library |


### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `3030` | TCP | Web UI |


!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://github.com/kikootwo/readmeabook){ .md-button .md-button--primary }
[Source Code](https://github.com/kikootwo/readmeabook){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.