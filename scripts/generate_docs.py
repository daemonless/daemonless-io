#!/usr/bin/env python3
"""
Generate MkDocs documentation from compose.yaml files in daemonless repos.
Produces docs with interactive placeholder support.
"""
import os
import re
import yaml
import jinja2
from pathlib import Path

# Paths - relative to daemonless-io repo
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent  # daemonless-io
REPOS_DIR = REPO_ROOT.parent   # Parent dir where repos are cloned
TEMPLATE_DIR = REPO_ROOT / "templates"
DOCS_DIR = REPO_ROOT / "docs" / "images"
PLACEHOLDER_PLUGIN = REPO_ROOT / "placeholder-plugin.yaml"

# Constants
CONFIG_ROOT_VAR = "@CONTAINER_CONFIG_ROOT@"
DEFAULT_CONFIG_ROOT = "/path/to/containers"
SHARED_PATHS = ["/downloads", "/movies", "/tv", "/music", "/books", "/media", "/data"]

# Skip these repos (not container images)
SKIP_REPOS = {"daemonless", "daemonless-io", "cit", "freebsd-ports"}

# Load Template
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("README.j2")

def get_tags(repo_path):
    """Determine available tags based on Containerfiles present."""
    tags = ["latest"]
    if (repo_path / "Containerfile.pkg").exists():
        tags.extend(["pkg", "pkg-latest"])
    return tags

def load_compose_config(repo_path):
    """Load configuration from compose.yaml x-daemonless extension."""
    compose_path = repo_path / "compose.yaml"
    if not compose_path.exists():
        return None

    with open(compose_path, "r") as f:
        data = yaml.safe_load(f)

    if not data:
        return None

    # Handle repos without services (base images)
    if 'services' not in data or not data['services']:
        meta = data.get('x-daemonless', {})
        if not meta:
            return None
        config = {
            'name': repo_path.name,
            'title': meta.get('title', repo_path.name.title()),
            'description': meta.get('description', ''),
            'category': meta.get('category', 'Uncategorized'),
            'upstream_url': meta.get('upstream_url', ''),
            'web_url': meta.get('web_url', ''),
            'freshports_url': meta.get('freshports_url', ''),
            'user': meta.get('user', 'bsd'),
            'mlock': meta.get('mlock', False),
            'upstream_binary': meta.get('upstream_binary', True),
            'icon': meta.get('icon', ':material-docker:'),
            'healthcheck': None,
            'env': [],
            'volumes': [],
            'ports': [],
            'tags': get_tags(repo_path),
            'repo_url': f"https://github.com/daemonless/{repo_path.name}"
        }
        return config

    # Get first service
    service_name = list(data['services'].keys())[0]
    service = data['services'][service_name]
    meta = data.get('x-daemonless', {})
    docs = meta.get('docs', {})

    config = {
        'name': repo_path.name,
        'title': meta.get('title', repo_path.name.title()),
        'description': meta.get('description', ''),
        'category': meta.get('category', 'Uncategorized'),
        'upstream_url': meta.get('upstream_url', ''),
        'web_url': meta.get('web_url', ''),
        'freshports_url': meta.get('freshports_url', ''),
        'user': meta.get('user', 'bsd'),
        'mlock': meta.get('mlock', False),
        'upstream_binary': meta.get('upstream_binary', True),
        'icon': meta.get('icon', ':material-docker:'),
        'healthcheck': meta.get('healthcheck', None),
        'env': [],
        'volumes': [],
        'ports': [],
        'tags': get_tags(repo_path),
        'repo_url': f"https://github.com/daemonless/{repo_path.name}"
    }

    # Parse Environment
    env_docs = {str(k): v for k, v in docs.get('env', {}).items()}
    env_vars = service.get('environment', [])
    if isinstance(env_vars, dict):
        env_items = list(env_vars.items())
    else:
        env_items = [e.split('=', 1) if '=' in e else (e, '') for e in env_vars]

    for key, val in env_items:
        display_val = val if val and val not in ['""', "''"] else ''
        if not display_val and any(x in key.upper() for x in ["PASS", "KEY", "SECRET", "TOKEN"]):
            display_val = f"<{key.upper()}>"

        item = {
            'name': key,
            'default': display_val,
            'desc': env_docs.get(str(key), '')
        }

        if key in ["PUID", "PGID", "TZ"]:
            item['placeholder'] = f"@{key}@"

        config['env'].append(item)

    # Parse Volumes
    vol_docs = {str(k): v for k, v in docs.get('volumes', {}).items()}
    for vol in service.get('volumes', []):
        if isinstance(vol, str):
            parts = vol.split(':')
            src, tgt = parts[0], parts[1] if len(parts) > 1 else parts[0]
        else:
            src, tgt = vol.get('source', ''), vol.get('target', '')

        clean_target = tgt.strip('/').replace('/', '_').upper()
        vol_info = vol_docs.get(str(tgt), '')
        desc = vol_info.get('desc', '') if isinstance(vol_info, dict) else str(vol_info)
        optional = vol_info.get('optional', False) if isinstance(vol_info, dict) else False

        if tgt in SHARED_PATHS:
            source_path = tgt.lstrip('/')
            placeholder = f"@{clean_target}_PATH@"
            root_var = None
        elif tgt == "/config":
            placeholder = f"@{config['name'].upper().replace('-', '_')}_CONFIG_PATH@"
            source_path = config['name']
            root_var = CONFIG_ROOT_VAR
        else:
            source_path = f"{config['name']}{tgt}"
            root_var = CONFIG_ROOT_VAR
            placeholder = f"@{config['name'].upper().replace('-', '_')}_{clean_target}_PATH@"

        config['volumes'].append({
            'path': tgt,
            'desc': desc,
            'optional': optional,
            'placeholder': placeholder,
            'source': source_path,
            'root_var': root_var
        })

    # Parse Ports
    port_docs = {str(k): v for k, v in docs.get('ports', {}).items()}
    for port in service.get('ports', []):
        if isinstance(port, str):
            parts = port.split(':')
            pub = parts[0]
            tgt = parts[1] if len(parts) > 1 else parts[0]
            proto = 'tcp'
        else:
            pub, tgt = port.get('published'), port.get('target')
            proto = port.get('protocol', 'tcp')

        config['ports'].append({
            'port': pub,
            'protocol': proto,
            'desc': port_docs.get(str(pub), ''),
            'name': 'web'
        })

    return config

