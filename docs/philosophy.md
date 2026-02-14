---
title: "Daemonless Philosophy: Bringing Modern DevOps to FreeBSD"
description: "Discover why we built Daemonless. We are bridging the gap between the stability of FreeBSD Jails and the convenience of OCI containerization for developers."
---

# The Daemonless Philosophy

**TL;DR:** We're bringing modern OCI container workflows to the world's most stable operating system. No Linux VMs, no "sysadmin drudgery"—just native FreeBSD performance.

## The Mission

FreeBSD has always been a masterpiece of engineering. Its Jails were "containers" before the word was even popular. But as the world moved towards OCI standards and immutable infrastructure, a gap formed. Many users felt they had to choose between the **logic and cohesiveness of FreeBSD** and the **convenience of modern DevOps.**

**Daemonless exists to close that gap.**

We believe you shouldn't have to leave your "home" OS to get a world-class container experience. By leveraging `podman` and `ocijail`, we're making FreeBSD a first-class citizen in the container world.

## Our Principles

### 1. "Docker-like" Simplicity
The workflow should be boring. `podman run` should just work. You shouldn't need to be a Jails expert to run a media server, but you should still get all the benefits of the FreeBSD kernel.

### 2. Community First
A project is only as strong as its contributors. Daemonless isn't a finished product; it's an evolving ecosystem. Whether it's adding a new image to the fleet or refining our build tool, `dbuild`, every contribution helps build the foundation for others.

### 3. Native & Minimal
We don't do "garbage hacks." Our images are minimal, our process supervision (s6) is robust, and our integration with FreeBSD features like ZFS and PF is seamless. We build on the shoulders of giants.

## The Journey So Far

I've been a FreeBSD user since the late 90s and a ports committer from 2002-2010. I've seen the system evolve, and I've felt the frustration of maintaining manual Jails. Daemonless is my answer to that frustration—a way to keep the OS I love while embracing the future of software deployment.

**The Goal:** Make "Docker on FreeBSD" so reliable and accessible that it becomes the default choice for anyone who values stability and performance.

---

### Join Us
If this vision resonates with you, we'd love to have you. 
*   **Explore the Fleet:** See what we've built so far in the [Image Catalog](images/index.md).
*   **Start Building:** Learn how to create your own images with [dbuild](guides/dbuild.md).
*   **Connect:** Join our [Discord](https://discord.gg/PTg5DJ2y) and help us shape the future of FreeBSD containers.
