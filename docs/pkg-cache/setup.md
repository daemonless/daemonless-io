---
title: "Host setup, ZFS, and sizing: Package Cache"
description: "Prepare your FreeBSD or Linux host for Daemonless Package Cache: ZFS dataset setup, disk sizing for FreeBSD and Linux repositories, port choices, and environment variable reference."
---

# Host setup, ZFS, and sizing

`ghcr.io/daemonless/pkg-cache:latest` renders its managed `nginx` configuration at startup from environment variables. Mount persistent `/config` and `/cache` volumes, publish port `80`, and it starts `nginx`, the stats collector, and the log rotator automatically.

---

## 1. Where to run it

One `pkg-cache` container can serve FreeBSD and Linux clients across your network regardless of which OS runs the container:

- **FreeBSD (`amd64` and `arm64`):** Built on FreeBSD `nginx-base` (`fjord`, `Podman` + `ocijail`, `AppJail Director`, or `Bastille`). With Podman's bridge network, set up the `pf` rules in the [Networking guide](../guides/networking.md#pfconf-setup) so port `80` answers.
- **Linux (`amd64` and `arm64`):** Built on Linux (Alpine) with `nginx` and `s6` from the same `ghcr.io/daemonless/pkg-cache:latest` tag (`fjord` or `Podman`).

### Port `80` or a custom host port

- **Port `80`:** Package managers (`pkg`, `apt`, `dnf`, `apk`, `pacman`) fetch over HTTP and check upstream cryptographic signatures on the client. Publishing port `80` keeps URLs short (`http://pkg-cache.home.lan/${ABI}/quarterly`).
- **Custom host port (such as `-p 8080:80`):** If port `80` on the host is already in use, map another host port. The landing page at `http://<host>:8080/` reads `location.host` and includes `:8080` in every copyable client command.

