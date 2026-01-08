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

### Automated Updates

Podman has a built-in auto-update system.

1.  Start your container with the `--label "io.containers.autoupdate=registry"` flag.
2.  Create a systemd user unit (or standard service) for the container.
3.  Run `podman auto-update` periodically (e.g., via cron or timer).

!!! note
    This requires running the container as a systemd service, which is advanced usage. The manual `pull && restart` method is universally supported.

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
