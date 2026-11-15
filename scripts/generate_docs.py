#!/usr/bin/env python3
"""
Generate Zensical documentation from compose.yaml files in daemonless repos.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import jinja2

# Paths - relative to daemonless-io repo (overridable for isolated worktrees)
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.resolve()
REPOS_DIR = Path(os.environ.get("REPOS_DIR", REPO_ROOT.parent)).expanduser().resolve()
DBUILD_REPO = Path(os.environ.get("DBUILD_REPO", REPOS_DIR / "dbuild")).expanduser().resolve()

if DBUILD_REPO.exists():
    sys.path.insert(0, str(DBUILD_REPO))
else:
    print(f"Error: dbuild repository not found at {DBUILD_REPO}")
    print("  Run 'make fetch' from the daemonless-io root to clone all required repositories.")
    sys.exit(1)

# pylint: disable=wrong-import-position
from dbuild.config import VALID_CATEGORIES, load as load_dbuild_config
from dbuild.docs import _enrich_metadata

TEMPLATE_DIR = DBUILD_REPO / "dbuild" / "templates"
LOCAL_TEMPLATE_DIR = SCRIPT_DIR / "templates"
DOCS_DIR = REPO_ROOT / "docs" / "images"

EXCLUDED_IMAGES = {"base-manifest-test"}
FEATURED_SLUGS = [
    "immich",
    "jellyfin",
    "plex",
    "nextcloud",
    "radarr",
    "sonarr",
    "grafana",
    "adguardhome",
    "tautulli",
    "uptime-kuma",
]

# Optional category / metadata preview overlay JSON for staging before repo rollout
_OVERLAY_PATH = os.environ.get("DAEMONLESS_CATEGORY_OVERLAY", "")
CATEGORY_OVERLAY = (
    json.loads(Path(_OVERLAY_PATH).expanduser().read_text(encoding="utf-8"))
    if _OVERLAY_PATH and Path(_OVERLAY_PATH).expanduser().is_file()
    else {}
)

# Local templates override dbuild templates
env = jinja2.Environment(
    loader=jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(str(LOCAL_TEMPLATE_DIR)),
        jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
    ])
)
template = env.get_template("README.mkdocs.j2")


def _apply_overlay(cfg, repo_name: str) -> None:
    """Apply optional preview metadata overrides in-memory without touching repos."""
    ov = CATEGORY_OVERLAY.get(repo_name)
    if not ov:
        return
    if "category" in ov:
        cfg.metadata.category = ov["category"]
    if "part_of" in ov:
        cfg.metadata.part_of = ov["part_of"]
    if "tags" in ov:
        cfg.metadata.tags = list(ov["tags"])
    if "type" in ov:
        cfg.type = ov["type"]
    if "image_class" in ov:
        cfg.metadata.image_class = ov["image_class"]
    if "notes" in ov:
        cfg.metadata.notes = ov["notes"]
    if "icon" in ov:
        cfg.metadata.icon = ov["icon"]


def _clean_manual_readme(text: str, config: dict) -> str:
    """Resolve legacy @PLACEHOLDER@ tokens in hand-maintained docs: manual READMEs."""
    app = config["name"]
    prefix = app.upper().replace("-", "_") + "_"
    replacements = {
        "@CONTAINER_CONFIG_ROOT@": "/containers",
        "@REGISTRY@": config.get("registry") or "ghcr.io/daemonless",
        "@PUID@": "1000",
        "@PGID@": "1000",
        "@TZ@": "UTC",
        "@INTERFACE@": "em0",
    }
    if config.get("default_port"):
        replacements[f"@{prefix}PORT@"] = str(config["default_port"])
    for k, v in replacements.items():
        text = text.replace(k, v)

    def _sub_path(m: re.Match) -> str:
        tok = m.group(1)
        if tok.startswith(prefix) and tok.endswith("_PATH"):
            sub = tok[len(prefix):-5].lower().replace("_", "-")
            return app if sub == "config" else f"{app}/{sub}"
        if tok.endswith("_PATH"):
            return f"/path/to/{tok[:-5].lower().replace('_', '/')}"
        return m.group(0)

    text = re.sub(r"@([A-Z][A-Z0-9_]+)@", _sub_path, text)
    text = re.sub(
        r"\n### Interactive Configuration\n.*?(?=\n## |\Z)",
        "\n",
        text,
        flags=re.S,
    )
    return text


def get_repo_config(repo_path: Path):
    """Load configuration using dbuild's native parser with explicit repo_dir."""
    try:
        cfg = load_dbuild_config(repo_path)
        if not cfg:
            return None

        _apply_overlay(cfg, repo_path.name)

        # Pass repo_dir explicitly so AppJail sidecars, service names, and base
        # versions resolve from the image repo instead of daemonless-io's cwd.
        context = _enrich_metadata(cfg, repo_dir=repo_path)

        if "registry" not in context:
            context["registry"] = cfg.registry or "ghcr.io/daemonless"

        context["type"] = cfg.type
        context["default_port"] = (
            str(context["ports"][0]["port"]) if context.get("ports") else ""
        )

        # Convert newlines to <br> so multiline descriptions display cleanly inside tables
        if context.get("description"):
            context["description"] = context["description"].strip().replace("\n", "<br>")

        return context
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error loading {repo_path.name}: {e}")
        return None


