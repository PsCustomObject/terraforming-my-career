#!/usr/bin/env python3

"""
sync_notes.py – Auto-sync Markdown notes to docs/ folder for Just the Docs

- Adds YAML front matter
- Syncs renamed files
- Detects and removes stale files in docs/
- Supports --dry-run, --clean, and --manual-toc

Version: v2.1.0

Changelog:
v2.1.0 (2025-11-08):
    - ✨ New: --manual-toc flag. Default behavior relies on Just-the-Docs’ native TOC.
      When --manual-toc is present, a manual TOC is generated and 'toc: false' is injected
      into the index front-matter to avoid duplicate TOCs.
    - 🔠 Manual TOC uses natural sort by TITLE and de-duplicates entries.
    - 🧷 Stable trailing newline and idempotent writes.
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

# Manual TOC marker only used when --manual-toc is enabled
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


def read_file_clean(path: Path) -> str:
    """Reads file content, handling BOM, and returns as UTF-8 string."""
    with open(path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8-sig")


def sha256(text: str) -> str:
    """Calculates SHA256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_chapter_title(filename: str):
    """Parses filename for chapter number and title."""
    match = re.match(r"chapter-(\d+)[-_ ]?(.*)\.md", filename, re.IGNORECASE)
    if match:
        chapter_number = int(match.group(1))
        raw_title = match.group(2).replace("-", " ").replace("_", " ").title()
        return chapter_number, f"Chapter {chapter_number} – {raw_title}"
    return None, Path(filename).stem.replace("-", " ").replace("_", " ").title()


def load_hashes() -> dict:
    """Loads file hashes from cache file."""
    if HASH_FILE.exists():
        with open(HASH_FILE, "r") as f:
            return json.load(f)
    return {}


def save_hashes(data: dict) -> None:
    """Saves file hashes to cache file."""
    with open(HASH_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _natural_title_key(markdown_item: str):
    """
    Extracts the [Title] from a markdown TOC item '- [Title](file.md)'
    and returns a list of chunks that produce a natural sort.
    """
    m = re.search(r"\[(.*?)\]", markdown_item)
    title = m.group(1) if m else markdown_item
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", title)]


def _build_default_index_front_matter(title: str, nav_order: int, manual_toc: bool) -> str:
    """
    Builds the index front matter. Adds 'toc: false' when manual_toc is True to
    suppress Just-the-Docs' built-in TOC (prevents duplication).
    """
    lines = [
        "---",
        f"title: {title}",
        f"nav_order: {nav_order}",
        "has_children: true",
    ]
    if manual_toc:
        lines.append("toc: false")
    lines.append("---")
    fm = "\n".join(lines)

    header = f"""
# {title}

Notes for the **{title}** section."""
    return fm + "\n" + header.strip("\n")


def create_or_update_section_index(
    target_dir: Path,
    nav_order: int,
    chapter_links=None,
    dry_run: bool = False,
    manual_toc: bool = False,
) -> None:
    """
    Creates or updates the index.md file for a section.
    - If manual_toc=False: do NOT generate a manual TOC (rely on Just-the-Docs).
      If an old marker exists, strip everything from the marker down.
    - If manual_toc=True: generate manual TOC with correct spacing and marker,
      add 'toc: false' in front-matter, de-duplicate & natural-sort by Title.
    """
    index_file = target_dir / "index.md"
    title = section_title_map.get(target_dir.name.lower(), target_dir.name.title())
    default_content = _build_default_index_front_matter(title, nav_order, manual_toc)

    # Determine the preserved content above the marker (or full content if no marker)
    if index_file.exists():
        existing = read_file_clean(index_file)
        if TOC_MARKER in existing:
            content_before = existing.split(TOC_MARKER)[0].rstrip()
        else:
            content_before = existing.rstrip()
    else:
        content_before = default_content.rstrip()

    # If the file was missing or had a different front matter (e.g., toggling manual_toc),
    # ensure we rebuild the header from the default template.
    # Detect by comparing the start of content_before to what default would produce.
    # We'll trust the default when index does not exist or when toggling manual_toc.
    if not index_file.exists():
        content_before = default_content.rstrip()
    else:
        # If switching manual_toc mode, front-matter may need update.
        fm_prefix = _build_default_index_front_matter(title, nav_order, manual_toc)
        # If the existing header differs materially (title/nav_order/has_children/toc),
        # rebuild the preserved header to the new default to keep things consistent.
        if not content_before.strip().startswith(fm_prefix.split("\n")[0]):
            content_before = fm_prefix.rstrip()

    # If manual_toc is disabled, we simply write content_before (no TOC block).
    if not manual_toc:
        content = content_before
        if not content.endswith("\n"):
            content += "\n"

        # Write only if different
        if index_file.exists():
            existing_content = read_file_clean(index_file)
            if existing_content == content:
                print(f"📁 Index is up to date: {index_file}")
                return
        if not dry_run:
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(content)
        print(f"📁 Index {'would be updated' if dry_run else 'updated'}: {index_file}")
        return

    # ---- Manual TOC mode below ----

    # TOC block with Layout A:
    # blank line after content_before
    # marker, then blank line
    # H2, then blank line
    # '---', then blank line
    TOC_MARKUP_STRING = (
        "\n\n"
        + TOC_MARKER
        + "\n\n"
        + "## TABLE OF CONTENTS\n\n"
        + "---\n\n"
    )

    content = f"{content_before}{TOC_MARKUP_STRING}"
    if not content.endswith("\n"):
        content += "\n"

    if chapter_links:
        # De-duplicate exact duplicates while preserving first occurrence
        unique = list(dict.fromkeys(chapter_links))
        # Natural sort by TITLE
        unique_sorted = sorted(unique, key=_natural_title_key)
        content += "\n".join(unique_sorted)
        if not content.endswith("\n"):
            content += "\n"

    # Write only if different
    if index_file.exists():
        existing_content = read_file_clean(index_file)
        if existing_content == content:
            print(f"📁 Index is up to date: {index_file}")
            return

    if not dry_run:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"📁 Index {'would be updated' if dry_run else 'updated'}: {index_file}")


def sync_notes(dry_run: bool = False, clean: bool = False, manual_toc: bool = False) -> None:
    """Main function to sync notes."""
    if clean and HASH_FILE.exists():
        if not dry_run:
            HASH_FILE.unlink()
        print(f"🧼 {'Would remove' if dry_run else 'Removed'} existing .sync_hashes.json")

    cache = load_hashes()
    updated = {}
    any_synced = False
    reverse_hash_map = {v: k for k, v in cache.items()}

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
        nav_order = section_order_map.get(section_name.lower(), 90) if section_name else 1
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

        # --- Index generation ---
        chapter_links = []
        for fname in md_files:
            if fname.lower() == "index.md":
                continue
            _, title = parse_chapter_title(fname)
            chapter_links.append(f"- [{title}]({fname})")

        if section_title:
            create_or_update_section_index(
                target_dir,
                nav_order,
                chapter_links=chapter_links,
                dry_run=dry_run,
                manual_toc=manual_toc,
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
        "--clean", action="store_true", help="Remove .sync_hashes.json and force rebuild"
    )
    parser.add_argument(
        "--manual-toc",
        action="store_true",
        help="Generate a manual section TOC in index.md and set 'toc: false' to disable Just-the-Docs' built-in TOC.",
    )
    args = parser.parse_args()
    sync_notes(dry_run=args.dry_run, clean=args.clean, manual_toc=args.manual_toc)

