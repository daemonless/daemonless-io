#!/usr/bin/env python3
"""
Fetch all image repositories from the daemonless GitHub organization.
Uses GitHub API to discover repos dynamically.
"""

import json
import os
import subprocess
import urllib.request
from pathlib import Path

# Constants
REPO_ROOT = Path(__file__).parent.parent
TARGET_REPOS_DIR = REPO_ROOT.parent

# Repos to skip (meta repos, not container images)
SKIP_REPOS = {"daemonless", "daemonless-io"}

def get_org_repos(org: str = "daemonless") -> list[str]:
    """Get list of public repos from GitHub org using the REST API."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?type=public&per_page=100&page={page}"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            print(f"Failed to list repos: {e}")
            return []
        if not data:
            break
        repos.extend(r["name"] for r in data)
        if len(data) < 100:
            break
        page += 1
    return repos

def clone_repo(name: str, org: str = "daemonless"):
    """Clone a single repo."""
    repo_url = f"https://github.com/{org}/{name}.git"
    target_path = TARGET_REPOS_DIR / name

    if target_path.exists():
        print(f"Updating {name}...")
        try:
            subprocess.run(
                ["git", "-C", str(target_path), "pull", "--ff-only"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to update {name}: {e}")
        return

    print(f"Cloning {name}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target_path)],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone {name}: {e}")

def main():
    os.makedirs(TARGET_REPOS_DIR, exist_ok=True)

    repos = get_org_repos()
    if not repos:
        print("No repos found or failed to fetch repo list")
        return

    for name in repos:
        if name in SKIP_REPOS:
            continue
        clone_repo(name)

    print(f"Done. Repos cloned to {TARGET_REPOS_DIR}")

if __name__ == "__main__":
    main()
