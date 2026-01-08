---
title: Plex Media Server - FreeBSD OCI Container
description: Plex Media Server on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# Plex Media Server

[Plex](https://plex.tv) organizes video, music and photos from personal media libraries and streams them to smart TVs, streaming boxes and mobile devices.

| | |
|---|---|
| **Port** | 32400 |
| **Registry** | `ghcr.io/daemonless/plex` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/plex](https://github.com/daemonless/plex) |

## Supported Architectures

| Architecture | Available | Tag |
|--------------|-----------|-----|
| x86-64 | ✅ | `amd64` |

## Version Tags

| Tag | Description |
|-----|-------------|
| `latest` | Latest public Plex release baked at build time |
| `x.y.z.build-hash` | Specific version (e.g., `1.42.2.10156-f737b826c`) |

## Application Setup

Access the web UI at `http://<your-ip>:32400/web` to configure Plex.

### VERSION Environment Variable

The `VERSION` parameter controls Plex update behavior:

| Value | Description |
|-------|-------------|
| `container` | Use the version baked into the container, no updates (default) |
| `public` | Update to latest public channel release |
| `latest` | Alias for `plexpass` |
| `plexpass` | Update to PlexPass channel (requires PlexOnlineToken in Preferences.xml) |
| `<specific-version>` | Update to a specific version (e.g., `1.42.2.10156-f737b826c`) |

**Note:** PlexPass versions require authentication. Log in via the web UI first, then restart the container with `VERSION=plexpass`.

### Claiming Your Server

To claim a new server, get a claim token from [plex.tv/claim](https://plex.tv/claim) (valid for 4 minutes) and pass it via `PLEX_CLAIM` environment variable on first run.

## Usage

### podman run

```bash
podman run -d \
  --name plex \
  -p 32400:32400 \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=America/New_York \
  -v /path/to/config:/config \
  -v /path/to/media:/data \
  -v /path/to/transcode:/transcode \
  ghcr.io/daemonless/plex:latest
```

### podman-compose

```yaml
services:
  plex:
    image: ghcr.io/daemonless/plex:latest
    container_name: plex
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
      # - VERSION=public
      # - PLEX_CLAIM=claim-xxxx
      # - ADVERTISE_IP=http://<your-ip>:32400/
    volumes:
      - /data/config/plex:/config
      - /data/media:/data
      - /tmp/plex-transcode:/transcode
    ports:
      - 32400:32400
      - 8324:8324
      - 32469:32469
      - 1900:1900/udp
      - 32410:32410/udp
      - 32412:32412/udp
      - 32413:32413/udp
      - 32414:32414/udp
    restart: unless-stopped
```

## Parameters

### Ports

| Port | Description |
|------|-------------|
| `32400` | Web UI and API |
| `8324` | Companion app |
| `32469` | DLNA |
| `1900/udp` | SSDP discovery |
| `32410-32414/udp` | GDM discovery |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUID` | `1000` | User ID |
| `PGID` | `1000` | Group ID |
| `TZ` | `UTC` | Timezone |
| `VERSION` | `container` | Update behavior (see above) |
| `PLEX_CLAIM` | | Claim token from plex.tv/claim |
| `ADVERTISE_IP` | | Override advertised IP |

### Volumes

| Path | Description |
|------|-------------|
| `/config` | Configuration and database |
| `/data` | Media library |
| `/transcode` | Temporary transcoding directory |

## User/Group Identifiers

Set `PUID` and `PGID` to match your host user to avoid permission issues:

```bash
id your_user
```

## Support Info

- Shell access: `podman exec -it plex /bin/sh`
- Logs: `podman logs plex`
- Container version: `podman inspect plex | grep org.opencontainers.image.version`

## Links

- [Plex Website](https://plex.tv/)
- [Plex Support](https://support.plex.tv/)
