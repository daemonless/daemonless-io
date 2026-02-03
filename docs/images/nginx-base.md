---
title: "Nginx Base on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Nginx Base on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
---

# :simple-nginx: Nginx Base

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/nginx-base/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/nginx-base/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/nginx-base?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/nginx-base/commits)

Shared base image for Nginx-based applications.

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
      nginx-base:
        image: @REGISTRY@/nginx-base:latest
        container_name: nginx-base
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name nginx-base \
      @REGISTRY@/nginx-base:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy nginx-base
      containers.podman.podman_container:
        name: nginx-base
        image: @REGISTRY@/nginx-base:latest
        state: started
        restart_policy: always
    ```

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

!!! info "Implementation Details"

    - **Architectures:** amd64
    - **User:** `root` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `@REGISTRY@/base` (FreeBSD 15.0).

[Website](https://nginx.org/){ .md-button .md-button--primary }
[Source Code](https://github.com/daemonless/nginx-base){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.