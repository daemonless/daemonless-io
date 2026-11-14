---
title: "fjord, container labels, and REST API: Reverse Proxy"
description: "Automate HTTPS hostnames in Daemonless Reverse Proxy using fjord pairing, io.daemonless.proxy container labels, the REST API, or the built-in CLI."
---

# fjord, container labels, and API

Services do not have to be added by hand. Reverse Proxy supports three ways for apps and scripts to register and update names automatically.

---

## 1. Pairing with fjord

[fjord](https://fjord.daemonless.io) pairs with Reverse Proxy when it installs it, or links from another machine with a pairing link.

### Installing Reverse Proxy from fjord

When you install **Reverse Proxy** from fjord's App Store:

1. fjord generates `RP_PAIRING_KEY` and `RP_SETUP_TOKEN` and passes them to the container.
2. Clicking **Finish setup** in fjord opens setup already verified, without copying a token from the log.
3. After setup, fjord lists your apps that have no name yet so you can name them in one click.
4. When a container's address changes, fjord updates its target in Reverse Proxy automatically.

### Pairing additional hosts

One Reverse Proxy instance can manage names for multiple hosts:

1. In Reverse Proxy, open **Settings -> Connected apps** and click **Link an app…**.
2. Copy the pairing link and paste it into fjord (or another compatible manager) on the second host.
3. **Settings -> Connected apps** lists each app and how many names came from it. An app installed via `RP_PAIRING_KEY` can be disconnected and reconnected; apps linked with a pairing link or manual key can be revoked.

---

## 2. Names from container labels (`io.daemonless.proxy`)

Containers on the same Podman host can ask for names with labels, the way Traefik users expect, without fjord or an API key.

### Mounting Podman's socket directory

Turn label naming on by giving the proxy Podman's socket directory:

- **In `compose.yaml`:** Point `RP_PODMAN_DIR` at `/var/run/podman` on the host (`${RP_PODMAN_DIR:-/path/to/containers/reverse-proxy/podman}:/var/run/podman:ro`). Mounting the directory rather than the `.sock` file keeps the mount working across a Podman service restart. On SELinux hosts (Fedora, RHEL), keep `security_opt: [label=disable]` so the container can access the socket.
- **In fjord:** Switch **Name containers by their labels** to **On**.

!!! warning "Security note on Unix sockets"
    `:ro` on a volume mount does **not** limit a Unix socket: whoever holds `podman.sock` can control Podman. Inside Reverse Proxy, only the root `podman-labels` unit reads `/var/run/podman/podman.sock`; the web UI and API (`bsd`) never access it. You can turn names from labels off in **Settings** while the socket stays mounted.

### Labeling your containers

For a Daemonless image (or any image declaring one `EXPOSE` port), one label is enough:

```yaml { linenums="0" }
services:
  radarr:
    image: ghcr.io/daemonless/radarr:latest
    container_name: radarr
    labels:
      - io.daemonless.proxy=true
```

### Supported labels

| Label | Example | Meaning |
| :--- | :--- | :--- |
| `io.daemonless.proxy` | `true` | Names the service after the container (`radarr` becomes `radarr.<your domain>`) using the image's exposed port. |
| `io.daemonless.proxy.name` | `movies` | Uses `movies.<your domain>` instead of the container name. |
| `io.daemonless.proxy.port` | `7878` | Picks the port when the image declares none or several. |
| `io.daemonless.proxy.names` | `films,cinema` | Adds comma-separated extra names (`films.<your domain>`, `cinema.<your domain>`). |
| `io.daemonless.proxy.public` | `true` | Opens the name to the internet when your proxy uses a public domain. |
| `io.daemonless.proxy.https` | `true` | Connects to the container over HTTPS and accepts its certificate. |
| `io.daemonless.proxy.own-origin` | `true` | Sends the backend's own address in `Origin` and `Referer` (for apps like UniFi). |

### Reachability and lifecycle

- **Shared network or published port:** The proxy reaches the container on a network they share (such as the default `podman` bridge, with no port published), or else through a published port on the host, and shows which path it picked on the **Names** page.
- **Stopped and removed containers:** A stopped container keeps its name, marked **down**, for as long as it exists. A removed container (`podman-compose down` or fjord's **Stop**) keeps its name, marked **down**, for **7 days**; after 7 days gone the name is removed and stays restorable for 24 hours. Bring the container back within 7 days and the name follows its new address.
- **UI edits persist:** Labels own the name, port, and access scope (shown read-only in the UI), while trusted networks, own-origin, icon, and uptime settings edited in the UI survive `podman-compose up`.
- **Unreachable or conflicting labels:** A label the proxy cannot honor, a name already taken, or a container with no shared network or published port is listed on the **Names** page with the reason instead of guessed at.

---

## 3. Container CLI (`reverse-proxy hosts`)

Inside the container you can list, add, remove, and restore names over the internal admin socket without an API key:

```sh { linenums="0" }
# List configured names and targets
podman exec reverse-proxy reverse-proxy hosts

# Add a home-only name (probes HTTP vs HTTPS and self-signed certs)
podman exec reverse-proxy reverse-proxy hosts add radarr 192.168.1.20:7878

# Add an HTTPS backend explicitly or open a name to the internet
podman exec reverse-proxy reverse-proxy hosts add unifi 192.168.1.10:8443 --https
podman exec reverse-proxy reverse-proxy hosts add radarr-pub 192.168.1.20:7878 --internet

# Remove a name (restorable for 24 hours) and restore it
podman exec reverse-proxy reverse-proxy hosts remove radarr
podman exec reverse-proxy reverse-proxy hosts restore radarr
```

---

## 4. REST API and app integration

Anything that can make an HTTPS request can manage names through the v1 REST API.

- **OpenAPI reference:** Every running proxy serves its OpenAPI 3 specification at `https://proxy.<your domain>/api/v1/openapi.json` (or `https://<proxy-ip>:8443/api/v1/openapi.json`).
- **Scoped bearer keys:** Create a key under **Settings -> Connected apps**. A key manages names only; it cannot read DNS secrets, export backups, or change the admin password.

### `curl` example

```sh { linenums="0" }
curl -fsS https://proxy.home.lan/api/v1/hosts \
  -H "Authorization: Bearer rp_..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "radarr",
    "target": { "address": "192.168.1.20", "port": 7878 },
    "access": "home"
  }'
```

### Pairing protocol for your own app

An app that manages services, such as a jail or VM manager, can pair the same way fjord does:

1. **Get a key** in one of three ways:
    - Have the user click **Settings -> Connected apps -> Link an app…**, paste the link into your app, and redeem it once at `POST /api/v1/pair`.
    - Install the proxy with `RP_PAIRING_KEY` (32+ random characters) and optional `RP_PAIRING_NAME`, `RP_PAIRING_ID`, and `RP_PAIRING_URL`.
    - Have the user create and paste a manual bearer key.
2. **Identify your app** with `PUT /api/v1/me` so **Settings -> Connected apps** shows its name and link.
3. **Pass a `ref`** such as `<app>:<instance-id>:<service>` when creating or updating hosts so retries never create duplicates and address changes update the existing name.
