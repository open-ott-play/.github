#!/usr/bin/env python3
"""Read-only check of profile links, anchors and diagrams; does not render GitHub pages."""
from __future__ import annotations

import argparse
import concurrent.futures
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ElementTree
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (ROOT / "profile" / "README.md", ROOT / "README.md")
SVG_ROOT = ROOT / "profile" / "assets"
LINK = re.compile(r"!?\[[^\]]*\]\(\s*(?P<target>[^)\s]+)")
HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(?P<text>.*?)[ \t]*#*[ \t]*$")
FENCE = re.compile(r"^ {0,3}(?:```|~~~)")
HTML_ID = re.compile(r"""<a\s[^>]*?(?:id|name)\s*=\s*["'](?P<name>[^"']+)["']""", re.IGNORECASE)
HTML_ANCHOR_LINK = re.compile(r"""href\s*=\s*["']#(?P<fragment>[^"']*)["']""", re.IGNORECASE)
EXTERNAL = re.compile(r"^https?://", re.IGNORECASE)
SELF_CONTAINED = re.compile(r"""(?:href|src)\s*=\s*["']\s*(?:https?:)?//""", re.IGNORECASE)
STYLE_IMPORT = re.compile(r"@import|url\(\s*['\"]?(?:https?:)?//", re.IGNORECASE)
USER_AGENT = "open-ott-play-profile-check/1.0 (+https://github.com/open-ott-play/.github)"
RETRY_STATUS = {403, 408, 425, 429, 500, 502, 503, 504}