def load_fallback_config(repo_path):
    """Fallback: load from .daemonless/config.yaml if no compose.yaml."""
    config_path = repo_path / ".daemonless" / "config.yaml"
    if not config_path.exists():
        return None

    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}

    # Minimal config for repos without compose.yaml
    return {
        'name': repo_path.name,
        'title': data.get('title', repo_path.name.title()),
        'description': data.get('description', ''),
        'category': data.get('category', 'Uncategorized'),
        'upstream_url': data.get('upstream_url', ''),
        'web_url': data.get('web_url', ''),
        'freshports_url': data.get('freshports_url', ''),
        'user': data.get('user', 'bsd'),
        'mlock': data.get('mlock', False),
        'upstream_binary': data.get('upstream_binary', True),
        'icon': data.get('icon', ':material-docker:'),
        'healthcheck': None,
        'docs': data.get('docs'),
        'env': [],
        'volumes': [],
        'ports': [{'port': data.get('port', '80'), 'protocol': 'tcp', 'desc': 'Web UI'}] if data.get('port') else [],
        'tags': get_tags(repo_path),
        'repo_url': f"https://github.com/daemonless/{repo_path.name}"
    }

def update_placeholders(configs):
    """Update placeholder-plugin.yaml with all placeholder definitions."""
    try:
        with open(PLACEHOLDER_PLUGIN, 'r') as f:
            plugin_data = yaml.safe_load(f) or {}
    except:
        plugin_data = {}

    # Settings for @ syntax
    plugin_data["settings"] = {
        "normal_prefix": "@",
        "normal_suffix": "@"
    }

    if "placeholders" not in plugin_data:
        plugin_data["placeholders"] = {}

    # Validators
    plugin_data["validators"] = {
        "port_number": {
            "name": "Port Number",
            "rules": [{
                "regex": "^[0-9]+$",
                "should_match": True,
                "error_message": "Must be a positive integer."
            }]
        }
    }

    def strip_syntax(s):
        return s.strip("@")

    # Global placeholders
    plugin_data["placeholders"][strip_syntax(CONFIG_ROOT_VAR)] = {
        "default": DEFAULT_CONFIG_ROOT,
        "description": "Container Configuration Root Path",
    }

    for path in SHARED_PATHS:
        name = path.strip('/').replace('/', '_').upper()
        plugin_data["placeholders"][f"{name}_PATH"] = {
            "default": f"/path/to{path}",
            "description": f"Global {path} Path"
        }

    # Common env placeholders
    try:
        import pytz
        tz_map = {tz: tz for tz in pytz.common_timezones}
    except ImportError:
        tz_map = {"UTC": "UTC", "America/New_York": "America/New_York", "America/Los_Angeles": "America/Los_Angeles"}

    plugin_data["placeholders"]["TZ"] = {
        "default": "UTC",
        "description": "Timezone",
        "values": tz_map
    }
    plugin_data["placeholders"]["PUID"] = {
        "default": "1000",
        "description": "User ID",
        "validators": ["port_number"]
    }
    plugin_data["placeholders"]["PGID"] = {
        "default": "1000",
        "description": "Group ID",
        "validators": ["port_number"]
    }

    # Per-image placeholders
    for config in configs:
        if config.get("ports"):
            main_port = config["ports"][0]["port"]
            var_name = f"{config['name'].upper().replace('-', '_')}_PORT"
            plugin_data["placeholders"][var_name] = {
                "default": str(main_port),
                "description": f"{config['title']} Host Port",
                "validators": ["port_number"]
            }

        for v in config.get("volumes", []):
            if not v.get("placeholder") or v['path'] in SHARED_PATHS:
                continue
            default_path = v.get("source", f"{config['name']}{v['path']}").lstrip("/")
            plugin_data["placeholders"][strip_syntax(v["placeholder"])] = {
                "default": default_path,
                "description": f"{config['title']} {v['path']} Path"
            }

    # Clean up old SET_ keys
    plugin_data["placeholders"] = {k: v for k, v in plugin_data["placeholders"].items() if not k.startswith("SET_")}

    with open(PLACEHOLDER_PLUGIN, 'w') as f:
        yaml.dump(plugin_data, f, sort_keys=False, default_flow_style=False)
    print("Updated placeholder-plugin.yaml")

