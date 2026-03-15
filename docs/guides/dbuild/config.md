# Configuration Reference

`dbuild` uses `compose.yaml` as the primary source of truth for metadata.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DBUILD_REGISTRY` | Override the target container registry (e.g., ghcr.io/myorg). |
| `GITHUB_TOKEN` | Authentication token for GitHub Packages and build secrets. |
| `GITHUB_ACTOR` | The username associated with GITHUB_TOKEN. |
| `DOCKERHUB_USERNAME` | Enable mirroring by providing a Docker Hub username. |
| `DOCKERHUB_TOKEN` | Personal access token for Docker Hub mirroring. |
| `CHROME_BIN` | Path to the Chrome/Chromium binary for screenshot testing. |


## Config File Locations

| File | Description |
|------|-------------|
| `compose.yaml` | The primary source of truth for metadata and documentation. |
| `.daemonless/config.yaml` | Project-specific build and test overrides. |
| `/usr/local/etc/daemonless.yaml` | Global templates for shared build variants. |


## Metadata (`x-daemonless`)

The `x-daemonless` section in `compose.yaml` (or `config.yaml`) defines discovery metadata:

| Field | Default | Description |
|-------|---------|-------------|
| `title` | (dir name) | Human-readable application title |
| `icon` | `:material-docker:` | Material or SimpleIcon identifier |
| `category` | `Apps` | Application category |
| `description` | `""` | Short description of the application |
| `upstream_url`| `""` | URL to the upstream source repository |
| `web_url` | `""` | URL to the official project website |
| `community` | `""` | Help link in `Name:URL` format |
| `appjail` | `None` | Enable AppJail documentation (bare key or config) |
| `user` | `bsd` | Internal container user (docs only) |