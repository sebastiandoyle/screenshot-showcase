#!/usr/bin/env python3
"""
Approach #4: AI-Generated Backgrounds
=====================================
Uses pre-generated AI backgrounds (Midjourney/DALL-E) for unique visual identity.

WORKFLOW:
1. Generate backgrounds in Midjourney/DALL-E with prompts below
2. Save to: ~/Developer/screenshot-showcase/gradients/ai_*.png
3. Run this script to composite with app screenshots

MIDJOURNEY PROMPTS (copy these):

For Health/Fitness apps:
    abstract gradient background, flowing organic shapes, soft coral and mint green,
    energetic but calm, 4k, smooth minimal --ar 9:19.5 --v 6

For Productivity apps:
    abstract gradient background, geometric subtle pattern, deep blue and silver,
    professional clean modern, 4k ultra smooth --ar 9:19.5 --v 6

For Games:
    abstract gradient background, dynamic swooshes, electric purple and neon orange,
    exciting energetic vibrant, 4k smooth --ar 9:19.5 --v 6

For Social apps:
    abstract gradient background, soft bokeh lights, warm sunset pink and gold,
    friendly welcoming, 4k smooth dreamy --ar 9:19.5 --v 6

For Finance apps:
    abstract gradient background, minimal geometric, dark green and gold accent,
    trustworthy premium, 4k ultra clean --ar 9:19.5 --v 6

Usage:
    python approach_04_ai_bg.py

Output: ./output/04_ai_backgrounds/
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IPHONE_SIZE = (1290, 2796)
CORNER_RADIUS = 55

HEADLINES = [
    ("Build Habits That Stick", "One day at a time"),
    ("Track Your Progress", "See your streaks grow"),
    ("Celebrate Every Win", "Small wins matter"),
    ("Stay Motivated", "Join 50,000+ users"),
]


def load_font(size, bold=False):
    paths = ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Helvetica.ttc"]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


def add_rounded_corners(img, radius):
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    output = Image.new('RGBA', img.size, (0, 0, 0, 0))
    output.paste(img, mask=mask)
    return output


def create_screenshot(bg_path, raw_path, headline, subtitle, output_path):
    """Composite AI background with app screenshot."""
    width, height = IPHONE_SIZE

    # Load AI background
    if os.path.exists(bg_path):
        background = Image.open(bg_path).convert('RGBA')
        background = background.resize((width, height), Image.LANCZOS)
    else:
        # Fallback gradient if no AI background
        background = Image.new('RGB', (width, height), (102, 126, 234))
        draw = ImageDraw.Draw(background)
        for y in range(height):
            ratio = y / height
            r = int(102 + (118 - 102) * ratio)
            g = int(126 + (75 - 126) * ratio)
            b = int(234 + (162 - 234) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        background = background.convert('RGBA')

    # Load screenshot
    if os.path.exists(raw_path):
        screenshot = Image.open(raw_path).convert('RGBA')
    else:
        screenshot = Image.new('RGBA', (390, 844), (40, 40, 40, 255))

    # Scale screenshot
    target_width = int(width * 0.65)
    scale = target_width / screenshot.width
    target_height = int(screenshot.height * scale)
    screenshot = screenshot.resize((target_width, target_height), Image.LANCZOS)
    screenshot = add_rounded_corners(screenshot, CORNER_RADIUS)

    # Create glow
    glow = Image.new('RGBA', (target_width + 100, target_height + 100), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(
        [(50, 50), (target_width + 50, target_height + 50)],
        radius=CORNER_RADIUS, fill=(255, 255, 255, 30)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=40))

    # Position
    x = (width - target_width) // 2
    y = int(height * 0.35)

    # Composite
    final = background.copy()
    final.paste(glow, (x - 50, y - 50), glow)
    final.paste(screenshot, (x, y), screenshot)

    # Add text
    draw = ImageDraw.Draw(final)
    headline_font = load_font(int(width * 0.065), bold=True)
    subtitle_font = load_font(int(width * 0.04))

    # Headline
    bbox = draw.textbbox((0, 0), headline, font=headline_font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((text_x, int(height * 0.08)), headline, fill=(255, 255, 255), font=headline_font)

    # Subtitle
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((text_x, int(height * 0.16)), subtitle, fill=(255, 255, 255, 200), font=subtitle_font)

    final.convert('RGB').save(output_path, quality=95)
    print(f"  Saved: {output_path}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    gradients_dir = os.path.join(base_dir, "gradients")
    output_dir = os.path.join(base_dir, "output", "04_ai_backgrounds")

    # Find AI backgrounds
    ai_backgrounds = sorted([f for f in os.listdir(gradients_dir)
                            if f.startswith('ai_') and f.endswith(('.png', '.jpg'))]
                           ) if os.path.exists(gradients_dir) else []

    raw_files = sorted([f for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    print(f"\n{'='*60}")
    print("APPROACH #4: AI-Generated Backgrounds")
    print(f"{'='*60}\n")

    if not ai_backgrounds:
        print("!"*60)
        print("NO AI BACKGROUNDS FOUND!")
        print("!"*60)
        print(f"\nTo use this approach:")
        print(f"1. Generate backgrounds in Midjourney/DALL-E")
        print(f"2. Save them to: {gradients_dir}/")
        print(f"3. Name them: ai_1.png, ai_2.png, etc.")
        print(f"\nSee prompts at the top of this script.")
        print(f"\nUsing fallback gradients instead...\n")

    for i in range(min(4, max(len(raw_files), 1))):
        headline, subtitle = HEADLINES[i]
        print(f"Screenshot {i+1}: {headline}")

        bg_path = os.path.join(gradients_dir, ai_backgrounds[i % len(ai_backgrounds)]) if ai_backgrounds else ""
        raw_path = os.path.join(raw_dir, raw_files[i % len(raw_files)]) if raw_files else ""
        output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")

        create_screenshot(bg_path, raw_path, headline, subtitle, output_path)

    print(f"\nDone! Screenshots saved to: {output_dir}")


if __name__ == "__main__":
    main()
