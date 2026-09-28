---
title: "ZFS Storage for Podman Containers on FreeBSD"
description: "Configure Podman to use ZFS for container storage on FreeBSD. Get copy-on-write layering, instant snapshots, compression, and data integrity checksums."
---

# ZFS Storage

Configure Podman to use ZFS on FreeBSD for optimal container storage.

## Benefits

| Feature | Benefit |
|---------|---------|
| Copy-on-write | Fast container creation |
| Snapshots | Easy backup/restore |
| Compression | Smaller storage footprint |
| Checksums | Data integrity |

## Understanding Storage Separation

When running containers on FreeBSD, it is essential to distinguish between **engine storage** and **application data**:

1. **Podman Engine Storage (`/var/db/containers/storage`):** Where Podman stores downloaded OCI layers, images, and jail root filesystems. Managed entirely by Podman. Never place personal configuration files or Compose directories here.
2. **Persistent Application Data (`/containers`):** Where your application configuration files (like `Caddyfile`), databases, and Compose files live.

## 1. Engine Storage (Podman Graphroot)

Create a dedicated dataset for Podman's internal image layer storage:

```bash
# Create dataset for Podman's internal storage (adjust 'zroot' to your pool name)
zfs create zroot/podman-storage
zfs set mountpoint=/var/db/containers/storage zroot/podman-storage
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
  Dataset: zroot/podman-storage
```

## 2. Application Data & Config Storage

Keep your container configuration and persistent volumes on a separate dataset. In Daemonless documentation, `/containers` is used as the standard convention, but you can place this anywhere on your filesystem:

```bash
# Create dataset for persistent container app data
zfs create zroot/containers
zfs set mountpoint=/containers zroot/containers

# Individual apps live in subdirectories
mkdir -p /containers/caddy /containers/tautulli

# Easy ZFS snapshots before container upgrades!
zfs snapshot zroot/containers@before-upgrade
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
