#!/usr/bin/env python3
"""
Pre-commit hook: Validate markdown frontmatter for bgslabs content.

Required fields:
- title (error if missing)
- date (error if missing)
- description (warning if missing)

Exit codes:
- 0: All checks passed
- 1: One or more errors found
"""

import sys
import tomllib
from pathlib import Path

REQUIRED_FIELDS = ["title", "date"]
OPTIONAL_FIELDS = ["description", "template", "taxonomies"]

CONTENT_DIR = Path("content")


def parse_frontmatter(content: str) -> dict | None:
    """Parse TOML frontmatter from markdown content."""
    match = content.split("+++\n")
    if len(match) < 3:
        return None

    toml_content = match[1]
    try:
        return tomllib.loads(toml_content)
    except Exception:
        return None


def validate_frontmatter(file_path: Path) -> tuple[bool, list[str]]:
    """Validate frontmatter of a single markdown file."""
    errors = []
    warnings = []

    try:
        content = file_path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)

        if frontmatter is None:
            errors.append(f"{file_path}: Could not parse frontmatter")
            return False, errors + warnings

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in frontmatter or not frontmatter[field]:
                errors.append(f"{file_path}: Missing required field '{field}'")

        # Check optional fields
        if "description" not in frontmatter:
            warnings.append(f"{file_path}: Missing optional field 'description'")

    except Exception as e:
        errors.append(f"{file_path}: Error reading file - {e}")

    return len(errors) == 0, errors + warnings


def main():
    """Main entry point."""
    all_errors = []
    all_warnings = []

    # Find all markdown files in content directory
    md_files = list(CONTENT_DIR.rglob("*.md"))

    if not md_files:
        print("No markdown files found in content/")
        return 0

    for md_file in md_files:
        # Skip special files
        if md_file.name.startswith("_"):
            continue

        is_valid, messages = validate_frontmatter(md_file)
        for msg in messages:
            if (
                "Missing required" in msg
                or "Could not parse" in msg
                or "Error reading" in msg
            ):
                all_errors.append(msg)
            else:
                all_warnings.append(msg)

    # Report results
    if all_warnings:
        print("\n[WARNINGS]")
        for warning in all_warnings:
            print(f"  {warning}")

    if all_errors:
        print("\n[ERRORS]")
        for error in all_errors:
            print(f"  {error}")
        print(f"\nPre-commit failed: {len(all_errors)} error(s) found")
        return 1

    print(f"Validated {len(md_files)} markdown files - OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