def generate_appliances_page(configs):
    """Generate docs/guides/appliances.md, filtered to type: appliance images."""
    try:
        tmpl = env.get_template("appliances.md.j2")
    except jinja2.TemplateNotFound:
        print("Warning: appliances.md.j2 not found, skipping Appliances page")
        return

    appliances = sorted(
        (c for c in configs if c.get("type") == "appliance"),
        key=lambda c: c["title"],
    )
    content = tmpl.render(appliances=appliances)

    out_path = REPO_ROOT / "docs" / "guides" / "appliances.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Generated {out_path} ({len(appliances)} appliance(s))")


def generate_status_page(configs):
    """Generate docs/images/index.md (catalog) and docs/status.md (version status)."""
    try:
        overview_tmpl = env.get_template("status.mkdocs.j2")
        version_tmpl = env.get_template("version-status.mkdocs.j2")
    except jinja2.TemplateNotFound as e:
        print(f"Warning: template not found ({e}), skipping status pages")
        return

    folded_children = {}
    for c in configs:
        if c.get("deprecated"):
            continue
        parent = c.get("part_of") or ""
        if parent:
            entry = folded_children.setdefault(
                parent,
                {"count": 0, "noun": "apps" if parent == "crafting-apps" else "parts", "names": []},
            )
            entry["count"] += 1
            entry["names"].append(c["title"])

    content = overview_tmpl.render(
        configs=configs,
        categories=[c for c in VALID_CATEGORIES if c != "Base"],
        folded_children=folded_children,
    )
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "index.md").write_text(content, encoding="utf-8")
    print("Generated docs/images/index.md")

    # Version status
    versions_file = REPO_ROOT / "daemonless-versions.json"
    last_check = "unknown"
    if versions_file.exists():
        last_check = json.loads(versions_file.read_text(encoding="utf-8")).get("last_check", "unknown")

    compare = SCRIPT_DIR / "compare-versions.py"
    cache_path = os.environ.get("COMPARE_VERSIONS_CACHE", "")
    version_data = {}
    if cache_path and Path(cache_path).is_file():
        version_data = json.loads(Path(cache_path).read_text(encoding="utf-8"))
    elif compare.exists() and versions_file.exists():
        result = subprocess.run([sys.executable, str(compare)], capture_output=True, text=True, check=False)
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.stdout.strip():
            version_data = json.loads(result.stdout)
            if cache_path:
                Path(cache_path).write_text(result.stdout, encoding="utf-8")

    last_updates = {c["name"]: c["last_update"] for c in configs}

    content = version_tmpl.render(
        last_check=last_check,
        last_updates=last_updates,
        configs=configs,
        **version_data,
    )
    (REPO_ROOT / "docs" / "status.md").write_text(content, encoding="utf-8")
    print("Generated docs/status.md")

    if versions_file.exists():
        (REPO_ROOT / "docs" / "daemonless-versions.json").write_text(
            versions_file.read_text(encoding="utf-8"), encoding="utf-8"
        )
        print("Published docs/daemonless-versions.json")


