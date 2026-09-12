#!/usr/bin/env python3
"""Fail CI on indexability, metadata, schema, or internal-link regressions.

Stdlib only by design: this gate must remain free, deterministic and portable.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.meta_description: str | None = None
        self.robots: str | None = None
        self.canonical: str | None = None
        self.h1_count = 0
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.jsonld: list[str] = []
        self._jsonld_active = False
        self._jsonld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        data = {k.lower(): v for k, v in attrs}
        tag = tag.lower()
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = (data.get("name") or "").lower()
            if name == "description":
                self.meta_description = data.get("content")
            elif name == "robots":
                self.robots = data.get("content")
        elif tag == "link" and (data.get("rel") or "").lower() == "canonical":
            self.canonical = data.get("href")
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "a" and data.get("href"):
            self.links.append(data["href"])
        elif tag == "img":
            self.images.append({
                "src": data.get("src"),
                "alt": data.get("alt"),
                "width": data.get("width"),
                "height": data.get("height"),
            })
        elif tag == "script" and (data.get("type") or "").lower() == "application/ld+json":
            self._jsonld_active = True
            self._jsonld_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._jsonld_active:
            self.jsonld.append("".join(self._jsonld_parts).strip())
            self._jsonld_active = False
            self._jsonld_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self._jsonld_active:
            self._jsonld_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def sitemap_urls(sitemap: Path) -> list[str]:
    root = ET.parse(sitemap).getroot()
    urls: list[str] = []
    # Only direct <url><loc> children are page URLs. Image/video/news sitemap
    # extensions also contain elements named *:loc and must never be audited as HTML.
    for url_node in root:
        if not url_node.tag.endswith("url"):
            continue
        for child in url_node:
            if child.tag.endswith("loc") and child.text:
                urls.append(child.text.strip())
                break
    return urls


def url_to_file(root: Path, url: str) -> Path:
    path = urlparse(url).path
    if not path or path == "/":
        return root / "index.html"
    rel = path.lstrip("/")
    candidate = root / rel
    if candidate.suffix:
        return candidate
    return candidate / "index.html"


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--host", required=True)
    ap.add_argument("--sitemap", default="sitemap.xml")
    ap.add_argument("--robots", default="robots.txt")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    host = args.host.rstrip("/")
    failures: list[str] = []
    warnings: list[str] = []

    sitemap = root / args.sitemap
    robots = root / args.robots
    if not sitemap.exists():
        failures.append(f"missing sitemap: {sitemap}")
        urls: list[str] = []
    else:
        try:
            urls = sitemap_urls(sitemap)
        except Exception as exc:
            failures.append(f"invalid sitemap XML: {exc}")
            urls = []

    if not urls:
        failures.append("sitemap contains no URLs")

    if not robots.exists():
        failures.append(f"missing robots.txt: {robots}")
    else:
        text = robots.read_text(encoding="utf-8")
        if "User-agent: *" not in text or "Allow: /" not in text:
            failures.append("robots.txt must explicitly allow the public site")
        if "Sitemap:" not in text:
            failures.append("robots.txt must advertise the sitemap")

    parsed: dict[str, tuple[Path, PageParser]] = {}
    for url in urls:
        if not url.startswith(host + "/") and url != host:
            failures.append(f"sitemap URL escapes canonical host: {url}")
            continue
        page_file = url_to_file(root, url)
        if not page_file.exists():
            failures.append(f"sitemap URL has no local page: {url} -> {page_file.relative_to(root)}")
            continue
        page = parse_page(page_file)
        parsed[url] = (page_file, page)

        if not page.title:
            failures.append(f"{url}: missing <title>")
        if not page.meta_description or len(page.meta_description.strip()) < 40:
            failures.append(f"{url}: missing/too-short meta description")
        if page.h1_count != 1:
            failures.append(f"{url}: expected exactly one H1, found {page.h1_count}")
        if page.canonical != url:
            failures.append(f"{url}: canonical is {page.canonical!r}, expected {url!r}")
        if page.robots and "noindex" in page.robots.lower():
            failures.append(f"{url}: sitemap page is marked noindex")

        for idx, raw in enumerate(page.jsonld, start=1):
            if not raw:
                failures.append(f"{url}: empty JSON-LD block #{idx}")
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                failures.append(f"{url}: invalid JSON-LD block #{idx}: {exc}")
                continue
            nodes = payload if isinstance(payload, list) else [payload]
            for node in nodes:
                if isinstance(node, dict) and "@context" not in node and "@graph" not in node:
                    warnings.append(f"{url}: JSON-LD block #{idx} has no explicit @context/@graph")

        for image in page.images:
            src = image["src"] or "<missing src>"
            if image["alt"] is None:
                failures.append(f"{url}: image missing alt attribute: {src}")
            if not image["width"] or not image["height"]:
                warnings.append(f"{url}: image lacks intrinsic width/height: {src}")

    # Validate same-site links and fragments across every indexed page.
    for source_url, (_, page) in parsed.items():
        for href in page.links:
            if href.startswith(("mailto:", "tel:", "sms:", "javascript:")):
                continue
            absolute = urljoin(source_url, href)
            target = urlparse(absolute)
            if target.scheme not in ("http", "https"):
                continue
            if f"{target.scheme}://{target.netloc}" != host:
                continue
            target_url = f"{host}{target.path or '/'}"
            target_file = url_to_file(root, target_url)
            if not target_file.exists():
                failures.append(f"{source_url}: broken internal link {href} -> {target_file.relative_to(root)}")
                continue
            if target.fragment:
                target_page = parsed.get(target_url)
                target_parser = target_page[1] if target_page else parse_page(target_file)
                if target.fragment not in target_parser.ids:
                    failures.append(f"{source_url}: missing fragment target #{target.fragment} in {target_url}")

    print(f"Search quality audit: {len(parsed)} indexed page(s), {len(warnings)} warning(s), {len(failures)} failure(s)")
    for item in warnings:
        print(f"WARN: {item}")
    for item in failures:
        print(f"FAIL: {item}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
