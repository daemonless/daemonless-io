---
title: "Arr Base on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Arr Base on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
---

# :material-layers: Arr Base

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/arr-base/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/arr-base/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/arr-base?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/arr-base/commits)

Shared base image for *Arr applications (Radarr, Sonarr, Lidarr, Prowlarr) containing common dependencies.

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
      arr-base:
        image: ghcr.io/daemonless/arr-base:latest
        container_name: arr-base
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name arr-base \
      ghcr.io/daemonless/arr-base:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy arr-base
      containers.podman.podman_container:
        name: arr-base
        image: ghcr.io/daemonless/arr-base:latest
        state: started
        restart_policy: always
    ```

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters

!!! info "Implementation Details"

    - **User:** `root` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://wiki.servarr.com/){ .md-button .md-button--primary }
[Source Code](https://github.com/daemonless/arr-base){ .md-button }


---

Need help? Join our [Discord](https://discord.gg/PTg5DJ2y) community.