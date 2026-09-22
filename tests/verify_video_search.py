#!/usr/bin/env python3
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = "https://sixthvision.com.au"
VIDEO_PAGE = "/real-estate-videography-melbourne/"
VIDEO_FILE = "/assets/video/showreel.mp4"
THUMB_FILE = "/assets/img/showreel-1600.webp"

errors = []

def fail(message):
    errors.append(message)

sitemap_path = ROOT / "video-sitemap.xml"
if not sitemap_path.exists():
    fail("video-sitemap.xml is missing")
else:
    try:
        root = ET.parse(sitemap_path).getroot()
        ns = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "video": "http://www.google.com/schemas/sitemap-video/1.1",
        }
        urls = root.findall("sm:url", ns)
        if len(urls) != 1:
            fail(f"expected exactly one video sitemap URL, found {len(urls)}")
        else:
            entry = urls[0]
            loc = (entry.findtext("sm:loc", default="", namespaces=ns) or "").strip()
            if loc != HOST + VIDEO_PAGE:
                fail(f"unexpected video host page: {loc}")
            video = entry.find("video:video", ns)
            if video is None:
                fail("video:video entry is missing")
            else:
                required = {
                    "thumbnail_loc": HOST + THUMB_FILE,
                    "title": "Sixth Vision Melbourne Property Showreel",
                    "description": None,
                    "content_loc": HOST + VIDEO_FILE,
                }
                for tag, wanted in required.items():
                    value = (video.findtext(f"video:{tag}", default="", namespaces=ns) or "").strip()
                    if not value:
                        fail(f"video:{tag} is missing")
                    elif wanted is not None and value != wanted:
                        fail(f"video:{tag} mismatch: {value}")
    except ET.ParseError as exc:
        fail(f"video-sitemap.xml is invalid XML: {exc}")

for rel in [VIDEO_PAGE.lstrip("/") + "index.html", VIDEO_FILE.lstrip("/"), THUMB_FILE.lstrip("/")]:
    if not (ROOT / rel).exists():
        fail(f"referenced video-search asset is missing: {rel}")

page_path = ROOT / VIDEO_PAGE.lstrip("/") / "index.html"
if page_path.exists():
    page = page_path.read_text(encoding="utf-8")
    if HOST + VIDEO_FILE not in page:
        fail("videography page VideoObject does not reference the sitemap content URL")
    if HOST + THUMB_FILE not in page:
        fail("videography page VideoObject does not reference the sitemap thumbnail")
    if '"@type":"VideoObject"' not in page:
        fail("videography page is missing VideoObject structured data")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if f"Sitemap: {HOST}/video-sitemap.xml" not in robots:
    fail("robots.txt does not advertise video-sitemap.xml")

if errors:
    for err in errors:
        print(f"ERROR: {err}")
    raise SystemExit(1)

print("Video search integrity OK")
