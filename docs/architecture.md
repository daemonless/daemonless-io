# Architecture

How daemonless container images are structured and built.

## Image Layers

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px' }}}%%
flowchart LR
    subgraph base_layer["Base Layer"]
        base["base<br/>s6, execline"]
    end

    subgraph intermediate["Intermediate Layers"]
        arr-base["arr-base<br/><small>sqlite3, icu, .NET</small>"]
        nginx-base["nginx-base<br/><small>nginx</small>"]
    end

    subgraph arr_apps[".NET Apps"]
        jellyfin["jellyfin"]
        lidarr["lidarr"]
        prowlarr["prowlarr"]
        radarr["radarr"]
        readarr["readarr"]
        sonarr["sonarr"]
    end

    subgraph nginx_apps["Nginx Apps"]
        nextcloud["nextcloud"]
        openspeedtest["openspeedtest"]
        organizr["organizr"]
        smokeping["smokeping"]
        vaultwarden["vaultwarden"]
    end

    subgraph base_apps["Direct Apps"]
        gitea["gitea"]
        immich-ml["immich-ml"]
        immich-postgres["immich-postgres"]
        immich-server["immich-server"]
        overseerr["overseerr"]
        plex["plex"]
        redis["redis"]
        sabnzbd["sabnzbd"]
        tailscale["tailscale"]
        tautulli["tautulli"]
        traefik["traefik"]
        transmission["transmission"]
        transmission-wireguard["transmission-wireguard"]
        unifi["unifi"]
        uptime-kuma["uptime-kuma"]
        woodpecker["woodpecker"]
    end

    %% Connections
    base --> arr-base
    base --> nginx-base
    arr-base --> jellyfin
    click jellyfin "../images/jellyfin/" "View jellyfin Docs"
    arr-base --> lidarr
    click lidarr "../images/lidarr/" "View lidarr Docs"
    arr-base --> prowlarr
    click prowlarr "../images/prowlarr/" "View prowlarr Docs"
    arr-base --> radarr
    click radarr "../images/radarr/" "View radarr Docs"
    arr-base --> readarr
    click readarr "../images/readarr/" "View readarr Docs"
    arr-base --> sonarr
    click sonarr "../images/sonarr/" "View sonarr Docs"
    nginx-base --> nextcloud
    click nextcloud "../images/nextcloud/" "View nextcloud Docs"
    nginx-base --> openspeedtest
    click openspeedtest "../images/openspeedtest/" "View openspeedtest Docs"
    nginx-base --> organizr
    click organizr "../images/organizr/" "View organizr Docs"
    nginx-base --> smokeping
    click smokeping "../images/smokeping/" "View smokeping Docs"
    nginx-base --> vaultwarden
    click vaultwarden "../images/vaultwarden/" "View vaultwarden Docs"
    base --> gitea
    click gitea "../images/gitea/" "View gitea Docs"
    base --> immich-ml
    click immich-ml "../images/immich-ml/" "View immich-ml Docs"
    base --> immich-postgres
    click immich-postgres "../images/immich-postgres/" "View immich-postgres Docs"
    base --> immich-server
    click immich-server "../images/immich-server/" "View immich-server Docs"
    base --> overseerr
    click overseerr "../images/overseerr/" "View overseerr Docs"
    base --> plex
    click plex "../images/plex/" "View plex Docs"
    base --> redis
    click redis "../images/redis/" "View redis Docs"
    base --> sabnzbd
    click sabnzbd "../images/sabnzbd/" "View sabnzbd Docs"
    base --> tailscale
    click tailscale "../images/tailscale/" "View tailscale Docs"
    base --> tautulli
    click tautulli "../images/tautulli/" "View tautulli Docs"
    base --> traefik
    click traefik "../images/traefik/" "View traefik Docs"
    base --> transmission
    click transmission "../images/transmission/" "View transmission Docs"
    base --> transmission-wireguard
    click transmission-wireguard "../images/transmission-wireguard/" "View transmission-wireguard Docs"
    base --> unifi
    click unifi "../images/unifi/" "View unifi Docs"
    base --> uptime-kuma
    click uptime-kuma "../images/uptime-kuma/" "View uptime-kuma Docs"
    base --> woodpecker
    click woodpecker "../images/woodpecker/" "View woodpecker Docs"

    %% Styling
    classDef baseStyle fill:#ab2b28,stroke:#333,color:#fff
    classDef intermediateStyle fill:#d35400,stroke:#333,color:#fff
    classDef appStyle fill:#2980b9,stroke:#333,color:#fff
    class base baseStyle
    class arr-base,nginx-base intermediateStyle
    class jellyfin,lidarr,prowlarr,radarr,readarr,sonarr,nextcloud,openspeedtest,organizr,smokeping,vaultwarden,gitea,immich-ml,immich-postgres,immich-server,overseerr,plex,redis,sabnzbd,tailscale,tautulli,traefik,transmission,transmission-wireguard,unifi,uptime-kuma,woodpecker appStyle
```

## Layer Descriptions

### Base Layer

The `base` image provides the foundation for all daemonless containers:

- **FreeBSD 15** (or 14) minimal base
- **s6** - Process supervision
- **execline** - Scripting language for s6
- **FreeBSD-utilities** - Core utilities

### Intermediate Layers

| Image | Purpose | Key Packages |
|-------|---------|--------------|
| **arr-base** | .NET runtime for *arr apps | sqlite3, icu, libunwind, .NET compat |
| **nginx-base** | Web server base | nginx |

### Application Layer

Final images that users run. Each inherits from either:

- `base` - Direct apps (Python, Go, Node.js apps)
- `arr-base` - .NET applications (Radarr, Sonarr, etc.)
- `nginx-base` - PHP/web applications (Nextcloud, Organizr, etc.)

## Build Order

When a base image changes, dependent images must be rebuilt:

1. **base** changes → rebuild everything
2. **arr-base** changes → rebuild *arr apps only
3. **nginx-base** changes → rebuild nginx apps only

## Image Inheritance

```
FreeBSD 15 Base
└── base (s6, execline)
    ├── arr-base (sqlite3, icu, .NET compat)
    │   ├── jellyfin
    │   ├── lidarr
    │   ├── prowlarr
    │   ├── radarr
    │   ├── readarr
    │   └── sonarr
    ├── nginx-base (nginx)
    │   ├── nextcloud
    │   ├── openspeedtest
    │   ├── organizr
    │   ├── smokeping
    │   └── vaultwarden
    ├── gitea
    ├── immich-ml
    ├── immich-postgres
    ├── immich-server
    ├── overseerr
    ├── plex
    ├── redis
    ├── sabnzbd
    ├── tailscale
    ├── tautulli
    ├── traefik
    ├── transmission
    ├── transmission-wireguard
    ├── unifi
    ├── uptime-kuma
    └── woodpecker
```

