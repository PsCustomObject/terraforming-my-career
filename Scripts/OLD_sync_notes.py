#!/usr/bin/env python3

"""
sync_notes.py – Auto-sync Markdown notes to docs/ folder for Just the Docs

- Adds YAML front matter
- Syncs renamed files
- Detects and removes stale files in docs/
- Supports --dry-run and --clean

Version: v2.0.0

Changelog:
v2.0.0 (2025-11-07):
    - 🐛 Fixed Value Error: Empty separator in index generation.
    - ✨ Feature: Added '## TABLE OF CONTENTS' header and separator.
    - 📝 Maintenance: Added semantic version and changelog to header.
    - 🩹 Fixed malformed TOC block causing SyntaxError.
    - 🧹 Corrected regex escaping in natural sort (use r"(\\d+)" -> r"(\d+)").
    - 🔠 Natural sort by TITLE with robust title extraction.
    - ➕ De-duplicate TOC entries before sorting.
    - 🧷 Stable final newline after list.
v1.0.0 (2025-06-15):
    - Initial release.

Author: PsCustomObject (2025)
"""

import os
import hashlib
import json
import re
import argparse
from pathlib import Path

SOURCE_DIR = Path(".").resolve()
DOCS_DIR = SOURCE_DIR / "docs"
HASH_FILE = SOURCE_DIR / ".sync_hashes.json"
EXCLUDE_DIRS = {"docs", ".git", "__pycache__"}
TOC_MARKER = "<!-- TOC:DO-NOT-EDIT -->"

section_title_map = {
    "reading_notes": "Reading Notes",
    "meta": "Meta",
    "terraform": "Terraform",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
}

section_order_map = {
    "reading_notes": 40,
    "meta": 30,
    "terraform": 20,
    "docker": 50,
    "kubernetes": 60,
    "aws": 10,
}


