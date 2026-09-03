#!/usr/bin/env python3
"""Enforce Sixth Vision Residential's approved public entity truth.

This prevents future SEO/design work from silently reintroducing stale addresses,
coordinates, contact details or cross-domain identity contradictions.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "growthproof" / "entity-truth.json"
INDEX = ROOT / "index.html"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def jsonld_nodes(html: str) -> list[dict]:
    blocks = re.findall(
        r'<script\s+type=["\']application/ld\+json["\']\s*>\s*(.*?)\s*</script>',
        html,
        flags=re.I | re.S,
    )
    nodes: list[dict] = []
    for i, raw in enumerate(blocks, 1):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON-LD block #{i}: {exc}")
        candidates = payload if isinstance(payload, list) else [payload]
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            graph = candidate.get("@graph")
            if isinstance(graph, list):
                nodes.extend(item for item in graph if isinstance(item, dict))
            else:
                nodes.append(candidate)
    return nodes


def main() -> int:
    truth = json.loads(MANIFEST.read_text(encoding="utf-8"))
    html = INDEX.read_text(encoding="utf-8")

    for literal in truth.get("forbidden_legacy_literals", []):
        if literal in html:
            fail(f"forbidden legacy entity literal remains: {literal}")

    nodes = jsonld_nodes(html)
    business = next((node for node in nodes if node.get("@id") == truth["business_id"]), None)
    if business is None:
        fail(f"business JSON-LD node not found: {truth['business_id']}")

    exact = {
        "name": truth["brand"],
        "legalName": truth["legal_name"],
        "iso6523Code": truth["iso6523_code"],
        "url": truth["canonical_url"],
        "telephone": truth["telephone_e164"],
    }
    for key, expected in exact.items():
        if business.get(key) != expected:
            fail(f"business.{key}={business.get(key)!r}; expected {expected!r}")

    address = business.get("address") or {}
    address_expected = truth["address"]
    checks = {
        "addressLocality": address_expected["locality"],
        "addressRegion": address_expected["region"],
        "addressCountry": address_expected["country"],
    }
    for key, expected in checks.items():
        if address.get(key) != expected:
            fail(f"business.address.{key}={address.get(key)!r}; expected {expected!r}")
    if address.get("streetAddress"):
        fail("service-area Residential entity unexpectedly publishes streetAddress")

    area = business.get("areaServed") or {}
    expected_area = truth["area_served"]
    if area.get("@type") != expected_area["type"] or area.get("name") != expected_area["name"]:
        fail(f"business.areaServed={area!r}; expected {expected_area!r}")

    if not truth.get("allow_precise_geo", False) and business.get("geo") is not None:
        fail("service-area Residential entity unexpectedly publishes precise geo")

    same_as = set(business.get("sameAs") or [])
    missing_same_as = [url for url in truth["required_same_as"] if url not in same_as]
    if missing_same_as:
        fail("missing required sameAs URL(s): " + ", ".join(missing_same_as))

    # Visible/contact surface must agree with the machine-readable entity.
    visible_literals = [
        f'tel:{truth["telephone_e164"]}',
        truth["telephone_display"],
        f'mailto:{truth["email"]}',
        truth["email"],
        truth["legal_name"],
        f'ABN {truth["abn_display"]}',
        f'rel="canonical" href="{truth["canonical_url"]}"',
    ]
    missing_visible = [item for item in visible_literals if item not in html]
    if missing_visible:
        fail("visible/contact entity evidence missing: " + ", ".join(missing_visible))

    print("Entity truth verified: Residential legal, contact, service-area and sibling-domain facts agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
