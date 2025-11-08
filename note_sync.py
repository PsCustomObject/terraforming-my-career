#!/usr/bin/env python3

"""
sync_notes.py — Auto-sync Markdown notes to docs/ folder for Just the Docs

- Adds YAML front matter
- Syncs renamed files
- Detects and removes stale files in docs/
- Supports nested directory structures with automatic index generation
- Canonical parent resolution from existing index front-matter
- Cleaner directory titles (Option A) + numeric-prefix stripping used for ordering
- Handles special cases of folders containing subfolders vs resource-only folders
- Generates manual TOC only for leaf folders (no subfolders) at depth 2+

Version: v3.1.0
Author: PsCustomObject (2025)
"""

import os
import hashlib
import json
import re
import argparse
from pathlib import Path
from typing import Optional, Tuple, Dict, List

SOURCE_DIR = Path(".").resolve()
DOCS_DIR = SOURCE_DIR / "docs"
HASH_FILE = SOURCE_DIR / ".sync_hashes.json"
EXCLUDE_DIRS = {"docs", ".git", "__pycache__"}

# Manual TOC marker used when we inject a custom list
TOC_MARKER = "<!-- TOC:DO-NOT-EDIT -->"

# Top-level section configuration
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


def parse_chapter_title(filename: str) -> Tuple[Optional[int], str]:
    """Parses filename for chapter number and title with better edge case handling."""
    # Special handling for README
    if filename.lower() == "readme.md":
        return None, "README"

    match = re.match(r"chapter[-_ ]?(\d+)[-_ ]?(.*?)\.md$", filename, re.IGNORECASE)
    if match:
        chapter_number = int(match.group(1))
        raw_title = match.group(2).replace("-", " ").replace("_", " ").strip()
        title_suffix = f" — {raw_title.title()}" if raw_title else ""
        return chapter_number, f"Chapter {chapter_number}{title_suffix}"
    # Fallback: clean up filename stem
    stem = Path(filename).stem
    clean_title = stem.replace("-", " ").replace("_", " ").strip()
    return None, clean_title.title() if clean_title else "Untitled"


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


def _extract_front_matter(content: str) -> Tuple[Dict, bool]:
    """
    Extracts front matter from content.
    Returns (front_matter_dict, has_valid_fm).
    """
    if not content.strip().startswith("---"):
        return {}, False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, False

    fm_dict = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            fm_dict[key.strip()] = value.strip()

    return fm_dict, True


def get_existing_title_for_dir(rel_path: Path) -> Optional[str]:
    """Return the exact 'title' from docs/<rel>/index.md, if present."""
    idx = DOCS_DIR / rel_path / "index.md"
    if idx.exists():
        try:
            c = read_file_clean(idx)
            fm, ok = _extract_front_matter(c)
            if ok and fm.get("title"):
                return fm["title"]
        except Exception:
            pass
    if len(rel_path.parts) == 1:
        mapped = section_title_map.get(rel_path.name.lower())
        if mapped:
            return mapped
    return None


def _split_numeric_prefix(name: str) -> Tuple[Optional[int], str]:
    """If name starts with '01-', return (1, 'rest'); else (None, name)."""
    m = re.match(r"^\s*(\d+)[-_ ]+(.*)$", name)
    if m:
        return int(m.group(1)), m.group(2)
    return None, name


def clean_dir_title(dir_name: str, parent_title: Optional[str]) -> Tuple[str, int]:
    """
    Produce a human title for a directory and a nav_order derived from numeric prefix.
    Rules (Option A):
      - If name has leading number, use it for nav_order, but strip it from visible title.
      - Replace - and _ with spaces, Title-Case.
      - If the title starts with the parent's title plus ' - ' (case-insensitive),
        drop that repeated prefix.
    Returns (title, nav_order).
    """
    num, remainder = _split_numeric_prefix(dir_name)
    nav = num if num is not None else 10  # default 10 if no numeric prefix
    visible = remainder.strip()

    if parent_title:
        norm_parent = parent_title.strip().lower()
        if visible.lower().startswith(norm_parent + " - "):
            visible = visible[len(parent_title) + 3 :].lstrip()

    visible = visible.replace("-", " ").replace("_", " ").strip()

    def smart_title(s: str) -> str:
        parts = s.split()
        acronyms = {
            "aws",
            "iam",
            "cpu",
            "gpu",
            "api",
            "ssl",
            "tls",
            "url",
            "http",
            "https",
            "dns",
        }
        out = []
        for p in parts:
            out.append(p.upper() if p.lower() in acronyms else p.capitalize())
        return " ".join(out) if out else s

    title = smart_title(visible) if visible else "Untitled"
    return title, nav


