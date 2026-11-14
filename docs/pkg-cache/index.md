---
title: "Package Cache: local multi-OS package caching appliance"
description: "Pull every package once and serve it over your LAN to FreeBSD hosts, jails, Linux VMs, and container builds. Supports FreeBSD pkg, Debian/Ubuntu apt, Fedora/EPEL dnf, Alpine apk, and Arch pacman on FreeBSD and Linux (amd64 and arm64)."
hide:
  - navigation
  - toc
---

<div class="rp-hero" markdown>

<div class="rp-hero-logo">
  <img src="logo.svg" alt="Daemonless Package Cache">
</div>

<div class="rp-platform-bar" markdown>
  <span class="rp-os-pill rp-os-pill--freebsd" markdown>:simple-freebsd: FreeBSD <span class="rp-os-arch">amd64 · arm64</span></span>
  <span class="rp-os-pill rp-os-pill--linux" markdown>:simple-linux: Linux <span class="rp-os-arch">amd64 · arm64</span></span>
  <span class="rp-os-pill rp-os-pill--ecosystems" markdown>:material-package-variant-closed: Caches <span class="rp-os-arch">pkg · apt · dnf · apk · pacman</span></span>
</div>

# Package Cache

<div class="rp-url-transform" markdown>
  <span class="rp-url-chip rp-url-chip--before" markdown>:material-cloud-download-outline: MISS · 20 jails pulling pkg.FreeBSD.org over WAN</span>
  <span class="rp-url-arrow">→</span>
  <span class="rp-url-chip rp-url-chip--after" markdown>:material-flash: HIT · Served from local LAN · 365d cached · verified</span>
</div>

<p class="rp-hero-subtitle">Pull every package once. Serve it to your hosts, jails, VMs, and container builds over your LAN.</p>

<p class="rp-hero-tagline" markdown>Caching proxy appliance for **FreeBSD `pkg`** (including `pkg audit` VuXML) and **Linux `apt`, `dnf`, `apk`, and `pacman`**. No `nginx.conf` to write, a live stats page with copy-paste client commands on port `80`, and package signature verification kept on every client.</p>

