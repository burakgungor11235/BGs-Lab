#!/usr/bin/env python3
"""
OG Image Generator for bgslabs
"""

import re
import tomllib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

WIDTH = 1200
HEIGHT = 630
PADDING = 64
CONTENT_WIDTH = WIDTH - (PADDING * 2)

CARBON_COLORS = {
    "background": "#FFFFFF",
    "text_primary": "#161616",
    "text_secondary": "#525252",
    "text_tertiary": "#8D8D8D",
    "accent_blue": "#0F62FE",
    "accent_green": "#198038",
    "border": "#E0E0E0",
}

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"
STATIC_DIR = BASE_DIR / "static"
FONTS_DIR = STATIC_DIR / "fonts"
OG_IMAGES_DIR = STATIC_DIR / "og_images"


def load_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a font from the fonts directory."""
    font_path = FONTS_DIR / font_name
    if not font_path.exists():
        raise FileNotFoundError(f"Font not found: {font_path}")
    return ImageFont.truetype(str(font_path), size)


def parse_frontmatter(content: str) -> dict:
    """Parse TOML frontmatter from markdown content."""
    match = re.match(r"\+\+\+\n(.*?)\n\+\+\+", content, re.DOTALL)
    if not match:
        return {}
    toml_content = match.group(1)
    try:
        data = tomllib.loads(toml_content)
        extra = data.get("extra", {})
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "date": data.get("date", ""),
            "tags": (
                data.get("taxonomies", {}).get("tags", [])
                if isinstance(data.get("taxonomies"), dict)
                else []
            ),
            "categories": (
                data.get("taxonomies", {}).get("categories", [])
                if isinstance(data.get("taxonomies"), dict)
                else []
            ),
            "stack": extra.get("stack", []),
        }
    except Exception as e:
        print(f"Error parsing frontmatter: {e}")
        return {}


def wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int = 2
) -> list:
    """Wrap text to fit within max_width, return list of lines (max max_lines)."""
    if not text:
        return [""] * max_lines

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = font.getbbox(test_line)
        test_width = bbox[2] - bbox[0]

        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
            if len(lines) >= max_lines:
                break

    if current_line and len(lines) < max_lines:
        lines.append(current_line)

    while len(lines) < max_lines:
        lines.append("")

    return lines


def truncate_with_ellipsis(
    text: str, font: ImageFont.FreeTypeFont, max_width: int
) -> str:
    """Truncate text with ellipsis if it doesn't fit."""
    if not text:
        return ""
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]

    if text_width <= max_width:
        return text

    ellipsis = "..."
    ellipsis_bbox = font.getbbox(ellipsis)
    ellipsis_width = ellipsis_bbox[2] - ellipsis_bbox[0]

    for i in range(len(text), 0, -1):
        test_text = text[:i]
        bbox = font.getbbox(test_text + ellipsis)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            return test_text + ellipsis

    return ellipsis


def estimate_read_time(content: str, words_per_minute: int = 200) -> str:
    """Estimate read time from markdown content."""
    if not content:
        return "1 min read"

    words = len(content.split())
    minutes = max(1, round(words / words_per_minute))
    return f"{minutes} min read"


