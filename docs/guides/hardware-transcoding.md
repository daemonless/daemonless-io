---
title: "Hardware Transcoding (VAAPI) on FreeBSD Containers"
description: "Enable Intel iGPU hardware video transcoding in FreeBSD jails and podman containers: DRM driver setup, devfs rules for /dev/dri passthrough, and app configuration for Jellyfin and Immich."
---

# Hardware Transcoding (VAAPI)

Intel iGPUs can transcode video in hardware on FreeBSD via VAAPI. Media images
(Jellyfin, Emby, Immich) ship ffmpeg with VAAPI support and the Intel iHD media
driver (`libva-intel-media-driver`), so the only work is on the host: load the
GPU driver and expose the render node to the container.

Measured on an Intel N150 (Twin Lake): 1080p30 H.264 → HEVC at ~90 fps
(3× realtime) using ~2% of the CPU time a software encode needs — where the
same box cannot even software-encode 1080p30 HEVC in realtime.

## 1. Host: DRM driver and firmware

Install the DRM kernel module and the GPU firmware for your iGPU generation,
then load it:

```sh
pkg install drm-latest-kmod gpu-firmware-intel-kmod-alderlake gpu-firmware-intel-kmod-tigerlake
kldload i915kms
```

!!! danger "Install firmware before loading the module"
    Loading `i915kms` without the matching GuC/HuC firmware packages present
    can panic the machine. Install the firmware first, and only add
    `i915kms` to `kld_list` in `rc.conf` once a manual load has proven stable.

Newer chips (e.g. Twin Lake / N150, PCI ID `0x46d4`) need `drm-latest-kmod`;
`drm-66-kmod` does not know them. Verify the load with `ls /dev/dri/` — you
should see `renderD128`.

## 2. Expose the render node

### Classic jails

Add a devfs ruleset to `/etc/devfs.rules`:

```
[devfsrules_jails_gpu=61182]
add include $devfsrules_hide_all
add include $devfsrules_unhide_basic
add include $devfsrules_unhide_login
add path 'bpf*' unhide
add path 'dri' unhide
add path 'dri/*' unhide mode 0666
add path 'drm*' unhide mode 0666
```

Configure the jail with `devfs_ruleset = 61182`.

### Podman

Pass the device through (CLI `--device /dev/dri/renderD128`, or in compose):

```yaml
services:
  jellyfin:
    devices:
      - /dev/dri/renderD128
```

!!! warning "podman devfs bug — host workaround required"
    Current podman on FreeBSD unhides the device node inside the container's
    devfs but not its parent `drm` directory, so the node stays unreachable.
    Until this is fixed upstream, use one of the two workarounds below.
    In both, `mode 0666` matters: daemonless images run as the non-root `bsd`
    user, and podman's own device rule creates the node root-only (0600).

**Option A — extend devfs ruleset 4 (recommended for dedicated hosts).**
podman mounts every container's `/dev` with ruleset 4 (`devfsrules_jail`), so
adding the GPU rules there makes passthrough work with nothing to re-run —
it survives container recreation and, via `/etc/devfs.rules`, reboots.

Apply live:

```sh
devfs rule -s 4 add path drm unhide
devfs rule -s 4 add path dri unhide
devfs rule -s 4 add path 'dri/*' unhide
devfs rule -s 4 add path 'drm/*' unhide mode 0666
```

Persist by redefining the ruleset in `/etc/devfs.rules`. The rc loader
**clears a ruleset before re-adding it** when a file redefines it, so the
section must restate the default content, not just the additions:

```
[devfsrules_jail=4]
add include $devfsrules_hide_all
add include $devfsrules_unhide_basic
add include $devfsrules_unhide_login
add path fuse unhide
add path zfs unhide
add path drm unhide
add path dri unhide
add path 'dri/*' unhide
add path 'drm/*' unhide mode 0666
```

Trade-offs: the GPU becomes visible to **every** ruleset-4 consumer — all
podman containers, and any jail whose ruleset includes `$devfsrules_jail` —
and the restated defaults must be kept in sync with
`/etc/defaults/devfs.rules` across OS upgrades. With this in place the
`devices:` entry is technically redundant, but keep it: it documents intent
and becomes the proper mechanism once podman is fixed.

**Option B — per-start rule application (opt-in, for shared hosts).**
Keeps GPU access scoped to containers you pass `--device` to, at the cost of
re-running after every container recreation or reboot (as root):

```sh
ROOT=$(podman mount <container>)
devfs -m "$ROOT/dev" rule apply path drm unhide
devfs -m "$ROOT/dev" rule apply path 'drm/*' unhide mode 0666
devfs -m "$ROOT/dev" rule apply path dri unhide
devfs -m "$ROOT/dev" rule apply path 'dri/*' unhide
podman unmount <container>
```

## 3. Configure the application

| App | Setting |
|-----|---------|
| Jellyfin | Dashboard → Playback → Transcoding → Hardware acceleration: **VAAPI**, device `/dev/dri/renderD128` |
| Immich | Administration → Settings → Video Transcoding → Hardware Acceleration: **VAAPI** |

Use VAAPI, not QSV — the QSV stack is Linux-only.

## 4. Verify

Inside the container (images that ship `libva-utils`):

```sh
podman exec <container> vainfo --display drm --device /dev/dri/renderD128
```

A working stack prints the iHD driver version and a list of
`VAProfile…/VAEntrypoint…` lines; `VAEntrypointEncSliceLP` entries are the
low-power hardware encoders. If `vainfo` fails to open the device, re-check
the devfs rules and node permissions (`ls -la /dev/drm/` inside the container).
