#!/usr/bin/env python3
"""Validate structural quality for /simple static site."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SIMPLE_DIR = ROOT / "simple"
STYLESHEET = SIMPLE_DIR / "styles.css"

REQUIRED_PAGES = [
    "index.html",
    "migration.html",
    "system-support.html",
    "services.html",
    "impact.html",
    "process.html",
    "faq.html",
    "contact.html",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def is_external(value: str) -> bool:
    parsed = urlsplit(value)
    return bool(parsed.scheme and parsed.scheme not in {"", "file"})


def strip_fragment_and_query(value: str) -> str:
    parsed = urlsplit(value)
    return parsed.path


def resolve_target(src_file: Path, raw_target: str) -> Path:
    cleaned = strip_fragment_and_query(raw_target)
    if cleaned.startswith("/"):
        return (ROOT / cleaned.lstrip("/")).resolve()
    return (src_file.parent / cleaned).resolve()


def extract_attr_values(text: str, attr: str) -> Iterable[str]:
    pattern = rf'{attr}\s*=\s*"([^"]+)"'
    return re.findall(pattern, text)


def nav_href_signature(text: str) -> tuple[str, ...] | None:
    nav_match = re.search(
        r'<nav class="top-nav"[\s\S]*?</nav>',
        text,
        flags=re.IGNORECASE,
    )
    if not nav_match:
        return None
    nav_block = nav_match.group(0)
    nav_block = re.sub(r'\saria-current="page"', "", nav_block)
    hrefs = tuple(
        href
        for href in extract_attr_values(nav_block, "href")
        if href.startswith("./") and href.endswith(".html")
    )
    return hrefs


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SIMPLE_DIR.exists():
        print("ERROR: simple directory not found.")
        return 1

    html_files = sorted(SIMPLE_DIR.glob("*.html"))
    if not html_files:
        print("ERROR: no HTML files found in /simple.")
        return 1

    for page in REQUIRED_PAGES:
        if not (SIMPLE_DIR / page).exists():
            errors.append(f"Missing required page: simple/{page}")

    reference_nav: tuple[str, ...] | None = None

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8")
        short = rel(html_file)

        if "<!doctype html>" not in text.lower():
            errors.append(f"{short}: missing doctype declaration.")
        if not re.search(r"<title>[\s\S]*?</title>", text, flags=re.IGNORECASE):
            errors.append(f"{short}: missing <title>.")
        if not re.search(r"<h1>[\s\S]*?</h1>", text, flags=re.IGNORECASE):
            errors.append(f"{short}: missing <h1>.")
        if 'class="top-nav"' not in text:
            errors.append(f"{short}: missing top navigation.")
        if 'class="site-footer"' not in text:
            errors.append(f"{short}: missing site footer.")

        current_nav = nav_href_signature(text)
        if current_nav is None:
            errors.append(f"{short}: unable to parse top navigation block.")
        elif reference_nav is None:
            reference_nav = current_nav
        elif current_nav != reference_nav:
            errors.append(f"{short}: top navigation links are inconsistent.")

        for href in extract_attr_values(text, "href"):
            if href.startswith(("mailto:", "tel:", "#", "javascript:")):
                continue
            if is_external(href):
                continue
            target_path = strip_fragment_and_query(href)
            if not target_path:
                continue
            resolved = resolve_target(html_file, href)
            if not resolved.exists():
                errors.append(f"{short}: broken link -> {href}")

        for src in extract_attr_values(text, "src"):
            if src.startswith(("data:", "blob:")):
                continue
            if is_external(src):
                continue
            target_path = strip_fragment_and_query(src)
            if not target_path:
                continue
            resolved = resolve_target(html_file, src)
            if not resolved.exists():
                errors.append(f"{short}: missing image/source -> {src}")

    css_text = STYLESHEET.read_text(encoding="utf-8") if STYLESHEET.exists() else ""
    uses_image_band = any("image-band" in p.read_text(encoding="utf-8") for p in html_files)
    if uses_image_band:
        for selector in [
            ".section-alt.image-band",
            ".image-band-bg",
            ".image-band-overlay",
            ".image-band-content",
        ]:
            if selector not in css_text:
                errors.append(f"simple/styles.css: missing selector {selector}")

    if len(html_files) < len(REQUIRED_PAGES):
        warnings.append("There are fewer HTML files than expected required pages.")

    if errors:
        print("Simple site validation failed.")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN: {item}")
        return 1

    print("Simple site validation passed.")
    print(f"Validated HTML files: {len(html_files)}")
    for item in warnings:
        print(f"WARN: {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
