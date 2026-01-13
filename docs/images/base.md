---
title: "Base on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Base on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
---

# :simple-freebsd: Base

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/base/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/base/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/base?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/base/commits)

FreeBSD base image with s6 supervision.

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
      base:
        image: ghcr.io/daemonless/base:latest
        container_name: base
        environment:
        volumes:
        ports:
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name base \
      ghcr.io/daemonless/base:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy base
      containers.podman.podman_container:
        name: base
        image: ghcr.io/daemonless/base:latest
        state: started
        restart_policy: always
    ```

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|

### Volumes

| Path | Description |
|------|-------------|

### Ports

| Port | Protocol | Description |
|------|----------|-------------|

!!! info "Implementation Details"

    - **User:** `root` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://www.freebsd.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/freebsd/freebsd-src){ .md-button }
