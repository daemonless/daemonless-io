# Quick Start

Get daemonless containers running on FreeBSD in 5 minutes.

## Prerequisites

!!! failure "Root Privileges Required"
    **Podman on FreeBSD currently requires root.** Rootless mode is not yet supported.
    All commands in this guide must be run as root (or via `sudo`/`doas`).

Install Podman and container networking:

```bash
pkg install podman-suite
```

!!! warning
    Currently, a temporary patch for ocijail is required for .NET applications (Radarr/Sonarr). This will be removed in a future update once OCI v1.3.0 support lands upstream.
    See [ocijail patch](guides/ocijail-patch.md).

## Host Configuration

### 1. Enable pf filtering

```bash
sysctl net.pf.filter_local=1
echo 'net.pf.filter_local=1' >> /etc/sysctl.conf
```

### 2. Mount fdescfs

```bash
mount -t fdescfs fdesc /dev/fd
echo 'fdesc /dev/fd fdescfs rw 0 0' >> /etc/fstab
```

### 3. Configure pf.conf

Add to `/etc/pf.conf`:

```
# Podman container networking
rdr-anchor "cni-rdr/*"
nat-anchor "cni-rdr/*"
table <cni-nat>
nat on $ext_if inet from <cni-nat> to any -> ($ext_if)
nat on $ext_if inet from 10.88.0.0/16 to any -> ($ext_if)
```

Reload pf:

```bash
pfctl -f /etc/pf.conf
```

### 4. Enable Podman service

```bash
sysrc podman_enable=YES
service podman start
```

## Run Your First Container

```bash
# Tautulli - no special annotations needed
podman run -d --name tautulli \
  -p 8181:8181 \
  -e PUID=1000 -e PGID=1000 \
  -v /data/config/tautulli:/config \
  ghcr.io/daemonless/tautulli:latest
```

Check it's running:

```bash
podman ps
podman logs -f tautulli
```

Access at: `http://localhost:8181`

## .NET Apps (Radarr, Sonarr, etc.)

These require the `allow.mlock` annotation and patched ocijail:

```bash
podman run -d --name radarr \
  -p 7878:7878 \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  -e PUID=1000 -e PGID=1000 \
  -v /data/config/radarr:/config \
  ghcr.io/daemonless/radarr:latest
```

## Optional: ZFS Storage

If you're using ZFS, configure Podman to use it for proper copy-on-write layering and snapshot support:

```bash
zfs create -o mountpoint=/var/db/containers/storage <pool>/podman
```

See [ZFS Storage](guides/zfs.md) for the required `storage.conf` configuration.

## Optional: Container DNS Resolution

To use container names as hostnames (e.g., for `postgres` to be reachable by name), the `cni-dnsname` plugin is required. This is **not required** for basic port-forwarded setups but is essential for multi-container apps like **Immich** and **Mealie**.

```bash
# Clone the ports overlay
git clone https://github.com/daemonless/freebsd-ports.git /usr/local/daemonless-ports

# Build and install
cd /usr/local/daemonless-ports/net/cni-dnsname
make install clean
```

Verify it's installed:

```bash
ls /usr/local/libexec/cni/dnsname
```

See [Networking Guide](guides/networking.md) for more details.

## Next Steps

- [Available Images](images/index.md) — Full image catalog
- [Permissions](guides/permissions.md) — Understanding PUID/PGID
- [Networking](guides/networking.md) — Port forwarding vs host network
