---
hide:
  - navigation
  - toc
---

<div class="hero">
  <div class="hero-content">
    <div class="hero-logo">
      <img src="assets/daemonless-logo.svg" alt="Daemonless">
    </div>
    <h1>daemonless</h1>
    <p class="hero-subtitle">Native FreeBSD OCI Containers. Jails without the System Administration.</p>
    <div class="hero-buttons">
       <a href="quick-start/" class="md-button md-button--primary">Get Started</a>
       <a href="images/" class="md-button">Explore Fleet</a>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-server-network: **Reliable Foundation**

    ---

    Built on **FreeBSD**, utilizing `s6` for robust process supervision and `ocijail` for secure isolation.

-   :material-feather: **Minimal Footprint**

    ---

    Ultra-lightweight images with cleaned package caches and minimal overhead.

-   :material-security: **Secure by Default**

    ---

    Run as any user with **PUID/PGID** support. True isolation with Jails.

-   :material-lan-connect: **Networking**

    ---

    Full port forwarding support and seamless integration with `pf` firewall.

-   :material-update: **Automated Updates**

    ---

    Automated CI/CD pipelines ensure images are built against the latest upstream releases and FreeBSD packages.

-   :material-github: **Transparent & Open**

    ---

    100% open source. Every image is built from a visible `Containerfile`.

</div>

## Quick Example

Launch your first container in seconds with a familiar syntax.

<div class="termy">

```bash
podman run -d --name radarr \
  -p 7878:7878 \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  -e PUID=1000 -e PGID=1000 \
  -v /data/config/radarr:/config \
  ghcr.io/daemonless/radarr:latest
```

</div>

## Why Daemonless?

<div class="grid cards" markdown>

-   **Philosophy**

    ---

    We believe in the power of FreeBSD Jails but understand the convenience of OCI containers. Daemonless bridges the gap.

    [:octicons-arrow-right-24: Read Philosophy](philosophy.md)

-   **Architecture**

    ---

    Understanding how Podman, ocijail, and FreeBSD kernel features work together.

    [:octicons-arrow-right-24: View Architecture](architecture.md)

-   **Community**

    ---

    Open source and community driven. Join us in building the future of FreeBSD containers.

    [:octicons-mark-github-24: GitHub](https://github.com/daemonless)

</div>
