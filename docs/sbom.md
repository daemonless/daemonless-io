---
title: "Software Bill of Materials (SBOM) for Daemonless Images"
description: "Every Daemonless container ships a complete SBOM in CycloneDX and SPDX formats — embedded in the image and signed as a registry attestation."
---

# Software Bill of Materials (SBOM)

Every Daemonless image ships with a complete Software Bill of Materials — a
full inventory of everything inside it — in the two industry-standard formats:

- **CycloneDX 1.6** (JSON)
- **SPDX 2.3** (JSON)

Each document lists both halves of the image:

- **FreeBSD packages** (base system + runtime), from `pkg`, with versions and
  licenses.
- **Application dependencies** (Node, Python, .NET, Go, Rust, …), each with its
  package URL (purl) and version.

## Tools you'll need

- **Embedded copy:** nothing beyond `podman` or `docker` — the same tool you
  already use to pull the image.
- **Registry attestation:** [`cosign`](https://docs.sigstore.dev/cosign/system_config/installation/)
  (the Sigstore CLI). Install it with `brew install cosign`, or grab a binary
  from the [releases page](https://github.com/sigstore/cosign/releases).

## Where to find it

Every image carries its SBOM in **two** places.

### 1. Inside the image

The CycloneDX and SPDX documents are baked into the image filesystem under
`/usr/share/sbom/` (following FreeBSD's own convention). Read them without
running the application by overriding the entrypoint:

```bash
# List the embedded SBOMs
podman run --rm --entrypoint '' ghcr.io/daemonless/radarr:pkg \
  ls /usr/share/sbom/

# Print one
podman run --rm --entrypoint '' ghcr.io/daemonless/radarr:pkg \
  cat /usr/share/sbom/radarr-pkg-cyclonedx.json
```

Or copy the whole directory out without starting the container:

```bash
cid=$(podman create ghcr.io/daemonless/radarr:pkg)
podman cp "$cid":/usr/share/sbom/ ./sbom/
podman rm "$cid"
```

The same commands work with `docker` — it's just files in the image.

### 2. Signed attestation in the registry

Each pushed image also has its SBOM attached in the registry as a
[Sigstore](https://www.sigstore.dev/) **cosign attestation**. amd64 images
are signed keylessly (no long-lived keys); aarch64 images are built on our own
native arm64 runner and signed with the daemonless key. This is the format
enterprise supply-chain tooling expects. Download it (no verification flags
needed):

```bash
cosign download attestation ghcr.io/daemonless/radarr:pkg
```

To *verify* the signature as well, keyless verification requires the identity
that signed it — the GitHub Actions workflow — and the OIDC issuer:

```bash
cosign verify-attestation --type cyclonedx \
  --certificate-identity-regexp 'https://github.com/daemonless/.+' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  ghcr.io/daemonless/radarr:pkg
```

aarch64 images (`-aarch64` tags) are verified against the daemonless public
key, [cosign.pub](https://daemonless.io/cosign.pub). They are stored in the
newer Sigstore bundle format, so use cosign 3 or later:

```bash
cosign verify-attestation --type cyclonedx \
  --key https://daemonless.io/cosign.pub \
  ghcr.io/daemonless/base:15.1-aarch64
```

## CVE coverage

The application-layer components carry standard purls (`pkg:npm/…`,
`pkg:pypi/…`, `pkg:golang/…`, `pkg:cargo/…`), so vulnerability scanners such
as Grype and Dependency-Track match CVEs against them automatically.

FreeBSD packages are listed with a `pkg:generic` purl. They parse cleanly in
any tool, but note: **no public vulnerability feed is currently keyed to
FreeBSD packages** in these scanners, so the FreeBSD layer will not
auto-correlate CVEs regardless of format. This is an ecosystem gap, not a
limitation of the SBOM itself.

## Standards & compliance

CycloneDX and SPDX are the two ISO-recognized SBOM standards. Shipping both,
signed and attached to each image, is aligned with the SBOM/attestation
expectations of frameworks like the EU Cyber Resilience Act (CRA) and typical
enterprise procurement checklists.
