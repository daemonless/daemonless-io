---
title: "Mealie on FreeBSD: Native OCI Container using Podman & Jails"
description: "Install Mealie on FreeBSD natively using Podman and Daemonless. Enjoy lightweight, secure OCI containers in FreeBSD Jails without the overhead of Linux VMs."
placeholders:
  MEALIE_PORT:
    default: "9000"
    description: Mealie Host Port
---

# :material-food: Mealie

[![Build Status](https://img.shields.io/github/actions/workflow/status/daemonless/mealie/build.yaml?style=flat-square&label=Build&color=green)](https://github.com/daemonless/mealie/actions)
[![Last Commit](https://img.shields.io/github/last-commit/daemonless/mealie?style=flat-square&label=Last+Commit&color=blue)](https://github.com/daemonless/mealie/commits)

Self-hosted recipe manager and meal planner on FreeBSD.

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
      mealie:
        image: ghcr.io/daemonless/mealie:latest
        container_name: mealie
        environment:
          - BASE_URL=http://localhost:9000
          - PUID=@PUID@
          - PGID=@PGID@
          - TZ=@TZ@
        volumes:
          - @CONTAINER_CONFIG_ROOT@/@MEALIE_CONFIG_PATH@:/config
        ports:
          - @MEALIE_PORT@:9000
        restart: unless-stopped
    ```

=== ":material-console: Podman CLI"

    ```bash
    podman run -d --name mealie \
      -p @MEALIE_PORT@:9000 \
      -e BASE_URL=http://localhost:9000 \
      -e PUID=@PUID@ \
      -e PGID=@PGID@ \
      -e TZ=@TZ@ \
      -v @CONTAINER_CONFIG_ROOT@/@MEALIE_CONFIG_PATH@:/config \ 
      ghcr.io/daemonless/mealie:latest
    ```

=== ":simple-ansible: Ansible"

    ```yaml
    - name: Deploy mealie
      containers.podman.podman_container:
        name: mealie
        image: ghcr.io/daemonless/mealie:latest
        state: started
        restart_policy: always
        env:
          BASE_URL: "http://localhost:9000"
          PUID: "@PUID@"
          PGID: "@PGID@"
          TZ: "@TZ@"
        ports:
          - "@MEALIE_PORT@:9000"
        volumes:
          - "@CONTAINER_CONFIG_ROOT@/@MEALIE_CONFIG_PATH@:/config"
    ```

Access the Web UI at: `http://localhost:@MEALIE_PORT@`

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Parameters
### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:9000` | The base URL for the application (e.g. https://mealie.example.com) |
| `PUID` | `1000` | User ID for the application process |
| `PGID` | `1000` | Group ID for the application process |
| `TZ` | `UTC` | Timezone for the container |
### Volumes

| Path | Description |
|------|-------------|
| `/config` | Data directory (database, images) |
### Ports

| Port | Protocol | Description |
|------|----------|-------------|
| `9000` | TCP | Web UI |

## Using PostgreSQL

By default, Mealie uses SQLite. For better performance with multiple users, use PostgreSQL:

```yaml
services:
  mealie:
    image: ghcr.io/daemonless/mealie:latest
    container_name: mealie
    environment:
      - BASE_URL=http://localhost:@MEALIE_PORT@
      - PUID=@PUID@
      - PGID=@PGID@
      - TZ=@TZ@
      - DB_ENGINE=postgres
      - POSTGRES_USER=mealie
      - POSTGRES_PASSWORD=changeme
      - POSTGRES_SERVER=localhost
      - POSTGRES_PORT=5432
      - POSTGRES_DB=mealie
    volumes:
      - @CONTAINER_CONFIG_ROOT@/@MEALIE_CONFIG_PATH@:/config
    ports:
      - "@MEALIE_PORT@:9000"
    depends_on:
      - postgres
    network_mode: host
    restart: unless-stopped

  postgres:
    image: ghcr.io/daemonless/postgres:latest
    container_name: mealie-postgres
    environment:
      - POSTGRES_USER=mealie
      - POSTGRES_PASSWORD=changeme
      - POSTGRES_DB=mealie
    volumes:
      - @CONTAINER_CONFIG_ROOT@/mealie-postgres:/config
    network_mode: host
    restart: unless-stopped
```

**Note:** With `network_mode: host`, use `localhost` for `POSTGRES_SERVER`.

## Migrating from Linux

**SQLite:** No issues, just copy your data.

**PostgreSQL:** You cannot copy the postgres data directory between Linux and FreeBSD due to locale incompatibilities. Use `pg_dump`/`pg_restore` instead:

```bash
# On Linux
podman exec mealie-postgres pg_dump -U mealie mealie > mealie.sql

# On FreeBSD (start fresh postgres first, then restore)
cat mealie.sql | podman exec -i mealie-postgres psql -U mealie -d mealie
```

See [daemonless/postgres README](https://github.com/daemonless/postgres#migrating-from-linux) for details.


!!! info "Implementation Details"

    - **User:** `bsd` (UID/GID set via [PUID/PGID](../guides/permissions.md)). Defaults to `1000:1000`.
    - **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD 15.0).

[Website](https://mealie.io/){ .md-button .md-button--primary }
[Source Code](https://github.com/mealie-recipes/mealie){ .md-button }
