---
title: "Quick Start Guide: Deploy FreeBSD Containers in 5 Minutes"
description: "Get started with Podman on FreeBSD. This guide walks you through host configuration, pf firewall setup, and deploying your first daemonless container in minutes."
placeholders:
  REGISTRY:
    default: "GitHub Container Registry"
    description: "Container Registry"
  INTERFACE:
    default: "em0"
    description: "Network Interface"
  PUID:
    default: "1000"
    description: "User ID"
  PGID:
    default: "1000"
    description: "Group ID"
  CONTAINER_CONFIG_ROOT:
    default: "/path/to/containers"
    description: "Config Path"
---

# Quick Start

Get daemonless containers running on FreeBSD in 5 minutes.

!!! tip "Customize Your Guide"
    Scroll to [Interactive Configuration](#interactive-configuration) at the bottom to set your PUID, PGID, and paths. All commands will update automatically.

## Podman

### Prerequisites

!!! failure "Root Privileges Required"
    **Podman on FreeBSD currently requires root.** Rootless mode is not yet supported. All commands in this guide must be run as root (or via `sudo`/`doas`).

Install Podman and container networking:

```bash
pkg install podman-suite
```

!!! warning "ocijail Patch Required"
    Currently, a temporary patch for `ocijail` is required for .NET applications (Radarr/Sonarr). 
    See [ocijail patch](ocijail-patch.md).

### Host Configuration

#### 1. Enable Networking
Configure the kernel to allow packet filtering for local traffic and ensure `fdescfs` is mounted.

```bash
# Enable pf filtering for jails
sysctl net.pf.filter_local=1
echo 'net.pf.filter_local=1' >> /etc/sysctl.conf

# Mount fdescfs
mount -t fdescfs fdesc /dev/fd
echo 'fdesc /dev/fd fdescfs rw 0 0' >> /etc/fstab
```

#### 2. Configure Firewall (`pf.conf`)
Add the following to `/etc/pf.conf`. Replace `@INTERFACE@` if your external interface is different.

```
# Primary network interface
ext_if=@INTERFACE@

# Podman container networking
rdr-anchor "cni-rdr/*"
nat-anchor "cni-rdr/*"
table <cni-nat>
nat on $ext_if inet from <cni-nat> to any -> ($ext_if)
nat on $ext_if inet from 10.88.0.0/16 to any -> ($ext_if)
```

Reload the configuration:
```bash
pfctl -f /etc/pf.conf
```

#### 3. Start Podman

```bash
sysrc podman_enable=YES
service podman start
```

### Run Your First Container

We'll start with **Tautulli**, a lightweight Python app that doesn't require special permissions.

```bash
podman run -d --name tautulli \
  -p 8181:8181 \
  -e PUID=@PUID@ -e PGID=@PGID@ \
  -v @CONTAINER_CONFIG_ROOT@/tautulli:/config \
  @REGISTRY@/tautulli:latest
```

Check the status:
```bash
podman ps
podman logs -f tautulli
```
Access the UI at: `http://localhost:8181`

### .NET Applications
Applications like **Radarr** and **Sonarr** require the `allow.mlock` jail annotation to function correctly on FreeBSD.

```bash
podman run -d --name radarr \
  -p 7878:7878 \
  --annotation 'org.freebsd.jail.allow.mlock=true' \
  -e PUID=@PUID@ -e PGID=@PGID@ \
  -v @CONTAINER_CONFIG_ROOT@/radarr:/config \
  @REGISTRY@/radarr:latest
```

### Advanced Setup (Optional)

=== "ZFS Storage"
    If you're using ZFS, configure Podman to use it for proper copy-on-write layering and snapshot support:
    ```bash
    zfs create -o mountpoint=/var/db/containers/storage <pool>/podman
    ```
    See [ZFS Storage](zfs.md) for `storage.conf` tuning.

=== "Container DNS"
    To use container names as hostnames (e.g. `postgres`), the `cni-dnsname` plugin is required.
    ```bash
    # Clone the ports overlay
    git clone https://github.com/daemonless/freebsd-ports.git /usr/local/daemonless-ports
    
    # Build and install
    cd /usr/local/daemonless-ports/net/cni-dnsname
    make install clean
    ```
    See [Networking Guide](networking.md) for details.

## AppJail

### Prerequisites

!!! warning
    This quick start guide is intended exclusively for OCI container users. For more general information, see the [AppJail Handbook](https://appjail.readthedocs.io), `appjail-tutorial(7)`, `director(1)` and `director-spec(5)` man pages.

!!! warning
    If you plan to use ZFS, set it up before running AppJail. See below for details.

Install AppJail and Director

```bash
pkg install -y appjail sysutils/py-director
```

### Host Configuration

#### 0. Configure trusted users (optional)

AppJail requires privileges to run, but it can be integrated with tools such as [security/doas](https://freshports.org/security/doas) to run it as a user without root privileges. This is recommended when you are the only person using the computer and have privileges, or in cases where there are more than two sysadmins or developers on the same server with root access.

**/usr/local/etc/doas.conf**:

```
permit nopass keepenv :appjail as root cmd appjail
```

This rule also assumes that you have a group named `appjail`. If you don't, don't worry:

```bash
pw groupadd -n appjail
```

To add your user to the `appjail` group simply run the following:

```bash
pw groupmod -n appjail -m "$USER"
```

Where `$USER` is your user. For these changes to take effect, you must log back into the system if you are adding yourself.

Similarly, there is a variant for `appjail-config` named `appjail-config-user`. The instructions for using it are similar to the above:

```
permit nopass :appjail as root cmd appjail-config
```

To test the changes above, simply run the following as a non-root user:

```bash
appjail help
appjail-config-user help
```

See also: [Trusted Users on AppJail Handbook](https://appjail.readthedocs.io/en/latest/trusted-users/).

#### 1. Enable Networking

!!! tip
    Not all network options require packet filtering (for example: aliasing, bridge-only, vnet-only, etc.), but it is particularly useful for Virtual Networks, a common network option in deployments.

AppJail does not require any configuration, as it uses the default settings, but we recommend that you at least configure the `EXT_IF` parameter to point to your external interface.

**/usr/local/etc/appjail/appjail.conf**:

```
EXT_IF=@INTERFACE@
```

NAT and port forwarding require IP forwarding, so let's set it up:

```bash
sysrc gateway_enable="YES"
sysctl net.inet.ip.forwarding=1
```

#### 2. Configure Firewall (pf.conf)

AppJail uses anchors like other applications that use `pf(4)` as a backend. Just enable `pf(4)` in your `rc.conf(5)`, put the anchors in the `pf.conf(5)` file and reload the rules.

```bash
# Enable pf(4):
sysrc pf_enable="YES"
sysrc pflog_enable="YES"
# Put the anchors in pf.conf(5):
cat << "EOF" >> /etc/pf.conf
nat-anchor "appjail-nat/jail/*"
nat-anchor "appjail-nat/network/*"
rdr-anchor "appjail-rdr/*"
EOF
# Reload the pf(4) rules:
service pf reload
# Or restart the rc(8) script if you don't have pf(4) started:
service pf restart
service pflog restart
```

See also: [Packet Filter on AppJail Handbook](https://appjail.readthedocs.io/en/latest/networking/packet-filter/).

#### 3. Start AppJail

If you want to start your jails at startup, enable AppJail's `rc(8)` script:

```
sysrc appjail_enable=YES
```

### .NET Applications

In an `appjail-template(5)` file, you can define any `jail(8)` parameter, including the one used by .NET applications.

### Run Your First Container

Let's deploy a simple web application.

```console
# mkdir -p -- "@CONTAINER_CONFIG_ROOT@/tautulli"
# appjail oci run \
    -d \
    -u root \
    -o overwrite=force \
    -o virtualnet=":<random> default" \
    -o nat \
    -o expose="8181:8181" \
    -o container="args:--pull" \
    -o ephemeral \
    -o fstab="@CONTAINER_CONFIG_ROOT@/tautulli /config" \
    -e PUID=@PUID@ \
    -e PGID=@PGID@ \
        @REGISTRY@/tautulli:latest tautulli
...
[00:00:54] [ info  ] [tautulli] Detached: pid:97368, log:jails/tautulli/container/2026-03-22.log
# appjail jail list -j tautulli
STATUS  NAME      ALT_NAME  TYPE   VERSION       PORTS  NETWORK_IP4
UP      tautulli  -         thick  15.0-RELEASE  -      10.0.0.3
# appjail jail list -j tautulli name container_pid
NAME      CONTAINER_PID
tautulli  97368
# appjail logs tail jails/tautulli/container/2026-03-22.log -f
2026-03-22 04:49:07 - ERROR :: MainThread : Tautulli PlexTV :: PlexTV called, but no token provided.
2026-03-22 04:49:07 - ERROR :: MainThread : Tautulli PlexTV :: PlexTV called, but no token provided.
2026-03-22 04:49:08 - INFO :: MainThread : Tautulli WebStart :: Initializing Tautulli web server...
2026-03-22 04:49:08 - WARNING :: MainThread : Tautulli WebStart :: Web server authentication is disabled!
2026-03-22 04:49:08 - INFO :: MainThread : Tautulli WebStart :: Thread Pool Size: 10.
2026-03-22 04:49:08 - INFO :: MainThread : Tautulli WebStart :: Starting Tautulli web server on http://0.0.0.0:8181/
/app/tautulli/lib/cherrypy/process/servers.py:410: UserWarning: Unable to verify that the server is bound on 8181
  warnings.warn(msg)
2026-03-22 04:49:13 - INFO :: MainThread : [22/Mar/2026:04:49:13] ENGINE Serving on http://0.0.0.0:8181
2026-03-22 04:49:18 - INFO :: MainThread : Tautulli is ready!
```

Access the UI at `http://10.0.0.3:8181`

**Notes**:

1. `-d`: The process will run in the background.
2. `-u root`: We run `s6` as root, but keep in mind that the process is already running as the `bsd` user inside the jail, which is also mapped based on the `PUID` and `PGID` environment variables. We recommend specifying the user explicitly. See [this pr](https://github.com/daemonless/dbuild/pull/7) for more details.
3. `-o overwrite=force`: Destroy the jail if it already exists, so that AppJail will recreate it instead of refusing to do so.
4. `-o virtualnet=":<random> default" -o nat -o expose="8181:8181"`: Network options. In this case, we chose to use Virtual Networks.
5. `-o container="args:--pull"`: Let's pull the image every time `buildah(1)` detects changes, so that AppJail always runs the jail using the latest image.
6. `-o ephemeral`: Mark this jail as ephemeral, so that when it stops (or starts, in the event of a power outage on the computer), AppJail will destroy it.
7. `@REGISTRY@/tautulli:latest tautulli`: The image, tag, and the jail name. The tag is optional.

### AppJail Director

Although you can use AppJail exclusively to deploy containers, it is recommended that you use AppJail Director. Environment variables set by `appjail-oci(1)` `run` will not be preserved after restarting the jail. You can use various `appjail-oci(1)` subcommands, such as `set-user`, `set-env`, etc., and then run the `from` subcommand, but this does not scale well when there are multiple containers. Another advantage is that Director defines its deployment file in YAML format declaratively, so it can be easily shared.

For example, the above deployment can easily be translated into a Director file:

**appjail-director.yml**:

```yaml
options:
  - virtualnet: ':<random> default'
  - nat:
services:
  tautulli:
    name: tautulli
    options:
      - expose: '8181:8181'
      - container: 'boot args:--pull'
    oci:
      user: root
      environment:
        - PUID: @PUID@
        - PGID: @PGID@
    volumes:
      - config: /config
volumes:
  config:
    device: '@CONTAINER_CONFIG_ROOT@/tautulli'
```

**Makejail**:

```
ARG tag=latest

OPTION overwrite=force
OPTION from=@REGISTRY@/tautulli:${tag}
```

**.env**:

```
DIRECTOR_PROJECT=tautulli
```

By default, `director(1)` uses `Makejail` (which is assumed to be in the same directory as the Director file) as its `appjail-makejail(5)` and executes it. Some options are defined in a `appjail-makejail(5)` file, while others are defined per service. The convention is to specify options that do not change frequently in a `appjail-makejail(5)` file and the rest per service in the Director file. You can also set parameters using `ARG`, as we did above to specify the image tag, whose default value is `latest`. Finally, we define a `.env` file with environment variables loaded by Director.

**Console**:

```
# appjail-director up
Starting Director (project:tautulli) ...
Creating tautulli (tautulli) ... Done.
 - Configuring the user (OCI) ... Done.
 - Configuring the environment (OCI):
   - PUID ... Done.
   - PGID ... Done.
Starting tautulli (tautulli) ... Done.
Finished: tautulli
# appjail-director info
tautulli:
 state: DONE
 last log: /root/.director/logs/2026-03-22_19h02m04s
 locked: false
 services:
  + tautulli (tautulli)
# ls /root/.director/logs/2026-03-22_19h02m04s/tautulli/
makejail.log		oci-environment.log	oci-user.log		start.log
# tail -1 /root/.director/logs/2026-03-22_19h02m04s/tautulli/start.log
[00:00:05] [ info  ] [tautulli] Detached: pid:83091, log:jails/tautulli/container/2026-03-22.log
```

### Advanced Setup (Optional)

=== "ZFS Storage"
    To enable ZFS, simply add `ENABLE_ZFS=1` to your `appjail.conf(5)` file. You may also need to configure `ZPOOL`, `ZROOTFS`, and `ZOPTS` if the default values do not suit your environment.

    See also: [ZFS on AppJail Handbook](https://appjail.readthedocs.io/en/latest/ZFS/).

=== "Container DNS"
    AppJail copies `DEFAULT_RESOLV_CONF` to the jail's `resolv.conf(5)` file, whose default value is `/etc/resolv.conf`. Since this file can be modified by many programs, it is recommended that you configure a custom `resolv.conf(5)` file in a more stable location, such as `/usr/local/etc/appjail/resolv.conf`.

    **/usr/local/etc/appjail/appjail.conf**:

    ```
    DEFAULT_RESOLV_CONF=/usr/local/etc/appjail/resolv.conf
    ```

    AppJail can be integrated with a third-party DNS server, and we can configure that server to read a `hosts(5)` file modified by `appjail-dns(8)`. Our first-class citizen is `dns/dnsmasq`, so let’s set it up. Before doing so, keep in mind that our `resolv.conf(5)` must point to an IP address where DNSMasq can receive packets, but the problem is that if we use a dynamic IP address, this can be problematic. To create a more deterministic environment, we’ll create an `if_tap(4)` interface and set a static IP address, so that our jails point to DNSMasq using that IP address.

    ```bash
    sysrc cloned_interfaces="tap0"
    sysrc ifconfig_tap0_name="ajdns"
    sysrc ifconfig_ajdns="inet 172.0.0.1/32"
    service netif cloneup
    service netif start ajdns
    ```

    **/usr/local/etc/appjail/resolv.conf**:

    ```
    nameserver 172.0.0.1
    ```

    Let's configure DNSMasq and `appjail-dns` rc script.

    ```bash
    sysrc appjail_dns_enable="YES"
    sysrc dnsmasq_enable="YES"
    sysrc dnsmasq_conf="/usr/local/share/appjail/files/dnsmasq.conf"
    touch /var/tmp/appjail-hosts
    service dnsmasq start
    service appjail-dns start
    cp /usr/local/etc/appjail/resolv.conf /etc/resolv.conf
    chflags schg /etc/resolv.conf
    ```

    To test our configuration, simply use a jail's name as the hostname and try to resolve it using a tool like `host(1)`.

    ```console
    # host tautulli
    tautulli has address 10.0.0.3
    ```

    If you've created a jail and then run `host(1)` before the `appjail-dns` rc script detects the changes, you may receive an `NXDOMAIN` error. If you don't want to wait, simply restart the `appjail-dns` rc script.

    ```console
    # service appjail-dns restart
    Stopping appjail_dns.
    Waiting for PIDS: 89362.
    AppJail log file (DNS): /var/log/appjail.log
    Starting appjail_dns.
    # host tautulli
    tautulli has address 10.0.0.3
    ```

    !!! note
        Please note that this only works with Virtual Networks.

    See also: [DNS on AppJail Handbook](https://appjail.readthedocs.io/en/latest/networking/DNS/).

---

## Interactive Configuration

<div class="placeholder-settings-panel"></div>

## Next Steps
- [Available Images](../images/index.md) — Full image fleet
- [Permissions](permissions.md) — Understanding PUID/PGID
- [Networking](networking.md) — Port forwarding vs host network
