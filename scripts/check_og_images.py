#!/usr/bin/env python3
"""
Pre-commit hook: Check that OG images exist for all content.

For each markdown file in content/blog/ and content/projects/,
verify that a corresponding PNG exists in static/og_images/.

Exit codes:
- 0: All OG images exist
- 1: Missing OG images found
"""

import sys
from pathlib import Path

CONTENT_DIR = Path("content")
STATIC_DIR = Path("static")
OG_IMAGES_DIR = STATIC_DIR / "og_images"


def get_expected_og_filename(markdown_file: Path) -> str:
    """Get the expected OG image filename for a markdown file."""
    return f"{markdown_file.stem}.png"


def check_og_image_exists(markdown_file: Path) -> tuple[bool, str]:
    """Check if OG image exists for a markdown file."""
    og_filename = get_expected_og_filename(markdown_file)
    og_path = OG_IMAGES_DIR / og_filename

    if og_path.exists():
        return True, og_filename
    return False, og_filename


def main():
    """Main entry point."""
    errors = []
    checked = 0
    missing = 0

    # Check blog content
    blog_dir = CONTENT_DIR / "blog"
    if blog_dir.exists():
        for md_file in blog_dir.rglob("*.md"):
            if md_file.name.startswith("_"):
                continue

            checked += 1
            exists, filename = check_og_image_exists(md_file)
            if not exists:
                errors.append(
                    f"blog/{md_file.name}: Missing static/og_images/{filename}"
                )
                missing += 1

    # Check projects content
    projects_dir = CONTENT_DIR / "projects"
    if projects_dir.exists():
        for md_file in projects_dir.rglob("*.md"):
            if md_file.name.startswith("_"):
                continue

            checked += 1
            exists, filename = check_og_image_exists(md_file)
            if not exists:
                errors.append(
                    f"projects/{md_file.name}: Missing static/og_images/{filename}"
                )
                missing += 1

    # Report results
    if errors:
        print("\n[MISSING OG IMAGES]")
        for error in errors:
            print(f"  {error}")
        print(
            f"\nPre-commit failed: {missing}/{checked} content files missing OG images"
        )
        print(f"Run: python scripts/generate_og.py")
        return 1

    print(f"Checked OG images for {checked} content files - OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
