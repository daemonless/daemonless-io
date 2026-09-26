---
title: "Virus Scanning for Stalwart Mail with ClamAV on FreeBSD"
description: "Scan incoming mail for viruses by connecting Stalwart to ClamAV's milter. Both run as daemonless containers on FreeBSD; infected messages are rejected during the SMTP session."
---

# Stalwart + ClamAV

This guide adds virus scanning to a [Stalwart](../images/stalwart.md) mail server
with the [ClamAV](../images/clamav.md) image. Infected messages are rejected while
the sender is still connected, so they never reach a mailbox.

## How it fits together

The ClamAV image runs three services:

| Service | Port | Role |
|---|---|---|
| `clamd` | `3310` | The scanning engine; holds the signatures in memory |
| `clamav-milter` | `7357` | Speaks the milter protocol that Stalwart uses for filters |
| `freshclam` | none | Keeps the signatures current and tells clamd to reload |

Stalwart hands each incoming message to `clamav-milter` at the SMTP `DATA`
stage. The milter scans it through clamd and answers:

- **Clean:** the message is accepted, with `X-Virus-Scanned` and
  `X-Virus-Status: Clean` headers added.
- **Infected:** Stalwart rejects the message with
  `503 5.5.3 Message rejected.`, and ClamAV logs
  `Message from <...> to <...> infected by <signature>`. Attachments are
  scanned too, not just the message body.
- **Scanner unavailable:** Stalwart defers the message with
  `451 4.3.5 Unable to accept message at this time.`, so the sending server
  retries later instead of the mail arriving unscanned.

## Requirements

- **Memory:** clamd keeps every signature in RAM, about 1.4 GB, and briefly
  holds a second copy while it reloads after an update. Plan for a few GB.
- **Container DNS:** Stalwart reaches ClamAV by its container name. On FreeBSD
  that needs container name resolution; see
  [Networking](networking.md). Without it, use the ClamAV container's IP
  address instead of `clamav` below.

## 1. Run both containers

Save as `compose.yaml`:

```yaml
name: mail

services:
  clamav:
    image: @REGISTRY@/clamav:latest
    container_name: clamav
    restart: always
    environment:
      - PUID=@PUID@
      - PGID=@PGID@
      - TZ=UTC
    volumes:
      - @CONTAINER_CONFIG_ROOT@/clamav:/config
    # No published ports: only Stalwart talks to ClamAV, over the compose
    # network. clamd and the milter have no authentication.

  stalwart:
    image: @REGISTRY@/stalwart:latest
    container_name: stalwart
    restart: always
    environment:
      - TZ=UTC
      - ADMIN_SECRET=changeme
      - ENABLE_V4PROXY=true
    volumes:
      - @CONTAINER_CONFIG_ROOT@/stalwart:/config
    ports:
      - "25:25"
      - "465:465"
      - "587:587"
      - "993:993"
      - "443:443"
      - "8080:8080"
    depends_on:
      - clamav
```

```bash
mkdir -p @CONTAINER_CONFIG_ROOT@/clamav @CONTAINER_CONFIG_ROOT@/stalwart
podman-compose up -d
```

## 2. Wait for the first signature download

On its first start, `freshclam` downloads the full signature database (a few
hundred MB) into `@CONTAINER_CONFIG_ROOT@/clamav/db`. clamd and the milter wait for it:

```bash
podman logs -f clamav
```

It's ready once you see `[clamav-milter] starting on port 7357`. Later restarts
reuse the downloaded database and come up in seconds.

!!! warning "Keep `/config` persistent"
    ClamAV's mirrors rate-limit hosts that download the whole database
    repeatedly. Recreating the container with an empty `/config` each time will
    eventually get you temporarily blocked.

## 3. Make Stalwart listen on IPv4

!!! warning "Stalwart 0.16 listens on IPv6 only on FreeBSD"
    A fresh Stalwart 0.16 creates its listeners (SMTP, IMAP, submission, ...)
    bound to `[::]` only. On Linux that also accepts IPv4, but FreeBSD
    containers keep `net.inet6.ip6.v6only=1`, so **nothing answers on IPv4**
    and mail sent to your published port 25 never arrives. Add an IPv4 bind to
    each listener you use.

In the web admin, edit each listener and add the IPv4 address next to the
IPv6 one (for SMTP: `0.0.0.0:25` alongside `[::]:25`). Or do it with
[`stalwart-cli`](https://stalw.art/docs/management/cli), for example for SMTP:

```bash
echo '{"@type":"upsert","object":"NetworkListener","matchOn":["name"],"value":{"smtp":{"name":"smtp","bind":{"[::]:25":true,"0.0.0.0:25":true},"protocol":"smtp","tlsImplicit":false}}}' |
  stalwart-cli --url http://your-host:8080 --user admin@your-domain apply --stdin
```

Restart the Stalwart container afterwards so the new binds take effect.

## 4. Add the milter in Stalwart

If Stalwart is new, finish its setup wizard first (see the
[Stalwart image page](../images/stalwart.md)). Then in the web admin, open
**Settings › MTA › Filters › Milters** and add a milter:

| Field | Value |
|---|---|
| Hostname | `clamav` |
| Port | `7357` |
| Stages | `data` only |
| Use TLS | off (the connection stays on the container network) |
| Temp-fail on error | on (the default: defer mail if ClamAV is down) |

Leave the timeouts and protocol version at their defaults, and save.

Only the `data` stage matters for virus scanning: that's the stage where
Stalwart passes the message body to the milter.

The same milter with `stalwart-cli`:

```bash
echo '{"@type":"create","object":"MtaMilter","value":{"clamav":{"hostname":"clamav","port":7357,"stages":{"data":true},"tempFailOnError":true,"useTls":false}}}' |
  stalwart-cli --url http://your-host:8080 --user admin@your-domain apply --stdin
```

## 5. Test it

Send a message containing the [EICAR test string](https://www.eicar.org/download-anti-malware-testfile/)
from **another host**. It's a harmless file every antivirus flags. With
[swaks](https://github.com/jetmore/swaks):

```bash
swaks --to you@your-domain --server mail.your-domain \
  --body 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
```

The server should answer `503 5.5.3 Message rejected.`, and ClamAV should
log the hit:

```bash
podman logs clamav | grep infected
```

A normal message goes through and arrives with an `X-Virus-Status: Clean`
header.

## Tuning

The milter's settings are in `@CONTAINER_CONFIG_ROOT@/clamav/clamav-milter.conf`,
written on first start. Edit it and restart the container.

| Option | Image default | Notes |
|---|---|---|
| `OnInfected` | `Reject` | ClamAV's own default is `Quarantine`; this image uses `Reject` because the milter quarantine action isn't handled the same way by every MTA |
| `OnFail` | `Defer` | What to do if clamd can't scan: `Defer` (retry later), `Accept` or `Reject` |
| `AddHeader` | `Replace` | Adds `X-Virus-Status` and replaces any the sender forged |
| `MaxFileSize` | 100 MB | Larger messages pass through **unscanned**. Keep it at least as large as Stalwart's maximum message size |

The full list of options is in `/usr/local/etc/clamav-milter.conf.sample` inside
the container.
