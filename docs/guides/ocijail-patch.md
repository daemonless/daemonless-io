# ocijail Patch

.NET applications require the `allow.mlock` jail parameter. Stock ocijail doesn't support this — you need the patched version.

## Why This Is Needed

!!! note "Upcoming Native Support (OCI v1.3.0)"
    **Good News:** The `allow.*` parameters required for .NET/Postgres have been accepted into the **OCI Runtime Specification v1.3.0**.
    
    Support is currently being implemented in `ocijail` by the upstream maintainer. Once released, this manual patching process will become obsolete.

FreeBSD jails have `allow.*` parameters controlling permitted operations. Some applications require specific permissions:

| Parameter | Required By | Purpose |
|-----------|-------------|---------|
| `allow.mlock` | .NET apps (Radarr, Sonarr, etc.) | Memory locking for GC |
| `allow.sysvipc` | PostgreSQL | Shared memory |
| `allow.raw_sockets` | Ping tools, SmokePing | ICMP functionality |

The stock ocijail runtime doesn't provide a way to pass generic `allow.*` flags through the OCI specification. Our patch adds support for mapping OCI annotations directly to jail parameters.

## Installation

### Option 1: Manual Ports Method

```bash
# Fetch patch
fetch  https://raw.githubusercontent.com/daemonless/daemonless/refs/heads/main/scripts/ocijail-allow-annotations.patch -o /tmp
mkdir -p /usr/ports/sysutils/ocijail/files 
# Copy patch to port's files directory
cp /tmp/ocijail-allow-annotations.patch /usr/ports/sysutils/ocijail/files/patch-daemonless-annotations

# Rebuild and install
cd /usr/ports/sysutils/ocijail
make reinstall clean
# Remove patch
rm /usr/ports/sysutils/ocijail/files/patch-daemonless-annotations
```

### Option 2: Automated Script

```bash
git clone https://github.com/daemonless/daemonless.git
cd daemonless
doas ./scripts/build-ocijail.sh
```

The script will:

1. Copy the port to a temporary directory (if `/usr/ports/sysutils/ocijail` exists)
2. Apply the patch
3. Build using the ports framework or bazel
4. Back up original and install patched version to `/usr/local/bin/ocijail`

### Option 3: Manual Build

```bash
# Requires bazel and git
pkg install bazel git

# Clone and build
git clone https://github.com/dfr/ocijail /tmp/ocijail
cd /tmp/ocijail

# Apply patch
fetch -o - https://raw.githubusercontent.com/daemonless/daemonless/main/scripts/ocijail-allow-annotations.patch | patch -p1

# Build
bazel build //...

# Install (backs up original)
cp /usr/local/bin/ocijail /usr/local/bin/ocijail.orig
cp bazel-bin/ocijail /usr/local/bin/ocijail
```

## Usage

After patching, use annotations to enable jail parameters:

```bash
# For .NET apps
podman run -d --name radarr \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  ghcr.io/daemonless/radarr:latest

# For ping functionality
podman run -d --name smokeping \
  --annotation 'org.freebsd.jail.allow.raw_sockets=true' \
  ghcr.io/daemonless/smokeping:latest
```

## Supported Annotations

Any `allow.*` jail parameter works:

| Annotation | Jail Parameter |
|------------|----------------|
| `org.freebsd.jail.allow.mlock=true` | `allow.mlock` |
| `org.freebsd.jail.allow.raw_sockets=true` | `allow.raw_sockets` |
| `org.freebsd.jail.allow.sysvipc=true` | `allow.sysvipc` |
| `org.freebsd.jail.allow.chflags=true` | `allow.chflags` |

See `jail(8)` for all available parameters.

## Verification

Verify the patch is working:

```bash
# Start a test container
podman run -d --name test-jail \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  ghcr.io/daemonless/base:15 sleep 86400

# Check jail parameters from host
jexec test-jail sysctl security.jail.param.allow.mlock
```

If output shows `security.jail.param.allow.mlock: 1`, the patch is working.

## Upstream Status

The long-term plan for ocijail is to support jail parameters through the FreeBSD extensions in the OCI v1.3.0 runtime specification. The maintainer has agreed that annotation-based controls make sense as a transitionary solution.
