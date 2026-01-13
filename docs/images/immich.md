# Immich

Self-hosted photo and video management solution.

| | |
|---|---|
| **Registry** | `ghcr.io/daemonless/immich` |
| **Source** | [https://github.com/immich-app/immich](https://github.com/immich-app/immich) |
| **Website** | [https://immich.app/](https://immich.app/) |

## Deployment

### Podman Compose

```yaml
services:
  immich:
    image: ghcr.io/daemonless/immich:latest
    container_name: immich
    environment:
      - DB_HOSTNAME=localhost
      - REDIS_HOSTNAME=localhost
      - IMMICH_MACHINE_LEARNING_URL=http://localhost:3003
    volumes:
      - /path/to/data:/data
      - /path/to/containers/immich/etc/localtime:/etc/localtime
    ports:
    restart: unless-stopped
```

### Podman CLI

```bash
podman run -d --name immich \
  -e DB_HOSTNAME=localhost \
  -e REDIS_HOSTNAME=localhost \
  -e IMMICH_MACHINE_LEARNING_URL=http://localhost:3003 \
  -v /path/to/data:/data \ 
  -v /path/to/containers/immich/etc/localtime:/etc/localtime \ 
  ghcr.io/daemonless/immich:latest
```

### Ansible

```yaml
- name: Deploy immich
  containers.podman.podman_container:
    name: immich
    image: ghcr.io/daemonless/immich:latest
    state: started
    restart_policy: always
    env:
      DB_HOSTNAME: "localhost"
      REDIS_HOSTNAME: "localhost"
      IMMICH_MACHINE_LEARNING_URL: "http://localhost:3003"
    volumes:
      - "/path/to/data:/data"
      - "/path/to/containers/immich/etc/localtime:/etc/localtime"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOSTNAME` | `localhost` |  |
| `REDIS_HOSTNAME` | `localhost` |  |
| `IMMICH_MACHINE_LEARNING_URL` | `http://localhost:3003` |  |

### Volumes

| Path | Description |
|------|-------------|
| `/data` | Media storage (mapped to UPLOAD_LOCATION) |
| `/etc/localtime` |  |

### Ports

| Port | Protocol | Description |
|------|----------|-------------|

## Notes

- **User:** `root` (UID/GID set via PUID/PGID)
- **Base:** Built on `ghcr.io/daemonless/base` (FreeBSD)