def generate_og_image(
    title: str,
    description: str,
    date_str: str,
    category: str,
    tags: list,
    output_path: Path,
):
    """Generate an OG image with Carbon design - SEO optimized."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color=CARBON_COLORS["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font("IBMPlexSans-Bold.ttf", 52)
    header_font = load_font("IBMPlexSans-Bold.ttf", 24)
    meta_font = load_font("IBMPlexMono-Regular.ttf", 22)
    small_font = load_font("IBMPlexMono-Regular.ttf", 18)
    desc_font = load_font("IBMPlexSans-Regular.ttf", 28)

    accent_width = 12
    draw.rectangle(
        [(0, 0), (accent_width, HEIGHT)],
        fill=CARBON_COLORS["accent_green"],
    )

    bgs_font = load_font("IBMPlexSans-Regular.ttf", 20)
    blog_font = load_font("IBMPlexSans-Regular.ttf", 20)

    bgs_text = "bg"
    blog_text = "slabs"

    bgs_bbox = bgs_font.getbbox(bgs_text)
    blog_bbox = blog_font.getbbox(blog_text)

    bgs_width = bgs_bbox[2] - bgs_bbox[0]
    blog_width = blog_bbox[2] - blog_bbox[0]

    draw.text(
        (PADDING + 20, PADDING),
        bgs_text,
        font=bgs_font,
        fill=CARBON_COLORS["text_primary"],
    )
    draw.text(
        (PADDING + 20 + bgs_width, PADDING),
        blog_text,
        font=blog_font,
        fill=CARBON_COLORS["text_secondary"],
    )

    date_formatted = ""
    if date_str:
        try:
            date_obj = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
            date_formatted = date_obj.strftime("%Y-%m-%d")
        except:
            date_formatted = str(date_str)

    if date_formatted:
        date_bbox = meta_font.getbbox(date_formatted)
        draw.text(
            (WIDTH - PADDING - 20 - date_bbox[2], PADDING),
            date_formatted,
            font=meta_font,
            fill=CARBON_COLORS["text_tertiary"],
        )

    title_y = PADDING + 50
    title_max_width = CONTENT_WIDTH - accent_width - 20
    title_lines = wrap_text(title, title_font, title_max_width, 2)
    title_lines = [
        truncate_with_ellipsis(line, title_font, title_max_width) if line else ""
        for line in title_lines
    ]

    for i, line in enumerate(title_lines):
        if line:
            bbox = title_font.getbbox(line)
            text_height = bbox[3] - bbox[1]
            draw.text(
                (PADDING + 20 + accent_width, title_y + (i * (text_height + 8))),
                line,
                font=title_font,
                fill=CARBON_COLORS["text_primary"],
            )

    title_hr_y = title_y + (len([l for l in title_lines if l]) * 60) + 15
    draw.line(
        [(PADDING + 20 + accent_width, title_hr_y), (WIDTH - PADDING - 20, title_hr_y)],
        fill=CARBON_COLORS["text_primary"],
        width=2,
    )

    meta_y = title_hr_y + 25

    tag_text = ""
    if tags and len(tags) > 0:
        display_tags = tags[:4]
        tag_text = " | ".join(display_tags)

    meta_parts = []
    if category:
        meta_parts.append(category.upper())
    if tag_text:
        meta_parts.append(tag_text.upper())

    if meta_parts:
        meta_text = " | ".join(meta_parts)
        draw.text(
            (PADDING + 20 + accent_width, meta_y),
            meta_text,
            font=small_font,
            fill=CARBON_COLORS["accent_blue"],
        )

    read_time = estimate_read_time(description)
    info_parts = [read_time]

    if description:
        word_count = len(description.split())
        info_parts.append(f"~{word_count} words")

    info_text = "  •  ".join(info_parts)
    draw.text(
        (PADDING + 20 + accent_width, meta_y + 30),
        info_text,
        font=small_font,
        fill=CARBON_COLORS["text_tertiary"],
    )

    desc_y = meta_y + 70
    desc_lines = (
        wrap_text(description, desc_font, title_max_width, 2) if description else []
    )

    for i, line in enumerate(desc_lines):
        if line:
            bbox = desc_font.getbbox(line)
            text_height = bbox[3] - bbox[1]
            draw.text(
                (PADDING + 20 + accent_width, desc_y + (i * (text_height + 6))),
                line,
                font=desc_font,
                fill=CARBON_COLORS["text_secondary"],
            )

    footer_y = HEIGHT - PADDING - 20
    draw.line(
        [(PADDING + 20, footer_y), (WIDTH - PADDING - 20, footer_y)],
        fill=CARBON_COLORS["text_primary"],
        width=2,
    )

    author_text = "Burak Güngör"
    bbox = header_font.getbbox(author_text)
    author_width = bbox[2] - bbox[0]

    draw.text(
        (WIDTH - PADDING - 20 - author_width, footer_y + 15),
        author_text,
        font=header_font,
        fill=CARBON_COLORS["text_primary"],
    )

    site_text = "bgslabs"
    site_bbox = small_font.getbbox(site_text)
    draw.text(
        (PADDING + 20, footer_y + 15),
        site_text,
        font=small_font,
        fill=CARBON_COLORS["text_tertiary"],
    )

    img.save(output_path, "PNG", optimize=True)
    print(f"Generated: {output_path}")


def get_category_from_path(content_path: Path) -> str:
    """Determine category based on content path."""
    path_str = str(content_path)
    if "blog" in path_str:
        return "Blog"
    elif "projects" in path_str:
        return "Project"
    return "Content"


def process_content_directory(content_dir: Path):
    """Process all markdown files in a content directory."""
    if not content_dir.exists():
        print(f"Content directory not found: {content_dir}")
        return

    OG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(content_dir.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue

        if any(part in {"assets", "static"} for part in md_file.parts):
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
            frontmatter = parse_frontmatter(content)

            title = frontmatter.get("title", "")
            if not title:
                title = md_file.stem.replace("-", " ").replace("_", " ").title()

            description = frontmatter.get("description", "")
            date_str = frontmatter.get("date", "")
            tags = frontmatter.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",")]

            category = get_category_from_path(md_file)

            slug = md_file.stem
            output_path = OG_IMAGES_DIR / f"{slug}.png"

            generate_og_image(
                title=title,
                description=description,
                date_str=date_str,
                category=category,
                tags=tags,
                output_path=output_path,
            )
        except Exception as e:
            print(f"Error processing {md_file}: {e}")


def main():
    """Main entry point."""
    print("Generating OG images for bgslabs...")
    print(f"Content directory: {CONTENT_DIR}")
    print(f"Output directory: {OG_IMAGES_DIR}")
    print("-" * 50)

    for subdir in ["blog", "projects"]:
        subdir_path = CONTENT_DIR / subdir
        if subdir_path.exists():
            print(f"\nProcessing {subdir}...")
            process_content_directory(subdir_path)

    print("\n" + "-" * 50)
    print("OG image generation complete!")


if __name__ == "__main__":
    main()
