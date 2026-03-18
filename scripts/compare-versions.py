#!/usr/bin/env python3
"""
Compare daemonless-versions.json against deployed ghcr.io tags.
Outputs JSON with outdated, current, errors, and summary.
"""

import json
import subprocess
import sys
import re
from pathlib import Path

VERSIONS_FILE = Path(__file__).parent.parent / "daemonless-versions.json"
ORG = "daemonless"

def get_deployed_versions(package: str, variant: str = None) -> dict:
    """Get currently deployed versions from ghcr.io tags.

    If variant is specified (e.g., "14" for postgres), only look for tags
    matching that variant (14-pkg, 14-pkg-latest, 14.x.x).
    """
    try:
        # Get all version info with tags grouped
        result = subprocess.run(
            ["gh", "api", f"/orgs/{ORG}/packages/container/{package}/versions",
             "--jq", '.[] | {tags: .metadata.container.tags}'],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return {}

    deployed = {}
    latest_is_pkg = False  # Track if 'latest' is aliased to a pkg build

    for line in lines:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            tags = data.get("tags", [])
        except json.JSONDecodeError:
            continue

        # Check if this version has the 'latest' alias alongside a pkg tag
        has_latest = "latest" in tags

        if variant:
            # Multi-version mode: look for variant-specific tags
            for tag in tags:
                # Version tags from push.py: {version}-{variant_tag}
                # e.g., "14.20_1-14-pkg-latest", "14.20_1-14", "11.4.9-11.4-pkg-latest"
                suffix_pkg_latest = f"-{variant}-pkg-latest"
                suffix_pkg = f"-{variant}-pkg"
                suffix_variant = f"-{variant}"

                if tag.endswith(suffix_pkg_latest) and tag.startswith(f"{variant}."):
                    version = tag[: -len(suffix_pkg_latest)]
                    if "pkg-latest" not in deployed:
                        deployed["pkg-latest"] = version
                elif tag.endswith(suffix_pkg) and tag.startswith(f"{variant}."):
                    version = tag[: -len(suffix_pkg)]
                    if "pkg" not in deployed:
                        deployed["pkg"] = version
                # Legacy: "14.20-pkg-latest" (without variant in suffix)
                elif tag.endswith("-pkg-latest") and tag.startswith(f"{variant}."):
                    version = tag.replace("-pkg-latest", "")
                    if "pkg-latest" not in deployed:
                        deployed["pkg-latest"] = version
                elif tag.endswith("-pkg") and tag.startswith(f"{variant}."):
                    version = tag.replace("-pkg", "")
                    if "pkg" not in deployed:
                        deployed["pkg"] = version
                # Plain version tag: "14.20_1-14" or "14.20"
                elif tag.endswith(suffix_variant) and tag.startswith(f"{variant}."):
                    version = tag[: -len(suffix_variant)]
                    if "pkg" not in deployed:
                        deployed["pkg"] = version
                elif tag.startswith(f"{variant}.") and "-" not in tag:
                    if "pkg" not in deployed:
                        deployed["pkg"] = tag
                    if "pkg-latest" not in deployed:
                        deployed["pkg-latest"] = tag
        else:
            # Standard single-version mode
            for tag in tags:
                if tag in ("latest", "pkg", "pkg-latest"):
                    continue
                if tag.endswith("-pkg-latest"):
                    # Only set if not already set (newest first from API)
                    if "pkg-latest" not in deployed:
                        deployed["pkg-latest"] = tag.replace("-pkg-latest", "")
                    if has_latest:
                        latest_is_pkg = True
                elif tag.endswith("-pkg"):
                    if "pkg" not in deployed:
                        deployed["pkg"] = tag.replace("-pkg", "")
                    if has_latest:
                        latest_is_pkg = True
                elif not "-" in tag or re.match(r"^\d+\.\d+", tag):
                    # Version tag without suffix = latest/upstream
                    if "latest" not in deployed and not latest_is_pkg:
                        deployed["latest"] = tag

            # If latest is just an alias to pkg, don't track it separately
            if latest_is_pkg:
                deployed.pop("latest", None)

    return deployed


def normalize_version(v: str) -> str:
    """Normalize version for comparison (strip 'v' prefix, handle epoch commas, etc)."""
    if not v:
        return ""
    v = v.lstrip("v")
    # Convert commas to underscores (OCI tags can't have commas)
    v = v.replace(",", "_")
    return v


def versions_match(available: str, deployed: str) -> bool:
    """Check if versions match (with normalization)."""
    return normalize_version(available) == normalize_version(deployed)


def main():
    outdated = []
    current = []
    errors = []
    deployed_all = {}  # name -> {tag: version} for all services
    base_names = {}   # name -> base repo name (for multi-variant images)

    with open(VERSIONS_FILE) as f:
        data = json.load(f)

    services = data.get("services", {})

    # Expand multi-version services into separate entries
    expanded_services = {}
    for name, versions in services.items():
        if versions.get("type") == "multi-version":
            # Expand variants into separate entries (e.g., postgres-14, postgres-17)
            for variant_id, variant_versions in versions.get("variants", {}).items():
                expanded_name = f"{name}-{variant_id}"
                expanded_services[expanded_name] = {
                    "_base_name": name,
                    "_variant": variant_id,
                    **variant_versions
                }
        else:
            expanded_services[name] = versions

    for name, versions in sorted(expanded_services.items()):
        base_name = versions.get("_base_name", name)
        variant = versions.get("_variant")

        deployed = get_deployed_versions(base_name, variant)
        deployed_all[name] = deployed
        base_names[name] = base_name

        if not deployed:
            errors.append({"name": name, "error": "No tags found in ghcr.io"})
            continue

        service_outdated = []

        # Check pkg
        if "pkg" in versions and "pkg" in deployed:
            if not versions_match(versions["pkg"], deployed["pkg"]):
                service_outdated.append({
                    "tag": "pkg",
                    "available": versions["pkg"],
                    "deployed": deployed["pkg"]
                })

        # Check pkg-latest
        if "pkg-latest" in versions and "pkg-latest" in deployed:
            if not versions_match(versions["pkg-latest"], deployed["pkg-latest"]):
                service_outdated.append({
                    "tag": "pkg-latest",
                    "available": versions["pkg-latest"],
                    "deployed": deployed["pkg-latest"]
                })

        # Check upstream (latest tag)
        if "upstream" in versions and "latest" in deployed:
            if not versions_match(versions["upstream"], deployed["latest"]):
                service_outdated.append({
                    "tag": "latest",
                    "available": versions["upstream"],
                    "deployed": deployed["latest"]
                })

        if service_outdated:
            outdated.append({"name": name, "updates": service_outdated})
        else:
            current.append(name)

    total_tags = sum(len(v) for v in deployed_all.values())
    outdated_tags = sum(len(item["updates"]) for item in outdated)

    print(json.dumps({
        "outdated": outdated,
        "current": current,
        "errors": errors,
        "deployed": deployed_all,
        "base_names": base_names,
        "summary": {
            "current_count": total_tags - outdated_tags,
            "outdated_count": outdated_tags,
            "error_count": len(errors)
        }
    }, indent=2))

    sys.exit(1 if outdated else 0)


if __name__ == "__main__":
    main()
