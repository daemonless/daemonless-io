#!/usr/bin/env python3
"""
Fetch all image repositories from the daemonless GitHub organization.
Uses GitHub API to discover repos dynamically.
"""

import os
import subprocess
from pathlib import Path

# Constants
REPO_ROOT = Path(__file__).parent.parent
TARGET_REPOS_DIR = REPO_ROOT.parent

# Repos to skip (meta repos, not container images)
SKIP_REPOS = {"daemonless", "daemonless-io"}

def get_org_repos(org: str = "daemonless") -> list[str]:
    """Get list of repos from GitHub org using gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "repo", "list", org, "--json", "name", "-q", ".[].name", "-L", "100"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to list repos: {e}")
        return []
    except FileNotFoundError:
        print("Error: 'gh' CLI not found. Install GitHub CLI or set GH_TOKEN.")
        return []

def clone_repo(name: str, org: str = "daemonless"):
    """Clone a single repo."""
    repo_url = f"https://github.com/{org}/{name}.git"
    target_path = TARGET_REPOS_DIR / name

    if target_path.exists():
        print(f"Skipping {name}: already exists")
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