def read_file_clean(path):
    """Reads file content, handling BOM, and returns as UTF-8 string."""
    with open(path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8-sig")


def sha256(text):
    """Calculates SHA256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_chapter_title(filename):
    """Parses filename for chapter number and title."""
    match = re.match(r"chapter-(\d+)[-_ ]?(.*)\.md", filename, re.IGNORECASE)
    if match:
        chapter_number = int(match.group(1))
        raw_title = match.group(2).replace("-", " ").replace("_", " ").title()
        return chapter_number, f"Chapter {chapter_number} – {raw_title}"
    return None, Path(filename).stem.replace("-", " ").replace("_", " ").title()


def load_hashes():
    """Loads file hashes from cache file."""
    if HASH_FILE.exists():
        with open(HASH_FILE, "r") as f:
            return json.load(f)
    return {}


def save_hashes(data):
    """Saves file hashes to cache file."""
    with open(HASH_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create_or_update_section_index(
    target_dir, nav_order, chapter_links=None, dry_run=False
):
    """
    Creates or updates the index.md file for a section with TOC.
    Includes logic to prevent unnecessary disk writes if content is unchanged.
    """
    index_file = target_dir / "index.md"
    title = section_title_map.get(target_dir.name.lower(), target_dir.name.title())

    default_content = f"""---
title: {title}
nav_order: {nav_order}
has_children: true
---

# {title}

Notes for the **{title}** section."""

    # Initialize with default; may be overridden by existing content
    content_before = default_content

    if index_file.exists():
        existing = read_file_clean(index_file)

        if not existing or TOC_MARKER not in existing:
            print(
                f"⚠️ Warning: index.md empty or TOC_MARKER invalid for {target_dir}. Rebuilding header."
            )
            content_before = default_content.rstrip()
        else:
            # Preserve content above the marker, stripped of trailing newlines
            content_before = existing.split(TOC_MARKER)[0].rstrip()
    else:
        # For a new file, ensure the content_before is also stripped.
        content_before = default_content.rstrip()

    # --- TOC Content Generation (spacing: Layout A) ---
    # Exactly one blank line before marker; one after marker; one after H2; one after '---'
    TOC_MARKUP_STRING = (
        "\n\n"  # one blank line after content_before
        + TOC_MARKER
        + "\n\n"  # one blank line after marker
        + "## TABLE OF CONTENTS\n\n"  # H2 + blank line
        + "---\n\n"  # horizontal rule + blank line
    )

    # Concatenate header + TOC block
    content = f"{content_before}{TOC_MARKUP_STRING}"
    if not content.endswith("\n"):
        content += "\n"

    # Build and insert chapter list
    if chapter_links:
        # De-duplicate exact duplicates
        unique = list(dict.fromkeys(chapter_links))

        # Natural sort by TITLE (extract the [...] part)
        def _title_key(s: str):
            m = re.search(r"\[(.*?)\]", s)
            title = m.group(1) if m else s
            # Split into numeric/non-numeric chunks for natural ordering
            return [
                int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", title)
            ]

        unique_sorted = sorted(unique, key=_title_key)

        content += "\n".join(unique_sorted)

        # Ensure the file ends with a newline for stable diffs
        if not content.endswith("\n"):
            content += "\n"

    # --- Index Stability Fix: write only if different ---
    if index_file.exists():
        existing_content = read_file_clean(index_file)
        if existing_content == content:
            print(f"📁 Index is up to date: {index_file}")
            return  # Content is the same, skip write and reporting 'updated'.

    # Only write if: 1) index_file did not exist, or 2) existing_content != content
    if not dry_run:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"📁 Index {'would be updated' if dry_run else 'updated'}: {index_file}")


def sync_notes(dry_run=False, clean=False):
    """Main function to sync notes."""
    if clean and HASH_FILE.exists():
        if not dry_run:
            HASH_FILE.unlink()
        print(
            f"🧼 {'Would remove' if dry_run else 'Removed'} existing .sync_hashes.json"
        )

    cache = load_hashes()
    updated = {}
    any_synced = False
    reverse_hash_map = {v: k for k, v in cache.items()}
    seen_hashes = set()

    for root, _, files in os.walk(SOURCE_DIR):
        rel = Path(root).relative_to(SOURCE_DIR)
        if any(p in EXCLUDE_DIRS for p in rel.parts):
            continue

        md_files = sorted(f for f in files if f.endswith(".md"))
        if not md_files:
            continue

        target_dir = DOCS_DIR / rel
        target_dir.mkdir(parents=True, exist_ok=True)

        section_name = rel.name if rel.parts else None
        nav_order = (
            section_order_map.get(section_name.lower(), 90) if section_name else 1
        )
        section_title = (
            section_title_map.get(section_name.lower(), section_name.title())
            if section_name
            else None
        )

        # --- File Sync Pass ---
        for i, fname in enumerate(md_files):
            if fname.lower() == "index.md":
                continue

            src_file = Path(root) / fname
            dst_file = target_dir / fname
            body = read_file_clean(src_file)

            chapter_num, title = parse_chapter_title(fname)
            nav_order_entry = chapter_num if chapter_num else (i + 1)

            front_matter = f'---\ntitle: "{title}"\n'
            if section_title:
                front_matter += f"parent: {section_title}\n"
            front_matter += f"nav_order: {nav_order_entry}\n---\n\n"

            final = front_matter + body
            file_hash = sha256(final)
            hash_key = str(src_file.relative_to(SOURCE_DIR))
            updated[hash_key] = file_hash
            seen_hashes.add(file_hash)

            if cache.get(hash_key) != file_hash:
                if file_hash in reverse_hash_map:
                    old_key = reverse_hash_map[file_hash]
                    old_path = DOCS_DIR / old_key
                    if old_path.exists():
                        if not dry_run:
                            old_path.unlink()
                        print(f"🔄 Renamed (deleted old): {old_path}")

                if not dry_run:
                    with open(dst_file, "w", encoding="utf-8") as f:
                        f.write(final)
                print(f"{'📝 Would sync' if dry_run else '✅ Synced'}: {dst_file}")
                any_synced = True

        # --- TOC Generation Pass (runs unconditionally) ---
        chapter_links = []
        for fname in md_files:
            if fname.lower() == "index.md":
                continue

            _, title = parse_chapter_title(fname)
            chapter_links.append(f"- [{title}]({fname})")

        if section_title:
            create_or_update_section_index(
                target_dir, nav_order, chapter_links, dry_run=dry_run
            )

    if not dry_run:
        save_hashes(updated)

    print(
        "\n🎉 Dry run complete. No files were written."
        if dry_run
        else ("\n🎉 Sync complete." if any_synced else "\n🔁 All up to date.")
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync Markdown notes to GitHub Pages docs/"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing files"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove .sync_hashes.json and force rebuild",
    )
    args = parser.parse_args()
    sync_notes(dry_run=args.dry_run, clean=args.clean)
