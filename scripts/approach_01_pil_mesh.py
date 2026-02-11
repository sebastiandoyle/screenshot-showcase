#!/usr/bin/env python3
"""
Approach #1: PIL + Premium Mesh Gradients
=========================================
Creates beautiful app store screenshots using programmatic mesh-style gradients.
Gradient is generated procedurally - no external files needed.

Usage:
    python approach_01_pil_mesh.py

Output: ../output/01_pil_mesh/
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Configuration
IPHONE_SIZE = (1290, 2796)  # 6.7" display
IPAD_SIZE = (2048, 2732)    # 13" iPad
CORNER_RADIUS = 55
SHADOW_SIZE = 40
SHADOW_BLUR = 25

# Headlines for habit building game
HEADLINES = [
    ("Build Habits That Stick", "One day at a time"),
    ("Track Your Progress", "See your streaks grow"),
    ("Celebrate Every Win", "Small wins lead to big changes"),
    ("Stay Consistent", "Your future self will thank you"),
]

# Color palettes (warm, cool, energetic, calm)
PALETTES = [
    [("#FF6B6B", "#4ECDC4", "#45B7D1")],  # Coral to Teal
    [("#667eea", "#764ba2", "#f093fb")],  # Purple Dreams
    [("#11998e", "#38ef7d", "#56ab2f")],  # Fresh Green
    [("#FF416C", "#FF4B2B", "#f5af19")],  # Sunset Fire
    [("#4158D0", "#C850C0", "#FFCC70")],  # Rainbow Flow
]


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def interpolate_color(c1, c2, t):
    """Interpolate between two RGB colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def create_mesh_gradient(width, height, colors, seed=None):
    """
    Create a beautiful mesh gradient background.
    Uses multiple radial gradients blended together for that premium mesh look.
    """
    if seed:
        random.seed(seed)

    img = Image.new('RGB', (width, height), hex_to_rgb(colors[0]))

    # Create multiple gradient "blobs" and blend them
    num_blobs = 5

    for _ in range(num_blobs):
        # Random position for blob center
        cx = random.randint(0, width)
        cy = random.randint(0, height)

        # Random radius
        radius = random.randint(min(width, height) // 2, max(width, height))

        # Pick random color from palette
        color = hex_to_rgb(random.choice(colors))

        # Create blob layer
        blob = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        for y in range(height):
            for x in range(width):
                # Distance from center
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)

                if dist < radius:
                    # Smooth falloff
                    alpha = int(255 * (1 - (dist / radius) ** 1.5) * 0.6)
                    blob.putpixel((x, y), (*color, alpha))

        # Apply blur for smoothness
        blob = blob.filter(ImageFilter.GaussianBlur(radius=80))

        # Composite onto main image
        img = Image.alpha_composite(img.convert('RGBA'), blob).convert('RGB')

    return img


def create_fast_gradient(width, height, colors, variation=0):
    """
    Fast gradient generation using line-by-line drawing.
    Much faster than per-pixel mesh gradient.
    """
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    c1 = hex_to_rgb(colors[0])
    c2 = hex_to_rgb(colors[1])
    c3 = hex_to_rgb(colors[2]) if len(colors) > 2 else c2

    # Add variation to starting point
    offset = int(height * 0.1 * variation)

    for y in range(height):
        # Two-segment gradient
        if y < height // 2:
            ratio = (y + offset) / (height // 2)
            ratio = max(0, min(1, ratio))
            color = interpolate_color(c1, c2, ratio)
        else:
            ratio = (y - height // 2) / (height // 2)
            ratio = max(0, min(1, ratio))
            color = interpolate_color(c2, c3, ratio)

        draw.line([(0, y), (width, y)], fill=color)

    # Add subtle noise for texture
    return img


def add_rounded_corners(img, radius):
    """Add rounded corners to an image."""
    # Create mask
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)

    # Apply mask
    output = Image.new('RGBA', img.size, (0, 0, 0, 0))
    output.paste(img, mask=mask)
    return output


def create_shadow(size, blur_radius, opacity=100):
    """Create a drop shadow."""
    shadow = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)

    # Draw shadow shape
    margin = blur_radius * 2
    draw.rounded_rectangle(
        [(margin, margin), (size[0] - margin, size[1] - margin)],
        radius=CORNER_RADIUS,
        fill=(0, 0, 0, opacity)
    )

    # Blur it
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return shadow


def load_font(size, bold=False):
    """Load system font with fallback."""
    font_paths = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue

    return ImageFont.load_default()


