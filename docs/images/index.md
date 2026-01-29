---
title: "Container Fleet: 30+ Native FreeBSD OCI Images"
description: "Browse all daemonless container images. Media servers, downloaders, databases, and utilities - all running natively on FreeBSD with Podman and ocijail."
---

# Container Fleet

Explore our collection of high-performance, FreeBSD-native OCI containers.

## Base

| Image | Port | Description |
|-------|------|-------------|
| [:material-layers: Arr Base](arr-base.md) | - | Shared base image for *Arr applications (Radarr, Sonarr, Lidarr, Prowlarr) containing common dependencies. |
| [:simple-freebsd: Base](base.md) | - | FreeBSD base image with s6 supervision. |
| [:simple-nginx: Nginx Base](nginx-base.md) | - | Shared base image for Nginx-based applications. |

## Infrastructure

| Image | Port | Description |
|-------|------|-------------|
| [:simple-cloudflare: Cloudflared](cloudflared.md) | 2000 | Cloudflare Tunnel client for exposing services securely. |
| [:simple-gitea: Gitea](gitea.md) | 3000 | Gitea self-hosted Git service on FreeBSD. |
| [:simple-tailscale: Tailscale](tailscale.md) | - | Tailscale mesh VPN on FreeBSD. |
| [:material-server-network: Traefik](traefik.md) | 80 | Modern HTTP reverse proxy and load balancer on FreeBSD. |
| [:material-hammer: Woodpecker CI](woodpecker.md) | 8000 | Woodpecker CI server and agent on FreeBSD. |

## Network

| Image | Port | Description |
|-------|------|-------------|
| [:simple-adguard: AdGuard Home](adguardhome.md) | 53 | Network-wide ads & trackers blocking DNS server on FreeBSD. |
| [:simple-adguard: AdGuardHome Sync](adguardhome-sync.md) | 8080 | Sync AdGuardHome configuration to replica instances. |

## Media Management

| Image | Port | Description |
|-------|------|-------------|
| [:material-book-open-page-variant: BookLore](booklore.md) | 6060 | Self-hosted digital library with smart shelves, metadata, OPDS support, and built-in reader. |
| [:material-music: Lidarr](lidarr.md) | 8686 | Lidarr music management on FreeBSD. |
| [:material-eye: Overseerr](overseerr.md) | 5055 | Overseerr media request management on FreeBSD. |
| [:material-magnet: Prowlarr](prowlarr.md) | 9696 | Prowlarr indexer management on FreeBSD. |
| [:material-movie: Radarr](radarr.md) | 7878 | Radarr movie management on FreeBSD. |
| [:material-television: Sonarr](sonarr.md) | 8989 | Sonarr TV series management on FreeBSD. |

## Downloaders

| Image | Port | Description |
|-------|------|-------------|
| [:material-download-network: SABnzbd](sabnzbd.md) | 8080 | SABnzbd Usenet downloader on FreeBSD. |
| [:simple-transmission: Transmission](transmission.md) | 9091 | Transmission BitTorrent client on FreeBSD. |
| [:simple-wireguard: Transmission with WireGuard](transmission-wireguard.md) | 9091 | Transmission BitTorrent client with built-in WireGuard VPN support. |

## Media Servers

| Image | Port | Description |
|-------|------|-------------|
| [:simple-jellyfin: Jellyfin](jellyfin.md) | 8096 | The Free Software Media System on FreeBSD. |
| [:simple-plex: Plex Media Server](plex.md) | 32400 | Plex Media Server on FreeBSD. |
| [:simple-plex: Tautulli](tautulli.md) | 8181 | Tautulli Plex monitoring on FreeBSD. |

## Databases

| Image | Port | Description |
|-------|------|-------------|
| [:simple-postgresql: Immich PostgreSQL](immich-postgres.md) | 5432 | PostgreSQL 14 with pgvector/pgvecto.rs extensions for Immich. |
| [:material-database: MariaDB](mariadb.md) | 3306 | MariaDB database server for FreeBSD. |
| [:simple-postgresql: PostgreSQL](postgres.md) | 5432 | The World's Most Advanced Open Source Relational Database on FreeBSD. |
| [:simple-redis: Redis](redis.md) | 6379 | Redis key-value store on FreeBSD. |

## Photos & Media

| Image | Port | Description |
|-------|------|-------------|
| [:simple-googlephotos: Immich](immich.md) | - | Self-hosted photo and video management solution. |
| [:material-brain: Immich Machine Learning](immich-ml.md) | 3003 | Immich Machine Learning service (Python/ONNX) on FreeBSD. |
| [:material-server: Immich Server](immich-server.md) | 2283 | Immich photo management server on FreeBSD. |

## Utilities

| Image | Port | Description |
|-------|------|-------------|
| [:material-view-dashboard: Homepage](homepage.md) | 3000 | A modern, highly customizable dashboard for your homelab. |
| [:material-food: Mealie](mealie.md) | 9000 | Self-hosted recipe manager and meal planner on FreeBSD. |
| [:simple-nextcloud: Nextcloud](nextcloud.md) | 8082 | Nextcloud self-hosted cloud on FreeBSD. |
| [:material-speedometer: OpenSpeedTest](openspeedtest.md) | 3005 | Self-hosted HTML5 Network Speed Test on FreeBSD. |
| [:material-view-dashboard: Organizr](organizr.md) | 8083 | HTPC/Homelab Services Organizer on FreeBSD. |
| [:material-pulse: SmokePing](smokeping.md) | 8081 | SmokePing network latency monitor on FreeBSD. |
| [:material-access-point-network: UniFi Network](unifi.md) | 8443 | UniFi Network Application on FreeBSD. |
| [:material-chart-line: Uptime Kuma](uptime-kuma.md) | 3001 | A fancy self-hosted monitoring tool on FreeBSD. |
| [:simple-bitwarden: Vaultwarden](vaultwarden.md) | 8080 | Vaultwarden (Bitwarden compatible backend) on FreeBSD. |
| [:simple-n8n: n8n](n8n.md) | 5678 | Workflow automation tool on FreeBSD. |

## Image Tags

| Tag | Source | Description |
|-----|--------|-------------|
| `:latest` | Upstream releases | Newest version from project |
| `:pkg` | FreeBSD quarterly | Stable, tested in ports |
| `:pkg-latest` | FreeBSD latest | Rolling package updates |
