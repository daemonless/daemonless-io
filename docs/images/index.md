# Container Fleet

Explore our collection of high-performance, FreeBSD-native OCI containers.

## Infrastructure

| Image | Port | Description |
|-------|------|-------------|
| [:simple-gitea: Gitea](gitea.md) | 3000 | Gitea self-hosted Git service on FreeBSD |
| [:simple-tailscale: Tailscale](tailscale.md) | None | Tailscale mesh VPN on FreeBSD |
| [:material-router-network: Traefik](traefik.md) | 80,443,8080 | Traefik reverse proxy on FreeBSD |
| [:material-hammer: Woodpecker](woodpecker.md) | None | Woodpecker CI server and agent |

## Network

| Image | Port | Description |
|-------|------|-------------|
| [:simple-adguard: AdGuard Home](adguardhome.md) | 3000 | Network-wide ads & trackers blocking DNS server on FreeBSD |
| [:simple-adguard: AdGuardHome Sync](adguardhome-sync.md) | 8080 | Sync AdGuardHome config to replica instances |

## Media Management

| Image | Port | Description | .NET |
|-------|------|-------------|------|
| [:material-music: Lidarr](lidarr.md) | 8686 | Lidarr music management on FreeBSD | :material-check: |
| [:material-eye: Overseerr](overseerr.md) | 5055 | Overseerr media request management on FreeBSD |  |
| [:material-magnet: Prowlarr](prowlarr.md) | 9696 | Prowlarr indexer management on FreeBSD | :material-check: |
| [:material-movie: Radarr](radarr.md) | 7878 | Radarr movie management on FreeBSD | :material-check: |
| [:material-television: Sonarr](sonarr.md) | 8989 | Sonarr TV show management on FreeBSD | :material-check: |
| [:material-television: Sonarr](sonarr-test.md) | 8989 | Sonarr TV show management on FreeBSD | :material-check: |

## Downloaders

| Image | Port | Description |
|-------|------|-------------|
| [:material-download-network: SABnzbd](sabnzbd.md) | 8080 | SABnzbd Usenet downloader on FreeBSD |
| [:simple-transmission: Transmission](transmission.md) | 9091 | Transmission BitTorrent client on FreeBSD |

## Media Servers

| Image | Port | Description |
|-------|------|-------------|
| [:simple-plex: Plex Media Server](plex.md) | 32400 | Plex Media Server on FreeBSD |
| [:simple-plex: Tautulli](tautulli.md) | 8181 | Tautulli Plex monitoring on FreeBSD |

## Databases

| Image | Port | Description |
|-------|------|-------------|
| [:simple-postgresql: Immich PostgreSQL](immich-postgres.md) | 5432 | PostgreSQL 14 with pgvector + VectorChord for Immich |
| [:material-database: PostgreSQL ${PG_VERSION}](postgres.md) | 5432 | PostgreSQL ${PG_VERSION} on FreeBSD |
| [:simple-redis: Redis](redis.md) | 6379 | Redis key-value store for FreeBSD |

## Photos & Media

| Image | Port | Description |
|-------|------|-------------|
| [:simple-googlephotos: Immich](immich.md) | None | Self-hosted photo and video management solution. |
| [:material-brain: Immich Machine Learning](immich-ml.md) | 3003 | Immich ML service for FreeBSD |
| [:material-server: Immich Server](immich-server.md) | 2283 | Immich photo management server for FreeBSD |

## Utilities

| Image | Port | Description |
|-------|------|-------------|
| [:material-food: Mealie](mealie.md) | 9000 | Mealie Recipe Manager on FreeBSD |
| [:simple-n8n: n8n](n8n.md) | 5678 | n8n workflow automation on FreeBSD |
| [:simple-nextcloud: Nextcloud](nextcloud.md) | 80 | Nextcloud self-hosted cloud on FreeBSD |
| [:material-speedometer: OpenSpeedTest](openspeedtest.md) | 3000 | HTML5 Network Speed Test on FreeBSD |
| [:material-view-dashboard: Organizr](organizr.md) | 80 | HTPC/Homelab Services Organizer on FreeBSD |
| [:simple-ubiquiti: UniFi](unifi.md) | 8443 | UniFi Network Application on FreeBSD |
| [:material-chart-line: Uptime Kuma](uptime-kuma.md) | 3001 | A fancy self-hosted monitoring tool on FreeBSD |
| [:simple-bitwarden: Vaultwarden](vaultwarden.md) | 80 | Vaultwarden (Bitwarden compatible backend) on FreeBSD |

## Uncategorized

| Image | Port | Description |
|-------|------|-------------|
| [:material-view-dashboard: Homepage](homepage.md) | 3000 | Homepage - A modern dashboard for your homelab |
| [:simple-jellyfin: Jellyfin](jellyfin.md) | 8096 | The Free Software Media System on FreeBSD |
| [:material-pulse: SmokePing](smokeping.md) | 80 | SmokePing network latency monitor on FreeBSD |
| [:simple-wireguard: Transmission WireGuard](transmission-wireguard.md) | 9091 | Transmission BitTorrent client with WireGuard VPN on FreeBSD |

## Image Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | Upstream releases | Newest version from project |
| `:pkg` | FreeBSD quarterly | Stable, tested in ports |
| `:pkg-latest` | FreeBSD latest | Rolling package updates |
