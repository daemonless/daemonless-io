#!/usr/bin/env python3
"""
Sync documentation from repositories to website.
Scans cloned repos and parses Containerfile labels to generate docs/images/*.md files.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Optional

# Constants
REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "images"
REPOS_DIR = REPO_ROOT.parent

# Base images to skip (no user-facing docs)
SKIP_REPOS = {"base", "arr-base", "nginx-base"}


def parse_metadata_file(metadata_path: Path) -> dict:
    """Parse .daemonless/config.yml or .daemonless.yml metadata file."""
    try:
        with open(metadata_path, 'r') as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        print(f"Error parsing {metadata_path}: {e}")
        return {}


def parse_containerfile_labels(containerfile: Path) -> dict:
    """Parse labels from a Containerfile."""
    labels = {}
    if not containerfile.exists():
        return labels

    content = containerfile.read_text()

    # Match io.daemonless.* labels
    pattern = r'io\.daemonless\.([a-z-]+)="([^"]*)"'
    for match in re.finditer(pattern, content):
        key = match.group(1)
        value = match.group(2)
        if value.startswith("${"):
            continue
        labels[key] = value

    # Match org.opencontainers.image.title
    title_match = re.search(r'org\.opencontainers\.image\.title="([^"]*)"', content)
    if title_match:
        labels["title"] = title_match.group(1)

    # Match org.opencontainers.image.description
    desc_match = re.search(r'org\.opencontainers\.image\.description="([^"]*)"', content)
    if desc_match:
        labels["description"] = desc_match.group(1)
    
    # Match Parent (FROM ...)
    from_match = re.search(r"FROM\s+ghcr\.io/daemonless/([^:\s]+)", content)
    if from_match:
        labels["parent"] = from_match.group(1)

    labels["type"] = "image"
    return labels


def get_image_tags(repo_path: Path) -> list[str]:
    """Determine available tags based on Containerfile variants."""
    tags = ["latest"]
    if (repo_path / "Containerfile.pkg").exists():
        tags.append("pkg")
        tags.append("pkg-latest")
    return tags


def parse_readme_sections(content: str) -> list[dict]:
    """Parse markdown content into ordered sections based on H2 headers."""
    sections = []
    current_title = "Intro"
    current_key = "intro"
    buffer = []

    def flush():
        nonlocal buffer
        text = "\n".join(buffer).strip()
        if text:
            sections.append({
                "key": current_key,
                "title": current_title,
                "content": text
            })
        buffer = []

    for line in content.splitlines():
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            # Normalize key: lowercase and remove special chars for reliable matching
            current_key = current_title.lower()
        else:
            buffer.append(line)
    
    flush()
    return sections


def extract_port(sections_list: list[dict], labels_port: Optional[str]) -> Optional[str]:
    """Extract port number from labels or README sections."""
    # Prefer Containerfile label
    if labels_port:
        return labels_port.split(",")[0]  # First port if multiple

    # Helper to find content by key
    def get_content(key_part):
        for s in sections_list:
            if key_part in s["key"]:
                return s["content"]
        return ""

    # Fallback to README parsing
    ports_content = get_content("ports")
    if ports_content:
        match = re.search(r"\|\s*(\d+)\s*\|", ports_content)
        if match:
            return match.group(1)
        # Try simple list format
        match = re.search(r"-\s*`?(\d+)`?", ports_content)
        if match:
            return match.group(1)

    qs_content = get_content("quick start")
    if qs_content:
        match = re.search(r"-p\s+(\d+):", qs_content)
        if match:
            return match.group(1)

    return None


def generate_header_table(image_name: str, config: dict, port: Optional[str]) -> str:
    """Generate the summary table at the top of the page."""
    rows = []

    if port:
        rows.append(f"| **Port** | {port} |")

    if config.get("type") == "stack":
        rows.append("| **Type** | Bundle / Stack |")
    else:
        registry = f"`ghcr.io/daemonless/{image_name}`"
        rows.append(f"| **Registry** | {registry} |")

        tags = [f"`:{tag}`" for tag in config.get("tags", ["latest"])]
        rows.append(f"| **Tags** | {', '.join(tags)} |")

    rows.append(f"| **Source** | [github.com/daemonless/{image_name}](https://github.com/daemonless/{image_name}) |")

    return "\n".join([
        "| | |",
        "|---|---|",
        *rows
    ])


def process_image(name: str, config: dict):
    """Process a single image and generate its documentation page."""
    repo_path = REPOS_DIR / name
    readme_path = repo_path / "README.md"

    if not readme_path.exists():
        print(f"Skipping {name}: README not found")
        return

    print(f"Processing {name}...")

    content = readme_path.read_text()
    
    # Parse sections preserving order
    sections_list = parse_readme_sections(content)
    
    # Map for easy lookup of specific sections
    sections_map = {s["key"]: s for s in sections_list}

    # Extract title (H1)
    title_match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else name.capitalize()

    # Intro is usually the first section if it has key 'intro'
    intro = ""
    if sections_list and sections_list[0]["key"] == "intro":
        intro = sections_list[0]["content"]
        # Remove H1 if present in intro text
        intro = re.sub(r"^#\s+.*$\n", "", intro, flags=re.MULTILINE).strip()

    port = extract_port(sections_list, config.get("port"))

    # SEO: Generate Frontmatter
    seo_desc = config.get("description", f"FreeBSD container image for {title}.")
    # Pad description for SEO (Bing recommends ~160 chars)
    seo_suffix = " Run this application natively on FreeBSD using Podman and the Daemonless framework. Secure, lightweight, and automated."
    full_desc = f"{seo_desc.rstrip('.')} {seo_suffix}"
    
    # Start building content with Frontmatter
    new_content = [
        "---",
        f"title: {title} - FreeBSD OCI Container",
        f"description: {full_desc}",
        "---",
        "",
        f"# {title}\n", 
        intro + "\n"
    ]

    # Header Table
    new_content.append(generate_header_table(name, config, port) + "\n")

    # Special Warnings (ocijail)
    # Scan all content for keywords
    full_text = content.lower()
    if "ocijail" in full_text or "mlock" in full_text:
         # Double check context to avoid false positives? 
         # Assuming if it's mentioned, it's relevant.
         # But usually it's in a Notes section.
         if "requires" in full_text or "patch" in full_text or "annotation" in full_text:
            new_content.append('!!! warning "Requires patched ocijail"\n    This application requires the `allow.mlock` annotation.\n    See [ocijail patch](../guides/ocijail-patch.md).\n')

    # consumed_indices tracks which sections have been handled (Intro is handled)
    consumed_indices = {0} if sections_list and sections_list[0]["key"] == "intro" else set()

    # Deployment Tabs (Quick Start, Compose, Ansible)
    # We look for specific keys
    tabs = []
    
    # Helper to find index and content
    def find_section(key_sub, exclude_subs=None):
        for i, s in enumerate(sections_list):
            if i in consumed_indices:
                continue
            if key_sub in s["key"]:
                # Check exclusions
                if exclude_subs and any(ex in s["key"] for ex in exclude_subs):
                    continue
                return i, s
        return None, None

    # 1. Compose (Check first to catch "Quick Start (Compose)")
    idx, sect = find_section("compose")
    if sect:
        content_pc = "\n".join("    " + line for line in sect["content"].splitlines())
        tabs.append(f'=== "Compose"\n\n{content_pc}\n')
        consumed_indices.add(idx)

    # 2. Ansible
    idx, sect = find_section("ansible")
    if sect:
        content_ans = "\n".join("    " + line for line in sect["content"].splitlines())
        tabs.append(f'=== "Ansible"\n\n{content_ans}\n')
        consumed_indices.add(idx)

    # 3. Podman CLI (Quick Start - excluding compose/ansible if mixed)
    idx, sect = find_section("quick start", exclude_subs=["compose", "ansible"])
    if sect:
        content_qs = "\n".join("    " + line for line in sect["content"].splitlines())
        # Insert at the beginning if we want CLI first, or just append
        # Usually CLI is first tab.
        tabs.insert(0, f'=== "Podman CLI"\n\n{content_qs}\n')
        consumed_indices.add(idx)

    if tabs:
        new_content.append("## Quick Start\n")
        new_content.append("\n".join(tabs))

    # Append all other sections in original order
    for i, section in enumerate(sections_list):
        if i in consumed_indices:
            continue
        
        # Add the section
        new_content.append(f"## {section['title']}\n")
        new_content.append(section['content'] + "\n")

    # Write output
    out_path = DOCS_DIR / f"{name}.md"
    os.makedirs(out_path.parent, exist_ok=True)
    out_path.write_text("\n".join(new_content))


def generate_index_page(images: dict):
    """Generate docs/images/index.md."""
    lines = [
        "# Container Fleet",
        "",
        "Explore our collection of high-performance, FreeBSD-native OCI containers.",
        ""
    ]

    # Category Order
    categories = [
        "Infrastructure",
        "Network",
        "Media Management",
        "Downloaders",
        "Media Servers",
        "Databases",
        "Photos & Media",
        "Utilities",
        "Uncategorized"
    ]

    # Group images
    by_category = {}
    for name, config in images.items():
        cat = config.get("category", "Uncategorized")
        by_category.setdefault(cat, []).append((name, config))

    for cat in categories:
        img_list = by_category.get(cat)
        if not img_list:
            continue
        
        lines.append(f"## {cat}")
        lines.append("")

        # Check if we need .NET column (Media Management usually)
        is_dotnet_cat = (cat == "Media Management")
        
        header = "| Image | Port | Description |"
        separator = "|-------|------|-------------|"
        if is_dotnet_cat:
            header += " .NET |"
            separator += "------|"
        
        lines.append(header)
        lines.append(separator)

        for name, config in sorted(img_list):
            title = config.get("title", name.title())
            port = config.get("port", "-")
            desc = config.get("description", "")
            icon = config.get("icon", ":material-docker:")
            
            row = f"| [{icon} {title}]({name}.md) | {port} | {desc} |"
            
            if is_dotnet_cat:
                parent = config.get("parent", "")
                dotnet_mark = ":material-check:" if parent == "arr-base" else ""
                row += f" {dotnet_mark} |"
            
            lines.append(row)
        
        lines.append("")

    # Add Image Tags section
    lines.extend([
        "## Image Tags",
        "",
        "| Tag | Source | Description |",
        "|-----|--------|-------------|",
        "| `:latest` | Upstream releases | Newest version from project |",
        "| `:pkg` | FreeBSD quarterly | Stable, tested in ports |",
        "| `:pkg-latest` | FreeBSD latest | Rolling package updates |",
        ""
    ])

    out_path = DOCS_DIR / "index.md"
    out_path.write_text("\n".join(lines))


def discover_images() -> dict:
    """Scan repos directory and build image metadata from Containerfiles or .daemonless/config.yml."""
    images = {}

    if not REPOS_DIR.exists():
        print(f"Repos directory not found: {REPOS_DIR}")
        return images

    for repo_path in sorted(REPOS_DIR.iterdir()):
        if not repo_path.is_dir():
            continue

        name = repo_path.name
        if name in SKIP_REPOS:
            continue
        
        metadata = {}
        file_metadata = {}
        container_labels = {}

        # Check new path first, then legacy
        metadata_file = repo_path / ".daemonless" / "config.yml"
        if not metadata_file.exists():
            metadata_file = repo_path / ".daemonless.yml"
        containerfile = repo_path / "Containerfile"

        if metadata_file.exists():
            file_metadata = parse_metadata_file(metadata_file)
        
        if containerfile.exists():
            container_labels = parse_containerfile_labels(containerfile)

        # Merge: file metadata overrides container labels
        metadata = {**container_labels, **file_metadata}

        if not metadata:
            continue

        # Skip WIP images
        if metadata.get("wip") == "true":
            continue

        images[name] = {
            "category": metadata.get("category", "Uncategorized"),
            "port": metadata.get("port"),
            "tags": get_image_tags(repo_path) if metadata.get("type", "image") == "image" else [],
            "title": metadata.get("title", name.title()),
            "type": metadata.get("type", "image"),
            "description": metadata.get("description") or "",
            "parent": metadata.get("parent"),
            "icon": metadata.get("icon"),
        }

    return images


def generate_nav_entries(images: dict) -> list[str]:
    """Generate the YAML lines for the Images navigation section."""
    lines = ["  - Images:", "    - Overview: images/index.md"]

    # Group by category
    by_category: dict[str, list[str]] = {}
    for name, config in images.items():
        category = config.get("category", "Uncategorized")
        by_category.setdefault(category, []).append(name)

    # Sort categories and items
    for category in sorted(by_category.keys()):
        lines.append(f"    - {category}:")
        for name in sorted(by_category[category]):
            display_name = images[name].get("title", name.title())
            lines.append(f"      - {display_name}: images/{name}.md")

    return lines


def update_mkdocs_yml(images: dict):
    """Update the Images section in mkdocs.yml."""
    mkdocs_path = REPO_ROOT / "mkdocs.yml"
    lines = mkdocs_path.read_text().splitlines()

    new_lines = []
    in_images = False
    images_processed = False

    for line in lines:
        if line.strip() == "- Images:":
            in_images = True
            if not images_processed:
                new_lines.extend(generate_nav_entries(images))
                images_processed = True
            continue

        if in_images:
            # Check if we exited Images section (next top-level nav item)
            if re.match(r"^  - \w", line) and "Overview:" not in line:
                in_images = False
                new_lines.append(line)
        else:
            new_lines.append(line)

    mkdocs_path.write_text("\n".join(new_lines) + "\n")


def main():
    images = discover_images()

    if not images:
        print("No images found. Run fetch_repos.py first.")
        return

    print(f"Found {len(images)} images")

    # Generate Index Page
    generate_index_page(images)

    # Sync docs
    for name, config in images.items():
        process_image(name, config)

    # Update mkdocs navigation
    update_mkdocs_yml(images)

    print("Done.")


if __name__ == "__main__":
    main()