def has_markdown_files_recursive(directory: Path) -> bool:
    """Check if a directory or any of its subdirectories contain markdown files (excludes index.md)."""
    for root, _, files in os.walk(directory):
        if any(f.endswith(".md") and f.lower() != "index.md" for f in files):
            return True
    return False


def has_child_dir_with_markdown(rel_path: Path) -> bool:
    """
    Return True if rel_path has at least one *immediate* child directory that (recursively)
    contains markdown files. Resource-only folders do NOT count.
    """
    src_dir = SOURCE_DIR / rel_path
    if not src_dir.exists() or not src_dir.is_dir():
        return False
    for child in src_dir.iterdir():
        if child.is_dir() and child.name not in EXCLUDE_DIRS:
            if has_markdown_files_recursive(child):
                return True
    return False


def _build_index_front_matter(
    title: str,
    nav_order: int,
    parent: Optional[str] = None,
    has_children: bool = False,
    toc_false: bool = False,
) -> str:
    """
    Build front matter.
    - has_children: Set to True only if this folder has child directories with markdown
    - toc_false: Set to True to suppress built-in TOC when we add a manual list
    """
    lines = ["---", f"title: {title}"]
    if parent:
        lines.append(f"parent: {parent}")
    lines.append(f"nav_order: {nav_order}")
    if has_children:
        lines.append("has_children: true")
    if toc_false:
        lines.append("toc: false")
    lines.append("---")
    return "\n".join(lines)


def create_or_update_index(
    target_dir: Path,
    rel_path: Path,
    nav_order: int,
    toc_lines: Optional[List[str]] = None,
    dry_run: bool = False,
) -> None:
    """
    Create or update the index.md file for a directory with optional inline TOC.
    - If toc_lines is provided, inject a manual TOC section and set 'toc: false' to suppress built-in TOC.
    - has_children is set based on whether this directory has subdirectories with markdown files.
    """
    index_file = target_dir / "index.md"

    # Determine parent title
    if len(rel_path.parts) == 0:
        dir_name = "Home"
        parent_title_for_this_index = None
        # Home should be first
        nav_order = 1
    elif len(rel_path.parts) == 1:
        section_key = rel_path.parts[0].lower()
        dir_name = section_title_map.get(section_key, rel_path.parts[0].title())
        parent_title_for_this_index = None
    else:
        parent_path = rel_path.parent
        parent_title_for_this_index = get_existing_title_for_dir(parent_path)
        if not parent_title_for_this_index:
            if len(parent_path.parts) == 1:
                parent_title_for_this_index = section_title_map.get(
                    parent_path.parts[0].lower(), parent_path.parts[0].title()
                )
            else:
                parent_title_for_this_index = parent_path.name.title()

        dir_name, _ = clean_dir_title(rel_path.name, parent_title_for_this_index)

    # Check if this directory has child directories with markdown
    has_subdirs = has_child_dir_with_markdown(rel_path)

    # Determine whether to suppress built-in TOC
    toc_false = toc_lines is not None and len(toc_lines) > 0

    # Build front matter with conditional has_children
    front_matter = _build_index_front_matter(
        title=dir_name,
        nav_order=nav_order,
        parent=parent_title_for_this_index,
        has_children=has_subdirs,
        toc_false=toc_false,
    )

    # Build content
    content_before = f"{front_matter}\n\n"

    # Check for existing content after TOC marker
    if index_file.exists():
        old_content = read_file_clean(index_file)
        if TOC_MARKER in old_content:
            parts = old_content.split(TOC_MARKER, 1)
            if len(parts) == 2:
                # Get content after the marker, but skip any existing TOC
                remaining = parts[1].strip()
                # Skip lines that look like TOC entries or TOC headers
                lines = remaining.split("\n")
                non_toc_lines = []
                skip_toc = True
                for line in lines:
                    stripped = line.strip()
                    if skip_toc:
                        # Skip empty lines, markdown list items, and TABLE OF CONTENTS header
                        if (
                            stripped
                            and not stripped.startswith("- [")
                            and not stripped.startswith("## TABLE OF CONTENTS")
                        ):
                            skip_toc = False
                            non_toc_lines.append(line)
                    else:
                        non_toc_lines.append(line)

                if non_toc_lines:
                    content_before += "\n".join(non_toc_lines) + "\n"

    # Inject manual TOC if provided
    if toc_lines:
        sorted_toc = sorted(toc_lines, key=_natural_title_key)
        toc_md = "\n".join(sorted_toc)
        content = f"{content_before}{TOC_MARKER}\n\n{toc_md}\n"
        if not content.endswith("\n"):
            content += "\n"
    else:
        content = content_before
        if not content.endswith("\n"):
            content += "\n"

    # Write only if changed
    if index_file.exists():
        existing_content = read_file_clean(index_file)
        if existing_content == content:
            print(f"📄 Index is up to date: {index_file}")
            return

    if not dry_run:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"📝 Index {'would be updated' if dry_run else 'updated'}: {index_file}")


