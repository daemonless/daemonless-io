---
title: "Hugo on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Hugo on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  HUGO_PORT:
    default: "1313"
    description: Hugo Host Port
---

# :simple-hugo: Hugo

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/hugo/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/hugo/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/hugo?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/hugo/commits)

The world's fastest framework for building websites.

## Version Tags

| Tag | Description | Best For |
| :--- | :--- | :--- |
| `latest` | **Upstream Binary**. Downloads the official release. | Most users. Matches Linux Docker behavior. |
| `pkg` | **FreeBSD Port**. Installs from Quarterly ports. | Stability. Uses system libraries. |
| `pkg-latest` | **FreeBSD Port**. Installs from Latest ports. | Bleeding edge system packages. |

## Prerequisites

Before deploying, ensure your host environment is ready. See the [Quick Start Guide](../quick-start.md) for host setup instructions.

## Deployment

=== ":material-docker: Podman Compose"

    ```yaml
    services:
      hugo:
        image: ghcr.io/daemonless/hugo:latest
        container_name: hugo
        environment:
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
          - HUGO_BASEURL=http://localhost:1313
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@HUGO_APP_PATH@:/app
        ports:
          - @HUGO_PORT@:1313
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name hugo \
      -p @HUGO_PORT@:1313 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -e HUGO_BASEURL=http://localhost:1313 \
      -v @CONTAINER_CONFIG_ROOT@/@HUGO_APP_PATH@:/app \ 
      ghcr.io/daemonless/hugo:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy hugo
      containers.podman.podman_container:
        name: hugo
        image: ghcr.io/daemonless/hugo:latest
        state: started
        restart_policy: always
        env:
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
          HUGO_BASEURL: "http://localhost:1313"
        ports:
          - "@HUGO_PORT@:1313"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@HUGO_APP_PATH@:/app"
    ```

Access the Web UI at: `http://localhost:@HUGO_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
| `HUGO_BASEURL` | `http://localhost:1313` | Hostname (and path) to the root |
### Volumes

| Path | Description |
|------|-------------|
| `/app` | Website source code (mount your repo here) |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `1313` | TCP | Dev Server Port |

!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://gohugo.io/){ .md-button .md-button--primary }
[Source Code](https://github.com/gohugoio/hugo){ .md-button }
[FreshPorts](https://www.freshports.org/www/gohugo/){ .md-button }