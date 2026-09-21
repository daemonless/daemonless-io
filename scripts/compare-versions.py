#!/usr/bin/env python3
"""
Compare daemonless-versions.json against what's actually published on ghcr.io.

Per-arch and label-based. The deployed version of every image is read from its
OCI `org.opencontainers.image.version` label, per architecture, by walking the
manifest list -- never parsed from tag names. Upstream targets come from
daemonless-versions.json:

  schema_version 2 : `pkg`/`pkg-latest` are {arch: version}; compared arch-for-arch.
  schema_version 1 : `pkg`/`pkg-latest` are scalars (amd64); compared against amd64.
  `upstream` (a binary release version) is always scalar and applies to every
  published arch.

Comparing each arch against the same arch means FreeBSD's aarch64 pkg lag (its
builder routinely trails amd64 on PORTREVISION bumps) no longer false-flags an
image as outdated, while a genuine per-arch miss still does.

Output JSON (contract consumed by version-status.mkdocs.j2 + the Discord notify):
  outdated   : [{name, updates: [{tag, arch, available, deployed}]}]
  current    : [name, ...]
  errors     : [{name, error}]
  warnings   : [{name, tag, reason}]
  deployed   : {name: {tag: display_version}}     # display = amd64 (or first) arch
  base_names : {name: base_repo}
  summary    : {current_count, outdated_count, error_count, warning_count}
"""

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

VERSIONS_FILE = Path(__file__).parent.parent / "daemonless-versions.json"
ORG = "daemonless"

# OCI reports FreeBSD arm64 as "arm64"; FreeBSD pkg repos call it "aarch64".
# daemonless-versions.json uses the pkg spelling, so normalise everything to it.
OCI_TO_PKG = {"amd64": "amd64", "arm64": "aarch64", "riscv64": "riscv64"}


def _sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


# --------------------------------------------------------------------------
# deployed: OCI version label, per arch, from the manifest list. No tag parsing.
# --------------------------------------------------------------------------
_deployed_cache = {}


def deployed_versions(repo, tag):
    """{pkg_arch: version} from each per-arch image's OCI version label.

    Empty dict means the tag doesn't exist on ghcr (or carries no version label).
    """
    key = (repo, tag)
    if key in _deployed_cache:
        return _deployed_cache[key]

    base = f"ghcr.io/{ORG}/{repo}"
    result = {}

    def label_of(ref):
        try:
            cfg = json.loads(_sh(f"skopeo inspect docker://{ref}") or "{}")
        except json.JSONDecodeError:
            return None, None
        return cfg.get("Architecture"), (cfg.get("Labels") or {}).get(
            "org.opencontainers.image.version"
        )

    try:
        raw = json.loads(_sh(f"skopeo inspect --raw docker://{base}:{tag}") or "{}")
    except json.JSONDecodeError:
        raw = {}

    manifests = raw.get("manifests")
    if manifests:  # multi-arch manifest list -> read each per-arch image's label
        for m in manifests:
            plat = m.get("platform", {})
            arch = plat.get("architecture")
            if plat.get("os") != "freebsd" or arch not in OCI_TO_PKG:
                continue  # skip attestations / non-freebsd entries
            _, ver = label_of(f"{base}@{m['digest']}")
            if ver:
                result[OCI_TO_PKG[arch]] = ver
    else:  # single-arch image (or tag missing -> empty label)
        arch, ver = label_of(f"{base}:{tag}")
        if arch in OCI_TO_PKG and ver:
            result[OCI_TO_PKG[arch]] = ver

    _deployed_cache[key] = result
    return result


# --------------------------------------------------------------------------
# manifest digest, for telling a real tag alias from a version coincidence
# --------------------------------------------------------------------------
_digest_cache = {}


def tag_digest(repo, tag):
    """Manifest digest of ghcr.io/<org>/<repo>:<tag>, or "" if it doesn't resolve."""
    key = (repo, tag)
    if key not in _digest_cache:
        _digest_cache[key] = _sh(
            f"skopeo inspect --format '{{{{.Digest}}}}' docker://ghcr.io/{ORG}/{repo}:{tag}"
        ).strip()
    return _digest_cache[key]


def aliases_pkg_build(repo, binary_tag, variant):
    """True iff `binary_tag` is the very same image as a pkg tag.

    Some images pin :latest to their pkg build (emby), so the binary `upstream`
    version says nothing about them. Identity has to come from the manifest
    digest: an upstream-binary :latest frequently happens to carry the same
    version string as :pkg-latest -- the port packaged the release we last
    built -- and treating that coincidence as an alias hides every later
    update, silently and permanently.
    """
    mine = tag_digest(repo, binary_tag)
    if not mine:
        return False
    for bt in ("pkg", "pkg-latest"):
        for cand in registry_tags(variant, bt):
            if tag_digest(repo, cand) == mine:
                return True
    return False


# --------------------------------------------------------------------------
# version comparison (FreeBSD X.Y.Z_PORTREVISION aware)
# --------------------------------------------------------------------------
def normalize_version(v):
    if not v:
        return ""
    return v.lstrip("v").replace(",", "_")


def parse_version_tuple(v):
    v = normalize_version(v)
    revision = 0
    if "_" in v:
        v, rev = v.rsplit("_", 1)
        if rev.isdigit():
            revision = int(rev)
    parts = []
    for part in re.split(r"[.\-]", v):
        parts.append(int(part) if part.isdigit() else part)
    return (parts, revision)


