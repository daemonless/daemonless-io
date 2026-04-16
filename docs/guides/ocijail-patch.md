---
title: "ocijail 0.5.0+: Native FreeBSD OCI Support"
description: "Native support for allow.mlock, allow.sysvipc, and other jail parameters in ocijail 0.5.0. No custom patching required."
---

# ocijail Native Support

Starting with version **0.5.0**, `ocijail` natively supports mapping OCI annotations directly to FreeBSD jail parameters. The custom patching process previously required for .NET and PostgreSQL applications is now obsolete.

## Why This Is Important

FreeBSD jails use `allow.*` parameters to control permitted operations. Some applications require specific permissions that aren't part of the standard Linux-centric OCI specification:

| Parameter | Required By | Purpose |
|-----------|-------------|---------|
| `allow.mlock` | .NET apps (Radarr, Sonarr, etc.) | Memory locking for Garbage Collection |
| `allow.sysvipc` | PostgreSQL, Redis | Shared memory / Inter-process communication |
| `allow.raw_sockets` | Ping, SmokePing | ICMP functionality |

In `ocijail` 0.5.0+, these are supported natively via OCI annotations.

## Installation

### Standard Method (Recommended)

Simply install or upgrade the official `ocijail` package from the FreeBSD repository.

```bash
# Update package repo
doas pkg update

# Install or upgrade ocijail
doas pkg install ocijail
```

Verify you have version **0.5.0** or higher:

```bash
ocijail --version
```

### From Ports

If you prefer building from source, use the standard `sysutils/ocijail` port. No custom patches are needed.

```bash
cd /usr/ports/sysutils/ocijail
doas make reinstall clean
```

## Usage

Use annotations in your `podman run` command or Compose file to enable specific jail parameters.

### Podman CLI

```bash
# For .NET apps (Radarr, Sonarr, etc.)
podman run -d --name radarr \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  ghcr.io/daemonless/radarr:latest

# For PostgreSQL
podman run -d --name postgres \
  --annotation 'org.freebsd.jail.allow.sysvipc=true' \
  ghcr.io/daemonless/postgres:15
```

### Podman Compose

```yaml
services:
  radarr:
    image: ghcr.io/daemonless/radarr:latest
    annotations:
      org.freebsd.jail.allow.mlock: "true"
```

## Supported Annotations

Any `allow.*` jail parameter can be toggled via the `org.freebsd.jail.` prefix:

| Annotation | Jail Parameter |
|------------|----------------|
| `org.freebsd.jail.allow.mlock=true` | `allow.mlock` |
| `org.freebsd.jail.allow.raw_sockets=true` | `allow.raw_sockets` |
| `org.freebsd.jail.allow.sysvipc=true` | `allow.sysvipc` |
| `org.freebsd.jail.allow.chflags=true` | `allow.chflags` |

See `jail(8)` for a full list of available parameters.

## Verification

You can verify that a parameter is correctly applied from the host:

```bash
# Start a test container
podman run -d --name test-jail \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  ghcr.io/daemonless/base:15 sleep 86400

# Check jail parameters from host
jexec test-jail sysctl security.jail.param.allow.mlock
```

If the output shows `security.jail.param.allow.mlock: 1`, the parameter is active.

## Legacy Patching (Obsolete)

Prior to version 0.5.0, `ocijail` required a custom patch (or the `build-ocijail.sh` script) to support these annotations. If you are running an older version of FreeBSD or `ocijail`, we strongly recommend upgrading to the official 0.5.0 release rather than maintaining a custom build.
