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

=== ":appjail-appjail: AppJail Director"

    **.env**:

    ```
    DIRECTOR_PROJECT=nginx-base
    ```

    **Makejail**:

    ```
    ARG tag=latest

    OPTION start
    OPTION overwrite=force
    OPTION from=@REGISTRY@/nginx-base:${tag}

    CMD chmod 655 /usr/local/www/html
    CMD echo "<h1>Hello!</h1>" > /usr/local/www/html/index.html
    ```

    **appjail-director.yml**:

    ```yaml
    options:
      - alias:
      - ip4_inherit:
      - ip6_inherit:
    services:
      nginx-base:
        name: nginx-base
        options:
          - container: 'boot args:--pull'
    ```

    **Console**:

    ```console
    # appjail-director up
    Starting Director (project:nginx-base) ...
    Creating nginx-base (nginx-base) ... Done.
    Finished: nginx-base
    # curl http://localhost
    <h1>Hello!</h1>
    ```

=== ":material-console: AppJail"

    ```console
    # mkdir -p wwwsrv
    # echo 'Hello, world!' > wwwsrv/index.html
    # appjail oci run -d \
        -o overwrite=force \
        -o alias \
        -o ip4_inherit \
        -o ip6_inherit \
        -o container="args:--pull" \
        -o fstab="$PWD/wwwsrv /usr/local/www/html nullfs ro" \
        -o ephemeral \
            @REGISTRY@/nginx-base nginx-base
    ...
    [00:00:14] [ info  ] [nginx-base] Detached: pid:39270, log:jails/nginx-base/container/2026-03-13.log
    # appjail logs tail jails/nginx-base/container/2026-03-13.log
    [init] Starting container initialization...
    ifconfig: up: permission denied
    [init] Running: /etc/cont-init.d/10-usermod
    [usermod] Setting up user bsd with PUID=1000 PGID=1000
    [usermod] User bsd configured (uid=1000, gid=1000)
    [init] Running: /etc/cont-init.d/20-nginx-perms
    [nginx-perms] Setting nginx directory ownership
    [nginx-perms] Nginx directories configured for bsd user
    [init] Initialization complete
    [init] Starting s6 supervision...
    # curl http://localhost
    <h1>Hello, world!</h1>
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

Need help? Join our [Discord](https://discord.gg/Kb9tkhecZT) community.
