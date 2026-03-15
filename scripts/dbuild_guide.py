#!/usr/bin/env python3
"""
Generate static dbuild guide pages from source code using Jinja2 templates.
"""
import sys
import argparse
import shutil
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = SCRIPT_DIR / "templates"
REPO_ROOT = SCRIPT_DIR.parent
REPOS_DIR = REPO_ROOT.parent
DBUILD_REPO = (REPOS_DIR / "dbuild").resolve()
GUIDES_DIR = REPO_ROOT / "docs" / "guides"
DBUILD_GUIDES_DIR = GUIDES_DIR / "dbuild"

if DBUILD_REPO.exists():
    sys.path.insert(0, str(DBUILD_REPO))
else:
    print(f"Error: dbuild repository not found at {DBUILD_REPO}")
    sys.exit(1)

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 is required to run this script. Run: pip install jinja2")
    sys.exit(1)

def generate():
    try:
        from dbuild.cli import _make_parser
        from dbuild.docs import DOCS_CONTENT
    except ImportError as e:
        print(f"Error: Could not import dbuild: {e}")
        return

    DBUILD_GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    parser = _make_parser()

    # 1. Generate index.md
    index_template = env.get_template("index.md.j2")
    index_content = index_template.render(examples=DOCS_CONTENT["EXAMPLES"])
    (DBUILD_GUIDES_DIR / "index.md").write_text(index_content)
    print(f"Updated {DBUILD_GUIDES_DIR / 'index.md'}")

    # 2. Generate commands.md
    commands_data = []
    subparsers = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
    for subparser_action in subparsers:
        for choice, subparser in sorted(subparser_action.choices.items()):
            if choice == "docs": continue
            
            cmd_info = {
                "description": subparser.description or subparser.help or "",
                "options": []
            }
            
            seen_actions = set()
            for action in subparser._option_string_actions.values():
                if action not in seen_actions:
                    opts = ", ".join(f"`{o}`" for o in action.option_strings)
                    help_text = (action.help or "").replace('%(default)s', str(action.default))
                    cmd_info["options"].append((opts, help_text))
                    seen_actions.add(action)
            
            commands_data.append((choice, cmd_info))

    commands_template = env.get_template("commands.md.j2")
    commands_content = commands_template.render(commands=commands_data)
    (DBUILD_GUIDES_DIR / "commands.md").write_text(commands_content)
    print(f"Generated {DBUILD_GUIDES_DIR / 'commands.md'}")

    # 3. Generate config.md
    config_template = env.get_template("config.md.j2")
    config_content = config_template.render(
        environment=DOCS_CONTENT["ENVIRONMENT"],
        files=DOCS_CONTENT["FILES"]
    )
    (DBUILD_GUIDES_DIR / "config.md").write_text(config_content)
    print(f"Generated {DBUILD_GUIDES_DIR / 'config.md'}")

    # 4. Cleanup old files and handle moves
    moves = [
        (GUIDES_DIR / "cit.md", DBUILD_GUIDES_DIR / "cit.md"),
        (GUIDES_DIR / "ci-cd.md", DBUILD_GUIDES_DIR / "ci.md"),
        (GUIDES_DIR / "linux-pre-build.md", DBUILD_GUIDES_DIR / "linux-pre-build.md"),
    ]

    for old_path, new_path in moves:
        if old_path.exists() and not new_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"Moved {old_path.name} to {new_path}")
        elif old_path.exists():
            old_path.unlink()
            print(f"Removed old {old_path.name} (already exists at {new_path})")

    old_dbuild = GUIDES_DIR / "dbuild.md"
    if old_dbuild.exists():
        old_dbuild.unlink()
        print(f"Removed old {old_dbuild}")

if __name__ == "__main__":
    generate()
