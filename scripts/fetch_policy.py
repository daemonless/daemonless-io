#!/usr/bin/env python3
"""
Generate docs/guides/llm-policy.md from LLM_POLICY.md in daemonless/daemonless.
That file is the source of truth; edit the policy there, not on this page.
"""

import re
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/daemonless/daemonless/main/LLM_POLICY.md"
OUTPUT = Path(__file__).parent.parent / "docs" / "guides" / "llm-policy.md"

FRONT_MATTER = """---
title: "LLM / AI Contribution Policy"
description: "Daemonless policy on AI-assisted contributions: use the tools, own the code, test it before you submit, and keep project communication in your own words."
---

"""

FOOTER = """

---

If you're porting an image, see [AI-Assisted Porting](ai-assisted-porting.md).
"""


def main():
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=30) as resp:
            policy = resp.read().decode("utf-8")
    except Exception as e:
        # Fail the build: the nav links to this page, so it must exist.
        print(f"Failed to fetch {SOURCE_URL}: {e}", file=sys.stderr)
        sys.exit(1)

    # A list needs a blank line before it to render; the source omits it.
    policy = re.sub(r"^((?!\* ).+)\n(?=\* )", r"\1\n\n", policy, flags=re.MULTILINE)

    OUTPUT.write_text(FRONT_MATTER + policy.strip() + FOOTER, encoding="utf-8")


if __name__ == "__main__":
    main()
