import json
import re
from pathlib import Path

INDEX = Path("index.html")
ABN_DISPLAY = "92 625 744 630"
ABN_COMPACT = "92625744630"
LEGAL_NAME = "SIXTH VISION PTY LTD"
ISO6523_ABN = f"0151:{ABN_COMPACT}"
LEGACY_GEO = (
    '      "geo": { "@type": "GeoCoordinates", "latitude": "-37.745313", '
    '"longitude": "144.99953" },\n'
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected exactly one source marker, found {text.count(old)}")
    return text.replace(old, new, 1)


def patch_business_entity(text: str) -> str:
    old = '      "name": "Sixth Vision",\n      "url": "https://sixthvision.com.au/",'
    new = (
        '      "name": "Sixth Vision",\n'
        f'      "legalName": "{LEGAL_NAME}",\n'
        f'      "iso6523Code": "{ISO6523_ABN}",\n'
        '      "url": "https://sixthvision.com.au/",'
    )
    text = replace_once(text, old, new, "residential organization identity")

    old_same_as = (
        '      "sameAs": [\n'
        '        "https://www.instagram.com/sixthvision.mel",\n'
        '        "https://www.facebook.com/sixthvisionmel/"\n'
        '      ],'
    )
    new_same_as = (
        '      "sameAs": [\n'
        '        "https://sixthvisioncommercial.com.au/",\n'
        '        "https://www.instagram.com/sixthvision.mel",\n'
        '        "https://www.facebook.com/sixthvisionmel/"\n'
        '      ],'
    )
    text = replace_once(text, old_same_as, new_same_as, "residential cross-domain identity")
    return text


def patch_service_area_location(text: str) -> str:
    """Remove the retired precise Preston/Bell pin from service-area schema.

    Sixth Vision publishes Melbourne as the service area and does not present
    this legacy coordinate as a current customer-facing location. Keeping an
    obsolete precise geo point would contradict the visible entity and reinforce
    stale third-party Preston citations. The generic Melbourne PostalAddress and
    areaServed fields remain intact.
    """
    if LEGACY_GEO in text:
        text = text.replace(LEGACY_GEO, "", 1)
    if "-37.745313" in text or "144.99953" in text:
        raise SystemExit("legacy Preston/Bell geo coordinate remains in Residential output")
    required = [
        '"addressLocality": "Melbourne"',
        '"addressRegion": "VIC"',
        '"addressCountry": "AU"',
        '"areaServed": { "@type": "City", "name": "Melbourne" }',
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit("service-area identity incomplete; missing: " + ", ".join(missing))
    return text


def patch_static_evidence(text: str) -> str:
    replacements = {
        '<span data-count="50000">0</span>': '<span data-count="50000">50,000</span>',
        '<span data-count="60">0</span>': '<span data-count="60">60</span>',
        '<span data-count="400">0</span>': '<span data-count="400">400</span>',
        '<span data-count="500">0</span>': '<span data-count="500">500</span>',
    }
    for old, new in replacements.items():
        if new in text:
            continue
        if old not in text:
            raise SystemExit(f"static evidence marker missing: {old}")
        text = text.replace(old, new, 1)
    return text


def patch_footer(text: str) -> str:
    marker = (
        '      &copy; <span id="year">2026</span> Sixth Vision &mdash; Real Estate Photography Melbourne '
        '&amp; Real Estate Videography Melbourne &middot; Melbourne VIC\n'
        '      <span class="footer-craft">'
    )
    replacement = (
        '      &copy; <span id="year">2026</span> Sixth Vision &mdash; Real Estate Photography Melbourne '
        '&amp; Real Estate Videography Melbourne &middot; Melbourne VIC\n'
        f'      <span class="footer-company">{LEGAL_NAME} &middot; ABN {ABN_DISPLAY}</span>\n'
        '      <span class="footer-craft">'
    )
    return replace_once(text, marker, replacement, "residential footer legal identity")


def validate_json_ld(text: str) -> None:
    blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', text, flags=re.S)
    if not blocks:
        raise SystemExit("No JSON-LD blocks found")
    for i, block in enumerate(blocks, 1):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"JSON-LD block {i} invalid: {exc}") from exc


def validate(text: str) -> None:
    required = [
        f'"legalName": "{LEGAL_NAME}"',
        f'"iso6523Code": "{ISO6523_ABN}"',
        "https://sixthvisioncommercial.com.au/",
        f"ABN {ABN_DISPLAY}",
        '<span data-count="50000">50,000</span>',
        '<span data-count="60">60</span>',
        '<span data-count="400">400</span>',
        '<span data-count="500">500</span>',
        '"addressLocality": "Melbourne"',
        '"areaServed": { "@type": "City", "name": "Melbourne" }',
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit("Validation failed; missing: " + ", ".join(missing))
    if "-37.745313" in text or "144.99953" in text:
        raise SystemExit("Validation failed; retired Preston/Bell geo coordinate still present")
    validate_json_ld(text)


def patch(text: str) -> str:
    text = patch_business_entity(text)
    text = patch_service_area_location(text)
    text = patch_static_evidence(text)
    text = patch_footer(text)
    validate(text)
    return text


def main() -> None:
    original = INDEX.read_text(encoding="utf-8")
    updated = patch(original)
    INDEX.write_text(updated, encoding="utf-8")
    # Idempotence gate: applying the patch twice must produce identical bytes.
    if patch(updated) != updated:
        raise SystemExit("Patch is not idempotent")


if __name__ == "__main__":
    main()
