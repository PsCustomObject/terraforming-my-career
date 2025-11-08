#!/usr/bin/env python3
"""
Diagnostic script to understand directory structure
Run this from your repository root to see what the script sees
"""

import os
from pathlib import Path

SOURCE_DIR = Path(".").resolve()
EXCLUDE_DIRS = {"docs", ".git", "__pycache__"}

def has_markdown_files_recursive(directory: Path) -> bool:
    """Check if a directory or any of its subdirectories contain markdown files (excludes index.md)."""
    for root, _, files in os.walk(directory):
        if any(f.endswith(".md") and f.lower() != "index.md" for f in files):
            return True
    return False

def has_child_dir_with_markdown(rel_path: Path) -> bool:
    """Return True if rel_path has at least one immediate child directory with markdown."""
    src_dir = SOURCE_DIR / rel_path
    if not src_dir.exists() or not src_dir.is_dir():
        return False
    
    child_dirs = []
    for child in src_dir.iterdir():
        if child.is_dir() and child.name not in EXCLUDE_DIRS:
            has_md = has_markdown_files_recursive(child)
            child_dirs.append((child.name, has_md))
    
    return child_dirs

print("=" * 70)
print("DIRECTORY STRUCTURE ANALYSIS")
print("=" * 70)
print(f"Working from: {SOURCE_DIR}\n")

# Scan top-level directories
for item in sorted(SOURCE_DIR.iterdir()):
    if not item.is_dir() or item.name in EXCLUDE_DIRS:
        continue
    
    print(f"\n📁 {item.name}/")
    
    # Check for direct MD files
    md_files = [f for f in item.iterdir() if f.is_file() and f.suffix == '.md' and f.name.lower() != 'index.md']
    if md_files:
        print(f"   📄 Direct .md files: {len(md_files)}")
        for f in md_files[:3]:  # Show first 3
            print(f"      - {f.name}")
        if len(md_files) > 3:
            print(f"      ... and {len(md_files) - 3} more")
    
    # Check for child directories
    child_dirs = has_child_dir_with_markdown(Path(item.name))
    if child_dirs:
        print(f"   📂 Child directories:")
        for child_name, has_md in child_dirs:
            status = "✅ (has .md)" if has_md else "❌ (no .md)"
            print(f"      - {child_name}/ {status}")
    
    # Summary
    has_subdirs_with_md = any(has_md for _, has_md in child_dirs)
    print(f"   🎯 has_child_dir_with_markdown: {has_subdirs_with_md}")
    print(f"   💡 Files should be excluded from nav: {has_subdirs_with_md}")

print("\n" + "=" * 70)
print("Based on this analysis:")
print("- Folders with 'has_child_dir_with_markdown: True' should have files excluded")
print("- Folders with 'has_child_dir_with_markdown: False' should have files in nav")
print("=" * 70)
