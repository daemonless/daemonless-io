# Deep Dive: OCI v1.3.0 Compliance & Roadmap

This document analyzes the current state of **Daemonless** in relation to the [OCI Runtime Specification v1.3.0](https://github.com/opencontainers/runtime-spec/releases/tag/v1.3.0), which officially introduces support for FreeBSD Jails.

## 1. Executive Summary

**Status:** `compliant-via-extension`

Daemonless images are fully OCI-compliant. However, the runtime environment (`ocijail` + `podman`) currently relies on a **custom patch** to support critical features (like `mlock` for .NET apps) via Annotations.

OCI v1.3.0 standardizes these features into the core specification. The path forward involves updating the runtime toolchain to support this new spec, while maintaining the annotation-based approach for compatibility with existing Podman versions.

## 2. OCI v1.3.0: The FreeBSD Spec

The new specification adds a dedicated `freebsd` object to the runtime configuration (`config.json`). This eliminates the need for "hacks" or overloading generic fields.

### Key Schema Changes

The `config.json` will now support a structure like this:

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

## 3. The Implementation Gap

While the **Spec** (JSON schema) is ready, the **Toolchain** is catching up.

### The Components

1.  **The Runtime (`ocijail`):** Reads `config.json` -> Creates Jail.
    *   *Current:* Does not read `freebsd` object.
    *   *Goal:* Update `ocijail` to parse the v1.3.0 `freebsd` object.
2.  **The Generator (`podman`/`conmon`):** Users run commands -> Generates `config.json`.
    *   *Current:* Podman has no native flags for FreeBSD (e.g., no `--allow-mlock`). It generates a generic Linux-like config.
    *   *Goal:* Podman needs to be patched or configured to emit the `freebsd` object in the JSON.

### The "Generator Gap"

Even if we update `ocijail` tomorrow to support v1.3.0, **Podman will not send it the right JSON** because Podman doesn't know about FreeBSD flags yet.

Therefore, our **Annotation Patch** (`org.freebsd.jail.*`) remains the only viable user-facing mechanism for now.

## 4. Roadmap & Suggestions

### Phase 1: Support v1.3.0 in `ocijail` (Immediate)
We should update our custom `ocijail` patch (or fork) to support **both**:
1.  The legacy Annotations (`org.freebsd.jail...`).
2.  The new `freebsd` JSON object.

*Why?* This makes the runtime "future-proof". If a user manually edits `config.json` or uses a custom generator, it works.

### Phase 2: Bridge the Gap (Short Term)
We should modify `ocijail` to **translate** annotations into the internal v1.3.0 struct before execution.
*   Input: `annotation: org.freebsd.jail.allow.mlock=true`
*   Internal Logic: Sets `conf.FreeBSD.Jail.Mlock = true`

This aligns our internal logic with the spec, even if the input is legacy.

### Phase 3: Update Podman / Containers.conf (Long Term)
Work with the upstream Podman/FreeBSD team to allow mapping CLI flags or `containers.conf` entries to the new OCI spec fields.

## 5. Action Items for Daemonless

1.  **Docs:** Update documentation to reference OCI v1.3.0 as the "North Star" but clarify why annotations are still needed (The Generator Gap).
2.  **Patch:** Review the current `ocijail` patch to ensure it doesn't *conflict* with upcoming native support.
3.  **Testing:** Once an upstream `ocijail` beta with v1.3.0 support lands, verify our images work without modification (using manually crafted `config.json`).

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

Daemonless is effectively compliant because it produces standard OCI images. The burden of v1.3.0 compliance lies with the runtime tools (`ocijail`, `podman`). We will continue to ship our compatibility patch until the upstream toolchain fully matures to support the new specification end-to-end.
