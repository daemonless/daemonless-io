---
title: "OCI v1.3.0 FreeBSD Support: Compliance and Roadmap"
description: "Technical deep dive into OCI Runtime Specification v1.3.0 FreeBSD support. How daemonless images comply and the roadmap for native jail parameter handling."
---

# Deep Dive: OCI v1.3.0 Compliance & Roadmap

This document analyzes the current state of **Daemonless** in relation to the [OCI Runtime Specification v1.3.0](https://github.com/opencontainers/runtime-spec/releases/tag/v1.3.0), which officially introduces support for FreeBSD Jails.

## 1. Executive Summary

**Status:** `compliant-via-extension` (Standard in `ocijail` 0.5.0+)

Daemonless images are fully OCI-compliant. As of `ocijail` 0.5.0, the runtime environment natively supports critical FreeBSD features (like `mlock` for .NET apps) via standard OCI Annotations and the OCI v1.3.0 `freebsd` object.

The previous requirement for a custom patch is obsolete. Our annotation-based approach (`org.freebsd.jail.*`) is now the standard mechanism for passing FreeBSD-specific jail parameters through generic OCI generators like Podman.

## 2. OCI v1.3.0: The FreeBSD Spec

The specification adds a dedicated `freebsd` object to the runtime configuration (`config.json`). This eliminates the need for overloading generic fields. `ocijail` 0.5.0+ fully supports this structure.

### Key Schema Changes

The `config.json` supports a structure like this:

```json
{
    "freebsd": {
        "jail": {
            "mlock": true,
            "allow.mount.zfs": true,
            "allow.raw_sockets": true,
            "devfs_ruleset": 4,
            "vnetInterfaces": ["epair0b"]
        }
    }
}
```

### Critical Parameters for Daemonless

| Parameter | Current Method (Daemonless) | OCI v1.3.0 Method | Impact |
| :--- | :--- | :--- | :--- |
| **Memory Locking** | `org.freebsd.jail.allow.mlock=true` | `freebsd.jail.mlock: true` | Required for all *Arr apps (.NET). |
| **Raw Sockets** | `org.freebsd.jail.allow.raw_sockets=true` | `freebsd.jail.allow.raw_sockets` | Required for `smokeping`. |
| **Mounts** | `mount` (generic) | `freebsd.jail.allow.mount.*` | Better ZFS integration potential. |
| **VNET** | Auto-calculated | `freebsd.jail.vnetInterfaces` | More explicit network control. |

## 3. The Implementation Status

The toolchain has caught up with the specification.

### The Components

1.  **The Runtime (`ocijail`):** Reads `config.json` -> Creates Jail.
    *   **Status:** Native support for `freebsd` object and `org.freebsd.jail.*` annotations since version 0.5.0.
2.  **The Generator (`podman`/`conmon`):** Users run commands -> Generates `config.json`.
    *   *Current:* Podman generates a generic OCI config. It does not yet natively emit the `freebsd` object from CLI flags.
    *   *Solution:* Users continue to use `--annotation` which `ocijail` now handles natively.

### The "Generator Gap"

While `ocijail` now supports the v1.3.0 JSON natively, **Podman does not yet emit that JSON** from standard CLI flags (e.g., no `--allow-mlock`).

Therefore, our **Annotation mechanism** (`org.freebsd.jail.*`) remains the primary user-facing tool, but it is now a **native feature of the runtime** rather than a custom patch.

## 4. Roadmap Status

### Phase 1: Support v1.3.0 in `ocijail` (Completed)
`ocijail 0.5.0` supports both the legacy Annotations and the new `freebsd` JSON object.

### Phase 2: Bridge the Gap (Completed)
`ocijail` natively translates `org.freebsd.jail.*` annotations into the internal jail parameters. This makes the runtime "future-proof" while remaining compatible with today's Podman.

### Phase 3: Update Podman / Containers.conf (In Progress)
Work continues with the upstream Podman/FreeBSD team to allow mapping CLI flags or `containers.conf` entries directly to the OCI spec fields.

## 5. Action Items for Daemonless

1.  **Docs:** (Updated) Documentation now reflects `ocijail 0.5.0` as the baseline.
2.  **Patch:** (Retired) The custom patch is no longer maintained; users are directed to the official package.
3.  **Testing:** Verified that `ocijail` 0.5.0+ runs all Daemonless images without modification.

## 6. Image Labels & Metadata

Daemonless images already strictly adhere to the [OCI Image Specification](https://github.com/opencontainers/image-spec) for static labels.

### Current Status: Good

We correctly use standard namespaces:
*   `org.opencontainers.image.title`
*   `org.opencontainers.image.source`
*   `org.opencontainers.image.licenses`
*   `io.daemonless.*` (Custom namespace for specific metadata)

### Recommendation: Add Dynamic Labels

To reach "Gold Standard" compliance, the build pipeline (`build.sh`) should be updated to inject dynamic build-time metadata:

*   `org.opencontainers.image.created`: RFC 3339 date/time of the build.
*   `org.opencontainers.image.revision`: Git commit SHA of the source code.
*   `org.opencontainers.image.version`: The semantic version of the packaged application.

This allows tools (like Renovate, Watchtower, or generic OCI scanners) to better understand the image lineage without pulling it.

## 7. Conclusion

Daemonless is effectively compliant because it produces standard OCI images. The burden of v1.3.0 compliance lies with the runtime tools (`ocijail`, `podman`). We will continue to use the annotation-based configuration as it is now natively supported by the toolchain.
