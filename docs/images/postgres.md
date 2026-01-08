---
title: PostgreSQL - FreeBSD OCI Container
description: PostgreSQL ${PG_VERSION} on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# PostgreSQL

PostgreSQL database server on FreeBSD. **Drop-in replacement** for the official `postgres` Docker image.

> **Requires [patched ocijail](https://github.com/daemonless/daemonless#ocijail-patch)** for SysV IPC support (`org.freebsd.jail.allow.sysvipc=true`)

| | |
|---|---|
| **Port** | 5432 |
| **Registry** | `ghcr.io/daemonless/postgres` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/postgres](https://github.com/daemonless/postgres) |

!!! warning "Requires patched ocijail"
    This application requires the `allow.mlock` annotation.
    See [ocijail patch](../guides/ocijail-patch.md).

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name postgres \
      -p 5432:5432 \
      -e POSTGRES_PASSWORD=mysecretpassword \
      -v /path/to/data:/var/lib/postgresql/data \
      --annotation 'org.freebsd.jail.allow.sysvipc=true' \
      ghcr.io/daemonless/postgres:17
    ```

=== "Compose"

    ```yaml
    services:
      postgres:
        image: ghcr.io/daemonless/postgres:17
        container_name: postgres
        environment:
          - POSTGRES_USER=postgres
          - POSTGRES_PASSWORD=mysecretpassword
          - POSTGRES_DB=mydb
        volumes:
          - /data/postgres:/var/lib/postgresql/data
        ports:
          - 5432:5432
        annotations:
          org.freebsd.jail.allow.sysvipc: "true"
        restart: unless-stopped
    ```

## Tags

| Tag | Base | Description |
|-----|------|-------------|
| `:17` | quarterly | PostgreSQL 17 |
| `:17-pkg` | quarterly | Alias for `:17` |
| `:17-pkg-latest` | latest | PostgreSQL 17 (latest packages) |
| `:14` | quarterly | PostgreSQL 14 |
| `:14-pkg` | quarterly | Alias for `:14` |
| `:14-pkg-latest` | latest | PostgreSQL 14 (latest packages) |
| `:latest` | quarterly | Alias for `:17` |
| `:pkg` | quarterly | Alias for `:17` |
| `:pkg-latest` | latest | Alias for `:17-pkg-latest` |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | Database superuser name |
| `POSTGRES_PASSWORD` | (empty) | Superuser password |
| `POSTGRES_DB` | `postgres` | Default database name |
| `PGDATA` | `/var/lib/postgresql/data` | Data directory |
| `POSTGRES_INITDB_ARGS` | (empty) | Extra args for initdb (e.g., `--data-checksums`) |
| `POSTGRES_HOST_AUTH_METHOD` | `scram-sha-256` | Auth method (`scram-sha-256`, `md5`, `trust`) |

### Docker Secrets

Secrets can be passed via `*_FILE` environment variables:

| Variable | Description |
|----------|-------------|
| `POSTGRES_PASSWORD_FILE` | Path to file containing password |

## Initialization Scripts

Place scripts in `/docker-entrypoint-initdb.d/` to run on first startup:

| Extension | Behavior |
|-----------|----------|
| `*.sh` | Executed if executable, sourced otherwise |
| `*.sql` | Run via psql against `$POSTGRES_DB` |
| `*.sql.gz` | Decompressed and run via psql |

Scripts run in sorted filename order after database creation.

## Volumes

| Path | Description |
|------|-------------|
| `/var/lib/postgresql/data` | PostgreSQL data directory |

## Ports

| Port | Description |
|------|-------------|
| 5432 | PostgreSQL |

## Notes

- **User:** `bsd` (UID/GID 1000)

## Migrating from Linux

**You cannot copy a Linux postgres data directory directly to FreeBSD.** PostgreSQL stores locale information (`en_US.utf8`) in the database cluster, and FreeBSD uses a different locale format (`en_US.UTF-8`). Attempting to use copied data will fail with:

```
FATAL: database locale is incompatible with operating system
DETAIL: The database was initialized with LC_COLLATE "en_US.utf8", which is not recognized by setlocale().
```

### Migration Steps

1. **Dump from Linux** (while postgres is running):
   ```bash
   podman exec postgres pg_dump -U myuser mydb > mydb.sql
   ```

2. **Start fresh FreeBSD postgres**:
   ```bash
   podman run -d --name postgres \
     -e POSTGRES_USER=myuser \
     -e POSTGRES_PASSWORD=mypassword \
     -e POSTGRES_DB=mydb \
     -v /containers/myapp/pgdata:/var/lib/postgresql/data \
     --annotation 'org.freebsd.jail.allow.sysvipc=true' \
     ghcr.io/daemonless/postgres:17
   ```

3. **Restore the dump**:
   ```bash
   cat mydb.sql | podman exec -i postgres psql -U myuser -d mydb
   ```

### Full Database Cluster Migration

To migrate all databases and roles:

```bash
# On source (Linux or FreeBSD)
podman exec postgres pg_dumpall -U postgres > all_databases.sql

# On target (after starting fresh postgres)
cat all_databases.sql | podman exec -i postgres psql -U postgres
```

## Migrating from FreeBSD to Linux

The same locale incompatibility applies in reverse. FreeBSD uses `C` or `en_US.UTF-8` locales, which Linux postgres may not recognize. Use pg_dump/restore:

```bash
# On FreeBSD
podman exec postgres pg_dump -U myuser mydb > mydb.sql

# On Linux (after starting fresh postgres)
cat mydb.sql | podman exec -i postgres psql -U myuser -d mydb
```

**Bottom line:** Always use `pg_dump`/`pg_restore` when moving postgres data between Linux and FreeBSD, regardless of direction.

## Links

- [PostgreSQL Website](https://www.postgresql.org/)
- [FreshPorts postgresql17-server](https://www.freshports.org/databases/postgresql17-server/)
- [FreshPorts postgresql14-server](https://www.freshports.org/databases/postgresql14-server/)
