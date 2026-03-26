#!/usr/bin/env python3
"""
Generate MkDocs documentation from compose.yaml files in daemonless repos.
Produces docs with interactive placeholder support.
"""
import json
import subprocess
import sys
from pathlib import Path
import yaml
import jinja2

# Paths - relative to daemonless-io repo
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
REPOS_DIR = REPO_ROOT.parent

# Add dbuild repo root to sys.path so we can import 'dbuild' package
DBUILD_REPO = (REPOS_DIR / "dbuild").resolve()
if DBUILD_REPO.exists():
    sys.path.insert(0, str(DBUILD_REPO))
else:
    print(f"Error: dbuild repository not found at {DBUILD_REPO}")
    print(f"  Run 'make fetch' from the daemonless-io root to clone all required repositories.")
    sys.exit(1)

# pylint: disable=wrong-import-position
from dbuild.config import load as load_dbuild_config, VALID_CATEGORIES
from dbuild.docs import _enrich_metadata, SHARED_PATHS

TEMPLATE_DIR = DBUILD_REPO / "dbuild" / "templates"
LOCAL_TEMPLATE_DIR = SCRIPT_DIR / "templates"
DOCS_DIR = REPO_ROOT / "docs" / "images"
PLACEHOLDER_PLUGIN = REPO_ROOT / "placeholder-plugin.yaml"

# Constants
CONFIG_ROOT_VAR = "@CONTAINER_CONFIG_ROOT@"
DEFAULT_CONFIG_ROOT = "/path/to/containers"

# Skip these repos (not container images)
SKIP_REPOS = {"daemonless", "daemonless-io", "cit", "freebsd-ports", "dbuild"}

# Local templates override dbuild templates
env = jinja2.Environment(loader=jinja2.ChoiceLoader([
    jinja2.FileSystemLoader(str(LOCAL_TEMPLATE_DIR)),
    jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
]))
template = env.get_template("README.mkdocs.j2")

def get_repo_config(repo_path):
    """Load configuration using dbuild's native parser."""
    try:
        cfg = load_dbuild_config(repo_path)
        if not cfg:
            return None

        # Use dbuild's internal enricher to get the same context used for README.md
        context = _enrich_metadata(cfg)

        # Add registry if not present (dbuild uses cfg.registry)
        if 'registry' not in context:
            context['registry'] = cfg.registry or "ghcr.io/daemonless"

        return context
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error loading {repo_path.name}: {e}")
        return None

def update_placeholders(configs):
    """Update placeholder-plugin.yaml with all placeholder definitions."""
    try:
        with open(PLACEHOLDER_PLUGIN, 'r', encoding='utf-8') as f:
            plugin_data = yaml.safe_load(f) or {}
    except FileNotFoundError:
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

    plugin_data["placeholders"]["INTERFACE"] = {
        "default": "em0",
        "description": "Host Network Interface",
    }

    for path in SHARED_PATHS:
        name = path.strip('/').replace('/', '_').upper()
        plugin_data["placeholders"][f"{name}_PATH"] = {
            "default": f"/path/to{path}",
            "description": f"Global {path} Path"
        }

    # Common env placeholders
    tz_map = {
        "UTC": "UTC",
        "America/New_York": "America/New_York",
        "America/Los_Angeles": "America/Los_Angeles"
    }
    try:
        import pytz # pylint: disable=import-outside-toplevel
        tz_map = {tz: tz for tz in pytz.common_timezones}
    except ImportError:
        pass

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
            src_val = v.get("source", f"{config['name']}{v['path']}")
            plugin_data["placeholders"][strip_syntax(v["placeholder"])] = {
                "default": src_val.lstrip("/"),
                "description": f"{config['title']} {v['path']} Path"
            }

    # Clean up old SET_ keys
    plugin_data["placeholders"] = {
        k: v for k, v in plugin_data["placeholders"].items()
        if not k.startswith("SET_")
    }

    with open(PLACEHOLDER_PLUGIN, 'w', encoding='utf-8') as f:
        yaml.dump(plugin_data, f, sort_keys=False, default_flow_style=False)
    print("Updated placeholder-plugin.yaml")

def generate_index_page(configs):
    """Generate the Fleet index page."""
    description = (
        "Browse all daemonless OCI images. Media servers, downloaders, "
        "databases, and utilities — all running natively on FreeBSD."
    )
    lines = [
        "---",
        'title: "OCI Image Fleet: 30+ Native FreeBSD Images"',
        f'description: "{description}"',
        "---",
        "",
        "# Image Fleet",
        "",
        "Explore our collection of high-performance, FreeBSD-native OCI images.",
        ""
    ]

    # Use VALID_CATEGORIES from dbuild + Uncategorized for index grouping
    categories = VALID_CATEGORIES + ["Uncategorized"]

    by_category = {}
    for config in configs:
        by_category.setdefault(config.get("category", "Uncategorized"), []).append(config)

    for cat in categories:
        img_list = by_category.get(cat)
        if not img_list:
            continue
        lines.extend([
            f"## {cat}", "",
            "| Image | Port | Description |",
            "|-------|------|-------------|"
        ])
        for config in sorted(img_list, key=lambda x: x['title']):
            port_info = config["ports"][0]["port"] if config.get("ports") else "-"
            icon = config.get("icon") or ":material-docker:"
            row = f"| [{icon} {config['title']}]({config['name']}.md) | " \
                  f"{port_info} | {config.get('description', '')} |"
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
    (DOCS_DIR / "index.md").write_text("\n".join(lines), encoding='utf-8')
    print("Generated docs/images/index.md")

