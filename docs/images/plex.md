---
title: "Plex Media Server on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Plex Media Server on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  PLEX_PORT:
    default: "32400"
    description: Plex Media Server Host Port
---

# :simple-plex: Plex Media Server

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/plex/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/plex/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/plex?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/plex/commits)

Plex Media Server on FreeBSD.

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
      plex:
        image: ghcr.io/daemonless/plex:latest
        container_name: plex
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - VERSION=container
          - PLEX_CLAIM=
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@PLEX_CONFIG_PATH@:/config
          - @CONTAINER_CONFIG_ROOT@/@PLEX_TRANSCODE_PATH@:/transcode # optional
          - @MOVIES_PATH@:/movies
          - @TV_PATH@:/tv
        ports:
          - @PLEX_PORT@:32400
          - 1900:1900
          - 32410:32410
          - 32412:32412
          - 32413:32413
          - 32414:32414
          - 32469:32469
          - 8324:8324
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name plex \
      -p @PLEX_PORT@:32400 \
      -p 1900:1900 \
      -p 32410:32410 \
      -p 32412:32412 \
      -p 32413:32413 \
      -p 32414:32414 \
      -p 32469:32469 \
      -p 8324:8324 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e VERSION=container \
      -e PLEX_CLAIM= \
      -v @CONTAINER_CONFIG_ROOT@/@PLEX_CONFIG_PATH@:/config \ 
      -v @CONTAINER_CONFIG_ROOT@/@PLEX_TRANSCODE_PATH@:/transcode \  # optional
      -v @MOVIES_PATH@:/movies \ 
      -v @TV_PATH@:/tv \ 
      ghcr.io/daemonless/plex:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy plex
      containers.podman.podman_container:
        name: plex
        image: ghcr.io/daemonless/plex:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          VERSION: "container"
          PLEX_CLAIM: ""
        ports:
          - "@PLEX_PORT@:32400"
          - "1900:1900"
          - "32410:32410"
          - "32412:32412"
          - "32413:32413"
          - "32414:32414"
          - "32469:32469"
          - "8324:8324"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@PLEX_CONFIG_PATH@:/config"
          - "@CONTAINER_CONFIG_ROOT@/@PLEX_TRANSCODE_PATH@:/transcode" # optional
          - "@MOVIES_PATH@:/movies"
          - "@TV_PATH@:/tv"
    ```

Access the Web UI at: `http://localhost:@PLEX_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `VERSION` | `container` | Plex update channel (container, public, plexpass) |
| `PLEX_CLAIM` | `` | Optional: Claim token from https://plex.tv/claim |
### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration directory |
| `/transcode` | Transcode directory (Optional) |
| `/movies` | Movie library |
| `/tv` | TV series library |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `32400` | TCP | Web UI |
| `1900` | TCP |  |
| `32410` | TCP |  |
| `32412` | TCP |  |
| `32413` | TCP |  |
| `32414` | TCP |  |
| `32469` | TCP |  |
| `8324` | TCP |  |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://plex.tv/){ .md-button .md-button--primary }
[Source Code](https://github.com/daemonless/plex){ .md-button }
[FreshPorts](https://www.freshports.org/multimedia/plexmediaserver/){ .md-button }