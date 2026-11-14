---
title: "Certificates, DNS providers, and access control: Reverse Proxy"
description: "How Daemonless Reverse Proxy handles name-constrained local root CAs, Let's Encrypt DNS-01 wildcard certificates across 10 DNS providers, LAN/VPN/VLAN access rules, and short links."
---

# Certificates, DNS, and access control

Daemonless Reverse Proxy gives every service an HTTPS certificate without opening ports `80` or `443` to the internet unless you choose to. You can switch between private home names and Let's Encrypt certificates anytime under **Settings -> Ending and certificates**.

---

## Choosing a certificate mode

| Mode | Example name | Device setup | Internet required? | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Just for home** | `radarr.home.lan` | Trust once per device (QR or command) | **No** | Works offline with no external account |
| **A free name from DuckDNS** | `radarr.you.duckdns.org` | **None** | Outbound DNS-01 renewal | Publicly trusted without buying a domain |
| **Your own domain** | `radarr.example.com` | **None** | Outbound DNS-01 renewal | Custom domain with one wildcard certificate |

---

## Mode 1: *Just for home* (name-constrained root CA)

When you pick a private ending (`apps.lan`, `home.arpa`, `home.lan`), Reverse Proxy generates its own root certificate authority inside `/config/secrets/`.

- **Restricted by X.509 `nameConstraints`:** The root certificate carries X.509 name constraints limiting it to your chosen ending, such as `.home.lan`. Browsers and operating systems reject it for any site outside that ending.
- **Included in backups:** Backups (`.rpbk`) include the root CA keypair. Restoring a backup onto a new machine keeps existing trust working on your phones and computers.
- **Non-default HTTP port:** If host port `80` is mapped to another port, set `RP_TRUST_PORT=<port>` so the `/trust` page's QR code and commands use that port.

---

## Modes 2 and 3: Let's Encrypt wildcard certificates (DNS-01)

With **DuckDNS** or **Your own domain**, Reverse Proxy uses ACME **DNS-01** challenges compiled into its Caddy binary:

1. **No inbound port forwarding required:** Domain control is proven by setting a temporary `_acme-challenge` TXT record through your DNS provider's API, so your router does not need ports `80` or `443` open from the internet.
2. **One wildcard covers every app:** The proxy requests one wildcard certificate (`*.<your domain>`) for every name under it, so app names do not appear in public certificate logs one by one.
3. **Tested on staging first:** When you enter a DNS token, the proxy checks its shape and tests it against **Let's Encrypt's staging service** before requesting the live certificate, avoiding rate limits on a bad token.
4. **Keeps the UI reachable if a token expires:** If a saved DNS token is later rejected by Caddy at startup, the proxy falls back to internal certificates so the admin UI stays reachable and explains how to replace the token.

### Supported DNS providers and permissions

All 10 providers below are compiled into the container's Caddy binary:

| Provider | Auto-detected by NS? | Fields in UI | Required token or key permissions |
| :--- | :--- | :--- | :--- |
| **Cloudflare** | Yes (`ns.cloudflare.com`) | `API token` | Make an API token from the **Edit zone DNS** template (**Zone -> DNS -> Edit**) scoped to the specific zone. |
| **Amazon Route 53** | Yes (`awsdns-`) | `Access key ID`, `Secret access key`, `Region` *(optional)* | IAM user or key allowed to change records in the hosted zone (`route53:ChangeResourceRecordSets`, `ListHostedZones`). |
| **DuckDNS** | Built-in (`*.duckdns.org`) | `Token` | Your 36-character token shown next to `token` at the top of [duckdns.org](https://www.duckdns.org). |
| **deSEC** | Yes (`desec.io`, `desec.org`) | `Token` | Token created under [Token management](https://desec.io/tokens). |
| **Porkbun** | Yes (`porkbun.com`) | `API key` (`pk1_...`), `Secret key` (`sk1_...`) | Make an API key at [porkbun.com/account/api](https://porkbun.com/account/api), then switch on **API access** for the domain on its details page. |
| **Hetzner** | Yes (`hetzner.com`, `hetzner.de`, `your-server.de`) | `API token` | API token created in the DNS console settings at [dns.hetzner.com/settings/api-token](https://dns.hetzner.com/settings/api-token). |
| **OVH** | Yes (`ovh.net`, `anycast.me`) | `Endpoint` (e.g. `ovh-eu`), `Application key`, `Application secret`, `Consumer key` | API keys created at [ovh.com/auth/api/createToken](https://www.ovh.com/auth/api/createToken) with `GET`, `PUT`, `POST`, and `DELETE` rights on `/domain/zone/*`. |
| **Gandi** | Yes (`gandi.net`) | `Personal access token` | Personal access token for the organization that owns the domain, allowed to manage domain name technical configurations. |
| **My own DNS server (RFC 2136)** | Manual selection | `Server` (`ns1.example.com:53`), `Key name`, `Key algorithm` (`hmac-sha256`), `Key` | A TSIG key the server accepts dynamic updates with (BIND, PowerDNS, Knot). |
| **acme-dns** | Manual selection | `Server`, `Username`, `Password`, `Subdomain` | Account returned when you registered with `acme-dns`; point `_acme-challenge` under your domain at that account's name with a CNAME record. |

---

## Who can open what

### Home network only vs internet

Every name defaults to **Home network only**:

- **Home network** includes private IPv4 ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) plus any subnets you add under **Settings -> Home network**.
- **Adding a VPN:** Add a VPN range such as `100.64.0.0/10` for Tailscale under **Settings -> Home network** so VPN devices can open home-only names.
- **Opening specific apps to the internet:** When using a public domain and forwarding port `443` on your router, you can open individual names to the internet. Outsiders asking for any home-only or unconfigured name get nothing back, not even a "not found" page; on the home network, a name nobody set up shows a 404 page saying so.

### Multi-VLAN hosts and listening networks

When the proxy container is attached to several networks or VLANs:

- Open **Settings -> Home network** to tick which attached networks the proxy answers on.
- On an unticked network the proxy does not answer, and its devices are never treated as home whatever your router does, while the proxy still reaches backend apps on that network.
- You can also view or set listening networks from the command line or `RP_LISTEN` in `compose.yaml`:

```sh { linenums="0" }
# List attached networks and mark (*) which ones the proxy answers on
podman exec reverse-proxy reverse-proxy listen

# Answer only on one subnet
podman exec reverse-proxy reverse-proxy listen 192.168.1.0/24

# Answer on all attached networks again
podman exec reverse-proxy reverse-proxy listen all
```

---

## Per-app routing options

When adding or editing a name, optional settings handle apps with extra requirements:

- **Extra names (`extraNames`):** Give the same app more than one name, such as `movies.home.lan` and `cinema.home.lan`.
- **HTTPS backend and self-signed certificates:** Detected automatically when probing `address:port`, or switched on manually when an app serves HTTPS with its own certificate, such as **UniFi** or **Proxmox**.
- **The service expects its own address (`ownOrigin`):** Sends the backend's own address in `Origin` and `Referer` headers for apps such as **UniFi** that refuse a sign-in coming from another hostname.
- **Short links (`go/<name>`):** Configured under **Settings -> Short links**. Change the word from `go` to another word, or turn short links off.