On FreeBSD with Podman and without `net.pf.filter_local=1` enabled before `pf` starts, the host cannot reach its own published container port; open `http://<server>:80` from another machine on your network or configure local `pf` filtering in the [Networking guide](../guides/networking.md#pfconf-setup).

---

## 2. Sizing `/cache` and ZFS setup

Package Cache keeps persistent logs and stats in `/config` and cached package files in `/cache`:

| Container path | Purpose |
| :--- | :--- |
| `/config` | Logs (`log/`, capped by `PKG_LOG_MAX_SIZE`), cumulative stats (`stats/`), and the startup ownership marker (`.chown_done`). |
| `/cache` | `nginx` `proxy_cache` storage (`levels=1:2`). Evicts least-recently-used (`LRU`) files when usage reaches `PKG_CACHE_SIZE` or when a file is unrequested for `90d`. |

!!! important "Mount `/config` as a persistent volume"
    On first start, `pkg-cache` recursively `chown`s `/config` and `/cache` to `PUID:PGID` (`1000:1000` by default) and records that in `/config/.chown_done`. With `SKIP_CHOWN=true` (the default), later starts check `/config/.chown_done` and skip walking `/cache`. If `/config` is not persistent, every restart walks `/cache` again.

### Sizing `PKG_CACHE_SIZE`

Size the `/cache` volume to at least `PKG_CACHE_SIZE` (default `50g`; for example `10g`, `100g`, `500g`). A full set of packages for one FreeBSD release and architecture is around `10G`. Every enabled repository family shares `PKG_CACHE_SIZE`, so with Debian, Ubuntu, or Fedora enabled, give it more than FreeBSD alone needs.

### ZFS dataset

On ZFS, give `/cache` its own child dataset so cached downloads stay out of snapshot retention and avoid extra `atime` writes:

```sh { linenums="0" }
zfs create -o mountpoint=/containers/pkg-cache zroot/containers/pkg-cache
zfs create \
  -o atime=off \
  -o compression=lz4 \
  -o recordsize=1M \
  -o com.sun:auto-snapshot=false \
  zroot/containers/pkg-cache/cache
```

---

## 3. Deploying Package Cache

=== ":material-sail-boat: fjord"

    1. Open **[fjord](https://fjord.daemonless.io)** and select **Daemonless pkg cache** from the catalog.
    2. Set `/config` and `/cache` paths, adjust `PKG_CACHE_SIZE` if needed, and turn on any Linux repository switches (`PKG_CACHE_APT`, `PKG_CACHE_DNF`, `PKG_CACHE_APK`, `PKG_CACHE_PACMAN`).
    3. Click **Install** and open `http://<host-ip>/`.

=== ":podman-podman: Podman Compose, AppJail, and Bastille"

    Copy `compose.yaml` (or download the **AppJail Director** or **Bastille** bundle) from the [Daemonless pkg cache image page](../images/pkg-cache.md), then bring it up:

    ```sh { linenums="0" }
    podman-compose up -d
    ```

=== ":material-console: Podman CLI"

    ```sh { linenums="0" }
    podman run -d --name pkg-cache \
      --restart always \
      -p 80:80 \
      -e PKG_UPSTREAM=pkg.FreeBSD.org \
      -e PKG_CACHE_SIZE=50g \
      -v /containers/pkg-cache:/config \
      -v /containers/pkg-cache/cache:/cache \
      ghcr.io/daemonless/pkg-cache:latest
    ```

---

## 4. Environment variables

All configuration uses environment variables checked at startup (`20-pkg-cache-init` and `pkg-cache-repos`). An invalid hostname, URL, boolean, or cache size exits with `[pkg-cache] invalid VAR` rather than writing a broken `nginx.conf`. The one exception is `PKG_LOG_MAX_SIZE`: an invalid value logs `[pkg-cache] invalid PKG_LOG_MAX_SIZE '...', using 50m` and falls back to `50m`.

### Core settings

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TZ` | `UTC` | Timezone for the container. |
| `PUID` / `PGID` | `1000` / `1000` | UID and GID recorded in `/config/.chown_done` for the `bsd` worker user. |
| `PKG_UPSTREAM` | `pkg.FreeBSD.org` | FreeBSD `pkg` mirror hostname to proxy, e.g. `pkg1.us.freebsd.org` or `pkg0.eu.freebsd.org`. Hostname only, with no `https://` scheme. |
| `PKG_CACHE_SIZE` | `50g` | Max on-disk cache size (`nginx` `max_size`), e.g. `10g`, `100g`, `500g`. Keep the `/cache` volume at least this big. |
| `PKG_RESOLVER` | *(from `/etc/resolv.conf`, fallback `1.1.1.1 8.8.8.8`)* | Space-separated DNS resolvers for runtime upstream resolution (`ipv6=off` is set). |
| `SKIP_CHOWN` | `true` | Skip recursive `chown` of `/config` and `/cache` once `/config/.chown_done` matches `PUID:PGID`. Set `false` to force a `chown` on every start. |
| `PKG_LOG_MAX_SIZE` | `50m` | Size cap for each on-disk log in `/config/log` (`access.log`, `error.log`), e.g. `10m`, `50m`, `1g`. Rotated via `SIGUSR1`; stats totals are kept separately and survive rotation. |

### Linux repository switches and upstream mirrors

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PKG_CACHE_APT` | `false` | Cache `apt` repositories (Debian and Ubuntu) under `/debian/`, `/debian-security/`, `/ubuntu/`, `/ubuntu-security/`, and `/ubuntu-ports/`: `true` or `false`. |
| `PKG_CACHE_DNF` | `false` | Cache `dnf` repositories (Fedora and EPEL) under `/fedora/` and `/epel/`: `true` or `false`. |
| `PKG_CACHE_APK` | `false` | Cache Alpine's `apk` repositories under `/alpine/`: `true` or `false`. |
| `PKG_CACHE_PACMAN` | `false` | Cache Arch Linux's `pacman` repositories under `/archlinux/`: `true` or `false`. |
| `PKG_DEBIAN_UPSTREAM` | `https://deb.debian.org/debian` | Debian mirror for `/debian/`, as a URL base. |
| `PKG_DEBIAN_SECURITY_UPSTREAM` | `https://deb.debian.org/debian-security` | Debian security mirror for `/debian-security/`, as a URL base. |
| `PKG_UBUNTU_UPSTREAM` | `https://archive.ubuntu.com/ubuntu` | Ubuntu mirror for `/ubuntu/` (`amd64`), as a URL base, e.g. `https://us.archive.ubuntu.com/ubuntu`. |
| `PKG_UBUNTU_SECURITY_UPSTREAM` | `https://security.ubuntu.com/ubuntu` | Ubuntu security mirror for `/ubuntu-security/`, as a URL base. |
| `PKG_UBUNTU_PORTS_UPSTREAM` | `https://ports.ubuntu.com/ubuntu-ports` | Ubuntu mirror for `/ubuntu-ports/` (`arm64` and other architectures), as a URL base. |
| `PKG_FEDORA_UPSTREAM` | `https://dl.fedoraproject.org/pub/fedora/linux` | Fedora mirror for `/fedora/`, ending at the directory holding `releases/` and `updates/`. Must answer directly without redirects; see [Mirrors, stats API, and troubleshooting](mirrors-and-operations.md). |
| `PKG_EPEL_UPSTREAM` | `https://dl.fedoraproject.org/pub/epel` | EPEL mirror for `/epel/`, as a URL base. |
| `PKG_ALPINE_UPSTREAM` | `https://dl-cdn.alpinelinux.org/alpine` | Alpine mirror for `/alpine/`, as a URL base. |
| `PKG_ARCH_UPSTREAM` | `https://geo.mirror.pkgbuild.com` | Arch Linux mirror for `/archlinux/`, as a URL base (the directory holding `core/` and `extra/`). |

---

## 5. Verify first boot

Check readiness and open the landing page:

```sh { linenums="0" }
curl -fsS http://pkg-cache.home.lan/healthz
# -> pkg-cache ok
```

Open `http://pkg-cache.home.lan/` in a browser to see enabled repository families and copy pre-filled client commands, then continue to [Client setup](clients.md).