def clean_orphaned_files(updated: dict, dry_run: bool = False) -> int:
    """Remove files/dirs in docs/ that no longer exist in source. Return count removed."""
    orphaned_count = 0

    # Orphaned files
    for root, _, files in os.walk(DOCS_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            doc_file = Path(root) / fname
            rel_path = doc_file.relative_to(DOCS_DIR)
            if fname == "index.md":
                continue
            src_file = SOURCE_DIR / rel_path
            hash_key = str(rel_path)
            if not src_file.exists() and hash_key not in updated:
                if not dry_run:
                    doc_file.unlink()
                print(
                    f"🗑️  {'Would remove' if dry_run else 'Removed'} orphaned file: {doc_file}"
                )
                orphaned_count += 1

    # Empty dirs (or dirs with only empty content)
    for root, _, _ in os.walk(DOCS_DIR, topdown=False):
        root_path = Path(root)
        if root_path == DOCS_DIR:
            continue
        rel_path = root_path.relative_to(DOCS_DIR)
        src_dir = SOURCE_DIR / rel_path

        has_md_files = False
        if src_dir.exists():
            for r, _, fl in os.walk(src_dir):
                if any(f.endswith(".md") for f in fl):
                    has_md_files = True
                    break

        if not src_dir.exists() or not has_md_files:
            try:
                if not dry_run:
                    for f in root_path.glob("*"):
                        if f.is_file():
                            f.unlink()
                    root_path.rmdir()
                print(
                    f"🗑️  {'Would remove' if dry_run else 'Removed'} empty directory: {root_path}"
                )
                orphaned_count += 1
            except OSError:
                pass

    return orphaned_count


def sync_notes(dry_run: bool = False, clean: bool = False) -> None:
    """Sync notes with nested directory support and smart TOC generation."""
    stats = {"synced": 0, "renamed": 0, "orphaned": 0, "unchanged": 0, "indexes": 0}

    if clean and HASH_FILE.exists():
        if not dry_run:
            HASH_FILE.unlink()
        print(
            f"🧼 {'Would remove' if dry_run else 'Removed'} existing .sync_hashes.json"
        )

    cache = load_hashes()
    updated = {}
    reverse_hash_map = {v: k for k, v in cache.items()}

    print("\n" + "=" * 70)
    print("🔍 DIRECTORY SCAN - Processing all directories...")
    print("=" * 70)

    for root, _, files in os.walk(SOURCE_DIR):
        rel = Path(root).relative_to(SOURCE_DIR)

        print(f"\n📂 Processing: {rel if rel.parts else 'ROOT'}")

        if any(p in EXCLUDE_DIRS for p in rel.parts):
            print("   ⏭️  Skipped (excluded directory)")
            continue

        md_files = sorted(
            f for f in files if f.endswith(".md") and f.lower() != "index.md"
        )

        src_path = Path(root)
        has_recursive_md = has_markdown_files_recursive(src_path)

        print(f"   📄 Direct MD files: {len(md_files)}")
        print(f"   🔄 Has MD files in subdirs: {has_recursive_md}")

        if not md_files and not has_recursive_md:
            print("   ⏭️  Skipped (no markdown files in tree)")
            continue

        target_dir = DOCS_DIR / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created/verified: {target_dir}")

        # CORRECTED LOGIC:
        # Files should be excluded from navigation based on their depth:
        # - Depth 0 (root): Never exclude (README should show)
        # - Depth 1 (sections like AWS, Terraform): Exclude if section has subfolders
        # - Depth 2+ (nested folders): Always exclude (only show in parent's TOC)

        depth = len(rel.parts)
        should_exclude_files_from_nav = False

        if depth == 0:
            # Root level - never exclude
            should_exclude_files_from_nav = False
        elif depth == 1:
            # Top-level section - exclude only if it has child directories
            should_exclude_files_from_nav = has_child_dir_with_markdown(rel)
        else:
            # Depth 2+ (nested folders) - always exclude from nav
            # These files will only appear in their parent folder's TOC
            should_exclude_files_from_nav = True

        print(f"   📏 Depth: {depth}")
        print(f"   🚫 Exclude files from nav: {should_exclude_files_from_nav}")

        # Determine parent title for files in this directory
        # IMPORTANT: Don't set parent if file is excluded from nav
        if len(rel.parts) == 0:
            parent_title = None
        elif len(rel.parts) == 1:
            section_name = rel.parts[0]
            parent_title = section_title_map.get(
                section_name.lower(), section_name.title()
            )
        else:
            parent_title = get_existing_title_for_dir(
                rel.parent
            ) or section_title_map.get(rel.parent.name.lower(), rel.parent.name.title())

        # --- File sync ---
        for i, fname in enumerate(md_files):
            src_file = Path(root) / fname
            dst_file = target_dir / fname
            body = read_file_clean(src_file)

            chapter_num, title = parse_chapter_title(fname)
            nav_order_entry = chapter_num if chapter_num is not None else (i + 1)

            front_matter = f'---\ntitle: "{title}"\n'

            # KEY FIX: Only set parent if file is NOT excluded from nav
            # When nav_exclude is true, parent causes issues in Just the Docs
            if should_exclude_files_from_nav:
                # Excluded from nav - don't set parent, just exclude
                front_matter += "nav_exclude: true\n"
            else:
                # Visible in nav - set parent and nav_order
                if parent_title:
                    front_matter += f"parent: {parent_title}\n"
                front_matter += f"nav_order: {nav_order_entry}\n"

            front_matter += "---\n\n"

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
                        print(f"   🔄 Renamed (deleted old): {old_path}")
                        stats["renamed"] += 1

                if not dry_run:
                    with open(dst_file, "w", encoding="utf-8") as f:
                        f.write(final)
                print(f"   {'📝 Would sync' if dry_run else '✅ Synced'}: {fname}")
                stats["synced"] += 1
            else:
                stats["unchanged"] += 1

        # --- Index generation for this directory ---
        if md_files or has_recursive_md:
            # Decide whether to generate TOC
            # IMPORTANT: For folders with has_children: true, Just the Docs automatically
            # shows child pages in the nav. We only need manual TOC for depth 2+ folders
            # where files are hidden from nav.

            toc_lines: List[str] = []
            has_subdirs = has_child_dir_with_markdown(rel)

            # Only generate TOC for depth 2+ folders with files
            # Don't generate for folders with has_children (nav handles it)
            should_generate_toc = False

            if depth >= 2 and not has_subdirs:
                # Depth 2+ with files (files are hidden from nav) - generate TOC
                should_generate_toc = True
                for fname in md_files:
                    _, t = parse_chapter_title(fname)
                    toc_lines.append(f"- [{t}]({fname})")

            # Only pass toc_lines if we should generate TOC
            toc_to_inject = toc_lines if should_generate_toc else None

            # Determine nav_order
            if len(rel.parts) == 0:
                # Root gets nav_order 1 (handled in create_or_update_index)
                nav_order = 1
            elif len(rel.parts) == 1:
                nav_order = section_order_map.get(rel.parts[0].lower(), 90)
            else:
                _, nav_order = clean_dir_title(
                    rel.name, get_existing_title_for_dir(rel.parent)
                )

            create_or_update_index(
                target_dir=target_dir,
                rel_path=rel,
                nav_order=nav_order,
                toc_lines=toc_to_inject,
                dry_run=dry_run,
            )
            stats["indexes"] += 1

    print("\n" + "=" * 70)
    print("🧹 CLEANUP PHASE - Removing orphaned files...")
    print("=" * 70)

    stats["orphaned"] = clean_orphaned_files(updated, dry_run)

    if not dry_run:
        save_hashes(updated)

    print("\n" + "=" * 70)
    print(
        "🎉 Sync complete!"
        if not dry_run
        else "🎉 Dry run complete. No files were written."
    )
    print(f"\n📊 Summary:")
    print(f"   ✅ Synced: {stats['synced']}")
    print(f"   🔄 Renamed: {stats['renamed']}")
    print(f"   📑 Indexes updated: {stats['indexes']}")
    print(f"   🗑️  Orphaned removed: {stats['orphaned']}")
    print(f"   📄 Unchanged: {stats['unchanged']}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync Markdown notes to docs/ for Just the Docs with nested TOC handling"
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
