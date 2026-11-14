---
title: "Client setup: Package Cache"
description: "Configure FreeBSD hosts, jails, Containerfiles, Debian, Ubuntu (amd64 and arm64), Fedora, EPEL, Alpine, and Arch Linux clients to use Daemonless Package Cache."
---

# Client setup

Open `http://<cache-host>/` in a browser to copy client commands filled in with your cache's host and port, or use the commands below. Package signature verification stays on every client.

---

## 1. FreeBSD hosts and jails (`pkg`)

Place an override in `/usr/local/etc/pkg/repos/FreeBSD.conf` rather than editing `/etc/pkg/FreeBSD.conf` directly.

### Check your repository name (`FreeBSD-ports` vs `FreeBSD`)

FreeBSD 15.0 renamed the default ports repository in `/etc/pkg/FreeBSD.conf` from `FreeBSD` to `FreeBSD-ports`. Check which repository name your system uses:

```sh { linenums="0" }
pkg -vv | grep -E '^  [A-Za-z0-9_-]+: \{'
```

=== "FreeBSD 15 (`FreeBSD-ports`)"

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

=== "FreeBSD 14 (`FreeBSD`)"

    ```sh { linenums="0" }
    mkdir -p /usr/local/etc/pkg/repos
    cat > /usr/local/etc/pkg/repos/FreeBSD.conf <<'EOF'
    FreeBSD: {
      url: "http://pkg-cache.home.lan/${ABI}/quarterly",
      mirror_type: "none",
      signature_type: "fingerprints",
      fingerprints: "/usr/share/keys/pkg",
      enabled: yes
    }
    EOF
    pkg update
    ```

Swap `quarterly` for `latest` to track rolling packages. Packages are still checked against FreeBSD's keys in `/usr/share/keys/pkg`.

!!! warning "Two rules for FreeBSD `pkg`"
    1. **Use plain `http://`, not `pkg+http://`:** `pkg` on FreeBSD 15 rejects the `pkg+` scheme unless `mirror_type` is `srv`.
    2. **Set `mirror_type: "none"`:** Leaving `mirror_type: "srv"` queries DNS `SRV` records and bypasses the cache.

### Caching `pkg audit` vulnerability checks (`VuXML`)

For `pkg audit`, fetch the FreeBSD vulnerability database through `/vuxml/` (cached for 1 hour):

```sh { linenums="0" }
echo 'VULNXML_SITE = "http://pkg-cache.home.lan/vuxml/vuln.xml.xz";' >> /usr/local/etc/pkg.conf
```

---

## 2. Linux hosts and VMs

Before pointing a Linux distribution at the cache, turn on its repository family in `pkg-cache` (`PKG_CACHE_APT=true`, `PKG_CACHE_DNF=true`, `PKG_CACHE_APK=true`, or `PKG_CACHE_PACMAN=true`). When a family is off, `pkg-cache` returns `404` naming the variable to enable.

### Debian (`apt`, `PKG_CACHE_APT=true`)

=== "Debian 12 and later"

    ```sh { linenums="0" }
    sed -i 's|http://deb.debian.org/|http://pkg-cache.home.lan/|' /etc/apt/sources.list.d/debian.sources
    apt-get update
    ```

=== "Debian 11 and older"

    ```sh { linenums="0" }
    sed -i 's|http://deb.debian.org/|http://pkg-cache.home.lan/|' /etc/apt/sources.list
    apt-get update
    ```

### Ubuntu (`apt`, `PKG_CACHE_APT=true`)

Covers `amd64` (`archive.ubuntu.com`), `security.ubuntu.com`, and `arm64` (`ports.ubuntu.com/ubuntu-ports`):

=== "Ubuntu 24.04 and later"

    ```sh { linenums="0" }
    sed -i -e 's|http://archive.ubuntu.com/ubuntu/|http://pkg-cache.home.lan/ubuntu/|' \
      -e 's|http://security.ubuntu.com/ubuntu/|http://pkg-cache.home.lan/ubuntu-security/|' \
      -e 's|http://ports.ubuntu.com/ubuntu-ports/|http://pkg-cache.home.lan/ubuntu-ports/|' \
      /etc/apt/sources.list.d/ubuntu.sources
    apt-get update
    ```

=== "Ubuntu 22.04 and older"

    ```sh { linenums="0" }
    sed -i -e 's|http://archive.ubuntu.com/ubuntu/|http://pkg-cache.home.lan/ubuntu/|' \
      -e 's|http://security.ubuntu.com/ubuntu/|http://pkg-cache.home.lan/ubuntu-security/|' \
      -e 's|http://ports.ubuntu.com/ubuntu-ports/|http://pkg-cache.home.lan/ubuntu-ports/|' \
      /etc/apt/sources.list
    apt-get update
    ```

### Fedora and EPEL (`dnf`, `PKG_CACHE_DNF=true`)

Comment out `metalink=` and set `baseurl=` to your cache:

=== "Fedora"

    ```sh { linenums="0" }
    sed -i -e 's|^metalink=|#metalink=|' \
      -e 's|^#baseurl=http://download.example/pub/fedora/linux|baseurl=http://pkg-cache.home.lan/fedora|' \
      /etc/yum.repos.d/fedora.repo /etc/yum.repos.d/fedora-updates.repo
    dnf makecache
    ```

    Packages are still checked against Fedora's keys. The `fedora-cisco-openh264` repository is Cisco's and keeps going straight to Cisco.

=== "EPEL (AlmaLinux, Rocky, RHEL)"

    Once `epel-release` is installed:

    ```sh { linenums="0" }
    sed -i -e 's|^metalink=|#metalink=|' \
      -e 's|^#baseurl=https://download.example/pub/epel|baseurl=http://pkg-cache.home.lan/epel|' \
      /etc/yum.repos.d/epel.repo
    dnf makecache
    ```

    Only EPEL comes through the cache; AlmaLinux, Rocky, or RHEL's own repositories go to their mirrors as before.

### Alpine (`apk`, `PKG_CACHE_APK=true`)

```sh { linenums="0" }
sed -i 's|https://dl-cdn.alpinelinux.org/alpine|http://pkg-cache.home.lan/alpine|' /etc/apk/repositories
apk update
```

Packages are still checked against Alpine's keys.

### Arch Linux (`pacman`, `PKG_CACHE_PACMAN=true`)

```sh { linenums="0" }
echo 'Server = http://pkg-cache.home.lan/archlinux/$repo/os/$arch' > /etc/pacman.d/mirrorlist
pacman -Syu
```

Packages are still checked against the Arch keyring.

---

## 3. Using the cache in a `Containerfile`

In a `Containerfile`, make the distribution's setup command above the first `RUN` instruction, before anything is installed.

---

## 4. Verifying cache hits from a client

Every proxied response includes an `X-Cache-Status` HTTP header (`MISS`, `HIT`, `REVALIDATED`, `EXPIRED`, `STALE`, or `UPDATING`):

```sh { linenums="0" }
curl -sI http://pkg-cache.home.lan/FreeBSD:15:amd64/quarterly/meta.conf | grep -i x-cache-status
# First request:  X-Cache-Status: MISS
# Second request: X-Cache-Status: HIT
```
