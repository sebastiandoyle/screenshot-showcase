#!/usr/bin/env python3
"""
3D Parallax Screenshot Generator
=================================
Creates a premium app store screenshot with:
- 3D perspective phone mockup
- Floating UI elements at different depths
- Parallax-style layered composition
- Decorative symbols, badges, and stats
- Glow effects and shadows for depth
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

IPHONE_SIZE = (1290, 2796)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def load_font(size, bold=False):
    paths = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


def create_gradient_background(width, height, colors, angle=135):
    """Create angled gradient background."""
    img = Image.new('RGB', (width, height))

    c1 = hex_to_rgb(colors[0])
    c2 = hex_to_rgb(colors[1])
    c3 = hex_to_rgb(colors[2]) if len(colors) > 2 else c2

    for y in range(height):
        for x in range(width):
            # Diagonal gradient
            t = (x / width * 0.3 + y / height * 0.7)

            if t < 0.5:
                ratio = t * 2
                r = int(c1[0] + (c2[0] - c1[0]) * ratio)
                g = int(c1[1] + (c2[1] - c1[1]) * ratio)
                b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            else:
                ratio = (t - 0.5) * 2
                r = int(c2[0] + (c3[0] - c2[0]) * ratio)
                g = int(c2[1] + (c3[1] - c2[1]) * ratio)
                b = int(c2[2] + (c3[2] - c2[2]) * ratio)

            img.putpixel((x, y), (r, g, b))

    return img


def create_3d_phone_frame(screenshot, rotation_y=15, rotation_x=5):
    """
    Create a 3D perspective phone mockup.
    Uses perspective transform to simulate 3D rotation.
    """
    # Phone dimensions (iPhone 15 Pro style)
    phone_padding = 20
    corner_radius = 60
    bezel_color = (20, 20, 25)

    # Add bezel/frame around screenshot
    phone_width = screenshot.width + phone_padding * 2
    phone_height = screenshot.height + phone_padding * 2

    phone = Image.new('RGBA', (phone_width, phone_height), (0, 0, 0, 0))
    phone_draw = ImageDraw.Draw(phone)

    # Draw phone body (dark frame)
    phone_draw.rounded_rectangle(
        [(0, 0), (phone_width, phone_height)],
        radius=corner_radius,
        fill=bezel_color
    )

    # Draw screen area
    screen_radius = corner_radius - 10
    phone_draw.rounded_rectangle(
        [(phone_padding, phone_padding),
         (phone_width - phone_padding, phone_height - phone_padding)],
        radius=screen_radius,
        fill=(0, 0, 0)
    )

    # Paste screenshot
    # Create rounded mask for screenshot
    mask = Image.new('L', screenshot.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), screenshot.size],
        radius=screen_radius,
        fill=255
    )

    phone.paste(screenshot, (phone_padding, phone_padding), mask)

    # Add notch (Dynamic Island style)
    notch_width = 180
    notch_height = 50
    notch_x = (phone_width - notch_width) // 2
    notch_y = phone_padding + 15
    phone_draw.rounded_rectangle(
        [(notch_x, notch_y), (notch_x + notch_width, notch_y + notch_height)],
        radius=25,
        fill=(0, 0, 0)
    )

    # Add side button highlights
    phone_draw.rounded_rectangle(
        [(phone_width - 4, 200), (phone_width, 350)],
        radius=2,
        fill=(40, 40, 45)
    )

    # 3D PERSPECTIVE TRANSFORM
    # Calculate perspective coefficients
    width, height = phone.size

    # Perspective skew amounts
    skew_x = int(width * 0.08 * (rotation_y / 15))
    skew_y = int(height * 0.02 * (rotation_x / 5))

    # Define the transformation
    # Original corners: top-left, top-right, bottom-right, bottom-left
    # Transform to create 3D effect
    coeffs = find_perspective_coeffs(
        [(skew_x, skew_y), (width - skew_x//2, 0),
         (width, height - skew_y), (0, height - skew_y//2)],
        [(0, 0), (width, 0), (width, height), (0, height)]
    )

    phone_3d = phone.transform(
        (width, height),
        Image.PERSPECTIVE,
        coeffs,
        Image.BICUBIC
    )

    return phone_3d


def find_perspective_coeffs(source_coords, target_coords):
    """Calculate perspective transform coefficients."""
    import numpy as np

    matrix = []
    for s, t in zip(source_coords, target_coords):
        matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
        matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])

    A = np.matrix(matrix, dtype=np.float64)
    B = np.array(s for s, t in zip(source_coords, target_coords) for s in s).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)


def create_3d_phone_simple(screenshot, tilt=12):
    """
    Simpler 3D effect using shearing and scaling.
    Works without numpy.
    """
    phone_padding = 25
    corner_radius = 55

    # Create phone frame
    phone_width = screenshot.width + phone_padding * 2
    phone_height = screenshot.height + phone_padding * 2

    phone = Image.new('RGBA', (phone_width, phone_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(phone)

    # Phone body
    draw.rounded_rectangle(
        [(0, 0), (phone_width, phone_height)],
        radius=corner_radius,
        fill=(25, 25, 30)
    )

    # Subtle edge highlight (3D effect)
    draw.rounded_rectangle(
        [(2, 2), (phone_width - 2, phone_height - 2)],
        radius=corner_radius - 2,
        outline=(60, 60, 70),
        width=2
    )

    # Screen
    screen_mask = Image.new('L', screenshot.size, 0)
    mask_draw = ImageDraw.Draw(screen_mask)
    mask_draw.rounded_rectangle(
        [(0, 0), screenshot.size],
        radius=corner_radius - 15,
        fill=255
    )
    phone.paste(screenshot, (phone_padding, phone_padding), screen_mask)

    # Dynamic Island
    island_w, island_h = 160, 45
    island_x = (phone_width - island_w) // 2
    draw.rounded_rectangle(
        [(island_x, phone_padding + 20),
         (island_x + island_w, phone_padding + 20 + island_h)],
        radius=22,
        fill=(0, 0, 0)
    )

    # Apply 3D transform using affine shear
    # This creates a subtle tilt effect
    shear_amount = tilt / 100

    # Create larger canvas for transform
    canvas_w = int(phone_width * 1.3)
    canvas_h = int(phone_height * 1.1)

    transformed = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))

    # Apply shear transform
    phone_sheared = phone.transform(
        phone.size,
        Image.AFFINE,
        (1, shear_amount, 0, -shear_amount * 0.3, 1, 0),
        Image.BICUBIC
    )

    # Scale slightly for depth
    scale = 0.95
    new_size = (int(phone_sheared.width * scale), int(phone_sheared.height * scale))
    phone_scaled = phone_sheared.resize(new_size, Image.LANCZOS)

    return phone_scaled


def create_floating_card(width, height, color, opacity=200, blur=0):
    """Create a floating glassmorphism card."""
    card = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Semi-transparent fill
    fill_color = (*hex_to_rgb(color), opacity)
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=25,
        fill=fill_color
    )

    # Subtle border
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=25,
        outline=(*hex_to_rgb(color)[:3], min(255, opacity + 50)),
        width=2
    )

    if blur > 0:
        card = card.filter(ImageFilter.GaussianBlur(blur))

    return card


def create_floating_badge(text, icon=None, bg_color="#FFFFFF", text_color="#000000"):
    """Create a floating badge/pill."""
    font = load_font(38, bold=True)

    # Measure text
    dummy = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Badge size
    padding_x = 35
    padding_y = 20
    badge_width = text_width + padding_x * 2
    badge_height = text_height + padding_y * 2

    if icon:
        badge_width += 50  # Space for icon

    badge = Image.new('RGBA', (badge_width, badge_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    # Background
    draw.rounded_rectangle(
        [(0, 0), (badge_width, badge_height)],
        radius=badge_height // 2,
        fill=(*hex_to_rgb(bg_color), 240)
    )

    # Text
    text_x = padding_x + (30 if icon else 0)
    text_y = padding_y - 5
    draw.text((text_x, text_y), text, fill=hex_to_rgb(text_color), font=font)

    # Icon placeholder (emoji or symbol)
    if icon:
        icon_font = load_font(35)
        draw.text((padding_x - 5, text_y), icon, fill=hex_to_rgb(text_color), font=icon_font)

    return badge


def create_stat_card(value, label, color="#FFFFFF"):
    """Create a floating stat card."""
    width, height = 180, 120

    card = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # Glassmorphism background
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=20,
        fill=(255, 255, 255, 30)
    )
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=20,
        outline=(255, 255, 255, 80),
        width=1
    )

    # Value (big)
    value_font = load_font(48, bold=True)
    draw.text((width // 2, 35), value, fill=(255, 255, 255), font=value_font, anchor="mm")

    # Label (small)
    label_font = load_font(24)
    draw.text((width // 2, 80), label, fill=(255, 255, 255, 200), font=label_font, anchor="mm")

    return card


def create_icon_circle(icon_char, size=80, bg_color="#FFFFFF", icon_color="#000000"):
    """Create a circular icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Circle background
    draw.ellipse([(0, 0), (size, size)], fill=(*hex_to_rgb(bg_color), 230))

    # Icon/emoji
    font = load_font(int(size * 0.5))
    draw.text((size // 2, size // 2), icon_char, fill=hex_to_rgb(icon_color), font=font, anchor="mm")

    return img


def create_glow(size, color, intensity=0.5):
    """Create a glow effect."""
    glow = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)

    cx, cy = size[0] // 2, size[1] // 2
    max_radius = min(size) // 2

    for r in range(max_radius, 0, -5):
        alpha = int(255 * intensity * (r / max_radius) ** 2)
        draw.ellipse(
            [(cx - r, cy - r), (cx + r, cy + r)],
            fill=(*hex_to_rgb(color), alpha)
        )

    glow = glow.filter(ImageFilter.GaussianBlur(radius=30))
    return glow


def create_3d_parallax_screenshot(screenshot_path, output_path):
    """
    Create the ultimate 3D parallax screenshot.
    """
    width, height = IPHONE_SIZE

    # === LAYER 0: BACKGROUND ===
    print("  Creating gradient background...")
    colors = ["#1a1a2e", "#16213e", "#0f3460"]
    background = create_gradient_background(width, height, colors)
    final = background.convert('RGBA')

    # === LAYER 1: BACKGROUND GLOWS (furthest back) ===
    print("  Adding depth glows...")

    # Large ambient glow top-right
    glow1 = create_glow((600, 600), "#4361ee", intensity=0.3)
    final.paste(glow1, (width - 400, -100), glow1)

    # Large ambient glow bottom-left
    glow2 = create_glow((700, 700), "#7209b7", intensity=0.25)
    final.paste(glow2, (-200, height - 500), glow2)

    # Accent glow middle
    glow3 = create_glow((400, 400), "#4cc9f0", intensity=0.2)
    final.paste(glow3, (100, height // 2 - 200), glow3)

    # === LAYER 2: BACK FLOATING ELEMENTS ===
    print("  Adding background elements...")

    # Floating icons (back layer - smaller, more transparent)
    icons_back = [
        ("", 60, (100, 400), "#4361ee"),
        ("", 55, (width - 150, 600), "#f72585"),
        ("", 50, (150, height - 600), "#4cc9f0"),
        ("", 45, (width - 120, height - 400), "#7209b7"),
    ]

    for icon, size, pos, color in icons_back:
        icon_img = create_icon_circle(icon, size, color)
        icon_img.putalpha(icon_img.getchannel('A').point(lambda x: int(x * 0.4)))
        # Add blur for depth
        icon_img = icon_img.filter(ImageFilter.GaussianBlur(radius=3))
        final.paste(icon_img, pos, icon_img)

    # === LAYER 3: THE 3D PHONE (main focus) ===
    print("  Creating 3D phone mockup...")

    if os.path.exists(screenshot_path):
        screenshot = Image.open(screenshot_path).convert('RGBA')
    else:
        screenshot = Image.new('RGBA', (390, 844), (30, 30, 40))

    # Scale screenshot for phone
    target_height = int(height * 0.55)
    scale = target_height / screenshot.height
    target_width = int(screenshot.width * scale)
    screenshot = screenshot.resize((target_width, target_height), Image.LANCZOS)

    # Create 3D phone
    phone = create_3d_phone_simple(screenshot, tilt=10)

    # Create phone shadow
    shadow = Image.new('RGBA', (phone.width + 100, phone.height + 100), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [(50, 60), (phone.width + 50, phone.height + 50)],
        radius=55,
        fill=(0, 0, 0, 100)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=40))

    # Position phone (slightly right of center for visual interest)
    phone_x = (width - phone.width) // 2 + 50
    phone_y = int(height * 0.28)

    # Paste shadow then phone
    final.paste(shadow, (phone_x - 50, phone_y - 30), shadow)
    final.paste(phone, (phone_x, phone_y), phone)

    # Phone glow effect
    phone_glow = create_glow((phone.width + 200, phone.height + 200), "#4cc9f0", intensity=0.15)
    final.paste(phone_glow, (phone_x - 100, phone_y - 100), phone_glow)

    # === LAYER 4: FLOATING UI CARDS (mid layer) ===
    print("  Adding floating UI elements...")

    # Stat card - top left (floating)
    stat1 = create_stat_card("47", "Day Streak")
    stat1_x, stat1_y = 60, int(height * 0.35)
    # Add shadow
    stat1_shadow = Image.new('RGBA', (stat1.width + 20, stat1.height + 20), (0, 0, 0, 0))
    stat1_shadow_draw = ImageDraw.Draw(stat1_shadow)
    stat1_shadow_draw.rounded_rectangle([(10, 15), (stat1.width + 10, stat1.height + 15)], radius=20, fill=(0, 0, 0, 60))
    stat1_shadow = stat1_shadow.filter(ImageFilter.GaussianBlur(radius=15))
    final.paste(stat1_shadow, (stat1_x - 10, stat1_y - 5), stat1_shadow)
    final.paste(stat1, (stat1_x, stat1_y), stat1)

    # Stat card - right side
    stat2 = create_stat_card("92%", "Consistency")
    stat2_x, stat2_y = width - 220, int(height * 0.55)
    stat2_shadow = Image.new('RGBA', (stat2.width + 20, stat2.height + 20), (0, 0, 0, 0))
    stat2_shadow_draw = ImageDraw.Draw(stat2_shadow)
    stat2_shadow_draw.rounded_rectangle([(10, 15), (stat2.width + 10, stat2.height + 15)], radius=20, fill=(0, 0, 0, 60))
    stat2_shadow = stat2_shadow.filter(ImageFilter.GaussianBlur(radius=15))
    final.paste(stat2_shadow, (stat2_x - 10, stat2_y - 5), stat2_shadow)
    final.paste(stat2, (stat2_x, stat2_y), stat2)

    # === LAYER 5: FLOATING BADGES (front layer) ===
    print("  Adding floating badges...")

    # Rating badge
    badge1 = create_floating_badge("4.9 Rating", "", "#FFFFFF", "#000000")
    badge1_x, badge1_y = 80, int(height * 0.18)
    final.paste(badge1, (badge1_x, badge1_y), badge1)

    # Users badge
    badge2 = create_floating_badge("50K+ Users", "", "#4cc9f0", "#FFFFFF")
    badge2_x, badge2_y = width - badge2.width - 80, int(height * 0.22)
    final.paste(badge2, (badge2_x, badge2_y), badge2)

    # Feature badge bottom
    badge3 = create_floating_badge("Free to Start", "", "#7209b7", "#FFFFFF")
    badge3_x = (width - badge3.width) // 2 - 100
    badge3_y = height - 350
    final.paste(badge3, (badge3_x, badge3_y), badge3)

    # === LAYER 6: FOREGROUND ICONS (closest) ===
    print("  Adding foreground elements...")

    icons_front = [
        ("", 75, (50, height - 500), "#f72585"),
        ("", 70, (width - 130, 350), "#4cc9f0"),
        ("", 65, (width - 100, height - 450), "#4361ee"),
    ]

    for icon, size, pos, color in icons_front:
        icon_img = create_icon_circle(icon, size, color)
        # Brighter, no blur (front layer)
        final.paste(icon_img, pos, icon_img)

    # === LAYER 7: HEADLINE TEXT ===
    print("  Adding headline...")
    draw = ImageDraw.Draw(final)

    headline = "Build Habits"
    subhead = "That Actually Stick"

    headline_font = load_font(110, bold=True)
    subhead_font = load_font(85, bold=True)

    # Headline with subtle shadow
    headline_y = int(height * 0.05)

    # Shadow
    draw.text((width // 2 + 3, headline_y + 3), headline,
              fill=(0, 0, 0, 100), font=headline_font, anchor="mt")
    # Main text
    draw.text((width // 2, headline_y), headline,
              fill=(255, 255, 255), font=headline_font, anchor="mt")

    # Subhead with gradient-ish color
    subhead_y = headline_y + 120
    draw.text((width // 2, subhead_y), subhead,
              fill=(76, 201, 240), font=subhead_font, anchor="mt")

    # === LAYER 8: BOTTOM CTA ===
    print("  Adding CTA...")

    cta_y = height - 200
    cta_font = load_font(55, bold=True)

    # CTA button
    cta_text = "Download Free"
    bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_width = bbox[2] - bbox[0] + 80
    cta_height = 100
    cta_x = (width - cta_width) // 2

    # Button glow
    btn_glow = create_glow((cta_width + 60, cta_height + 60), "#4cc9f0", intensity=0.4)
    final.paste(btn_glow, (cta_x - 30, cta_y - 30), btn_glow)

    # Button
    draw.rounded_rectangle(
        [(cta_x, cta_y), (cta_x + cta_width, cta_y + cta_height)],
        radius=50,
        fill=(255, 255, 255)
    )
    draw.text((width // 2, cta_y + cta_height // 2), cta_text,
              fill=(20, 20, 30), font=cta_font, anchor="mm")

    # === SAVE ===
    print("  Saving...")
    final.convert('RGB').save(output_path, quality=95)
    print(f"  DONE: {output_path}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "3d_parallax")

    os.makedirs(output_dir, exist_ok=True)

    raw_files = sorted([f for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    print("\n" + "="*60)
    print("3D PARALLAX SCREENSHOT GENERATOR")
    print("="*60 + "\n")

    if raw_files:
        screenshot_path = os.path.join(raw_dir, raw_files[0])
    else:
        screenshot_path = ""

    output_path = os.path.join(output_dir, "3d_parallax_screenshot.png")

    create_3d_parallax_screenshot(screenshot_path, output_path)

    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
