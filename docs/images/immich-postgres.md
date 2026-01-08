---
title: immich-postgres - FreeBSD OCI Container
description: PostgreSQL 14 with pgvector + VectorChord for Immich  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# immich-postgres

PostgreSQL 14 with pgvector + VectorChord for [Immich](https://immich.app/).

!!! note "Part of the Immich Stack"
    This is just one component of Immich. For the complete setup (docker-compose, configuration, etc.), please see the [Daemonless Immich Stack](https://github.com/daemonless/immich).

Drop-in compatible with official Immich PostgreSQL image.

| | |
|---|---|
| **Port** | 5432 |
| **Registry** | `ghcr.io/daemonless/immich-postgres` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/immich-postgres](https://github.com/daemonless/immich-postgres) |

!!! warning "Requires patched ocijail"
    This application requires the `allow.mlock` annotation.
    See [ocijail patch](../guides/ocijail-patch.md).

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name immich-postgres \
      --annotation 'org.freebsd.jail.allow.sysvipc=true' \
      -p 5432:5432 \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=immich \
      -v /containers/immich/postgres:/config \
      ghcr.io/daemonless/immich-postgres:latest
    ```
    
    **Note:** The `org.freebsd.jail.allow.sysvipc=true` annotation is required for PostgreSQL shared memory. This requires a patched version of `ocijail`. See the [ocijail patch guide](https://daemonless.io/guides/ocijail-patch/) for build instructions.

=== "Compose"

    ```yaml
    services:
      immich-postgres:
        image: ghcr.io/daemonless/immich-postgres:latest
        container_name: immich-postgres
        environment:
          - POSTGRES_PASSWORD=postgres
          - POSTGRES_DB=immich
        volumes:
          - /data/config/postgres:/config
        ports:
          - 5432:5432
        annotations:
          org.freebsd.jail.allow.sysvipc: "true"
        restart: unless-stopped
    ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database superuser name | `postgres` |
| `POSTGRES_PASSWORD` | Superuser password | `postgres` |
| `POSTGRES_DB` | Default database to create | `immich` |
| `PGDATA` | Data directory location | `/config/data` |

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | `databases/postgresql14-server` | FreeBSD latest packages (Alias for :pkg-latest) |
| `:pkg` | `databases/postgresql14-server` | FreeBSD quarterly packages |
| `:pkg-latest` | `databases/postgresql14-server` | FreeBSD latest packages |

## Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration and data directory (PGDATA is in `/config/data`) |

## Ports

| Port | Description |
|------|-------------|
| 5432 | PostgreSQL |

## Features

- **PostgreSQL 14:** Matches official Immich requirements.
- **pgvector:** 0.8.x extension installed (via ports).
- **VectorChord:** 0.4.x extension installed (built from source).
- **Auto-init:** Extensions enabled automatically on database creation.

## Extensions

Extensions are automatically enabled:

```sql
CREATE EXTENSION IF NOT EXISTS vector;      -- pgvector
CREATE EXTENSION IF NOT EXISTS vchord;      -- VectorChord
```

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base-image` (FreeBSD)
- **Migration:** Fully compatible with official Immich Postgres data.

## Links

- [Immich](https://immich.app/)
- [PostgreSQL](https://www.postgresql.org/)
