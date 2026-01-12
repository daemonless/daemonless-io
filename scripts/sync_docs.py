#!/usr/bin/env python3
import os
import re
import yaml
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "images"
REPOS_DIR = REPO_ROOT.parent
SKIP_REPOS = set()

def parse_metadata_file(metadata_path: Path) -> dict:
    try:
        with open(metadata_path, 'r') as f:
            return yaml.safe_load(f)
    except:
        return {}

def parse_containerfile_labels(containerfile: Path) -> dict:
    labels = {}
    if not containerfile.exists(): return labels
    content = containerfile.read_text()
    args = {}
    for match in re.finditer(r'ARG\s+([A-Z0-9_]+)=([^\s\n]+)', content):
        args[match.group(1)] = match.group(2).strip('"\'')
    def substitute(value):
        for k, v in args.items():
            value = value.replace(f"${{{k}}}", v).replace(f"${k}", v)
        return value
    for match in re.finditer(r'io\.daemonless\.([a-z-]+)="([^"]*)"', content):
        labels[match.group(1)] = substitute(match.group(2))
    title_match = re.search(r'org\.opencontainers\.image\.title="([^"]*)"', content)
    if title_match: labels["title"] = substitute(title_match.group(1))
    desc_match = re.search(r'org\.opencontainers\.image\.description="([^"]*)"', content)
    if desc_match: labels["description"] = substitute(desc_match.group(1))
    from_match = re.search(r"FROM\s+ghcr\.io/daemonless/([^:\s]+)", content)
    if from_match: labels["parent"] = from_match.group(1)
    labels["type"] = "image"
    return labels

def get_image_tags(repo_path: Path) -> list[str]:
    tags = ["latest"]
    if (repo_path / "Containerfile.pkg").exists(): tags.extend(["pkg", "pkg-latest"])
    return tags

def parse_readme_sections(content: str) -> list[dict]:
    sections = []
    current_title, current_key, buffer = "Intro", "intro", []
    def flush():
        text = "\n".join(buffer).strip()
        if text: sections.append({"key": current_key, "title": current_title, "content": text})
    for line in content.splitlines():
        if line.startswith("## ") or line.startswith("### "):
            flush()
            current_title = line.lstrip("#").strip()
            current_key = current_title.lower()
            buffer = []
        else: buffer.append(line)
    flush()
    return sections

def extract_port(sections_list: list[dict], labels_port: Optional[str]) -> Optional[str]:
    if labels_port: return labels_port.split(",")[0]
    for s in sections_list:
        if "ports" in s["key"]:
            m = re.search(r"\|\s*(\d+)\s*\|", s["content"])
            if m: return m.group(1)
            m = re.search(r"-\s*`?(\d+)`?", s["content"])
            if m: return m.group(1)
    return None

def generate_header_table(image_name: str, config: dict, port_var: str) -> str:
    rows = [f"| **Port** | {port_var} |"]
    if config.get("type") == "stack": rows.append("| **Type** | Bundle / Stack |")
    else:
        rows.append(f"| **Registry** | `ghcr.io/daemonless/{image_name}` |")
        tags = [f"`:{tag}`" for tag in config.get("tags", ["latest"])]
        rows.append(f"| **Tags** | {', '.join(tags)} |")
    rows.append(f"| **Source** | [github.com/daemonless/{image_name}](https://github.com/daemonless/{image_name}) |")
    return "\n".join(["| | |", "|---|---|", *rows])

def process_image(name: str, config: dict):
    repo_path = REPOS_DIR / name
    readme_path = repo_path / "README.md"
    if not readme_path.exists(): return
    raw_content = readme_path.read_text()
    port_var = f"SET_{name.upper().replace('-', '_')}_PORT"
    content = raw_content.replace("SET_PORT", port_var)
    sections_list = parse_readme_sections(content)
    title_match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else name.capitalize()
    intro = sections_list[0]["content"] if sections_list and sections_list[0]["key"] == "intro" else ""
    intro = re.sub(r"^#\s+.*$\n", "", intro, flags=re.MULTILINE).strip()
    # Remove existing header table from intro
    if "| | |" in intro:
        intro = intro.split("| | |")[0].strip()
    port = extract_port(sections_list, config.get("port"))
    seo_suffix = " Run this application natively on FreeBSD using Podman and the Daemonless framework."
    full_desc = f"{config.get('description', '').rstrip('.')}.{seo_suffix}"
    new_content = ["---", f"title: {title} - FreeBSD OCI Container", f"description: {full_desc}", "---", "", f"# {title}\n", intro + "\n"]
    new_content.append(generate_header_table(name, config, port_var) + "\n")
    if any(x in content.lower() for x in ["ocijail", "mlock"]):
        new_content.append('!!! warning "Requires patched ocijail"\n    This application requires the `allow.mlock` annotation.\n    See [ocijail patch](../guides/ocijail-patch.md).\n')
    consumed_indices = {0} if sections_list and sections_list[0]["key"] == "intro" else set()
    tabs = []
    def find_section(key_sub, exclude=None):
        for i, s in enumerate(sections_list):
            if i not in consumed_indices and key_sub in s["key"]:
                if exclude and any(ex in s["key"] for ex in exclude): continue
                return i, s
        return None, None
    for key, label in [("compose", "Podman Compose"), ("ansible", "Ansible"), ("podman cli", "Podman CLI")]:
        idx, sect = find_section(key, exclude=["compose", "ansible"] if key=="podman cli" else None)
        if sect:
            c = "\n".join("    " + line for line in sect["content"].splitlines())
            if key == "podman cli": tabs.insert(0, f'=== "{label}"\n\n{c}\n')
            else: tabs.append(f'=== "{label}"\n\n{c}\n')
            consumed_indices.add(idx)
    if tabs:
        new_content.append("## Quick Start\n")
        new_content.append("\n".join(tabs))
    for i, section in enumerate(sections_list):
        if i not in consumed_indices:
            new_content.append(f"## {section['title']}\n")
            new_content.append(section['content'] + "\n")
    out_path = DOCS_DIR / f"{name}.md"
    os.makedirs(out_path.parent, exist_ok=True)
    out_path.write_text("\n".join(new_content))