<div class="rp-hero-buttons" markdown>
  [Install](#install){ .md-button .md-button--primary }
  [Setup and ZFS guide](setup.md){ .md-button }
  [Client commands](#clients){ .md-button }
  [Image spec](../images/pkg-cache.md){ .md-button }
  [:fontawesome-brands-github: GitHub](https://github.com/daemonless/pkg-cache){ .md-button }
</div>

</div>

<div class="pc-hero-showcase">
<div class="rp-window-frame">
  <div class="rp-window-header">
    <span class="rp-window-dot red"></span>
    <span class="rp-window-dot yellow"></span>
    <span class="rp-window-dot green"></span>
    <span class="rp-window-title">http://pkg-cache.home.lan/: Live stats and client setup</span>
    <span class="rp-window-badge">Light and dark theme</span>
  </div>
  <div class="pc-dash">
    <div class="pc-dash__topbar">
      <span class="pc-dash__brand">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 8l-9-5-9 5v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>
        <span><b>P</b>ACKAGE CACHE</span>
      </span>
      <span class="pc-dash__endpoints">stats.json · healthz</span>
    </div>
    <div class="pc-dash__body">
      <div class="pc-dash__status">
        <span class="pc-dash__dot"></span>
        <span>All good: caching FreeBSD, Debian and Ubuntu, Fedora and EPEL, Alpine; <strong>84 % of requests served from here</strong>.</span>
      </div>
      <div class="pc-dash__tiles">
        <div class="pc-dash__tile">
          <div class="pc-dash__tile-label">Served from cache</div>
          <div class="pc-dash__tile-big">84<small>%</small></div>
          <div class="pc-dash__tile-sub">10,492 of 12,490 requests</div>
          <div class="pc-dash__track pc-dash__track--ok"><span style="width: 84%"></span></div>
        </div>
        <div class="pc-dash__tile">
          <div class="pc-dash__tile-label">Bandwidth saved</div>
          <div class="pc-dash__tile-big">48.2 GB</div>
          <div class="pc-dash__tile-sub">9.4 GB fetched upstream in 1,998 requests</div>
          <div class="pc-dash__track pc-dash__track--ok"><span style="width: 83%"></span></div>
        </div>
        <div class="pc-dash__tile">
          <div class="pc-dash__tile-label">Disk</div>
          <div class="pc-dash__tile-big">18.6 GB<small>used</small></div>
          <div class="pc-dash__tile-sub">37 % of 50.0 GB · 4,120 files</div>
          <div class="pc-dash__track"><span style="width: 37%"></span></div>
        </div>
      </div>
      <div class="pc-dash__split">
        <div class="pc-dash__panel">
          <div class="pc-dash__panel-head">What it caches</div>
          <div class="pc-dash__row">
            <div class="pc-dash__row-main"><b>FreeBSD</b><span>pkg · 8,910 requests, 86 % from here, 34.1 GB served</span></div>
            <span class="pc-dash__chip pc-dash__chip--on">On</span>
          </div>
          <div class="pc-dash__row">
            <div class="pc-dash__row-main"><b>Debian and Ubuntu</b><span>apt · 2,140 requests, 81 % from here, 9.6 GB served</span></div>
            <span class="pc-dash__chip pc-dash__chip--on">On</span>
          </div>
          <div class="pc-dash__row">
            <div class="pc-dash__row-main"><b>Fedora and EPEL</b><span>dnf · 1,120 requests, 79 % from here, 3.8 GB served</span></div>
            <span class="pc-dash__chip pc-dash__chip--on">On</span>
          </div>
          <div class="pc-dash__row">
            <div class="pc-dash__row-main"><b>Alpine</b><span>apk · 320 requests, 88 % from here, 712 MB served</span></div>
            <span class="pc-dash__chip pc-dash__chip--on">On</span>
          </div>
        </div>
        <div class="pc-dash__panel">
          <div class="pc-dash__panel-head">Recent requests</div>
          <div class="pc-dash__req">
            <span class="pc-dash__st pc-dash__st--hit">HIT</span>
            <span class="pc-dash__path">FreeBSD:15:amd64/latest/All/<b>llvm19-19.1.7.pkg</b></span>
            <span class="pc-dash__size">284.6 MB</span>
          </div>
          <div class="pc-dash__req">
            <span class="pc-dash__st pc-dash__st--hit">HIT</span>
            <span class="pc-dash__path">debian/pool/main/p/python3.13/<b>libpython3.13_amd64.deb</b></span>
            <span class="pc-dash__size">2.1 MB</span>
          </div>
          <div class="pc-dash__req">
            <span class="pc-dash__st pc-dash__st--hit">HIT</span>
            <span class="pc-dash__path">fedora/updates/43/Everything/x86_64/Packages/<b>podman.rpm</b></span>
            <span class="pc-dash__size">15.8 MB</span>
          </div>
          <div class="pc-dash__req">
            <span class="pc-dash__st pc-dash__st--hit">REVALIDATED</span>
            <span class="pc-dash__path">FreeBSD:15:amd64/latest/<b>packagesite.tzst</b></span>
            <span class="pc-dash__size">7.9 MB</span>
          </div>
          <div class="pc-dash__req">
            <span class="pc-dash__st pc-dash__st--miss">MISS</span>
            <span class="pc-dash__path">alpine/v3.23/main/aarch64/<b>busybox-1.37.0-r9.apk</b></span>
            <span class="pc-dash__size">518 KB</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</div>

<div class="pc-shot-caption" markdown>
  Open `http://<cache-host>/` in a browser for live hit rates, top clients, and pre-filled client setup commands · [:material-image-outline: View first-boot UI screenshot](dashboard.png){ .glightbox data-gallery="pc-hero" }
</div>

<div class="rp-section" markdown>
<div class="rp-section-head" markdown>
  <span class="rp-eyebrow">Platforms</span>
  <h2>Runs on FreeBSD and Linux</h2>
  <p>One multi-OS manifest tag, <code>ghcr.io/daemonless/pkg-cache:latest</code>, resolves to a FreeBSD jail image or a Linux container on both <code>amd64</code> and <code>arm64</code>.</p>
</div>

<div class="rp-platform-grid" markdown>
<div class="rp-platform-card rp-platform-card--freebsd" markdown>
<div class="rp-platform-card__top" markdown>
<h3 class="rp-platform-card__title" markdown>:simple-freebsd: FreeBSD</h3>
<span class="rp-arch-chips"><span class="rp-arch-chip">amd64</span><span class="rp-arch-chip">arm64</span></span>
</div>

Built on FreeBSD `nginx-base`. Put `/cache` on a ZFS dataset and serve packages to hosts, jails, and `Containerfile` builds on your network.

<div class="rp-runtime-row">
  <span class="rp-runtime-tag">fjord</span>
  <span class="rp-runtime-tag">Podman + ocijail</span>
  <span class="rp-runtime-tag">AppJail Director</span>
  <span class="rp-runtime-tag">Bastille</span>
</div>
</div>

<div class="rp-platform-card rp-platform-card--linux" markdown>
<div class="rp-platform-card__top" markdown>
<h3 class="rp-platform-card__title" markdown>:simple-linux: Linux</h3>
<span class="rp-arch-chips"><span class="rp-arch-chip">amd64</span><span class="rp-arch-chip">arm64</span></span>
</div>

Built on Linux (Alpine) with `nginx` and `s6`, running the same startup config renderer, repository switches, log rotator, and stats landing page on `amd64` and `arm64`.

<div class="rp-runtime-row">
  <span class="rp-runtime-tag">fjord</span>
  <span class="rp-runtime-tag">Podman</span>
</div>
</div>
</div>
</div>

<div class="rp-section" markdown>
<div class="rp-section-head" markdown>
  <span class="rp-eyebrow">Repositories</span>
  <h2>One cache for FreeBSD and Linux</h2>
  <p>FreeBSD <code>pkg</code> and <code>pkg audit</code> are active by default. Set one environment variable per family to cache Linux packages alongside FreeBSD.</p>
</div>

<div class="pc-distro-grid" markdown>
<div class="pc-distro-card pc-distro-card--default" markdown>
<div class="pc-distro-card__head" markdown>
<h3 markdown>:simple-freebsd: FreeBSD</h3>
<span class="pc-distro-toggle pc-distro-toggle--on">On by default</span>
</div>

Caches `quarterly` and `latest` binary packages across FreeBSD releases and ABIs (`amd64`, `aarch64`), plus the `pkg audit` vulnerability database (`vuxml.freebsd.org`).

<div class="pc-route-list">
  <span class="pc-route-pill">/${ABI}/quarterly</span>
  <span class="pc-route-pill">/${ABI}/latest</span>
  <span class="pc-route-pill">/vuxml/</span>
</div>
</div>

<div class="pc-distro-card" markdown>
<div class="pc-distro-card__head" markdown>
<h3 markdown>:simple-debian: Debian and Ubuntu</h3>
<span class="pc-distro-toggle">PKG_CACHE_APT=true</span>
</div>

Proxies `apt` repositories including security channels and `ubuntu-ports` (`arm64`), keeping `.deb` pools and `by-hash` indexes for a year while refreshing `dists/` every minute.

<div class="pc-route-list">
  <span class="pc-route-pill">/debian/</span>
  <span class="pc-route-pill">/debian-security/</span>
  <span class="pc-route-pill">/ubuntu/</span>
  <span class="pc-route-pill">/ubuntu-security/</span>
  <span class="pc-route-pill">/ubuntu-ports/</span>
</div>
</div>

<div class="pc-distro-card" markdown>
<div class="pc-distro-card__head" markdown>
<h3 markdown>:simple-fedora: Fedora and EPEL</h3>
<span class="pc-distro-toggle">PKG_CACHE_DNF=true</span>
</div>

Proxies `dnf` RPM packages and checksummed `repodata/` for 365 days while revalidating `repomd.xml` every minute.

<div class="pc-route-list">
  <span class="pc-route-pill">/fedora/</span>
  <span class="pc-route-pill">/epel/</span>
</div>
</div>

<div class="pc-distro-card" markdown>
<div class="pc-distro-card__head" markdown>
<h3 markdown>:simple-alpinelinux: Alpine Linux</h3>
<span class="pc-distro-toggle">PKG_CACHE_APK=true</span>
</div>

Proxies Alpine `apk` repositories, caching versioned `.apk` packages for 365 days and refreshing `APKINDEX.tar.gz` every minute.

<div class="pc-route-list">
  <span class="pc-route-pill">/alpine/</span>
</div>
</div>

<div class="pc-distro-card" markdown>
<div class="pc-distro-card__head" markdown>
<h3 markdown>:simple-archlinux: Arch Linux</h3>
<span class="pc-distro-toggle">PKG_CACHE_PACMAN=true</span>
</div>

Serves as `pacman`'s local mirror, caching `.pkg.tar.*` archives and `.sig` files for 365 days while refreshing `.db` and `.files` every minute.

<div class="pc-route-list">
  <span class="pc-route-pill">/archlinux/</span>
</div>
</div>

<div class="pc-distro-card" markdown>
<div class="pc-distro-card__head" markdown>
<h3 markdown>:material-hammer-wrench: Containerfiles</h3>
<span class="pc-distro-toggle pc-distro-toggle--on">First RUN</span>
</div>

In a `Containerfile`, put the distribution's setup command in the first `RUN` instruction, before anything is installed, so image builds pull cached packages over your LAN.

<div class="pc-route-list">
  <span class="pc-route-pill">Containerfile</span>
</div>
</div>
</div>
</div>

<div class="rp-section" markdown>
<div class="rp-section-head" markdown>
  <span class="rp-eyebrow">How it works</span>
  <h2>Cached packages, fresh indexes, verified signatures</h2>
  <p>Public mirrors often send <code>Cache-Control: no-cache</code> or redirect clients away, while generic proxies can serve stale package indexes. Package Cache sets separate rules for package files and metadata.</p>
</div>

<div class="rp-modes" markdown>
<div class="rp-mode-card" markdown>
<span class="rp-mode-index">01 / Immutable packages</span>
<h3>Cached for 365 days</h3>
<span class="rp-mode-domain">*.pkg · *.deb · *.rpm · *.apk · *.zst</span>

Package filenames include their version and are immutable once published. The first machine pulls upstream (`MISS`); later requests get a local `HIT`, with automatic LRU eviction at `PKG_CACHE_SIZE`.
</div>

<div class="rp-mode-card" markdown>
<span class="rp-mode-index">02 / Live indexes and lock coalescing</span>
<h3>1-minute metadata and stale fallback</h3>
<span class="rp-mode-domain">proxy_cache_lock · use_stale 5xx</span>

Catalogs (`packagesite.tzst`, `dists/`, `repomd.xml`, `APKINDEX.tar.gz`) refresh after 1 minute using `If-Modified-Since`. When several machines fetch the same uncached file at once, `proxy_cache_lock` sends one upstream download and serves cached copies during upstream `5xx` errors.
</div>

<div class="rp-mode-card" markdown>
<span class="rp-mode-index">03 / End-to-end verification</span>
<h3>Client signatures stay enabled</h3>
<span class="rp-mode-domain">/usr/share/keys/pkg · GPG · pacman-key</span>

Signature checking stays on every client. FreeBSD `pkg` fingerprints, Debian and Ubuntu `apt` keys, Fedora RPM GPG keys, Alpine keys, and the Arch keyring verify packages on the client before install.
</div>
</div>
</div>

<div class="rp-section rp-section--tight" id="clients" markdown>
<div class="rp-section-head" markdown>
  <span class="rp-eyebrow">Client setup</span>
  <h2>Point hosts, jails, and builds at the cache</h2>
  <p>Open <code>http://&lt;cache-host&gt;/</code> in a browser for commands filled in with your cache's address, or copy them below. See <a href="clients/">Client setup</a> for full details.</p>
</div>
</div>

=== ":simple-freebsd: FreeBSD (`pkg`)"

    Drop `/usr/local/etc/pkg/repos/FreeBSD.conf` on any FreeBSD host or jail. Use `FreeBSD-ports` on **FreeBSD 15** (check `pkg -vv`) or `FreeBSD` on **FreeBSD 14**, and use plain `http://` with `mirror_type: "none"`:

    ```sh { linenums="0" }
    mkdir -p /usr/local/etc/pkg/repos
    cat > /usr/local/etc/pkg/repos/FreeBSD.conf <<'EOF'
    FreeBSD-ports: {
      url: "http://pkg-cache.home.lan/${ABI}/quarterly",
      mirror_type: "none",
      signature_type: "fingerprints",
      fingerprints: "/usr/share/keys/pkg",
      enabled: yes
    }
    EOF
    pkg update
    ```

    Fetch the `pkg audit` vulnerability database through the cache too:

    ```sh { linenums="0" }
    echo 'VULNXML_SITE = "http://pkg-cache.home.lan/vuxml/vuln.xml.xz";' >> /usr/local/etc/pkg.conf
    ```

=== ":simple-debian: Debian and Ubuntu (`apt`)"

    Turn on `PKG_CACHE_APT=true` on the cache, then point `apt` at it:

    ```sh { linenums="0" }
    # Debian 12 and later (/etc/apt/sources.list.d/debian.sources)
    sed -i 's|http://deb.debian.org/|http://pkg-cache.home.lan/|' /etc/apt/sources.list.d/debian.sources
    apt-get update
    ```

    ```sh { linenums="0" }
    # Ubuntu 24.04 and later (archive, security, and ubuntu-ports)
    sed -i -e 's|http://archive.ubuntu.com/ubuntu/|http://pkg-cache.home.lan/ubuntu/|' \
      -e 's|http://security.ubuntu.com/ubuntu/|http://pkg-cache.home.lan/ubuntu-security/|' \
      -e 's|http://ports.ubuntu.com/ubuntu-ports/|http://pkg-cache.home.lan/ubuntu-ports/|' \
      /etc/apt/sources.list.d/ubuntu.sources
    apt-get update
    ```

=== ":simple-fedora: Fedora and EPEL (`dnf`)"

    Turn on `PKG_CACHE_DNF=true` on the cache (with a non-redirecting `PKG_FEDORA_UPSTREAM` mirror), then switch `dnf` from `metalink` to `baseurl`:

    ```sh { linenums="0" }
    # Fedora
    sed -i -e 's|^metalink=|#metalink=|' \
      -e 's|^#baseurl=http://download.example/pub/fedora/linux|baseurl=http://pkg-cache.home.lan/fedora|' \
      /etc/yum.repos.d/fedora.repo /etc/yum.repos.d/fedora-updates.repo
    dnf makecache
    ```

    ```sh { linenums="0" }
    # EPEL (AlmaLinux, Rocky, RHEL)
    sed -i -e 's|^metalink=|#metalink=|' \
      -e 's|^#baseurl=https://download.example/pub/epel|baseurl=http://pkg-cache.home.lan/epel|' \
      /etc/yum.repos.d/epel.repo
    dnf makecache
    ```

=== ":simple-alpinelinux: Alpine and Arch"

    Turn on `PKG_CACHE_APK=true` or `PKG_CACHE_PACMAN=true` on the cache:

    ```sh { linenums="0" }
    # Alpine (apk)
    sed -i 's|https://dl-cdn.alpinelinux.org/alpine|http://pkg-cache.home.lan/alpine|' /etc/apk/repositories
    apk update
    ```

    ```sh { linenums="0" }
    # Arch Linux (pacman)
    echo 'Server = http://pkg-cache.home.lan/archlinux/$repo/os/$arch' > /etc/pacman.d/mirrorlist
    pacman -Syu
    ```

<div class="rp-section rp-section--tight" id="install" markdown>
<div class="rp-section-head" markdown>
  <span class="rp-eyebrow">Install</span>
  <h2>Deploy on FreeBSD or Linux</h2>
  <p>Mount persistent <code>/config</code> and <code>/cache</code> directories, publish port <code>80</code>, and open <code>http://&lt;cache-host&gt;/</code>.</p>
</div>
</div>

=== ":material-sail-boat: fjord"

    1. Open **[fjord](https://fjord.daemonless.io)** on your FreeBSD or Linux host.
    2. Find **Daemonless pkg cache** in the catalog and click **Install**.
    3. Turn on any Linux repository switches (`PKG_CACHE_APT`, `PKG_CACHE_DNF`, `PKG_CACHE_APK`, `PKG_CACHE_PACMAN`) in Settings if you also cache Linux machines, then open `http://<host-ip>/`.

=== ":podman-podman: Podman Compose"

    ```yaml { linenums="0" }
    services:
      pkg-cache:
        image: ghcr.io/daemonless/pkg-cache:latest
        container_name: pkg-cache
        restart: unless-stopped

        environment:
          - TZ=UTC
          - PKG_UPSTREAM=pkg.FreeBSD.org
          - PKG_CACHE_SIZE=50g
          - SKIP_CHOWN=true
          - PKG_LOG_MAX_SIZE=50m
          - PKG_CACHE_APT=${PKG_CACHE_APT:-false}
          - PKG_CACHE_DNF=${PKG_CACHE_DNF:-false}
          - PKG_CACHE_APK=${PKG_CACHE_APK:-false}
          - PKG_CACHE_PACMAN=${PKG_CACHE_PACMAN:-false}

        volumes:
          - /containers/pkg-cache:/config
          - /containers/pkg-cache/cache:/cache

        ports:
          - 80:80
    ```

    Start it with `podman-compose up -d`, then open `http://<server>:80`. For FreeBSD `pf` port forwarding, boot auto-start (`restart: always`), interactive path placeholders, and **AppJail Director** or **Bastille** bundles, see the [Host setup guide](setup.md) and the [Daemonless pkg cache image page](../images/pkg-cache.md).

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

    See the [Daemonless pkg cache image page](../images/pkg-cache.md) for **AppJail Director** and **Bastille** deployment files.

<div class="rp-section" id="docs" markdown>
<div class="rp-section-head" markdown>
  <span class="rp-eyebrow">Documentation</span>
  <h2>Setup and operations guides</h2>
  <p>Storage sizing, ZFS setup, client commands for FreeBSD and Linux, mirror selection, and <code>/stats.json</code> monitoring.</p>
</div>

<div class="rp-setup-steps" markdown>
<div class="rp-setup-step" markdown>
<span class="rp-setup-step__num">1</span>
<h4>Size `/cache`</h4>
<p>Default <code>PKG_CACHE_SIZE</code> is <code>50g</code> (about <code>10G</code> per FreeBSD release and architecture; give it more with Linux families on).</p>
</div>

<div class="rp-setup-step" markdown>
<span class="rp-setup-step__num">2</span>
<h4>Start the appliance</h4>
<p>Deploy on port <code>80</code> with persistent <code>/config</code> and <code>/cache</code> volumes.</p>
</div>

<div class="rp-setup-step" markdown>
<span class="rp-setup-step__num">3</span>
<h4>Pick mirrors</h4>
<p>Point <code>PKG_UPSTREAM</code> and optional Linux mirror variables at non-redirecting mirrors near you.</p>
</div>

<div class="rp-setup-step" markdown>
<span class="rp-setup-step__num">4</span>
<h4>Point your clients</h4>
<p>Run the client command for each machine or <code>Containerfile</code>, then watch hits at <code>http://&lt;cache-host&gt;/</code>.</p>
</div>
</div>

<div class="rp-docs-grid" markdown>
<a class="rp-doc-card" href="setup/" markdown>
<span class="rp-doc-card__title" markdown>:material-rocket-launch-outline: Host setup, ZFS, and sizing <span class="rp-doc-card__arrow">→</span></span>
<p>FreeBSD and Linux setup, ZFS dataset creation, cache sizing, and all <code>PKG_*</code> environment variables.</p>
</a>

<a class="rp-doc-card" href="clients/" markdown>
<span class="rp-doc-card__title" markdown>:material-laptop: Client setup <span class="rp-doc-card__arrow">→</span></span>
<p>Client commands for FreeBSD 14 and 15 (<code>FreeBSD-ports</code>, <code>pkg audit</code>), Debian, Ubuntu, Fedora, EPEL, Alpine, Arch, and <code>Containerfile</code> builds.</p>
</a>

<a class="rp-doc-card" href="mirrors-and-operations/" markdown>
<span class="rp-doc-card__title" markdown>:material-chart-timeline-variant: Mirrors, stats API, and troubleshooting <span class="rp-doc-card__arrow">→</span></span>
<p>Upstream mirror selection, why redirecting mirrors bypass caches, <code>/stats.json</code> and <code>/healthz</code> schemas, log rotation, and common fixes.</p>
</a>

<a class="rp-doc-card" href="../images/pkg-cache/" markdown>
<span class="rp-doc-card__title" markdown>:material-cube-outline: Image spec and bundles <span class="rp-doc-card__arrow">→</span></span>
<p>Downloadable Podman Compose, AppJail Director, and Bastille bundles with path and port placeholders.</p>
</a>
</div>
</div>

<div class="rp-section" markdown>
<div class="rp-footer-bar" markdown>
<div markdown>
**Open source (`BSD-2-Clause`)**: built on `nginx` (`nginx-base` on FreeBSD, Linux (Alpine) with `nginx` and `s6` on Linux).
</div>
<div class="rp-footer-links" markdown>
[:fontawesome-brands-github: daemonless/pkg-cache](https://github.com/daemonless/pkg-cache)
[:material-package-variant: Image spec](../images/pkg-cache.md)
[:material-shield-check: Reverse Proxy](../reverse-proxy/index.md)
[:fontawesome-brands-discord: Community](../community.md)
</div>
</div>
</div>
