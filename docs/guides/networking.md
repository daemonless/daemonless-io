# Networking

FreeBSD Podman containers support several networking modes. Understanding which one to use is critical for connectivity and performance.

## Bridge Networking (Default)

The container gets its own IP address on a virtual network (usually `10.88.0.0/16`).

### Port Forwarding

```bash
podman run -d -p 7878:7878 --name radarr ghcr.io/daemonless/radarr:latest
```

Maps container port to host port. Requires pf configuration.

### Multiple Ports

```bash
podman run -d \
  -p 80:80 \
  -p 443:443 \
  -p 8080:8080 \
  --name traefik ghcr.io/daemonless/traefik:latest
```

### pf.conf Setup

Add to `/etc/pf.conf`:

```
# Podman container networking
rdr-anchor "cni-rdr/*"
nat-anchor "cni-rdr/*"
table <cni-nat>
nat on $ext_if inet from <cni-nat> to any -> ($ext_if)
nat on $ext_if inet from 10.88.0.0/16 to any -> ($ext_if)
```

Enable local filtering:

```bash
sysctl net.pf.filter_local=1
echo 'net.pf.filter_local=1' >> /etc/sysctl.conf
pfctl -f /etc/pf.conf
```

## Host Networking

The container shares the host's network stack directly. No separate IP address.

```bash
podman run -d --network=host --name unifi ghcr.io/daemonless/unifi:latest
```

### Use Cases

- Applications needing L2 network discovery (UniFi adopting APs, SmokePing)
- Avoiding NAT overhead
- Simpler setup without pf configuration

!!! note
    Port mapping (`-p`) has no effect in host mode; the application listens on the host IP directly.

| Pros | Cons |
|------|------|
| Simpler setup | Less isolation |
| No pf config needed | Port conflicts possible |
| Better performance | Container sees all host interfaces |

## VNET (Virtual Network Stack)

VNET provides a private, isolated network stack for the jail.

```bash
podman run -d --name gitea \
  --annotation 'org.freebsd.jail.vnet=new' \
  ghcr.io/daemonless/gitea:latest
```

### Use Cases

- Applications managing their own network interfaces or routing (WireGuard, Gitea)
- Higher isolation than bridge mode

### Limitations

- **Port Forwarding:** Standard `-p` mapping not supported by stock ocijail with VNET. Access via container's internal IP.
- **Kernel Support:** Requires VNET support (default in FreeBSD 13+).

## Container-to-Container Communication

Multi-container apps (like Immich) need services to find each other. FreeBSD has some limitations here compared to Linux.

### Option 1: Host Networking (Recommended)

The simplest approach today. All containers share the host network and communicate via `localhost`:

```yaml
services:
  app:
    network_mode: host
    environment:
      - DB_HOSTNAME=localhost
      - REDIS_HOSTNAME=localhost
```

| Pros | Cons |
|------|------|
| No extra setup | Port conflicts possible |
| Works out of the box | Less isolation |
| Matches Linux behavior | Services bind to host ports |

### Option 2: DNS Resolution (cni-dnsname)

The `cni-dnsname` plugin enables containers to resolve each other by name (e.g., `postgres`, `redis`). This is required for multi-container apps like Immich and Mealie when using podman-compose.

!!! warning "Not Yet in FreeBSD Ports"
    `cni-dnsname` is not in the official FreeBSD ports tree. Use our port from [daemonless/freebsd-ports](https://github.com/daemonless/freebsd-ports).

#### Installation

```bash
# Clone the ports overlay
git clone https://github.com/daemonless/freebsd-ports.git /usr/local/daemonless-ports

# Build and install
cd /usr/local/daemonless-ports/net/cni-dnsname
make install clean
```

#### Verify Installation

```bash
ls /usr/local/libexec/cni/dnsname
# Should exist
```

With cni-dnsname installed, containers can resolve each other by name:

```bash
# From inside one container, reach another by name
ping immich_postgres
curl http://immich_server:2283
```

### Option 3: Static IPs

Look up or assign container IPs and use them directly:

```bash
podman inspect -f '{{.NetworkSettings.IPAddress}}' radarr
```

Or create a network with static IPs in your compose file. More complex but avoids both host networking and dnsname.

## Comparison Summary

| Feature | Bridge (Default) | Host | VNET |
|---------|------------------|------|------|
| **IP Address** | Private (10.88.x.x) | Shared with Host | Private (10.88.x.x) |
| **Port Mapping** | Supported (`-p`) | Not needed | Not supported |
| **Isolation** | High | Low | Very High |
| **Best For** | Most Apps | Network Discovery | VPNs / High Isolation |
| **pf Required** | Yes | No | Yes |
