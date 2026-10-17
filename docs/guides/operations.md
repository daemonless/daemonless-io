---
title: "Container Operations: Updates, Backups, and Maintenance"
description: "Day-to-day management of daemonless containers. Update images, backup configs with ZFS snapshots, prune old layers, and troubleshoot common issues."
---

# Operations

Day-to-day management of your containers: updates, backups, and maintenance.

## Updating Containers

The default `ghcr.io` registry images are versioned using tags.

- `:latest` - Builds daily from the upstream project's latest stable release.
- `:pkg` - Builds from FreeBSD quarterly packages.
- `:pkg-latest` - Builds from FreeBSD latest packages.

### Podman CLI

1.  **Pull new image**:
    ```bash
    podman pull ghcr.io/daemonless/radarr:latest
    ```
2.  **Stop and remove old container**:
    ```bash
    podman stop radarr
    podman rm radarr
    ```
3.  **Start new container**:
    Run your original `podman run` command again. Since `/config` is a volume, your data persists.

### Podman Compose

1.  **Pull new images**:
    ```bash
    podman-compose pull
    ```
2.  **Recreate containers**:
    ```bash
    podman-compose up -d
    ```
    This automatically stops the old container and creates a new one *only* if the image has changed.

!!! warning "Check that it really restarted"
    `podman-compose up -d` can exit 0 after failing to recreate a container. Check `podman ps`: the container's CREATED time should be just now.

### Automated Updates

`podman auto-update` drives systemd units, which FreeBSD does not have. Schedule the pull and recreate instead, for example from `/etc/crontab`:

```
# m  h  dom mon dow who   command
30   4  *   *   *   root  cd /containers/radarr && /usr/local/bin/podman-compose pull && /usr/local/bin/podman-compose up -d
```

[fjord](https://fjord.daemonless.io) updates a stack in one click and can roll the update back.

### AppJail Director

`appjail-director up` leaves a running jail alone unless its spec changed. To move a service to a newer image, destroy its jail and bring the project up again; `container: args:--pull` in the service's options pulls the image as it rebuilds:

```bash
appjail stop radarr
appjail jail destroy -f radarr
appjail-director up
```

A sidecar in a bundle (a database, Redis) has no `--pull`: pull its image first with `buildah pull --policy always <image>`.

## Backups

Backing up your data is critical. All daemonless containers store persistent data in the volume mounted to `/config`.

### Backup Strategy

1.  **Stop the container**: Ensure database integrity (Radarr, Sonarr, etc. use SQLite).
    ```bash
    podman stop radarr
    ```
2.  **Archive the config directory**:
    ```bash
    tar -czvf radarr-backup-$(date +%F).tar.gz /path/to/config/radarr
    ```
3.  **Restart the container**:
    ```bash
    podman start radarr
    ```

### ZFS Snapshots

If your data is on ZFS, you can use snapshots for instant backups without long downtime.

```bash
# Snapshot
zfs snapshot zroot/data/config@backup-$(date +%F)

# Rollback (if needed)
# 1. Stop container
# 2. Rollback
zfs rollback zroot/data/config@backup-2024-01-01
# 3. Start container
```

## Maintenance

### Pruning Images

Over time, old image layers can accumulate.

```bash
# Remove unused images
podman image prune

# Remove all unused images (including untagged)
podman image prune -a
```

### Checking Logs

If a container fails to start:

```bash
podman logs radarr
```

If the application crashes but the container is running:
Check the internal service logs mapped to your host:

```bash
tail -f /path/to/config/radarr/logs/daemonless/radarr/current
```
