---
title: "Stack Choices"
description: "How to declare database and part choices in compose.yaml with x-daemonless.choices."
---

# Stack Choices

A choice lets an image repository offer alternatives under `x-daemonless.choices`. The default option is the compose as it stands, so `podman-compose up -d` with nothing set gives the default. dbuild renders every option into the README and the site.

## A database choice

Vikunja declares its database choice like this:

```yaml
x-daemonless:
  choices:
    database:
      kind: database
      offers: [sqlite, postgres, mariadb, external]
      default: sqlite
      env:
        type: VIKUNJA_DATABASE_TYPE
        host: VIKUNJA_DATABASE_HOST
        user: VIKUNJA_DATABASE_USER
        password: VIKUNJA_DATABASE_PASSWORD
        name: VIKUNJA_DATABASE_DATABASE
      types: { mariadb: mysql }
```

- Roles are type, host, port, user, password, name; omit port if the app has none.
- `types` only when the app's word for an engine differs.
- `external` needs postgres or mariadb in `offers`.
- Add each variable to the service's `environment:` and to `docs.env`.
- Never write a postgres or mariadb service yourself; dbuild adds it.

!!! warning "The empty-default rule"
    Use `${VAR:-}` when the app also reads a config file that env overrides (grafana, gitea). A non-empty default switches an existing install to an empty SQLite database.

## A part choice

Immich declares an optional part like this:

```yaml
x-daemonless:
  choices:
    machine_learning:
      label: Machine learning
      default: "on"
      options:
        "on":
          label: "With machine learning"
          profile: ml
        "off":
          label: "Without machine learning"
          drop: [immich-machine-learning]
          env: { IMMICH_ML_ENABLED: "false" }
          ask:
            - name: IMMICH_MACHINE_LEARNING_URL
              label: "External ML URL"
```

- `profile` switches on services carrying that compose profile.
- `env` sets environment variables for that option.
- `drop` removes named services from the stack.
- `ask` prompts for values in `.env` and on the site.

## When it does not fit yet

- The app takes a single database URL (vaultwarden).
- The stack uses `network_mode: host` or already has its own database service (paperless).
- The engine needs per-app server settings (uptime-kuma).

## Generate and check

Run `dbuild generate` then `dbuild lint`.

Lint checks:

- Offers are known engines.
- Each mapped variable is in the service's environment.
- The default option adds no service.
- The compose has no postgres or mariadb service of its own.
- A part's profile exists on a service.
- A dropped service exists.

## Test

Run every offered option from the README's own generated snippet on a FreeBSD host. Check that the app's tables are in the engine picked and no SQLite file appeared.
