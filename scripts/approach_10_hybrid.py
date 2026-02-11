#!/usr/bin/env python3
"""
Approach #10: Hybrid Screenshot Engine
======================================
Config-driven system that combines all approaches into one powerful tool.

Styles:
- "premium": Mesh gradients with glow effects
- "authentic": Ugly ads style (iMessage, Notes, Twitter)
- "minimal": Clean solid backgrounds
- "storytelling": Connected narrative carousel
- "glassmorphism": Modern blur effects (requires Playwright)

Usage:
    python approach_10_hybrid.py [config.json]
    python approach_10_hybrid.py --demo  # Uses built-in demo config

Output: ../output/10_hybrid_engine/
"""

import os
import sys
import json
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

IPHONE_SIZE = (1290, 2796)
IPAD_SIZE = (2048, 2732)
CORNER_RADIUS = 55


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def load_font(size, bold=False):
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
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    output = Image.new('RGBA', img.size, (0, 0, 0, 0))
    output.paste(img, mask=mask)
    return output


def create_shadow(img, blur=25, opacity=80, offset=(0, 15)):
    shadow = Image.new('RGBA',
                      (img.width + 80, img.height + 80),
                      (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [(40 + offset[0], 40 + offset[1]),
         (img.width + 40 + offset[0], img.height + 40 + offset[1])],
        radius=CORNER_RADIUS,
        fill=(0, 0, 0, opacity)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    return shadow


def get_text_color(bg_color):
    """Auto-contrast: dark text on light, white on dark."""
    r, g, b = bg_color[:3]
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return (255, 255, 255) if luminance < 0.5 else (30, 30, 30)


def fit_text(draw, text, font_size, max_width, bold=False):
    """Find font size that fits text within max_width."""
    while font_size > 20:
        font = load_font(font_size, bold)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        font_size -= 5
    return load_font(20, bold)


# ============================================================
# BACKGROUND GENERATORS
# ============================================================

def create_gradient_background(width, height, colors):
    """Create a smooth gradient background."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    c1 = hex_to_rgb(colors[0])
    c2 = hex_to_rgb(colors[1])

    for y in range(height):
        ratio = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return img


def create_mesh_background(width, height, colors, seed=42):
    """Create a mesh-style gradient with blended orbs."""
    import random
    random.seed(seed)

    img = create_gradient_background(width, height, colors[:2])
    img = img.convert('RGBA')

    # Add gradient orbs
    for _ in range(4):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        radius = random.randint(400, 800)
        color = hex_to_rgb(random.choice(colors))

        orb = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        orb_draw = ImageDraw.Draw(orb)

        for r in range(radius, 0, -10):
            alpha = int(40 * (r / radius))
            orb_draw.ellipse(
                [(cx - r, cy - r), (cx + r, cy + r)],
                fill=(*color, alpha)
            )

        orb = orb.filter(ImageFilter.GaussianBlur(radius=60))
        img = Image.alpha_composite(img, orb)

    return img.convert('RGB')


def create_solid_background(width, height, color):
    """Create a solid color background."""
    return Image.new('RGB', (width, height), hex_to_rgb(color))


# ============================================================
# STYLE-SPECIFIC GENERATORS
# ============================================================

class ScreenshotEngine:
    """Main engine for generating app store screenshots."""

    def __init__(self, config):
        self.config = config
        self.style = config.get('style', 'premium')
        self.app_name = config.get('app_name', 'App')
        self.colors = config.get('color_scheme', ['#667eea', '#764ba2'])

    def generate_all(self, raw_dir, output_dir):
        """Generate all screenshots based on config."""
        screenshots = self.config.get('screenshots', [])

        for i, shot in enumerate(screenshots):
            print(f"  [{i+1}/{len(screenshots)}] {shot.get('headline', 'Screenshot')}")

            raw_path = os.path.join(raw_dir, shot.get('image', ''))
            output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")

            if self.style == 'premium':
                self._generate_premium(raw_path, shot, output_path, i)
            elif self.style == 'authentic':
                self._generate_authentic(raw_path, shot, output_path, i)
            elif self.style == 'minimal':
                self._generate_minimal(raw_path, shot, output_path, i)
            elif self.style == 'storytelling':
                self._generate_storytelling(raw_path, shot, output_path, i)
            else:
                self._generate_premium(raw_path, shot, output_path, i)

    def _load_screenshot(self, path, target_width_ratio=0.65):
        """Load and scale a screenshot."""
        width, height = IPHONE_SIZE

        if os.path.exists(path):
            img = Image.open(path).convert('RGBA')
        else:
            # Placeholder
            img = Image.new('RGBA', (390, 844), (40, 40, 40, 255))

        target_width = int(width * target_width_ratio)
        scale = target_width / img.width
        target_height = int(img.height * scale)
        img = img.resize((target_width, target_height), Image.LANCZOS)

        return add_rounded_corners(img, CORNER_RADIUS)

    def _generate_premium(self, raw_path, shot, output_path, index):
        """Premium style: mesh gradients, glow effects, shadows."""
        width, height = IPHONE_SIZE

        # Background
        bg = create_mesh_background(width, height, self.colors, seed=index * 17)
        final = bg.convert('RGBA')

        # Screenshot
        screenshot = self._load_screenshot(raw_path)

        # Create glow
        glow_color = self.colors[index % len(self.colors)]
        glow = Image.new('RGBA',
                        (screenshot.width + 120, screenshot.height + 120),
                        (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.rounded_rectangle(
            [(60, 60), (screenshot.width + 60, screenshot.height + 60)],
            radius=CORNER_RADIUS,
            fill=(*hex_to_rgb(glow_color), 50)
        )
        glow = glow.filter(ImageFilter.GaussianBlur(radius=40))

        # Shadow
        shadow = create_shadow(screenshot)

        # Position
        x = (width - screenshot.width) // 2
        y = int(height * 0.35)

        final.paste(glow, (x - 60, y - 60), glow)
        final.paste(shadow, (x - 40, y - 25), shadow)
        final.paste(screenshot, (x, y), screenshot)

        # Text
        draw = ImageDraw.Draw(final)
        headline = shot.get('headline', '')
        subtitle = shot.get('subtitle', '')

        text_color = (255, 255, 255)

        # Headline
        headline_font = fit_text(draw, headline, int(width * 0.07), width - 160, bold=True)
        bbox = draw.textbbox((0, 0), headline, font=headline_font)
        text_x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((text_x, int(height * 0.08)), headline, fill=text_color, font=headline_font)

        # Subtitle
        if subtitle:
            subtitle_font = load_font(int(width * 0.04))
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            text_x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((text_x, int(height * 0.16)), subtitle, fill=text_color, font=subtitle_font)

        final.convert('RGB').save(output_path, quality=95)

    def _generate_authentic(self, raw_path, shot, output_path, index):
        """Authentic style: iMessage, Notes, Twitter formats."""
        width, height = IPHONE_SIZE
        format_type = shot.get('format', ['imessage', 'notes', 'twitter', 'pov'][index % 4])

        if format_type == 'imessage':
            self._create_imessage(raw_path, shot, output_path)
        elif format_type == 'notes':
            self._create_notes(raw_path, shot, output_path)
        elif format_type == 'twitter':
            self._create_twitter(raw_path, shot, output_path)
        else:
            self._create_pov(raw_path, shot, output_path)

    def _create_imessage(self, raw_path, shot, output_path):
        """Create iMessage conversation."""
        width, height = IPHONE_SIZE
        img = Image.new('RGB', (width, height), (242, 242, 247))
        draw = ImageDraw.Draw(img)

        messages = shot.get('messages', [
            {"from": "friend", "text": "you need to try this app"},
            {"from": "me", "text": "which one"},
            {"from": "friend", "text": "the habit tracker, its actually good"},
        ])

        y = 300
        msg_font = load_font(48)

        for msg in messages:
            is_me = msg.get('from') == 'me'
            text = msg.get('text', '')

            # Bubble
            bbox = draw.textbbox((0, 0), text, font=msg_font)
            bubble_w = min(bbox[2] - bbox[0] + 50, int(width * 0.7))
            bubble_h = 80

            if is_me:
                x = width - 60 - bubble_w
                color = (0, 122, 255)
                text_color = (255, 255, 255)
            else:
                x = 60
                color = (229, 229, 234)
                text_color = (28, 28, 30)

            draw.rounded_rectangle([(x, y), (x + bubble_w, y + bubble_h)],
                                  radius=30, fill=color)
            draw.text((x + 25, y + 18), text, fill=text_color, font=msg_font)
            y += bubble_h + 15

        # Add screenshot
        if os.path.exists(raw_path):
            screenshot = self._load_screenshot(raw_path, 0.5)
            x = 60
            y += 20
            img.paste(screenshot.convert('RGB'), (x, y))

        img.save(output_path, quality=95)

    def _create_notes(self, raw_path, shot, output_path):
        """Create Notes app style."""
        width, height = IPHONE_SIZE
        img = Image.new('RGB', (width, height), (255, 252, 225))
        draw = ImageDraw.Draw(img)

        # Lines
        for y in range(200, height, 70):
            draw.line([(60, y), (width - 60, y)], fill=(200, 200, 180), width=1)

        # Content
        title_font = load_font(65, bold=True)
        body_font = load_font(48)

        draw.text((80, 100), shot.get('headline', 'Notes'), fill=(28, 28, 30), font=title_font)

        y = 280
        for line in shot.get('note_text', 'Check out this app!').split('\n'):
            draw.text((80, y), line, fill=(28, 28, 30), font=body_font)
            y += 70

        img.save(output_path, quality=95)

    def _create_twitter(self, raw_path, shot, output_path):
        """Create Twitter/X style."""
        width, height = IPHONE_SIZE
        img = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        name_font = load_font(50, bold=True)
        handle_font = load_font(45)
        body_font = load_font(52)

        draw.ellipse([(80, 280), (180, 380)], fill=(50, 50, 50))
        draw.text((200, 285), shot.get('username', 'user'), fill=(231, 233, 234), font=name_font)
        draw.text((200, 340), shot.get('handle', '@user'), fill=(142, 142, 147), font=handle_font)

        y = 450
        for line in shot.get('tweet', 'This app changed my life').split('\n'):
            draw.text((80, y), line, fill=(231, 233, 234), font=body_font)
            y += 65

        img.save(output_path, quality=95)

    def _create_pov(self, raw_path, shot, output_path):
        """Create TikTok POV style."""
        width, height = IPHONE_SIZE

        if os.path.exists(raw_path):
            bg = Image.open(raw_path).convert('RGB').resize((width, height), Image.LANCZOS)
            enhancer = ImageEnhance.Brightness(bg)
            bg = enhancer.enhance(0.4)
        else:
            bg = Image.new('RGB', (width, height), (20, 20, 20))

        img = bg.convert('RGBA')
        draw = ImageDraw.Draw(img)

        headline_font = load_font(75, bold=True)
        pov_font = load_font(55)

        draw.text((width // 2, 250), "POV:", fill=(255, 255, 255), font=pov_font, anchor="mm")
        draw.text((width // 2, 350), shot.get('headline', 'You found it'),
                 fill=(255, 255, 255), font=headline_font, anchor="mm")

        img.convert('RGB').save(output_path, quality=95)

    def _generate_minimal(self, raw_path, shot, output_path, index):
        """Minimal style: clean solid backgrounds."""
        width, height = IPHONE_SIZE

        bg_color = self.colors[index % len(self.colors)]
        bg = create_solid_background(width, height, bg_color)
        final = bg.convert('RGBA')

        # Screenshot
        screenshot = self._load_screenshot(raw_path, 0.7)
        shadow = create_shadow(screenshot, blur=20, opacity=60)

        x = (width - screenshot.width) // 2
        y = int(height * 0.32)

        final.paste(shadow, (x - 40, y - 25), shadow)
        final.paste(screenshot, (x, y), screenshot)

        # Text
        draw = ImageDraw.Draw(final)
        text_color = get_text_color(hex_to_rgb(bg_color))

        headline = shot.get('headline', '')
        headline_font = load_font(int(width * 0.07), bold=True)
        bbox = draw.textbbox((0, 0), headline, font=headline_font)
        text_x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((text_x, int(height * 0.1)), headline, fill=text_color, font=headline_font)

        final.convert('RGB').save(output_path, quality=95)

    def _generate_storytelling(self, raw_path, shot, output_path, index):
        """Storytelling style: evolving colors, progress indicators."""
        width, height = IPHONE_SIZE

        # Evolving color palette
        story_colors = [
            ['#2D1B4E', '#1A1A2E'],
            ['#1A1A2E', '#16213E'],
            ['#16213E', '#0F3460'],
            ['#0F3460', '#1A4B1A'],
            ['#1A4B1A', '#2D2D0D'],
        ]

        colors = story_colors[index % len(story_colors)]
        bg = create_gradient_background(width, height, colors)
        final = bg.convert('RGBA')
        draw = ImageDraw.Draw(final)

        # Progress bar
        total = len(self.config.get('screenshots', []))
        bar_y = 120
        bar_width = width - 160
        segment = bar_width / total

        for i in range(total):
            x1 = 80 + i * segment + 5
            x2 = 80 + (i + 1) * segment - 5
            color = (255, 200, 100) if i <= index else (60, 60, 60)
            draw.rounded_rectangle([(x1, bar_y), (x2, bar_y + 8)], radius=4, fill=color)

        # Screenshot
        screenshot = self._load_screenshot(raw_path, 0.65)
        x = (width - screenshot.width) // 2
        y = int(height * 0.35)
        final.paste(screenshot, (x, y), screenshot)

        # Text
        headline = shot.get('headline', '')
        headline_font = load_font(int(width * 0.065), bold=True)
        bbox = draw.textbbox((0, 0), headline, font=headline_font)
        text_x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((text_x, int(height * 0.16)), headline, fill=(255, 255, 255), font=headline_font)

        # Step indicator
        step_font = load_font(55, bold=True)
        step_x = width - 100
        step_y = height - 150
        draw.ellipse([(step_x - 50, step_y - 50), (step_x + 50, step_y + 50)],
                    fill=(255, 200, 100))
        draw.text((step_x, step_y), str(index + 1), fill=(0, 0, 0), font=step_font, anchor="mm")

        final.convert('RGB').save(output_path, quality=95)


# ============================================================
# DEMO CONFIG
# ============================================================

DEMO_CONFIG = {
    "app_name": "HabitFlow",
    "style": "premium",
    "color_scheme": ["#667eea", "#764ba2", "#f093fb"],
    "screenshots": [
        {"image": "1.png", "headline": "Build Habits That Stick", "subtitle": "One day at a time"},
        {"image": "2.png", "headline": "Track Your Progress", "subtitle": "Watch your streaks grow"},
        {"image": "3.png", "headline": "Celebrate Every Win", "subtitle": "Small wins matter"},
        {"image": "4.png", "headline": "Stay Motivated", "subtitle": "Join 50,000+ users"},
    ]
}


def main():
    """Run the hybrid screenshot engine."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "10_hybrid_engine")

    # Load config
    if len(sys.argv) > 1 and sys.argv[1] != '--demo':
        config_path = sys.argv[1]
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = DEMO_CONFIG

    # Map raw files to config
    raw_files = sorted([f for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    for i, shot in enumerate(config['screenshots']):
        if raw_files and 'image' in shot:
            shot['image'] = raw_files[i % len(raw_files)]

    print(f"\n{'='*60}")
    print(f"APPROACH #10: Hybrid Screenshot Engine")
    print(f"Style: {config.get('style', 'premium').upper()}")
    print(f"{'='*60}\n")

    engine = ScreenshotEngine(config)
    engine.generate_all(raw_dir, output_dir)

    print(f"\nDone! Screenshots saved to: {output_dir}")

    # Generate all styles for comparison
    print("\n" + "="*60)
    print("BONUS: Generating all styles for comparison...")
    print("="*60 + "\n")

    for style in ['premium', 'minimal', 'storytelling', 'authentic']:
        style_config = config.copy()
        style_config['style'] = style
        style_output = os.path.join(base_dir, "output", "10_hybrid_engine", f"style_{style}")
        os.makedirs(style_output, exist_ok=True)

        print(f"Style: {style}")
        engine = ScreenshotEngine(style_config)
        engine.generate_all(raw_dir, style_output)
        print()


if __name__ == "__main__":
    main()
