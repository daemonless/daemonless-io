# Daemonless: Native OCI containers for FreeBSD

**TL;DR:** Native FreeBSD container images for self-hosted apps using Podman + ocijail. No Linux VM needed.  See: [https://daemonless.io/quick-start/](https://daemonless.io/quick-start/)

A bit of background: I've been a FreeBSD user since the late 90s and was a ports committer from 2002-2010 (working on the GNOME and Multimedia teams).

I've always kept a mixed homelab of Linux and FreeBSD, and while I use both daily, **I have always felt more "at home" with FreeBSD.** There is a logic and cohesiveness to the Base System + Ports approach that just clicks for me.

Because of this, I've wanted to move more of my core services (like the *Arr* stack) off Linux and onto FreeBSD. **However, the workflow was always the blocker:**

I didn't want to give up the convenience of the OCI/Container workflow (immutable infrastructure, easy updates) that I have on Linux. I certainly didn't want to go back to the "sysadmin drudgery" of manually maintaining dependencies inside 15 different Jails. But I also didn't want to run a heavy Linux VM just to use Docker on top of my preferred OS.

## The Solution: Daemonless

With `podman` and `ocijail` stabilizing on FreeBSD, we can finally bridge this gap. I built **Daemonless** (named for podman's daemonless architecture) to provide a polished, "Docker-like" experience that runs natively on FreeBSD.

### Currently Available Images

* **Media Management:** Radarr, Sonarr, Prowlarr, Lidarr, Readarr, Bazarr, Jellyfin
* **Downloaders:** SABnzbd, Transmission
* **Web/Infrastructure:** nginx, Vaultwarden, Smokeping, OpenSpeedTest

## Key Technical Features

* **s6 Process Supervision:** We don't just run raw binaries as PID 1. Our base images implement **s6** to handle process supervision. This ensures no zombie processes, proper signal handling, and robust service uptime.
* **PUID/PGID Support:** Permission issues are the bane of self-hosting. We've implemented standard `PUID` and `PGID` support (using `pw` under the hood). You can map the container's internal user to your host user, so your ZFS datasets and bind mounts work without permission errors.
* **Automated CI/CD:** Reliability is key. We have a fully automated CI/CD pipeline via Github. Every image is built and tested automatically.

## Flexible Tagging Options

We know users have different needs regarding stability vs. bleeding-edge features, so our images support three distinct tags:

* **:latest** — Targets the **absolute newest application version** (upstream binary or source build). *Note: If an app requires complex, FreeBSD-specific patching that is hard to maintain outside of ports, this tag automatically aliases to* `:pkg-latest` *to ensure stability.*
* **:pkg** — Uses the **FreeBSD 'Quarterly' repo**. Best for maximum stability and well-tested packages.
* **:pkg-latest** — Uses the **FreeBSD 'Latest' repo**. A rolling release balance between stability and freshness.

## Where to find it

* **Quick Start Guide:** [https://daemonless.io/quick-start/](https://daemonless.io/quick-start/)
* **Website:** [https://daemonless.io](https://daemonless.io)
* **Available Images:** [https://daemonless.io/images/](https://daemonless.io/images/)
* **GitHub:** [https://github.com/daemonless](https://github.com/daemonless)

## A Note on .NET Apps (Radarr/Sonarr/etc.)

Currently, running .NET applications inside OCI containers on FreeBSD requires specific jail parameters (like `allow.mlock`) which aren't exposed in standard `ocijail` yet.

* We have a guide on how to apply a small patch: [Ocijail Patch Guide](https://daemonless.io/guides/ocijail-patch/)
* **Good News:** We are in contact with the upstream maintainer. Support for these parameters is part of the newly released [**OCI Runtime Specification v1.3.0**](https://github.com/opencontainers/runtime-spec/blob/main/config-freebsd.md), and native support will be landing in `ocijail` soon, rendering manual patching obsolete.

**The Goal:** I want to make "Docker on FreeBSD" as boring and reliable as it is on Linux, allowing us to use the OS we feel most at home with, without sacrificing modern tooling.
