#!/usr/bin/env python3
"""Fail CI on Residential index contamination or legacy CMS regression."""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HOST = "sixthvision.com.au"
MARKERS = ROOT / "security" / "forbidden-index-markers.txt"
LEGACY_PATHS = ROOT / "security" / "legacy-cms-paths.txt"


def policy_lines(path: Path) -> tuple[str, ...]:
    if not path.exists():
        raise RuntimeError(f"missing policy file: {path.relative_to(ROOT)}")
    values = tuple(
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    if not values:
        raise RuntimeError(f"empty policy file: {path.relative_to(ROOT)}")
    return values


def url_to_file(url: str) -> Path:
    path = urlparse(url).path
    if not path or path == "/":
        return ROOT / "index.html"
    rel = path.lstrip("/")
    candidate = ROOT / rel
    return candidate if candidate.suffix else candidate / "index.html"


def main() -> int:
    failures: list[str] = []
    markers = tuple(x.lower() for x in policy_lines(MARKERS))
    legacy_paths = policy_lines(LEGACY_PATHS)

    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        failures.append("missing sitemap.xml")
        urls: list[str] = []
    else:
        try:
            xml_root = ET.parse(sitemap).getroot()
        except Exception as exc:
            failures.append(f"invalid sitemap.xml: {exc}")
            urls = []
        else:
            urls = []
            for node in xml_root:
                if not node.tag.endswith("url"):
                    continue
                for child in node:
                    if child.tag.endswith("loc") and child.text:
                        urls.append(child.text.strip())
                        break

    if not urls:
        failures.append("sitemap contains no page URLs")

    sitemap_text = sitemap.read_text(encoding="utf-8", errors="ignore").lower() if sitemap.exists() else ""
    for marker in markers:
        if marker in sitemap_text:
            failures.append(f"forbidden marker {marker!r} found in sitemap.xml")

    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != HOST:
            failures.append(f"sitemap URL escapes canonical host: {url}")
            continue
        if any(parsed.path.startswith(path) for path in legacy_paths):
            failures.append(f"legacy CMS/runtime path appears in sitemap: {url}")
        page = url_to_file(url)
        if not page.exists():
            # Search-quality CI owns missing-page diagnostics; keep this test focused.
            continue
        text = page.read_text(encoding="utf-8", errors="ignore").lower()
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden marker {marker!r} found in {page.relative_to(ROOT)}")

    # Public static assets can still carry injected script/text even when HTML is clean.
    assets = ROOT / "assets"
    if assets.exists():
        for path in assets.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".js", ".css", ".html"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for marker in markers:
                if marker in text:
                    failures.append(f"forbidden marker {marker!r} found in {path.relative_to(ROOT)}")

    # A static production repository should never contain executable WordPress/PHP runtime.
    for path in ROOT.rglob("*.php"):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        failures.append(f"unexpected PHP runtime file: {path.relative_to(ROOT)}")

    if failures:
        for item in failures:
            print(f"FAIL: {item}", file=sys.stderr)
        return 1

    print(
        f"Residential index hygiene verified across {len(urls)} sitemap page(s): "
        "no high-signal spam markers, off-domain URLs, legacy CMS sitemap entries, "
        "or PHP runtime files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