def update_mkdocs_yaml(configs):
    """Update mkdocs.yaml navigation with all images."""
    mkdocs_path = REPO_ROOT / "mkdocs.yaml"
    if not mkdocs_path.exists():
        return

    lines = mkdocs_path.read_text(encoding='utf-8').splitlines()
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
                new_lines.append("  - Image Fleet:")
                new_lines.append("    - Overview: images/index.md")
                new_lines.append("    - Version Status: status.md")
                # Use VALID_CATEGORIES from dbuild for navigation ordering
                for cat in VALID_CATEGORIES + ["Uncategorized"]:
                    if cat not in by_cat:
                        continue
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

    mkdocs_path.write_text("\n".join(new_lines) + "\n", encoding='utf-8')
    print("Updated mkdocs.yaml")

def generate_status_page(configs):
    """Generate docs/images/index.md (build overview) and docs/status.md (version status)."""
    try:
        overview_tmpl = env.get_template("status.mkdocs.j2")
        version_tmpl = env.get_template("version-status.mkdocs.j2")
    except jinja2.TemplateNotFound as e:
        print(f"Warning: template not found ({e}), skipping status pages")
        return

    # Fleet overview
    content = overview_tmpl.render(configs=configs, categories=VALID_CATEGORIES + ["Uncategorized"])
    (REPO_ROOT / "docs" / "images" / "index.md").write_text(content, encoding='utf-8')
    print("Generated docs/images/index.md")

    # Version status
    versions_file = REPO_ROOT / "daemonless-versions.json"
    last_check = "unknown"
    if versions_file.exists():
        last_check = json.loads(versions_file.read_text()).get("last_check", "unknown")

    compare = SCRIPT_DIR / "compare-versions.py"
    version_data = {}
    if compare.exists():
        result = subprocess.run([sys.executable, str(compare)],
                                capture_output=True, text=True)
        if result.stdout.strip():
            version_data = json.loads(result.stdout)

    # Add last_updates map for the status page
    last_updates = {c["name"]: c["last_update"] for c in configs}

    content = version_tmpl.render(last_check=last_check, last_updates=last_updates, configs=configs, **version_data)
    (REPO_ROOT / "docs" / "status.md").write_text(content, encoding='utf-8')
    print("Generated docs/status.md")


def get_last_commit_date(repo_path):
    """Get the last commit date for a repo in ISO format."""
    try:
        # 1. Try git log
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            # Return YYYY-MM-DD
            return result.stdout.strip().split('T')[0]

        # 2. Try git log on the directory specifically
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('T')[0]
    except Exception as e:
        print(f"Error getting git date for {repo_path.name}: {e}")

    # 3. Fallback to filesystem mtime of compose.yaml or README.md
    try:
        for fname in ["compose.yaml", "README.md", "."]:
            fpath = repo_path / fname
            if fpath.exists():
                import datetime
                mtime = fpath.stat().st_mtime
                return datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except Exception:
        pass

    return "Unknown"

def main():
    """Main entry point for the documentation generator."""
    configs = []

    # Discover repos
    for repo in sorted(REPOS_DIR.iterdir()):
        if not repo.is_dir() or repo.name.startswith('.'):
            continue

        # A valid image repo MUST have a compose.yaml or a .daemonless config
        is_image_repo = (repo / "compose.yaml").exists() or \
                        (repo / ".daemonless" / "config.yaml").exists()

        if not is_image_repo:
            continue

        # Load using dbuild logic
        config = get_repo_config(repo)
        if not config:
            continue

        # Add last commit date
        config["last_update"] = get_last_commit_date(repo)

        configs.append(config)

        # Generate MkDocs page
        try:
            out_path = DOCS_DIR / f"{config['name']}.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Check for manual docs: supports both docs: manual and docs: { manual: true }
            docs_val = config.get('docs')
            is_manual = (docs_val == 'manual' or
                         (isinstance(docs_val, dict) and docs_val.get('manual', False)))
            if is_manual:
                # Copy README.md from repo for manual docs
                readme_path = repo / "README.md"
                if readme_path.exists():
                    out_path.write_text(readme_path.read_text(encoding='utf-8'), encoding='utf-8')
                    print(f"Copied docs/images/{config['name']}.md (manual)")
                else:
                    print(f"Warning: {repo.name} has docs: manual but no README.md")
            else:
                # Generate from consolidated dbuild template
                mkdocs_content = template.render(config, render_mode="mkdocs")
                out_path.write_text(mkdocs_content, encoding='utf-8')
                print(f"Generated docs/images/{config['name']}.md")
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"Error generating {config['name']}: {e}")

    if not configs:
        print("No configs found")
        return

    # Update supporting files
    update_placeholders(configs)
    update_mkdocs_yaml(configs)
    generate_status_page(configs)

    print(f"\nGenerated {len(configs)} image docs")

if __name__ == "__main__":
    main()
