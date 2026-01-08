# Permissions (PUID/PGID)

All daemonless containers support running as a non-root user via `PUID` and `PGID` environment variables.

## The Problem

By default, containers often run as root or a hardcoded user ID. When you mount a host directory into a container:

- Files created by the container are owned by root
- The container may not have access to files owned by your user
- Security implications of running as root

## How It Works

Images include a `bsd` user. At startup, an init script reads `PUID` and `PGID` and reconfigures the internal user to match those IDs.

When you set `PUID=1000` and `PGID=1000`:

1. The container configures the `bsd` user with UID 1000 and GID 1000
2. The application runs as this user via `s6-setuidgid`
3. Files are created with matching ownership

## Finding Your UID/GID

```bash
id $USER
# uid=1000(ahze) gid=1000(ahze) groups=1000(ahze),0(wheel)
```

## Usage

### Podman CLI

```bash
podman run -d --name radarr \
  -e PUID=1000 \
  -e PGID=1000 \
  -v /data/config/radarr:/config \
  ghcr.io/daemonless/radarr:latest
```

### podman-compose

```yaml
services:
  radarr:
    image: ghcr.io/daemonless/radarr:latest
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - /data/config/radarr:/config
```

## Automatic Directory Handling

The base image automatically ensures `/config` is owned by the specified PUID/PGID.

For **additional volumes** (like `/movies` or `/downloads`), the container will not recursively change permissions to avoid slow startup on large libraries. Ensure your host user has appropriate access before starting.

## Troubleshooting

### Permission Denied

If the container can't write to mounted volumes:

```bash
# Check current ownership
ls -la /data/config/radarr

# Fix ownership
chown -R 1000:1000 /data/config/radarr
```

### NFS Mounts

For NFS, ensure the UID/GID matches across systems. All daemonless containers default to `1000:1000` for consistent NFS access.

## Technical Details

- **Internal User:** Application runs via `s6-setuidgid bsd`
- **Default:** If no variables provided, defaults to `PUID=1000` and `PGID=1000`
- **Implementation:** Handled by `/etc/cont-init.d/10-usermod` before app starts