def generate_index_page(configs):
    """Generate the Fleet index page."""
    lines = ["# Container Fleet", "", "Explore our collection of high-performance, FreeBSD-native OCI containers.", ""]
    categories = ["Base", "Infrastructure", "Network", "Media Management", "Downloaders", "Media Servers", "Databases", "Photos & Media", "Utilities", "Uncategorized"]

    by_category = {}
    for config in configs:
        by_category.setdefault(config.get("category", "Uncategorized"), []).append(config)

    for cat in categories:
        img_list = by_category.get(cat)
        if not img_list:
            continue
        lines.extend([f"## {cat}", "", "| Image | Port | Description |", "|-------|------|-------------|"])
        for config in sorted(img_list, key=lambda x: x['title']):
            port_str = str(config["ports"][0]["port"]) if config.get("ports") else "-"
            icon = config.get("icon") or ":material-docker:"
            row = f"| [{icon} {config['title']}]({config['name']}.md) | {port_str} | {config.get('description', '')} |"
            lines.append(row)
        lines.append("")

    lines.extend([
        "## Image Tags", "",
        "| Tag | Source | Description |",
        "|-----|--------|-------------|",
        "| `:latest` | Upstream releases | Newest version from project |",
        "| `:pkg` | FreeBSD quarterly | Stable, tested in ports |",
        "| `:pkg-latest` | FreeBSD latest | Rolling package updates |",
        ""
    ])

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "index.md").write_text("\n".join(lines))
    print("Generated docs/images/index.md")

def update_mkdocs_yaml(configs):
    """Update mkdocs.yaml navigation with all images."""
    mkdocs_path = REPO_ROOT / "mkdocs.yaml"
    if not mkdocs_path.exists():
        return

    lines = mkdocs_path.read_text().splitlines()
    new_lines = []
    in_fleet = False
    processed = False

    by_cat = {}
    for config in configs:
        cat = config.get("category", "Uncategorized")
        by_cat.setdefault(cat, []).append(config)

    for line in lines:
        if line.strip() == "- Fleet:":
            in_fleet = True
            if not processed:
                new_lines.append("  - Fleet:")
                new_lines.append("    - Overview: images/index.md")
                for cat in sorted(by_cat.keys()):
                    new_lines.append(f"    - {cat}:")
                    for config in sorted(by_cat[cat], key=lambda x: x['title']):
                        new_lines.append(f"      - {config['title']}: images/{config['name']}.md")
                processed = True
            continue
        if in_fleet:
            if line.startswith("  - ") and not line.strip().startswith("- Overview"):
                in_fleet = False
                new_lines.append(line)
            continue
        new_lines.append(line)

    mkdocs_path.write_text("\n".join(new_lines) + "\n")
    print("Updated mkdocs.yaml")

def main():
    configs = []

    # Discover repos
    for repo in sorted(REPOS_DIR.iterdir()):
        if not repo.is_dir() or repo.name in SKIP_REPOS:
            continue
        if repo.name.startswith('.'):
            continue

        # Try compose.yaml first, then fallback
        config = load_compose_config(repo)
        if not config:
            config = load_fallback_config(repo)

        if not config:
            continue

        configs.append(config)

        # Generate MkDocs page
        try:
            out_path = DOCS_DIR / f"{config['name']}.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)

            if config.get('docs') == 'manual':
                # Copy README.md from repo for manual docs
                readme_path = repo / "README.md"
                if readme_path.exists():
                    out_path.write_text(readme_path.read_text())
                    print(f"Copied docs/images/{config['name']}.md (manual)")
                else:
                    print(f"Warning: {repo.name} has docs: manual but no README.md")
            else:
                # Generate from template
                mkdocs_content = template.render(config, render_mode="mkdocs")
                out_path.write_text(mkdocs_content)
                print(f"Generated docs/images/{config['name']}.md")
        except Exception as e:
            print(f"Error generating {config['name']}: {e}")

    if not configs:
        print("No configs found")
        return

    # Update supporting files
    update_placeholders(configs)
    generate_index_page(configs)
    update_mkdocs_yaml(configs)

    print(f"\nGenerated {len(configs)} image docs")

if __name__ == "__main__":
    main()