def is_newer(available, deployed):
    """True iff `available` is strictly newer than `deployed`.

    Equal, deployed-ahead, or not confidently orderable -> not outdated (quiet).
    """
    a, d = normalize_version(available), normalize_version(deployed)
    if not a or a == d:
        return False
    try:
        return parse_version_tuple(a) > parse_version_tuple(d)
    except TypeError:
        return False


# --------------------------------------------------------------------------
# upstream target normalisation + registry-tag derivation
# --------------------------------------------------------------------------
def upstream_map(entry, is_binary, deployed_arches):
    """Normalise a versions.json entry to {arch: version}.

    - dict            -> schema-2 per-arch pkg target, used as-is.
    - scalar + binary -> a release version; applies to every published arch.
    - scalar + pkg    -> schema-1 amd64-only target.
    """
    if isinstance(entry, dict):
        return dict(entry)
    if is_binary:
        return {arch: entry for arch in deployed_arches}
    return {"amd64": entry}


def registry_tags(variant, build_type):
    """Ordered candidate registry tags for a (variant, build_type); the first
    that resolves on ghcr wins. We don't assume a "-pkg" suffix: for a
    multi-version image's base pkg flavor we also try the bare variant tag,
    because some images publish it that way (cnpg-postgres "17"/"17-standard",
    not "17-pkg") while others alias to "17-pkg". Non-base flavors
    (pkg-latest, pkg-krb, ...) keep their explicit suffix so we never mistake
    them for the base tag.
    """
    if build_type == "upstream":
        return [f"{variant}-latest"] if variant else ["latest"]
    if not variant:
        return [build_type]  # plain image: "pkg" / "pkg-latest"
    tags = [f"{variant}-{build_type}"]
    if build_type == "pkg":
        tags.append(variant)  # base flavor may be published as the bare tag
    return tags


def check_service(name, versions):
    """Compare one (expanded) service against ghcr. Pure per-image work so it
    can run in a thread pool -- each call only does independent skopeo reads."""
    base = versions.get("_base_name", name)
    variant = versions.get("_variant")
    broken = versions.get("_broken", [])

    # Build types to check: every non-meta key except `upstream`, which is
    # tracked under the `latest` display tag.
    checks = [
        (bt, bt, False)
        for bt in versions
        if not bt.startswith("_") and bt not in ("upstream", "type")
    ]
    if "upstream" in versions:
        checks.append(("latest", "upstream", True))

    display, updates, warns, saw_any = {}, [], [], False
    for tag_key, entry_key, is_binary in checks:
        dep, resolved_tag = {}, None
        for cand in registry_tags(variant, entry_key):
            dep = deployed_versions(base, cand)
            if dep:
                resolved_tag = cand
                break
        if not dep:
            continue  # this variant/arch isn't published
        saw_any = True
        display[tag_key] = dep.get("amd64") or next(iter(dep.values()))

        if tag_key in broken:
            warns.append({"name": name, "tag": tag_key, "reason": "build broken"})
            continue

        # A `latest` that is literally the pkg image tracks the FreeBSD package,
        # not the binary `upstream` -- skip that comparison; the pkg tag's own
        # check covers it. Decided by manifest digest, never by version string.
        if is_binary and aliases_pkg_build(base, resolved_tag, variant):
            continue

        up = upstream_map(versions[entry_key], is_binary, list(dep))
        for arch in sorted(dep):
            target = up.get(arch)
            if target and is_newer(target, dep[arch]):
                updates.append(
                    {"tag": tag_key, "arch": arch,
                     "available": target, "deployed": dep[arch]}
                )

    return {"name": name, "base": base, "display": display,
            "updates": updates, "warnings": warns, "saw_any": saw_any}


# --------------------------------------------------------------------------
def main():
    data = json.loads(VERSIONS_FILE.read_text())
    services = data.get("services", {})

    # Expand multi-version services into per-variant entries (postgres-14, ...),
    # tracking the base repo so the renderer can group + link them.
    expanded = {}
    for name, versions in services.items():
        if versions.get("type") == "multi-version":
            for vid, vv in versions.get("variants", {}).items():
                expanded[f"{name}-{vid}"] = {"_base_name": name, "_variant": vid, **vv}
            base = {
                k: v
                for k, v in versions.items()
                if k not in ("type", "variants", "default", "upstream")
                and not k.startswith("_")
            }
            if base:
                entry = base.copy()
                if "upstream" in versions:
                    entry["upstream"] = versions["upstream"]
                expanded[name] = entry
        else:
            expanded[name] = versions

    # Each service is independent I/O (skopeo reads) -> run them concurrently.
    # ThreadPoolExecutor.map preserves input order, so output stays deterministic.
    workers = int(os.environ.get("COMPARE_WORKERS", "12"))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda kv: check_service(*kv), sorted(expanded.items())))

    outdated, current, errors, warnings = [], [], [], []
    deployed_all, base_names = {}, {}
    for r in results:
        name = r["name"]
        base_names[name] = r["base"]
        warnings.extend(r["warnings"])
        if not r["saw_any"]:
            errors.append({"name": name, "error": "No published tags found on ghcr.io"})
            continue
        deployed_all[name] = r["display"]
        if r["updates"]:
            outdated.append({"name": name, "updates": r["updates"]})
        else:
            current.append(name)

    total_tags = sum(len(v) for v in deployed_all.values())
    outdated_tags = sum(len(item["updates"]) for item in outdated)

    print(json.dumps({
        "schema_version": data.get("schema_version", 1),
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
            "warning_count": len(warnings),
        },
    }, indent=2))

    sys.exit(1 if outdated else 0)


if __name__ == "__main__":
    main()
