#!/usr/bin/env python3
"""
Approach #8: Storytelling Carousel (Connected Narrative)
========================================================
Creates 5 screenshots as one continuous story following the framework:
1. Hook - Emotional problem statement
2. Solution - App solves it
3. How - Key feature in action
4. Proof - Results/transformation
5. CTA - Social proof + urgency

Design features:
- Color flow that evolves across screenshots
- Numbered steps create completion drive
- Final screenshot has premium gold treatment

Usage:
    python approach_08_storytelling.py

Output: ../output/08_storytelling/
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IPHONE_SIZE = (1290, 2796)
CORNER_RADIUS = 55

# Story-driven color palette (evolves through screenshots)
STORY_COLORS = [
    {"bg": ("#2D1B4E", "#1A1A2E"), "accent": "#FF6B6B", "text": "#FFFFFF"},  # 1: Problem (dark, tense)
    {"bg": ("#1A1A2E", "#16213E"), "accent": "#4ECDC4", "text": "#FFFFFF"},  # 2: Discovery (hope)
    {"bg": ("#16213E", "#0F3460"), "accent": "#45B7D1", "text": "#FFFFFF"},  # 3: Action (momentum)
    {"bg": ("#0F3460", "#1A4B1A"), "accent": "#96E6A1", "text": "#FFFFFF"},  # 4: Success (growth)
    {"bg": ("#1A4B1A", "#2D2D0D"), "accent": "#FFD700", "text": "#FFFFFF"},  # 5: Premium (gold)
]

# Story content for habit app
STORY_CONTENT = [
    {
        "step": "1",
        "headline": "Tired of Starting Over?",
        "subtext": "We've all been there.\nNew year, new goals, same result.",
        "cta": None,
    },
    {
        "step": "2",
        "headline": "Meet Your New Routine",
        "subtext": "Simple tracking that actually sticks.",
        "cta": None,
    },
    {
        "step": "3",
        "headline": "Build Your Streak",
        "subtext": "One day at a time.\nWatch your progress grow.",
        "cta": None,
    },
    {
        "step": "4",
        "headline": "See Real Results",
        "subtext": "47 days and counting.\nYou've got this.",
        "cta": None,
    },
    {
        "step": "5",
        "headline": "Join 50,000+ Users",
        "subtext": "4.9 Rating\n\nStart your streak today.",
        "cta": "Download Free",
    },
]


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient(width, height, color1, color2, direction="vertical"):
    """Create a smooth gradient."""
    img = Image.new('RGB', (width, height))
    c1 = hex_to_rgb(color1)
    c2 = hex_to_rgb(color2)

    for i in range(height if direction == "vertical" else width):
        ratio = i / (height if direction == "vertical" else width)
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)

        if direction == "vertical":
            ImageDraw.Draw(img).line([(0, i), (width, i)], fill=(r, g, b))
        else:
            ImageDraw.Draw(img).line([(i, 0), (i, height)], fill=(r, g, b))

    return img


def load_font(size, bold=False):
    """Load system font."""
    paths = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


def add_rounded_corners(img, radius):
    """Add rounded corners."""
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    output = Image.new('RGBA', img.size, (0, 0, 0, 0))
    output.paste(img, mask=mask)
    return output


def create_step_indicator(draw, step, x, y, colors, is_current=False):
    """Draw a numbered step indicator."""
    size = 100

    # Background circle
    if is_current:
        fill_color = hex_to_rgb(colors["accent"])
    else:
        fill_color = (80, 80, 80)

    draw.ellipse([(x - size//2, y - size//2),
                  (x + size//2, y + size//2)], fill=fill_color)

    # Step number
    font = load_font(55, bold=True)
    draw.text((x, y), step, fill=(255, 255, 255), font=font, anchor="mm")


def create_progress_bar(draw, current_step, total_steps, y, width, colors):
    """Draw a progress bar at the top."""
    bar_height = 8
    margin = 80
    bar_width = width - margin * 2
    segment_width = bar_width / total_steps
    gap = 10

    for i in range(total_steps):
        x1 = margin + i * segment_width + gap/2
        x2 = margin + (i + 1) * segment_width - gap/2

        if i < current_step:
            color = hex_to_rgb(colors["accent"])
        else:
            color = (60, 60, 60)

        draw.rounded_rectangle(
            [(x1, y), (x2, y + bar_height)],
            radius=bar_height//2,
            fill=color
        )


def create_glow_effect(img, color, radius=50):
    """Add a subtle glow behind an image."""
    glow_size = (img.width + radius * 4, img.height + radius * 4)
    glow = Image.new('RGBA', glow_size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    glow_draw.rounded_rectangle(
        [(radius * 2, radius * 2),
         (img.width + radius * 2, img.height + radius * 2)],
        radius=CORNER_RADIUS,
        fill=(*hex_to_rgb(color), 60)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius))

    return glow


def create_story_screenshot(
    raw_screenshot_path,
    step_index,
    output_path
):
    """Create a single screenshot in the story sequence."""
    width, height = IPHONE_SIZE
    colors = STORY_COLORS[step_index]
    content = STORY_CONTENT[step_index]

    # Create gradient background
    bg_colors = colors["bg"]
    background = create_gradient(width, height, bg_colors[0], bg_colors[1])
    img = background.convert('RGBA')
    draw = ImageDraw.Draw(img)

    # Progress bar at top
    create_progress_bar(draw, step_index + 1, 5, 120, width, colors)

    # Main headline
    headline_font = load_font(int(width * 0.075), bold=True)
    headline_y = int(height * 0.09)

    # Multi-line headline support
    headline = content["headline"]
    bbox = draw.textbbox((0, 0), headline, font=headline_font)
    text_width = bbox[2] - bbox[0]
    headline_x = (width - text_width) // 2

    draw.text((headline_x, headline_y), headline,
              fill=hex_to_rgb(colors["text"]), font=headline_font)

    # Subtext
    subtext_font = load_font(int(width * 0.04))
    subtext_y = headline_y + int(width * 0.12)

    if content["subtext"]:
        for line in content["subtext"].split('\n'):
            bbox = draw.textbbox((0, 0), line, font=subtext_font)
            text_width = bbox[2] - bbox[0]
            line_x = (width - text_width) // 2
            draw.text((line_x, subtext_y), line,
                     fill=(*hex_to_rgb(colors["text"])[:3],), font=subtext_font)
            subtext_y += int(width * 0.06)

    # App screenshot with glow
    if os.path.exists(raw_screenshot_path):
        screenshot = Image.open(raw_screenshot_path).convert('RGBA')

        # Scale
        target_width = int(width * 0.7)
        scale = target_width / screenshot.width
        target_height = int(screenshot.height * scale)
        screenshot = screenshot.resize((target_width, target_height), Image.LANCZOS)

        # Add rounded corners
        screenshot = add_rounded_corners(screenshot, CORNER_RADIUS)

        # Create glow
        glow = create_glow_effect(screenshot, colors["accent"], radius=40)

        # Position (vertically centered in remaining space)
        screenshot_y = int(height * 0.32)
        screenshot_x = (width - target_width) // 2
        glow_x = screenshot_x - 80
        glow_y = screenshot_y - 80

        # Composite
        img.paste(glow, (glow_x, glow_y), glow)
        img.paste(screenshot, (screenshot_x, screenshot_y), screenshot)

    # CTA button on final screenshot
    if content["cta"]:
        cta_font = load_font(55, bold=True)
        cta_y = height - 350
        cta_text = content["cta"]

        bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        btn_width = bbox[2] - bbox[0] + 120
        btn_height = 120
        btn_x = (width - btn_width) // 2

        # Gold gradient button
        draw.rounded_rectangle(
            [(btn_x, cta_y), (btn_x + btn_width, cta_y + btn_height)],
            radius=60,
            fill=hex_to_rgb(colors["accent"])
        )

        draw.text(
            (width // 2, cta_y + btn_height // 2),
            cta_text,
            fill=(0, 0, 0),
            font=cta_font,
            anchor="mm"
        )

        # Stars rating
        stars_y = cta_y - 80
        stars_text = "4.9"
        rating_font = load_font(50, bold=True)
        draw.text((width // 2, stars_y), stars_text,
                 fill=hex_to_rgb("#FFD700"), font=rating_font, anchor="mm")

    # Step indicator in corner
    step_x = width - 100
    step_y = height - 150
    create_step_indicator(draw, content["step"], step_x, step_y, colors, is_current=True)

    # Save
    img.convert('RGB').save(output_path, quality=95)
    print(f"  Saved: {output_path}")


def main():
    """Generate all story screenshots."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "08_storytelling")

    # Get screenshots
    raw_files = sorted([f for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    print(f"\n{'='*60}")
    print("APPROACH #8: Storytelling Carousel")
    print(f"{'='*60}\n")

    for i in range(5):
        content = STORY_CONTENT[i]
        print(f"Screenshot {i+1}: {content['headline']}")

        raw_path = os.path.join(raw_dir, raw_files[i % len(raw_files)]) if raw_files else ""
        output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")

        create_story_screenshot(raw_path, i, output_path)
        print()

    print(f"Done! Screenshots saved to: {output_dir}")


if __name__ == "__main__":
    main()
