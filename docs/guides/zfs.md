# ZFS Storage

Configure Podman to use ZFS on FreeBSD for optimal container storage.

## Benefits

| Feature | Benefit |
|---------|---------|
| Copy-on-write | Fast container creation |
| Snapshots | Easy backup/restore |
| Compression | Smaller storage footprint |
| Checksums | Data integrity |

## Create ZFS Dataset

Create a dedicated dataset for container storage:

```bash
# Create dataset (adjust 'zroot' to your pool name)
zfs create zroot/containers
zfs set mountpoint=/var/db/containers/storage zroot/containers
```

## Configure Podman

Edit `/usr/local/etc/containers/storage.conf`:

```toml
[storage]
driver = "zfs"
runroot = "/var/run/containers/storage"
graphroot = "/var/db/containers/storage"

[storage.options.zfs]
mountopt = "nodev"
```

## Verify Configuration

```bash
podman info | grep -A 5 "store"
```

Expected output:

```
graphDriverName: zfs
graphRoot: /var/db/containers/storage
graphStatus:
  Dataset: zroot/containers
```

## Separate Config Storage

Keep container configs on a separate dataset for easy backup:

```bash
zfs create zroot/data/config
zfs set mountpoint=/data/config zroot/data/config

# Snapshot before upgrades
zfs snapshot zroot/data/config@before-upgrade
```

## Troubleshooting

### "driver zfs is not supported"

Ensure:

1. Your ZFS pool is imported and healthy
2. The `graphroot` directory exists and is a ZFS dataset
3. You are running Podman as root

### Permission Issues

```bash
chown -R root:wheel /var/db/containers
```

### Reset Storage

```bash
# Stop all containers first
podman stop -a
podman system reset
```