def generate_index_page(images: dict):
    lines = ["# Container Fleet", "", "Explore our collection of high-performance, FreeBSD-native OCI containers.", ""]
    categories = ["Base", "Infrastructure", "Network", "Media Management", "Downloaders", "Media Servers", "Databases", "Photos & Media", "Utilities", "Uncategorized"]
    by_category = {}
    for name, config in images.items(): by_category.setdefault(config.get("category", "Uncategorized"), []).append((name, config))
    for cat in categories:
        img_list = by_category.get(cat)
        if not img_list: continue
        lines.extend([f"## {cat}", "", "| Image | Port | Description |", "|-------|------|-------------|"])
        for name, config in sorted(img_list):
            icon = config.get('icon', ':material-docker:')
            if not icon: icon = ':material-docker:'
            row = f"| [{icon} {config.get('title', name.title())}]({name}.md) | {config.get('port', '-')} | {config.get('description', '')} |"
            if cat == "Media Management": row += f" {':material-check:' if config.get('parent') == 'arr-base' else ''} |"
            lines.append(row)
        lines.append("")
    lines.extend(["## Image Tags", "", "| Tag | Source | Description |", "|-----|--------|-------------|", "| `:latest` | Upstream releases | Newest version from project |", "| `:pkg` | FreeBSD quarterly | Stable, tested in ports |", "| `:pkg-latest` | FreeBSD latest | Rolling package updates |", ""])
    (DOCS_DIR / "index.md").write_text("\n".join(lines))

def discover_images() -> dict:
    images = {}
    for repo_path in sorted(REPOS_DIR.iterdir()):
        if not repo_path.is_dir() or repo_path.name in SKIP_REPOS: continue
        
        m = {}
        # Priority 1: compose.yaml (x-daemonless)
        c_yaml = repo_path / "compose.yaml"
        if c_yaml.exists():
            try:
                with open(c_yaml, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'x-daemonless' in data:
                        m = data['x-daemonless']
            except: pass

        # Priority 2: .daemonless/config.yaml or .daemonless.yaml
        if not m:
            m_file = repo_path / ".daemonless" / "config.yaml"
            if not m_file.exists(): m_file = repo_path / ".daemonless.yaml"
            if m_file.exists():
                m = parse_metadata_file(m_file)

        # Fallback: Containerfile labels
        c_file = repo_path / "Containerfile"
        cont_m = parse_containerfile_labels(c_file) if c_file.exists() else {}
        m = {**cont_m, **m}
        
        if not m or m.get("wip") == "true": continue
        images[repo_path.name] = {"category": m.get("category", "Uncategorized"), "port": m.get("port"), "tags": get_image_tags(repo_path), "title": m.get("title", repo_path.name.title()), "type": m.get("type", "image"), "description": m.get("description") or "", "parent": m.get("parent"), "icon": m.get("icon")}
    return images

def update_mkdocs_yml(images: dict):
    mkdocs_path = REPO_ROOT / "mkdocs.yaml"
    lines = mkdocs_path.read_text().splitlines()
    new_lines, in_images, processed = [], False, False
    for line in lines:
        if line.strip() == "- Fleet:":
            in_images = True
            if not processed:
                new_lines.extend(["  - Fleet:", "    - Overview: images/index.md"])
                by_cat = {}
                for name, config in images.items(): by_cat.setdefault(config.get("category", "Uncategorized"), []).append(name)
                for cat in sorted(by_cat.keys()):
                    new_lines.append(f"    - {cat}:")
                    for name in sorted(by_cat[cat]): new_lines.append(f"      - {images[name].get('title', name.title())}: images/{name}.md")
                processed = True
            continue
        if in_images:
            if re.match(r"^  - \w", line) and "Overview:" not in line:
                in_images = False
                new_lines.append(line)
        else: new_lines.append(line)
    mkdocs_path.write_text("\n".join(new_lines) + "\n")

def update_placeholder_plugin_yaml(images: dict):
    plugin_path = REPO_ROOT / "placeholder-plugin.yaml"
    if not plugin_path.exists(): return
    
    try:
        with open(plugin_path, 'r') as f:
            data = yaml.safe_load(f) or {}
    except:
        data = {}

    if "placeholders" not in data:
        data["placeholders"] = {}

    for name, config in images.items():
        port = config.get("port")
        if not port: continue
        
        # Take the first port if multiple are listed (e.g., "7878/tcp")
        port = port.split(",")[0].split("/")[0]
        
        var_name = f"SET_{name.upper().replace('-', '_')}_PORT"
        title = config.get("title", name.title())
        
        data["placeholders"][var_name] = {
            "default": str(port),
            "description": f"{title} Host Port"
        }

    with open(plugin_path, 'w') as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)

def main():
    images = discover_images()
    if not images: return
    generate_index_page(images)
    for name, config in images.items(): process_image(name, config)
    update_mkdocs_yml(images)
    update_placeholder_plugin_yaml(images)

if __name__ == "__main__": main()