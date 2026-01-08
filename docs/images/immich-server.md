---
title: immich-server - FreeBSD OCI Container
description: Immich photo management server for FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# immich-server

Main application server (Node.js) for [Immich](https://immich.app/).

> **Note:** This is just one component of Immich. For the complete setup (compose, configuration, etc.), see the [Daemonless Immich Stack](https://github.com/daemonless/immich).

| | |
|---|---|
| **Port** | 2283 |
| **Registry** | `ghcr.io/daemonless/immich-server` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/immich-server](https://github.com/daemonless/immich-server) |

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name immich-server \
      -p 2283:2283 \
      -e DB_HOSTNAME=immich-postgres \
      -e DB_USERNAME=postgres \
      -e DB_PASSWORD=postgres \
      -e DB_DATABASE_NAME=immich \
      -e REDIS_HOSTNAME=redis \
      -v /containers/immich/library:/data \
      ghcr.io/daemonless/immich-server:latest
    ```

=== "Compose"

    ```yaml
    services:
      immich-server:
        image: ghcr.io/daemonless/immich-server:latest
        container_name: immich-server
        environment:
          - DB_HOSTNAME=immich-postgres
          - DB_USERNAME=postgres
          - DB_PASSWORD=postgres
          - DB_DATABASE_NAME=immich
          - REDIS_HOSTNAME=redis
        volumes:
          - /containers/immich/library:/data
        ports:
          - 2283:2283
        restart: unless-stopped
        depends_on:
          - immich-postgres
          - redis
    ```

## Prerequisites

> [!IMPORTANT]
> **Container Networking**: Immich requires the CNI `dnsname` plugin for internal communication between services. Ensure it is installed and configured on your host.

## Prerequisites

> [!IMPORTANT]
> **Container Networking**: Immich requires the CNI `dnsname` plugin for internal communication between services. Ensure it is installed and configured on your host.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOSTNAME` | PostgreSQL hostname | - |
| `DB_USERNAME` | PostgreSQL username | - |
| `DB_PASSWORD` | PostgreSQL password | - |
| `DB_DATABASE_NAME` | PostgreSQL database name | - |
| `REDIS_HOSTNAME` | Redis hostname | - |
| `IMMICH_PORT` | Server listening port | `2283` |
| `IMMICH_MEDIA_LOCATION` | Media library directory | `/data` |
| `IMMICH_MACHINE_LEARNING_URL` | URL to ML service (see Notes) | - |

## Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | [Immich Releases](https://github.com/immich-app/immich/releases) | Latest upstream release |

## Volumes

| Path | Description |
|------|-------------|
| `/data` | Media library (photos/videos) |
| `/config` | Configuration directory |

## Ports

| Port | Description |
|------|-------------|
| 2283 | Web UI and API |

## Notes

- **User:** `bsd` (UID/GID set via PUID/PGID, default 1000)
- **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD)
- **Machine Learning:** Native FreeBSD ML is available via [`ghcr.io/daemonless/immich-ml`](https://github.com/daemonless/immich-ml) (CPU only).
- **Ultra HDR:** Includes patched `sharp` library to support Ultra HDR images from Pixel phones (via `libvips` 8.18+).
- **DNS:** Requires `dnsname` CNI plugin for container name resolution (see [networking guide](https://daemonless.io/guides/networking/#option-2-dns-resolution-cni-dnsname))

## Links

- [Immich](https://immich.app/)
- [GitHub](https://github.com/immich-app/immich)
