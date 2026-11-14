---
title: "Mirrors, stats API, and troubleshooting: Package Cache"
description: "Select upstream mirrors, review TTL and stale-on-error rules, inspect /stats.json and /healthz, manage logs, and troubleshoot client issues."
---

# Mirrors, stats API, and troubleshooting

---

## 1. Selecting upstream mirrors

By default, `pkg-cache` proxies primary upstreams (`pkg.FreeBSD.org`, `deb.debian.org`, `archive.ubuntu.com`, `dl.fedoraproject.org`, `dl-cdn.alpinelinux.org`, `geo.mirror.pkgbuild.com`). Pointing at a mirror near you reduces `MISS` latency and load on primary mirrors.

### FreeBSD mirrors (`PKG_UPSTREAM`)

`PKG_UPSTREAM` defaults to `pkg.FreeBSD.org` and takes a mirror hostname such as `pkg1.us.freebsd.org` or `pkg0.eu.freebsd.org` (hostname only, with no `https://` scheme or trailing path).

### Non-redirecting mirrors (required for Fedora)

`pkg-cache` fetches files from the configured upstream and returns them to your clients. **If an upstream mirror answers with a `301` or `302` redirect to another mirror, the client follows `Location:` out to the internet and bypasses the cache.**

This matters when overriding `PKG_FEDORA_UPSTREAM` (which defaults to Fedora's master `https://dl.fedoraproject.org/pub/fedora/linux`). Before choosing a mirror near you, check with `curl -sI` that it answers `200` itself rather than redirecting:

```sh { linenums="0" }
curl -sI https://mirror.example.org/fedora/linux/releases/43/Everything/x86_64/os/repodata/repomd.xml | head -n 5
# Good: HTTP/2 200
# Bad:  HTTP/2 302 (redirects clients around the cache)
```

### IPv4 upstream resolution (`ipv6=off`)

On hosts without a working global IPv6 route, trying upstream `AAAA` records first causes connection timeouts before falling back to IPv4. `pkg-cache` sets `ipv6=off` on its runtime `resolver` so upstream fetches use IPv4 directly.

---

## 2. Caching rules, concurrency, and stale fallback

Public mirrors often return `Cache-Control` or `Expires` headers that prevent caching. `pkg-cache` ignores the upstream's `Cache-Control`, `Expires`, and `Set-Cookie` when deciding what to cache and sets per-path TTLs:

| Family | Immutable files (`365d` TTL) | Mutable metadata (`1m` TTL) | Other |
| :--- | :--- | :--- | :--- |
| **FreeBSD (`pkg`)** | `/All/*.pkg` | `meta.{conf,txz,tzst}`, `packagesite.{pkg,txz,tzst}`, `data.{pkg,txz,tzst}` | `/vuxml/*` (`1h`), fallback (`10m`) |
| **Debian / Ubuntu (`apt`)** | `*.deb`, `*.udeb`, `*.dsc`, `*.tar.*`, `/by-hash/` | `/dists/*` (`InRelease`, `Release`, non-hashed indexes) | Fallback (`10m`) |
| **Fedora / EPEL (`dnf`)** | `*.rpm`, checksummed `/repodata/*` | `/repodata/repomd.xml`, `repomd.xml.asc` | Fallback (`10m`) |
| **Alpine (`apk`)** | `*.apk` | `APKINDEX.tar.gz` | Fallback (`10m`) |
| **Arch (`pacman`)** | `*.pkg.tar.*`, `*.pkg.tar.*.sig` | `*.db*`, `*.files*` (and `.sig`) | Fallback (`10m`) |

### Concurrent lock and stale-on-error

- **Concurrent download lock (`proxy_cache_lock on`):** When multiple clients request the same uncached file at once, `nginx` sends one upstream request (`60s` lock timeout) and serves the result to waiting clients.
- **Conditional revalidation (`proxy_cache_revalidate on`):** Expired `1m` catalog indexes are checked with `If-Modified-Since` instead of re-downloading unchanged files every minute.
- **Stale fallback (`proxy_cache_use_stale`):** If an upstream mirror errors or returns `500`, `502`, `503`, or `504`, `pkg-cache` serves cached copies (`STALE`) while upstream recovers.

---

## 3. Built-in endpoints and `/stats.json`

`pkg-cache` serves four local endpoints. `/healthz`, `/repos.json`, and `/stats.json` are not logged (`access_log off`); `/` is logged (`st == "-"`) and skipped by `pkg-cache-stats`, so monitoring requests do not affect hit-rate numbers:

| Endpoint | Content-Type | Purpose |
| :--- | :--- | :--- |
| `/` | `text/html` | Live stats and client setup page (refreshes every 15 seconds, with a light and dark theme toggle). |
| `/healthz` | `text/plain` | Readiness probe returning `200` `pkg-cache ok\n`. |
| `/repos.json` | `application/json` | Active repository switches: `{"freebsd":true,"apt":false,"dnf":false,"apk":false,"pacman":false}`. |
| `/stats.json` | `application/json` | Cumulative request and byte counters, cache disk usage, per-family stats, top 10 client IPs, and 15 most recent requests. |

### `/stats.json` schema

`pkg-cache-stats` reads new bytes appended to `/config/log/access.log` every 5 seconds, scans `/cache` disk usage once per minute, and atomically writes `/config/stats/stats.json`:

```json { linenums="0" }
{
  "generated": 1794689070,
  "started": 1794271757,
  "since": 1791837504,
  "upstream": "pkg.FreeBSD.org",
  "cache": {
    "bytes": 22173830144,
    "max_bytes": 53687091200,
    "objects": 3956
  },
  "requests": {
    "hit": 10492, "miss": 1915, "expired": 83, "stale": 0,
    "updating": 1, "revalidated": 530, "bypass": 0, "other": 0, "error": 0, "total": 13021
  },
  "bytes": {
    "hit": 49843655440, "miss": 9425720146, "expired": 518737894, "stale": 0,
    "updating": 0, "revalidated": 694927545, "bypass": 0, "other": 0, "error": 0, "total": 60483040925
  },
  "repos": {
    "freebsd": { "requests": 8910, "cached": 7662, "bytes": 41200100000, "cached_bytes": 34100000000 },
    "apt":     { "requests": 2140, "cached": 1733, "bytes": 11800000000, "cached_bytes": 9600000000 },
    "dnf":     { "requests": 1120, "cached": 885,  "bytes": 4900000000,  "cached_bytes": 3800000000 },
    "apk":     { "requests": 320,  "cached": 282,  "bytes": 810000000,   "cached_bytes": 712000000 },
    "pacman":  { "requests": 0,    "cached": 0,    "bytes": 0,           "cached_bytes": 0 }
  },
  "clients": [
    { "ip": "192.168.1.20", "requests": 5678, "bytes": 23262315818 }
  ],
  "recent": [
    {
      "ip": "192.168.1.20",
      "status": "HIT",
      "path": "/FreeBSD:15:amd64/latest/All/llvm19-19.1.7.pkg",
      "code": 200,
      "bytes": 298426368,
      "repo": "freebsd"
    }
  ]
}
```

Upstream `5xx` responses are counted under `error` rather than `miss` so upstream errors do not lower the reported cache hit rate.

---

## 4. Log rotation and cache eviction

### Log size cap (`PKG_LOG_MAX_SIZE`)

Every 5 minutes, `pkg-cache-logrotate` checks `/config/log/access.log` and `/config/log/error.log` against `PKG_LOG_MAX_SIZE` (default `50m`). When a log exceeds the cap, it is moved aside, `nginx` reopens log files via `SIGUSR1`, and the rotated file is removed. Because `pkg-cache-stats` stores folded totals in `/config/stats/counters` and `/config/stats/clients`, log rotation and container restarts keep cumulative statistics intact.

### Automatic cache eviction

`nginx` evicts least-recently-used entries automatically whenever `/cache` reaches `PKG_CACHE_SIZE` or when an entry goes unrequested for `90d`.

---

## 5. Troubleshooting

??? question "`pkg` rejects `pkg+http://` on FreeBSD 15"
    Change `url: "pkg+http://..."` to `url: "http://..."` in `/usr/local/etc/pkg/repos/FreeBSD.conf`. On FreeBSD 15, `pkg` rejects the `pkg+` scheme unless `mirror_type` is `srv`.

??? question "FreeBSD 15 client still downloads from `pkg.FreeBSD.org`"
    Run `pkg -vv` on the client and check the repositories listed at the bottom:

    1. On **FreeBSD 15**, the default ports repository is named `FreeBSD-ports`, not `FreeBSD`. Rename the block in `/usr/local/etc/pkg/repos/FreeBSD.conf` to `FreeBSD-ports: { ... }`.
    2. Check that `mirror_type: "none"` is set inside the block.

??? question "Linux client receives `404 This pkg-cache does not cache <family> repositories`"
    Each Linux family is off until enabled. Set `PKG_CACHE_APT=true`, `PKG_CACHE_DNF=true`, `PKG_CACHE_APK=true`, or `PKG_CACHE_PACMAN=true` in your stack environment and recreate the container (`podman-compose up -d`). Check `/repos.json` to confirm the family is `true`.

??? question "Fedora `dnf` packages are not showing up in `/stats.json`"
    Check two things:

    1. On the **Fedora client**, check that `metalink=` is commented out (`#metalink=`) and `baseurl=http://<cache-host>/fedora` is enabled in `/etc/yum.repos.d/fedora.repo` and `/etc/yum.repos.d/fedora-updates.repo`.
    2. On **`pkg-cache`**, check that `PKG_FEDORA_UPSTREAM` returns `200` directly rather than redirecting (`curl -sI <mirror-url>`).

??? question "Container startup walks `/cache` on every restart"
    Check that `/config` is mounted as a persistent volume alongside `/cache` and `SKIP_CHOWN` is `true` (default). The `.chown_done` marker lives in `/config`, so `/config` must persist across restarts for the `chown` skip to take effect.