def markdown_targets(path: Path) -> list[tuple[str, int]]:
    targets: list[tuple[str, int]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        targets.extend((match.group("target"), number) for match in LINK.finditer(line))
    return targets


def markdown_headings(text: str) -> list[str]:
    """Heading texts GitHub renders, skipping fenced code and HTML comments."""
    headings: list[str] = []
    fenced = False
    commented = False
    for line in text.splitlines():
        if commented:
            if "-->" not in line:
                continue
            line = line.split("-->", 1)[1]
            commented = False
        while "<!--" in line:
            before, after = line.split("<!--", 1)
            if "-->" in after:
                line = before + after.split("-->", 1)[1]
            else:
                line = before
                commented = True
                break
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = HEADING.match(line)
        if match:
            headings.append(match.group("text"))
    return headings


def slugify(heading: str) -> str:
    """Approximate GitHub's heading anchor: inline markup removed, punctuation dropped."""
    text = re.sub(r"<[^>]+>", "", heading)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    text = re.sub(r"[*`~]", "", text)
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return text.strip().replace(" ", "-")


def heading_slugs(text: str) -> set[str]:
    """Every anchor GitHub generates for the headings, including suffixed duplicates."""
    slugs: set[str] = set()
    occurrences: dict[str, int] = {}
    for heading in markdown_headings(text):
        base = slugify(heading)
        if not base:
            continue
        slug = base
        while slug in slugs:
            occurrences[base] = occurrences.get(base, 0) + 1
            slug = f"{base}-{occurrences[base]}"
        slugs.add(slug)
    return slugs


def document_anchors(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path not in cache:
        text = path.read_text(encoding="utf-8")
        cache[path] = heading_slugs(text) | {match.group("name") for match in HTML_ID.finditer(text)}
    return cache[path]


def anchor_references(path: Path) -> list[tuple[str, int]]:
    references: list[tuple[str, int]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for match in LINK.finditer(line):
            target = match.group("target")
            if target.startswith("#") and len(target) > 1:
                references.append((urllib.parse.unquote(target[1:]), number))
        for match in HTML_ANCHOR_LINK.finditer(line):
            if match.group("fragment"):
                references.append((urllib.parse.unquote(match.group("fragment")), number))
    return references


def local_path(document: Path, target: str) -> Path | None:
    if target.startswith("#") or target.startswith("mailto:"):
        return None
    split = urllib.parse.urlsplit(target)
    if split.scheme or split.netloc:
        return None
    relative = urllib.parse.unquote(split.path)
    if not relative:
        return None
    candidate = (document.parent / relative).resolve() if not relative.startswith("/") else (ROOT / relative.lstrip("/")).resolve()
    if ROOT not in candidate.parents and candidate != ROOT:
        raise ValueError(f"outside the repository: {target}")
    return candidate


def request(url: str, timeout: float) -> tuple[int | None, str]:
    last = "no attempt"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response.read(1)
                return response.status, response.geturl()
        except urllib.error.HTTPError as error:
            last = f"HTTP {error.code}"
            if error.code not in RETRY_STATUS:
                return error.code, url
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last = f"{type(error).__name__}: {getattr(error, 'reason', error)}"
        if attempt < 2:
            time.sleep(2**attempt)
    return None, last


def check_svg(path: Path) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as error:
        return [f"{path.relative_to(ROOT)}: invalid XML ({error})"]
    if not root.tag.endswith("svg"):
        problems.append(f"{path.relative_to(ROOT)}: root element is not <svg>")
    if 'xmlns="http://www.w3.org/2000/svg"' not in text:
        problems.append(f"{path.relative_to(ROOT)}: missing xmlns (GitHub renders it as plain text)")
    namespace = root.tag[: root.tag.index("}") + 1] if root.tag.startswith("{") else ""
    if root.find(f"{namespace}title") is None and root.find(f"{namespace}desc") is None:
        problems.append(f"{path.relative_to(ROOT)}: missing <title>/<desc> (assistive text)")
    if SELF_CONTAINED.search(text) or STYLE_IMPORT.search(text):
        problems.append(f"{path.relative_to(ROOT)}: references an external resource; GitHub may block or strip it")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="check files and SVGs without network requests")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--report", type=Path, help="write the problems as a Markdown list to this file")
    arguments = parser.parse_args()

    problems: list[str] = []
    external: dict[str, str] = {}
    local_count = 0
    anchors_checked = 0
    anchor_cache: dict[Path, set[str]] = {}
    for document in DOCUMENTS:
        if not document.is_file():
            problems.append(f"{document.relative_to(ROOT)}: missing")
            continue
        for target, line in markdown_targets(document):
            if EXTERNAL.match(target):
                external.setdefault(target, f"{document.relative_to(ROOT)}:{line}")
                continue
            try:
                resolved = local_path(document, target)
            except ValueError as error:
                problems.append(f"{document.relative_to(ROOT)}:{line}: {error}")
                continue
            if resolved is None:
                continue
            local_count += 1
            if not resolved.exists():
                problems.append(f"{document.relative_to(ROOT)}:{line}: broken path {target}")
            elif resolved.is_file() and resolved.suffix.lower() == ".md":
                fragment = urllib.parse.unquote(urllib.parse.urlsplit(target).fragment)
                if fragment:
                    anchors_checked += 1
                    if fragment not in document_anchors(resolved, anchor_cache):
                        problems.append(f"{document.relative_to(ROOT)}:{line}: missing anchor {target}")

    for document in DOCUMENTS:
        if not document.is_file():
            continue
        for fragment, line in anchor_references(document):
            anchors_checked += 1
            if fragment not in document_anchors(document, anchor_cache):
                problems.append(f"{document.relative_to(ROOT)}:{line}: missing anchor #{fragment}")

    svgs = sorted(SVG_ROOT.rglob("*.svg")) if SVG_ROOT.is_dir() else []
    if not svgs:
        problems.append(f"{SVG_ROOT.relative_to(ROOT)}: no diagrams found")
    for svg in svgs:
        problems.extend(check_svg(svg))

    checked = 0
    if not arguments.offline and external:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = {pool.submit(request, url, arguments.timeout): url for url in external}
            for future in concurrent.futures.as_completed(results):
                url = results[future]
                status, detail = future.result()
                checked += 1
                if status is None or not 200 <= status < 400:
                    problems.append(f"{external[url]}: {url} -> {detail}")

    if problems:
        print("Profile check failed:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if arguments.report:
            arguments.report.write_text("".join(f"- {problem}\n" for problem in problems), encoding="utf-8")
        return 1
    if arguments.report:
        arguments.report.unlink(missing_ok=True)
    print(
        f"Profile check passed: {len(DOCUMENTS)} documents, {local_count} local references, "
        f"{anchors_checked} anchors, {len(svgs)} diagrams, {checked} external links"
        + (" (network skipped)" if arguments.offline else "")
    )
    print("GitHub rendering, redirects after the first response and link rot after the run are outside this check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
