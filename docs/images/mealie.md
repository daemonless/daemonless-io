---
title: Mealie - FreeBSD OCI Container
description: Mealie Recipe Manager on FreeBSD  Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated.
---

# Mealie

**Self-hosted recipe manager and meal planner.**

Mealie is a self-hosted recipe manager and meal planner with a focus on providing a pleasant user experience for the whole family. It features:
- **Recipe Imports:** Easily import recipes from the web by URL.
- **Meal Planning:** Drag-and-drop meal planner.
- **Shopping Lists:** Auto-generated shopping lists from your meal plan.
- **AI Integration:** Use LLMs (Gemini, ChatGPT) to parse ingredients and instructions.

| | |
|---|---|
| **Port** | 9000 |
| **Registry** | `ghcr.io/daemonless/mealie` |
| **Tags** | `:latest` |
| **Source** | [github.com/daemonless/mealie](https://github.com/daemonless/mealie) |

!!! warning "Requires patched ocijail"
    This application requires the `allow.mlock` annotation.
    See [ocijail patch](../guides/ocijail-patch.md).

## Quick Start

=== "Podman CLI"

    ```bash
    podman run -d --name mealie \
      -p 9000:9000 \
      -v mealie-data:/app/data \
      ghcr.io/daemonless/mealie:latest
    ```
    
    Access at: http://localhost:9000
    Default login: `changeme@example.com` / `MyPassword`

=== "Compose"

    ```yaml
    services:
      mealie:
        image: ghcr.io/daemonless/mealie:latest
        container_name: mealie
        environment:
          - TZ=America/New_York
          - BASE_URL=https://mealie.example.com
    
          # --- AI Integration (Select One) ---
    
          # Option 1: Google Gemini (Free Tier Available)
          # - OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
          # - OPENAI_API_KEY=your_gemini_api_key
          # - OPENAI_MODEL=gemini-2.5-flash
          # - OPENAI_ENABLE_IMAGE_SERVICES=true
    
          # Option 2: OpenAI (ChatGPT)
          # - OPENAI_BASE_URL=https://api.openai.com/v1
          # - OPENAI_API_KEY=your_openai_api_key
          # - OPENAI_MODEL=gpt-4o-mini
          # - OPENAI_ENABLE_IMAGE_SERVICES=true
    
        volumes:
          - mealie-data:/app/data
        ports:
          - 9000:9000
        restart: unless-stopped
    
    volumes:
      mealie-data:
    ```

## Quick Start - PostgreSQL

> **Requires [patched ocijail](https://github.com/daemonless/daemonless#ocijail-patch)** for SysV IPC support

```bash
# Create network
podman network create mealie-net

# Start PostgreSQL
podman run -d --name mealie-postgres \
  --network mealie-net \
  -e POSTGRES_USER=mealie \
  -e POSTGRES_PASSWORD=mealie \
  -e POSTGRES_DB=mealie \
  --annotation 'org.freebsd.jail.allow.sysvipc=true' \
  -v mealie-postgres:/var/lib/postgresql/data \
  ghcr.io/daemonless/postgres:17

# Start Mealie
podman run -d --name mealie \
  --network mealie-net \
  -p 9000:9000 \
  -e DB_ENGINE=postgres \
  -e POSTGRES_USER=mealie \
  -e POSTGRES_PASSWORD=mealie \
  -e POSTGRES_SERVER=mealie-postgres \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=mealie \
  -v mealie-data:/app/data \
  ghcr.io/daemonless/mealie:latest
```

## podman-compose - PostgreSQL

> **Requires [patched ocijail](https://github.com/daemonless/daemonless#ocijail-patch)** for SysV IPC support

```yaml
services:
  mealie:
    image: ghcr.io/daemonless/mealie:latest
    container_name: mealie
    depends_on:
      - postgres
    environment:
      - TZ=America/New_York
      - BASE_URL=https://mealie.example.com
      - DB_ENGINE=postgres
      - POSTGRES_USER=mealie
      - POSTGRES_PASSWORD=mealie
      - POSTGRES_SERVER=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=mealie

      # See AI Integration options above in the SQLite example

    volumes:
      - mealie-data:/app/data
    ports:
      - 9000:9000
    restart: unless-stopped

  postgres:
    image: ghcr.io/daemonless/postgres:17
    container_name: mealie-postgres
    annotations:
      org.freebsd.jail.allow.sysvipc: "true"
    environment:
      - POSTGRES_USER=mealie
      - POSTGRES_PASSWORD=mealie
      - POSTGRES_DB=mealie
    volumes:
      - mealie-postgres:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  mealie-data:
  mealie-postgres:
```

## AI Integration

Mealie uses OpenAI-compatible APIs to automatically parse ingredients and instructions from imported URLs. You can use either Google Gemini or the official OpenAI API.

### Option 1: Google Gemini

Google's Gemini models are fast and offer a generous free tier.
Get an API key from [Google AI Studio](https://aistudio.google.com/api-keys).
| Variable | Value |
|----------|-------|
| `OPENAI_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `OPENAI_API_KEY` | `your-google-api-key` |
| `OPENAI_MODEL` | `gemini-2.5-flash` or `gemini-3-flash` |
| `OPENAI_ENABLE_IMAGE_SERVICES` | `true` |

### Option 2: OpenAI (ChatGPT)

Standard OpenAI integration.
Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys).

| Variable | Value |
|----------|-------|
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` (Default) |
| `OPENAI_API_KEY` | `your-openai-api-key` |
| `OPENAI_MODEL` | `gpt-4o-mini` or `gpt-4o` |
| `OPENAI_ENABLE_IMAGE_SERVICES` | `true` |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TZ` | `UTC` | Timezone |
| `BASE_URL` | - | Public URL for the instance |
| `DB_ENGINE` | `sqlite` | Database engine (`sqlite` or `postgres`) |
| `ALLOW_SIGNUP` | `true` | Enable/disable user registration |

### PostgreSQL Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | - | Database user |
| `POSTGRES_PASSWORD` | - | Database password |
| `POSTGRES_SERVER` | - | Database hostname |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | - | Database name |

## Volumes

| Path | Description |
|------|-------------|
| `/app/data` | Application data (recipes, images, SQLite DB) |

## Ports

| Port | Description |
|------|-------------|
| 9000 | Web UI |

## Notes

- **User:** `bsd` (UID/GID 1000)
- **PostgreSQL:** Requires `--annotation 'org.freebsd.jail.allow.sysvipc=true'`
- **DNS:** Requires `dnsname` CNI plugin for container name resolution (see [networking guide](https://daemonless.io/guides/networking/#option-2-dns-resolution-cni-dnsname))

## Migrating from Linux

**SQLite:** No issues, just copy your data.

**PostgreSQL:** You cannot copy the postgres data directory between Linux and FreeBSD due to locale incompatibilities. Use `pg_dump`/`pg_restore` instead:

```bash
# On Linux
podman exec mealie-postgres pg_dump -U mealie mealie > mealie.sql

# On FreeBSD (start fresh postgres first, then restore)
cat mealie.sql | podman exec -i mealie-postgres psql -U mealie -d mealie
```

See [daemonless/postgres README](https://github.com/daemonless/postgres#migrating-from-linux) for details.

## Links

- [Mealie Website](https://mealie.io/)
- [Mealie Documentation](https://docs.mealie.io/)
- [GitHub](https://github.com/mealie-recipes/mealie)
