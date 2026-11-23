#!/usr/bin/env python3
"""Fail the build when Markdown or placeholders reached published HTML unrendered.

Checks across all generated HTML pages:
1. Unrendered icon shortcodes (:material-server:, :simple-*, :fjord-fjord:, etc.).
2. Annotated code blocks (# (1)) missing their <ol> note list immediately after.
3. Unrendered admonitions / details fences (!!! note, ??? ") left as body text.
4. Broken YAML frontmatter rendered into visible <p>title: ... body text.
5. Raw @[A-Z][A-Z0-9_]+@ placeholder tokens leaked into rendered HTML.
6. External img.shields.io badge requests on /status/.
7. Nested <a> tags (e.g. double-wrapped GLightbox anchors).
"""
from html.parser import HTMLParser
import pathlib
import re
import sys


class _NestedAnchorFinder(HTMLParser):
    """Collect hrefs of <a> elements opened while already inside an <a>."""

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.nested: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        if self.depth > 0:
            href = dict(attrs).get("href") or ""
            self.nested.append(href)
        self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.depth > 0:
            self.depth -= 1


site = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site")
icon = re.compile(
    r":(?:material|fontawesome|octicons|simple|fjord|podman|appjail|bastille)-[a-z0-9-]+:"
)
marker = re.compile(r'<span class="c1?">(?:#|//|--)\s*\((\d+)\)!?\s*</span>')
raw_admonition = re.compile(r"(?:<p>|<li>|\n)\s*(?:!!!|\?\?\?\+?)\s+(?:[a-z]+|\"|&quot;)")
raw_frontmatter = re.compile(r"<p>\s*title:\s*(?:\"|&quot;|')")
raw_placeholder = re.compile(r"@[A-Z][A-Z0-9_]{2,}@")
raw_md_link = re.compile(r"\[[^\]\n<]{2,80}\]\((?:https?://|\.\.?/|/[a-z])[^)\s]+\)")

problems = []

for page in sorted(site.rglob("*.html")):
    html = page.read_text(errors="replace")
    # Strip <script>, <pre>, and <code> before prose-only checks.
    prose = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S)
    prose = re.sub(r"<pre[^>]*>.*?</pre>", "", prose, flags=re.S)
    prose = re.sub(r"<code[^>]*>.*?</code>", "", prose, flags=re.S)

    for m in icon.finditer(prose):
        problems.append(f"{page}: icon code shown as text: {m.group(0)}")
    for m in raw_admonition.finditer(prose):
        snippet = " ".join(m.group(0).split())
        problems.append(f"{page}: unrendered admonition shown as text: {snippet}")
    for m in raw_frontmatter.finditer(prose):
        problems.append(f"{page}: broken YAML frontmatter rendered as body text")
    for m in raw_placeholder.finditer(prose):
        problems.append(f"{page}: raw placeholder token in prose: {m.group(0)}")
    for m in raw_md_link.finditer(prose):
        problems.append(f"{page}: unrendered markdown link in prose: {m.group(0)}")

    anchor_finder = _NestedAnchorFinder()
    anchor_finder.feed(prose)
    anchor_finder.close()
    for href in anchor_finder.nested:
        problems.append(f"{page}: nested <a> tag (href={href!r})")

    # Check code blocks on generated image pages for leaked @PLACEHOLDER@ tokens too.
    if "/images/" in page.as_posix():
        for block in re.finditer(r"<pre[^>]*>.*?</pre>", html, re.S):
            for m in raw_placeholder.finditer(block.group(0)):
                problems.append(f"{page}: raw placeholder token in code block: {m.group(0)}")

    # Each code block with markers must be followed by the list of notes.
    for block in re.finditer(r"<pre[^>]*>.*?</pre>", html, re.S):
        if not marker.search(block.group(0)):
            continue
        rest = re.sub(r"^(\s*</(?:code|div|span)>)*\s*", "", html[block.end():block.end() + 2000])
        if not rest.startswith("<ol"):
            problems.append(
                f"{page}: a code block's # (1) notes are not a list after it "
                "(Markdown inside HTML without the markdown attribute?)"
            )

status_html = site / "status" / "index.html"
if status_html.exists() and "img.shields.io" in status_html.read_text(errors="replace"):
    problems.append(f"{status_html}: external img.shields.io badge URL found on /status/")

for p in problems:
    print(p)
if not problems:
    print("Rendered: no raw icon codes, admonitions, placeholders, frontmatter leaks, or nested anchors.")
sys.exit(1 if problems else 0)