def _is_portrait(path: Path) -> bool:
    """Taller than 1.5x its width: a phone view or a full-page capture."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
        return h > 1.5 * w
    except Exception:
        return False


def _copy_or_compress_screenshot(src: Path, dst_dir: Path) -> str:
    """Copy screenshot, converting >1 MB raster PNG/JPEGs to crisp WebP."""
    if src.suffix.lower() in {".png", ".jpg", ".jpeg"} and src.stat().st_size > 1_000_000:
        try:
            from PIL import Image
            out_name = f"{src.stem}.webp"
            out_path = dst_dir / out_name
            with Image.open(src) as im:
                if im.mode == "P" and "transparency" in im.info:
                    im = im.convert("RGBA")
                elif im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
                if im.width > 1920:
                    ratio = 1920 / im.width
                    im = im.resize((1920, int(im.height * ratio)), Image.Resampling.LANCZOS)
                im.save(out_path, format="WEBP", quality=82, method=6)
            return out_name
        except Exception as exc:
            print(f"  warn: WebP conversion failed for {src.name} ({exc}), copying original")
    shutil.copy2(src, dst_dir / src.name)
    return src.name


GHCR = "ghcr.io"


def own_packages(config):
    """The ghcr.io package names this repo publishes."""
    registry = (config.get("registry") or "").rstrip("/")
    if not registry.startswith(GHCR + "/"):
        return []
    prefix = registry + "/"
    if config.get("type") == "stack":
        images = [p.get("image", "") for p in config.get("stack_parts") or []]
        return sorted({
            i[len(prefix):].split(":")[0].split("@")[0]
            for i in images
            if i.startswith(prefix)
        })
    return [config["name"]]


def pull_token_denied(package, org="daemonless"):
    """True when ghcr.io refuses an anonymous pull token for the package."""
    url = f"https://{GHCR}/token?scope=repository:{org}/{package}:pull&service={GHCR}"
    try:
        with urllib.request.urlopen(url, timeout=15):
            return False
    except urllib.error.HTTPError as e:
        return e.code == 403
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def unpublished(configs):
    """Names of images none of whose packages can be pulled yet."""
    todo = {c["name"]: own_packages(c) for c in configs}
    packages = sorted({p for ps in todo.values() for p in ps})
    with ThreadPoolExecutor(max_workers=12) as pool:
        denied = dict(zip(packages, pool.map(pull_token_denied, packages)))
    return {name for name, ps in todo.items() if ps and all(denied[p] for p in ps)}


def get_last_commit_date(repo_path: Path) -> str:
    """Get the last commit date for a repo in YYYY-MM-DD format."""
    try:
        for cmd in (
            ["git", "log", "-1", "--format=%cI"],
            ["git", "log", "-1", "--format=%cI", "."],
        ):
            result = subprocess.run(
                cmd, cwd=repo_path, capture_output=True, text=True, check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("T")[0]
    except Exception as e:
        print(f"Error getting git date for {repo_path.name}: {e}")

    try:
        for fname in ("compose.yaml", "README.md", "."):
            fpath = repo_path / fname
            if fpath.exists():
                mtime = fpath.stat().st_mtime
                return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        pass

    return "Unknown"


def generate_org_readme(configs):
    """Generate the GitHub Organization README (daemonless/README.md)."""
    if REPOS_DIR != REPO_ROOT.parent.resolve() and os.environ.get("WRITE_ORG_README") != "1":
        print("Skipping external Org README write (isolated REPOS_DIR mode)")
        return

    try:
        org_tmpl = env.get_template("ORGANIZATION_README.j2")
    except jinja2.TemplateNotFound:
        print("Warning: ORGANIZATION_README.j2 not found, skipping Org README")
        return

    by_category = {}
    for config in configs:
        cat = config.get("category", "Uncategorized")
        by_category.setdefault(cat, []).append(config)

    categories = [c for c in VALID_CATEGORIES if c in by_category]
    for cat in sorted(by_category.keys()):
        if cat not in categories:
            categories.append(cat)

    for cat in categories:
        by_category[cat].sort(key=lambda x: x["title"])

    content = org_tmpl.render(categories=categories, by_category=by_category)
    org_readme_path = REPOS_DIR / "daemonless" / "README.md"
    org_readme_path.write_text(content, encoding="utf-8")
    print(f"Updated {org_readme_path}")


def render_zensical_config(configs):
    """Render zensical.toml from scripts/templates/zensical.toml.j2."""
    try:
        tmpl = env.get_template("zensical.toml.j2")
    except jinja2.TemplateNotFound:
        print("Warning: zensical.toml.j2 not found, skipping config")
        return

    active = [c for c in configs if not c.get("deprecated")]
    by_cat = {}
    for c in active:
        cat = c.get("category") or "Uncategorized"
        by_cat.setdefault(cat, []).append(c)

    ordered_cats = [c for c in VALID_CATEGORIES if c in by_cat]
    for cat in sorted(by_cat):
        if cat not in ordered_cats:
            ordered_cats.append(cat)

    image_nav_groups = []
    total_entries = 0
    for cat in ordered_cats:
        items = [
            {
                "title": c["title"].replace("\\", "\\\\").replace('"', '\\"'),
                "name": c["name"],
            }
            for c in sorted(by_cat[cat], key=lambda x: x["title"].lower())
        ]
        total_entries += len(items)
        image_nav_groups.append({
            "category": cat.replace("\\", "\\\\").replace('"', '\\"'),
            "entries": items,
        })

    content = tmpl.render(image_nav_groups=image_nav_groups)
    if not content.endswith("\n"):
        content += "\n"
    (REPO_ROOT / "zensical.toml").write_text(content, encoding="utf-8")
    print(
        f"Generated zensical.toml ({total_entries} image nav entries across "
        f"{len(image_nav_groups)} categories)"
    )


def generate_homepage(configs):
    """Render the homepage template to docs/index.md."""
    try:
        tmpl = env.get_template("home.mkdocs.j2")
    except jinja2.TemplateNotFound:
        print("Warning: home.mkdocs.j2 not found, skipping homepage")
        return

    active = [c for c in configs if not c.get("deprecated")]
    by_name = {c["name"]: c for c in active}
    featured_apps = []
    for slug in FEATURED_SLUGS:
        c = by_name.get(slug)
        if c and c.get("screenshots"):
            featured_apps.append({
                "name": c["name"],
                "title": c["title"],
                "category": c.get("category", ""),
                "screenshot": c["screenshots"][0].lstrip("/"),
            })

    content = tmpl.render(active_count=len(active), featured_apps=featured_apps)
    (REPO_ROOT / "docs" / "index.md").write_text(content, encoding="utf-8")
    print(f"Generated docs/index.md (homepage, {len(active)} images)")


def main():
    """Main entry point for the documentation generator."""
    logos_dst = DOCS_DIR / "logos"
    if logos_dst.exists():
        shutil.rmtree(logos_dst)
    logos_dst.mkdir(parents=True, exist_ok=True)

    # Purge stale generated image markdown files before regenerating
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for stale_md in DOCS_DIR.glob("*.md"):
        if stale_md.name != "index.md":
            stale_md.unlink()

    configs = []
    loaded = []
    for repo in sorted(REPOS_DIR.iterdir()):
        if not repo.is_dir() or repo.name.startswith(".") or repo.name in EXCLUDED_IMAGES:
            continue

        is_image_repo = (
            (repo / "compose.yaml").exists()
            or (repo / ".daemonless" / "config.yaml").exists()
        )
        if not is_image_repo:
            continue

        config = get_repo_config(repo)
        if config and config.get("name") not in EXCLUDED_IMAGES:
            loaded.append((repo, config))

    hidden = unpublished([c for _, c in loaded])
    for repo, config in loaded:
        if config["name"] in hidden:
            print(f"Skipped {config['name']}: not published on {GHCR} yet")
            continue

        config["last_update"] = get_last_commit_date(repo)

        screenshot_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
        screenshots_src = repo / ".daemonless" / "screenshots"
        screenshots_dst = DOCS_DIR / "screenshots" / config["name"]
        screenshots = []
        if screenshots_src.exists():
            if screenshots_dst.exists():
                shutil.rmtree(screenshots_dst)
            screenshots_dst.mkdir(parents=True, exist_ok=True)
            for f in sorted(screenshots_src.iterdir()):
                if f.suffix.lower() not in screenshot_exts:
                    continue
                if _is_portrait(f):
                    print(f"  skip screenshot {config['name']}/{f.name}: taller than wide")
                    continue
                out_name = _copy_or_compress_screenshot(f, screenshots_dst)
                screenshots.append(f"/images/screenshots/{config['name']}/{out_name}")
        config["screenshots"] = screenshots

        logo_src = None
        for ext in (".svg", ".png"):
            candidate = repo / ".daemonless" / f"logo{ext}"
            if candidate.exists():
                logo_src = candidate
                break

        if logo_src:
            dst_name = f"{config['name']}{logo_src.suffix.lower()}"
            shutil.copy2(logo_src, logos_dst / dst_name)
            config["logo"] = dst_name
        else:
            config["logo"] = config.get("logo", "")

        logo_dark_src = None
        for ext in (".svg", ".png"):
            candidate = repo / ".daemonless" / f"logo-dark{ext}"
            if candidate.exists():
                logo_dark_src = candidate
                break

        if logo_dark_src:
            dst_dark_name = f"{config['name']}-dark{logo_dark_src.suffix.lower()}"
            shutil.copy2(logo_dark_src, logos_dst / dst_dark_name)
            config["logo_dark"] = dst_dark_name
        else:
            config["logo_dark"] = config.get("logo_dark", "")

        configs.append(config)

        try:
            out_path = DOCS_DIR / f"{config['name']}.md"
            docs_val = config.get("docs")
            is_manual = (
                docs_val == "manual"
                or (isinstance(docs_val, dict) and docs_val.get("manual", False))
            )
            if is_manual:
                readme_path = repo / "README.md"
                if readme_path.exists():
                    raw_md = readme_path.read_text(encoding="utf-8")
                    out_path.write_text(_clean_manual_readme(raw_md, config), encoding="utf-8")
                    print(f"Copied docs/images/{config['name']}.md (manual)")
                else:
                    print(f"Warning: {repo.name} has docs: manual but no README.md")
            else:
                mkdocs_content = template.render(config, render_mode="mkdocs")
                out_path.write_text(mkdocs_content, encoding="utf-8")
                print(f"Generated docs/images/{config['name']}.md")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error generating {config['name']}: {e}")

    if not configs:
        print("No configs found")
        return

    render_zensical_config(configs)
    generate_homepage(configs)
    generate_status_page(configs)
    generate_org_readme(configs)
    generate_appliances_page(configs)

    print(f"\nGenerated {len(configs)} image docs")


if __name__ == "__main__":
    main()
