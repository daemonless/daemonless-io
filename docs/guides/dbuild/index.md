---
title: "dbuild: The Universal Build Engine for FreeBSD OCI Containers"
description: "Master the full lifecycle of FreeBSD OCI images with dbuild. Automate native builds, cumulative integration tests, SBOM generation, and multi-arch registry pushes."
---

# dbuild

## What is dbuild?

dbuild is the primary build engine for the Daemonless project. It provides a unified interface for building, testing, and publishing FreeBSD OCI container images, ensuring consistency between local development and CI/CD environments.

It bridges the gap between modern OCI image standards and native FreeBSD Jails. By handling the complexity of `ocijail`, networking, and jail annotations automatically, `dbuild` allows you to focus on your application logic rather than system administration.

### FreeBSD Port

dbuild is available as a native FreeBSD port: [sysutils/py-dbuild](https://www.freshports.org/sysutils/py-dbuild/).

- **Maintainer**: [dtxdf@FreeBSD.org](mailto:dtxdf@FreeBSD.org)
- **FreshPorts**: [https://www.freshports.org/sysutils/py-dbuild/](https://www.freshports.org/sysutils/py-dbuild/)

## The Lifecycle

dbuild manages the entire journey of a container image through three main phases:

1. **Build**: Automatically detects `Containerfile` variants and builds native FreeBSD images using Podman.
2. **Test**: Executes [Quality Gates (CIT)](cit.md) to validate port bindings, health endpoints, and visual regressions.
3. **Publish**: Handles multi-arch tagging, registry authentication, and SBOM generation.

## Key Features

- **Multi-variant builds**: Automatically detects `Containerfile` and `Containerfile.<variant>` (e.g. `.pkg`).
- **Quality Gates**: Integrated testing that blocks registry pushes if validation fails.
- **Documentation Automation**: Renders `README.md` and `Containerfile` from `compose.yaml` metadata.
- **CI First**: Designed to run identically on local machines, GitHub Actions, and Woodpecker CI.

## Installation

dbuild is available as a native FreeBSD package:

```bash
pkg install sysutils/py-dbuild
```

## Quick Start

Jump straight into building your first FreeBSD container image by following the [Complete Workflow Guide](workflow.md).

**Build and push all variants**
```bash
dbuild build --push
```

**Initialize from a FreeBSD Port**
```bash
dbuild init --freebsd-port net-p2p/transmission
```

**Run specific tests**
```bash
dbuild test --variant pkg
```


## Next Steps

- Review the [Command Reference](commands.md) for full CLI details.
- Learn how to configure your project in the [Configuration Guide](config.md).
- Deep dive into testing with the [Quality Gates (CIT) Guide](cit.md).
- Understand the [CI/CD Pipeline](ci.md) and how to automate your builds.