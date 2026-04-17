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
            # Multi-version mode: discover all build types by scanning for {variant}-*
            # alias tags, then read the version from the co-located version tag.
            # Works for both postgres-style (14.22-14-pkg, alias=14-pkg) and
            # samba-style (4.16.11_10-pkg, alias=416-pkg; 4.22.7_1-422-pkg-krb, alias=422-pkg-krb).
            prefix = f"{variant}-"
            for tag in tags:
                if not tag.startswith(prefix):
                    continue
                build_type = tag[len(prefix):]  # "pkg", "pkg-latest", "pkg-krb", etc.
                if build_type in deployed:
                    continue
                alias = tag
                suffix = f"-{alias}"  # e.g. "-422-pkg-krb"
                # Primary: version tag embeds variant (e.g. 4.22.7_1-422-pkg-krb)
                for t in tags:
                    if t != alias and t.endswith(suffix):
                        deployed[build_type] = t[:-len(suffix)]
                        break
                # Fallback: variant is an alias for a plain-named tag
                # (e.g. 4.16.11_10-pkg when alias is 416-pkg, variant tag is pkg)
                if build_type not in deployed:
                    plain_suffix = f"-{build_type}"
                    for t in tags:
                        if t != alias and t not in (build_type, "latest") and t.endswith(plain_suffix):
                            deployed[build_type] = t.removesuffix(plain_suffix)
                            break
        else:
            # Standard single-version mode: find the digest that carries each alias,
            # then read the version from the co-located version tag on that digest.
            if "pkg-latest" in tags and "pkg-latest" not in deployed:
                for t in tags:
                    if t != "pkg-latest" and t.endswith("-pkg-latest"):
                        deployed["pkg-latest"] = t.removesuffix("-pkg-latest")
                        if has_latest:
                            latest_is_pkg = True
                        break
            if "pkg" in tags and "pkg" not in deployed:
                for t in tags:
                    if t != "pkg" and t.endswith("-pkg"):
                        deployed["pkg"] = t.removesuffix("-pkg")
                        if has_latest:
                            latest_is_pkg = True
                        break
            if "latest" in tags and "latest" not in deployed and not latest_is_pkg:
                for t in tags:
                    if t not in ("latest", "pkg", "pkg-latest") and not t.endswith(("-pkg", "-pkg-latest")):
                        deployed["latest"] = t
                        break

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

        # Check all tracked build types
        for build_type, available in versions.items():
            if build_type.startswith("_") or build_type == "upstream":
                continue
            if build_type in deployed:
                if not versions_match(available, deployed[build_type]):
                    service_outdated.append({
                        "tag": build_type,
                        "available": available,
                        "deployed": deployed[build_type]
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
