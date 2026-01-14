---
title: "Woodpecker CI on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Woodpecker CI on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  WOODPECKER_PORT:
    default: "8000"
    description: Woodpecker CI Host Port
---

# :material-hammer: Woodpecker CI

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/woodpecker/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/woodpecker/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/woodpecker?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/woodpecker/commits)

Woodpecker CI server and agent on FreeBSD.

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
      woodpecker:
        image: ghcr.io/daemonless/woodpecker:latest
        container_name: woodpecker
        environment:
          - WOODPECKER_SERVER_ENABLE=true
          - WOODPECKER_DATABASE_DRIVER=sqlite3
          - WOODPECKER_DATABASE_DATASOURCE=/config/woodpecker.sqlite
          - WOODPECKER_AGENT_SECRET=agent-secret
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@WOODPECKER_CONFIG_PATH@:/config
        ports:
          - @WOODPECKER_PORT@:8000
          - 9000:9000
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name woodpecker \
      -p @WOODPECKER_PORT@:8000 \
      -p 9000:9000 \
      -e WOODPECKER_SERVER_ENABLE=true \
      -e WOODPECKER_DATABASE_DRIVER=sqlite3 \
      -e WOODPECKER_DATABASE_DATASOURCE=/config/woodpecker.sqlite \
      -e WOODPECKER_AGENT_SECRET=agent-secret \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@WOODPECKER_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/woodpecker:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy woodpecker
      containers.podman.podman_container:
        name: woodpecker
        image: ghcr.io/daemonless/woodpecker:latest
        state: started
        restart_policy: always
        env:
          WOODPECKER_SERVER_ENABLE: "true"
          WOODPECKER_DATABASE_DRIVER: "sqlite3"
          WOODPECKER_DATABASE_DATASOURCE: "/config/woodpecker.sqlite"
          WOODPECKER_AGENT_SECRET: "agent-secret"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@WOODPECKER_PORT@:8000"
          - "9000:9000"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@WOODPECKER_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@WOODPECKER_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WOODPECKER_SERVER_ENABLE` | `true` | Enable Woodpecker Server (true/false) |
| `WOODPECKER_DATABASE_DRIVER` | `sqlite3` |  |
| `WOODPECKER_DATABASE_DATASOURCE` | `/config/woodpecker.sqlite` |  |
| `WOODPECKER_AGENT_SECRET` | `agent-secret` | Shared secret for server-agent communication |
| `PUID` | `1000` |  |
| `PGID` | `1000` |  |
| `TZ` | `UTC` |  |
### Volumes

| Path | Description |
|------|-------------|
| `/config` | Data directory (database, logs) |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `8000` | TCP | Server Web UI/API |
| `9000` | TCP | GRPC (Server/Agent communication) |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://woodpecker-ci.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/woodpecker-ci/woodpecker){ .md-button }
[FreshPorts](https://www.freshports.org/devel/woodpecker-server/){ .md-button }