#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MANIFEST = ROOT / "growthproof" / "claims-truth.json"

def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)

truth = json.loads(MANIFEST.read_text(encoding="utf-8"))
html = INDEX.read_text(encoding="utf-8")

for claim in truth["owner_verified_claims"]:
    for literal in claim["required_literals"]:
        if literal not in html:
            fail(f"owner-verified claim missing: {claim['id']} -> {literal}")

for claim in truth["unsupported_external_statistics"]:
    if claim.lower() in html.lower():
        fail(f"unsupported external statistic reintroduced: {claim}")

# Guard the one real wording conflict found in the live source: video must not
# be swept into the Residential 24-hour photography promise.
for forbidden in [
    "photography, floor plan, drone and cinematic video for one Melbourne listing, delivered within 24 hours",
    "cinematic video and drone for Melbourne's finest listings — delivered within 24 hours",
    "photo and video for twenty of Melbourne’s leading builders — fast, consistent, and always within the 24-hour guarantee",
]:
    if forbidden.lower() in html.lower():
        fail(f"ambiguous turnaround wording remains: {forbidden}")

if "Photography in 24 hours; video in&nbsp;48." not in html:
    fail("canonical split photo/video turnaround statement is missing")

print("Residential owner-verified claim truth and turnaround wording verified")