def get_text_color(background_color):
    """Determine if text should be white or dark based on background."""
    r, g, b = background_color[:3]
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return (255, 255, 255) if luminance < 0.5 else (30, 30, 30)


def create_screenshot(
    raw_screenshot_path,
    headline,
    subtitle,
    output_path,
    palette_index=0,
    size=IPHONE_SIZE
):
    """
    Create a complete app store screenshot.
    """
    width, height = size
    colors = PALETTES[palette_index % len(PALETTES)][0]

    # 1. Create gradient background
    print(f"  Creating gradient background...")
    background = create_fast_gradient(width, height, colors, variation=palette_index * 0.3)

    # 2. Load and process screenshot
    print(f"  Processing screenshot...")
    if os.path.exists(raw_screenshot_path):
        screenshot = Image.open(raw_screenshot_path).convert('RGBA')
    else:
        # Create placeholder if no screenshot
        screenshot = Image.new('RGBA', (390, 844), (40, 40, 40, 255))
        draw = ImageDraw.Draw(screenshot)
        draw.text((195, 422), "App\nScreenshot", fill=(100, 100, 100), anchor="mm")

    # Scale screenshot to fit (60% of width)
    target_width = int(width * 0.65)
    scale = target_width / screenshot.width
    target_height = int(screenshot.height * scale)
    screenshot = screenshot.resize((target_width, target_height), Image.LANCZOS)

    # Add rounded corners to screenshot
    screenshot = add_rounded_corners(screenshot, CORNER_RADIUS)

    # 3. Create shadow
    shadow_size = (target_width + SHADOW_SIZE * 2, target_height + SHADOW_SIZE * 2)
    shadow = create_shadow(shadow_size, SHADOW_BLUR, opacity=80)

    # 4. Calculate positions
    # Screenshot positioned in lower 2/3 of image
    screenshot_x = (width - target_width) // 2
    screenshot_y = int(height * 0.35)

    shadow_x = screenshot_x - SHADOW_SIZE
    shadow_y = screenshot_y - SHADOW_SIZE + 15  # Slight offset down

    # 5. Composite everything
    final = background.convert('RGBA')

    # Add shadow
    final.paste(shadow, (shadow_x, shadow_y), shadow)

    # Add screenshot
    final.paste(screenshot, (screenshot_x, screenshot_y), screenshot)

    # 6. Add text
    draw = ImageDraw.Draw(final)

    # Sample background color for text contrast
    sample_y = int(height * 0.15)
    sample_color = background.getpixel((width // 2, sample_y))
    text_color = get_text_color(sample_color)

    # Headline
    headline_font = load_font(int(width * 0.065), bold=True)
    headline_y = int(height * 0.08)

    # Center text
    bbox = draw.textbbox((0, 0), headline, font=headline_font)
    text_width = bbox[2] - bbox[0]
    headline_x = (width - text_width) // 2

    draw.text((headline_x, headline_y), headline, fill=text_color, font=headline_font)

    # Subtitle
    if subtitle:
        subtitle_font = load_font(int(width * 0.04))
        subtitle_y = headline_y + int(width * 0.09)

        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        text_width = bbox[2] - bbox[0]
        subtitle_x = (width - text_width) // 2

        # Slightly transparent subtitle
        subtitle_color = (*text_color[:3], 200)
        draw.text((subtitle_x, subtitle_y), subtitle, fill=text_color, font=subtitle_font)

    # 7. Save
    final.convert('RGB').save(output_path, quality=95)
    print(f"  Saved: {output_path}")


def main():
    """Generate all screenshots for Approach #1."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "01_pil_mesh")

    # Get list of raw screenshots
    raw_files = sorted([f for f in os.listdir(raw_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])

    if not raw_files:
        print("No screenshots found in raw/ folder. Creating with placeholders...")
        raw_files = [None, None, None, None]

    print(f"\n{'='*60}")
    print("APPROACH #1: PIL + Mesh Gradients")
    print(f"{'='*60}\n")

    for i, raw_file in enumerate(raw_files[:4]):  # Max 4 screenshots
        headline, subtitle = HEADLINES[i % len(HEADLINES)]

        raw_path = os.path.join(raw_dir, raw_file) if raw_file else ""
        output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")

        print(f"Screenshot {i+1}: {headline}")
        create_screenshot(
            raw_path,
            headline,
            subtitle,
            output_path,
            palette_index=i
        )
        print()

    print(f"Done! Screenshots saved to: {output_dir}")


if __name__ == "__main__":
    main()
