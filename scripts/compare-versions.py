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
    all_tags = set()       # Flat union of every tag across all digests
    ARCH_SUFFIXES = ("-aarch64", "-riscv64")

    for line in lines:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            tags = data.get("tags", [])
        except json.JSONDecodeError:
            continue

        all_tags.update(tags)

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
                # Fallback 1: variant is an alias for a plain-named tag
                # (e.g. 4.16.11_10-pkg when alias is 416-pkg, variant tag is pkg)
                if build_type not in deployed:
                    plain_suffix = f"-{build_type}"
                    for t in tags:
                        if t != alias and t not in (build_type, "latest") and t.endswith(plain_suffix):
                            deployed[build_type] = t.removesuffix(plain_suffix)
                            break
                # Fallback 2: version tag ends in just the variant id, not the full alias
                # (e.g. postgres: alias=14-pkg, version tag=14.22-14, ends in "-14" not "-14-pkg")
                if build_type not in deployed:
                    id_suffix = f"-{variant}"
                    for t in tags:
                        if t != alias and t not in (build_type, "latest", variant) and t.endswith(id_suffix):
                            deployed[build_type] = t[:-len(id_suffix)]
                            break
        else:
            # 'latest' is a pkg alias when it shares a digest with pkg/pkg-latest
            # (this co-location survives multi-arch: both ride the manifest digest).
            if "latest" in tags and (
                "pkg" in tags
                or "pkg-latest" in tags
                or any(t.endswith(("-pkg", "-pkg-latest")) for t in tags)
            ):
                latest_is_pkg = True

    if not variant:
        # Pair alias -> version tag by name across ALL digests, not by same-digest
        # co-location: multi-arch manifests own the aliases while `<ver>-pkg` tags
        # stay on the per-arch image digests. Highest version wins so stale leftover
        # tags can't. Arch-suffixed tags don't end in `-pkg`, so they self-exclude.
        def _best(suffix: str) -> str:
            cands = [
                t.removesuffix(suffix)
                for t in all_tags
                if t not in ("pkg", "pkg-latest", "latest") and t.endswith(suffix)
            ]
            if not cands:
                return None
            try:
                return max(cands, key=parse_version_tuple)
            except TypeError:
                return cands[0]

        if "pkg-latest" in all_tags:
            v = _best("-pkg-latest")
            if v is not None:
                deployed["pkg-latest"] = v
        if "pkg" in all_tags:
            v = _best("-pkg")  # `<ver>-pkg-latest` ends in `-latest`, won't match
            if v is not None:
                deployed["pkg"] = v
        if "latest" in all_tags and not latest_is_pkg:
            # Highest bare version = current :latest build; ghcr keeps old bare
            # tags (0.107.74 ... 0.107.77), so first-from-set would pick a stale one.
            cands = [
                t for t in all_tags
                if t not in ("latest", "pkg", "pkg-latest")
                and not t.endswith(("-pkg", "-pkg-latest"))
                and not t.endswith(ARCH_SUFFIXES)
            ]
            if cands:
                try:
                    deployed["latest"] = max(cands, key=parse_version_tuple)
                except TypeError:
                    deployed["latest"] = cands[0]

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


def parse_version_tuple(v: str):
    """Parse a version string into a comparable tuple.

    Handles FreeBSD pkg versioning: X.Y.Z_PORTREVISION
    e.g. "4.23.6_1" -> ((4, 23, 6), 1)
         "4.23.7"   -> ((4, 23, 7), 0)
    """
    v = normalize_version(v)
    revision = 0
    if "_" in v:
        v, rev = v.rsplit("_", 1)
        try:
            revision = int(rev)
        except ValueError:
            pass
    parts = []
    for part in re.split(r"[.\-]", v):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(part)
    return (parts, revision)


def versions_match(available: str, deployed: str) -> bool:
    """Return True if versions match or deployed is already newer than available."""
    a = normalize_version(available)
    d = normalize_version(deployed)
    if a == d:
        return True
    # If what's deployed is already newer, don't flag as outdated
    try:
        if parse_version_tuple(d) > parse_version_tuple(a):
            return True
    except Exception:
        pass
    return False


def main():
    outdated = []
    current = []
    errors = []
    warnings = []
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
            # Also expand top-level pkg/pkg-latest as a plain base entry
            base = {k: v for k, v in versions.items()
                    if k not in ("type", "variants", "default", "upstream") and not k.startswith("_")}
            if base:
                entry = base.copy()
                if "upstream" in versions:
                    entry["upstream"] = versions["upstream"]
                expanded_services[name] = entry
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
        broken = versions.get("_broken", [])

        # Check all tracked build types
        for build_type, available in versions.items():
            if build_type.startswith("_") or build_type == "upstream":
                continue
            if build_type in broken:
                warnings.append({"name": name, "tag": build_type, "reason": "build broken"})
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
        "warnings": warnings,
        "deployed": deployed_all,
        "base_names": base_names,
        "summary": {
            "current_count": total_tags - outdated_tags,
            "outdated_count": outdated_tags,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }
    }, indent=2))

    sys.exit(1 if outdated else 0)


if __name__ == "__main__":
    main()
