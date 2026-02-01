---
title: "Quick Start: FreeBSD Containers in 5 Minutes"
description: "Get Podman containers running on FreeBSD fast. Install podman-suite, configure pf firewall, and deploy your first daemonless container with this step-by-step guide."
placeholders:
  REGISTRY:
    default: "GitHub Container Registry"
    description: "Container Registry"
  INTERFACE:
    default: "em0"
    description: "Network Interface"
  PUID:
    default: "1000"
    description: "User ID"
  PGID:
    default: "1000"
    description: "Group ID"
  CONTAINER_CONFIG_ROOT:
    default: "/path/to/containers"
    description: "Config Path"
---

# Quick Start

Get daemonless containers running on FreeBSD in 5 minutes.

!!! tip "Customize Your Guide"
    Scroll to [Interactive Configuration](#interactive-configuration) at the bottom to set your PUID, PGID, and paths. All commands will update automatically.

## Prerequisites

!!! failure "Root Privileges Required"
    **Podman on FreeBSD currently requires root.** Rootless mode is not yet supported. All commands in this guide must be run as root (or via `sudo`/`doas`).

Install Podman and container networking:

```bash
pkg install podman-suite
```

!!! warning "ocijail Patch Required"
    Currently, a temporary patch for `ocijail` is required for .NET applications (Radarr/Sonarr). 
    See [ocijail patch](guides/ocijail-patch.md).

## Host Configuration

### 1. Enable Networking
Configure the kernel to allow packet filtering for local traffic and ensure `fdescfs` is mounted.

```bash
# Enable pf filtering for jails
sysctl net.pf.filter_local=1
echo 'net.pf.filter_local=1' >> /etc/sysctl.conf

# Mount fdescfs
mount -t fdescfs fdesc /dev/fd
echo 'fdesc /dev/fd fdescfs rw 0 0' >> /etc/fstab
```

### 2. Configure Firewall (`pf.conf`)
Add the following to `/etc/pf.conf`. Replace `@INTERFACE@` if your external interface is different.

```
# Primary network interface
ext_if=@INTERFACE@

# Podman container networking
rdr-anchor "cni-rdr/*"
nat-anchor "cni-rdr/*"
table <cni-nat>
nat on $ext_if inet from <cni-nat> to any -> ($ext_if)
nat on $ext_if inet from 10.88.0.0/16 to any -> ($ext_if)
```

Reload the configuration:
```bash
pfctl -f /etc/pf.conf
```

### 3. Start Podman

```bash
sysrc podman_enable=YES
service podman start
```

## Run Your First Container

We'll start with **Tautulli**, a lightweight Python app that doesn't require special permissions.

```bash
podman run -d --name tautulli \
  -p 8181:8181 \
  -e PUID=@PUID@ -e PGID=@PGID@ \
  -v @CONTAINER_CONFIG_ROOT@/tautulli:/config \
  @REGISTRY@/tautulli:latest
```

Check the status:
```bash
podman ps
podman logs -f tautulli
```
Access the UI at: `http://localhost:8181`

## .NET Applications
Applications like **Radarr** and **Sonarr** require the `allow.mlock` jail annotation to function correctly on FreeBSD.

```bash
podman run -d --name radarr \
  -p 7878:7878 \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  -e PUID=@PUID@ -e PGID=@PGID@ \
  -v @CONTAINER_CONFIG_ROOT@/radarr:/config \
  @REGISTRY@/radarr:latest
```

## Advanced Setup (Optional)

=== "ZFS Storage"
    If you're using ZFS, configure Podman to use it for proper copy-on-write layering and snapshot support:
    ```bash
    zfs create -o mountpoint=/var/db/containers/storage <pool>/podman
    ```
    See [ZFS Storage](guides/zfs.md) for `storage.conf` tuning.

=== "Container DNS"
    To use container names as hostnames (e.g. `postgres`), the `cni-dnsname` plugin is required.
    ```bash
    # Clone the ports overlay
    git clone https://github.com/daemonless/freebsd-ports.git /usr/local/daemonless-ports
    
    # Build and install
    cd /usr/local/daemonless-ports/net/cni-dnsname
    make install clean
    ```
    See [Networking Guide](guides/networking.md) for details.

---

### Interactive Configuration

<div class="placeholder-settings-panel"></div>

### Next Steps
- [Available Images](images/index.md) — Full image fleet
- [Permissions](guides/permissions.md) — Understanding PUID/PGID
- [Networking](guides/networking.md) — Port forwarding vs host network