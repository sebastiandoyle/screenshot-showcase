#!/usr/bin/env python3
"""
Approach #5: "Ugly Ads" / Raw Authentic Style
=============================================
Creates intentionally unpolished screenshots that look like real user content.
Based on psychology research showing 20-35% higher conversion rates.

Formats:
- iMessage conversation recommending the app
- Notes app with handwritten-style review
- Twitter/X post praising the app
- "POV: you just discovered..." TikTok style

Usage:
    python approach_05_ugly_ads.py

Output: ../output/05_ugly_ads/
"""

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import textwrap

# Configuration
IPHONE_SIZE = (1290, 2796)

# iOS System Colors
IOS_GRAY_BG = (242, 242, 247)       # System background
IOS_BLUE = (0, 122, 255)            # iMessage blue
IOS_GREEN = (52, 199, 89)           # Green bubble
IOS_DARK = (28, 28, 30)             # Dark text
IOS_SECONDARY = (142, 142, 147)     # Secondary text
IOS_WHITE = (255, 255, 255)
NOTES_YELLOW = (255, 252, 225)      # Notes app yellow
TWITTER_BG = (0, 0, 0)              # Twitter dark mode
TWITTER_WHITE = (231, 233, 234)


def load_font(size, weight="regular"):
    """Load SF Pro font with fallback."""
    font_paths = {
        "regular": [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/SFNSText.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ],
        "bold": [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/SFNSDisplay.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ]
    }

    for path in font_paths.get(weight, font_paths["regular"]):
        try:
            return ImageFont.truetype(path, size)
        except:
            continue

    return ImageFont.load_default()


def draw_rounded_rect(draw, coords, radius, fill):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = coords
    draw.rounded_rectangle(coords, radius=radius, fill=fill)


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def create_imessage_screenshot(
    app_screenshot_path,
    output_path,
    messages=None
):
    """
    Create an iMessage conversation screenshot where someone
    recommends the app to a friend.
    """
    width, height = IPHONE_SIZE
    img = Image.new('RGB', (width, height), IOS_GRAY_BG)
    draw = ImageDraw.Draw(img)

    # Default messages
    if messages is None:
        messages = [
            {"sender": "friend", "text": "yo have you tried that habit app yet?"},
            {"sender": "me", "text": "which one"},
            {"sender": "friend", "text": "the one I sent you last week, it actually works"},
            {"sender": "me", "text": "oh that one, downloading now"},
            {"sender": "friend", "image": True},  # The app screenshot
            {"sender": "friend", "text": "this is my streak rn"},
            {"sender": "me", "text": "wait thats actually sick"},
            {"sender": "me", "text": "ok im sold"},
        ]

    # Draw iMessage header
    header_font = load_font(50, "bold")
    time_font = load_font(40)

    # Status bar
    draw.text((60, 50), "9:41", fill=IOS_DARK, font=time_font)

    # Contact name
    contact_y = 150
    draw.text((width // 2, contact_y), "bestie", fill=IOS_DARK,
              font=header_font, anchor="mm")

    # Messages
    y = 280
    bubble_margin = 60
    max_bubble_width = int(width * 0.7)
    message_font = load_font(48)

    for msg in messages:
        is_me = msg["sender"] == "me"

        if msg.get("image"):
            # Load and display app screenshot
            if os.path.exists(app_screenshot_path):
                app_img = Image.open(app_screenshot_path).convert('RGBA')
                # Scale to fit in bubble
                img_width = int(width * 0.55)
                scale = img_width / app_img.width
                img_height = int(app_img.height * scale)
                app_img = app_img.resize((img_width, img_height), Image.LANCZOS)

                # Position
                if is_me:
                    x = width - bubble_margin - img_width
                else:
                    x = bubble_margin

                # Add rounded corners to image
                mask = Image.new('L', (img_width, img_height), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle([(0, 0), (img_width, img_height)],
                                           radius=30, fill=255)

                # Paste with mask
                img.paste(app_img, (x, y), mask)
                y += img_height + 25
        else:
            text = msg["text"]
            lines = wrap_text(text, message_font, max_bubble_width - 50, draw)

            # Calculate bubble size
            line_height = 55
            bubble_height = len(lines) * line_height + 40
            bubble_width = max(
                draw.textbbox((0, 0), line, font=message_font)[2]
                for line in lines
            ) + 50

            # Position bubble
            if is_me:
                bubble_x = width - bubble_margin - bubble_width
                bubble_color = IOS_BLUE
                text_color = IOS_WHITE
            else:
                bubble_x = bubble_margin
                bubble_color = (229, 229, 234)  # Light gray
                text_color = IOS_DARK

            # Draw bubble
            draw_rounded_rect(
                draw,
                (bubble_x, y, bubble_x + bubble_width, y + bubble_height),
                radius=30,
                fill=bubble_color
            )

            # Draw text
            text_y = y + 20
            for line in lines:
                draw.text((bubble_x + 25, text_y), line,
                         fill=text_color, font=message_font)
                text_y += line_height

            y += bubble_height + 15

    # iMessage input bar at bottom
    input_y = height - 180
    draw_rounded_rect(
        draw,
        (bubble_margin, input_y, width - bubble_margin, input_y + 100),
        radius=50,
        fill=(229, 229, 234)
    )
    input_font = load_font(44)
    draw.text((bubble_margin + 40, input_y + 28), "iMessage",
              fill=IOS_SECONDARY, font=input_font)

    img.save(output_path, quality=95)
    print(f"  Saved: {output_path}")


def create_notes_screenshot(
    app_screenshot_path,
    output_path,
    note_text=None
):
    """
    Create a Notes app screenshot with a personal review.
    """
    width, height = IPHONE_SIZE
    img = Image.new('RGB', (width, height), NOTES_YELLOW)
    draw = ImageDraw.Draw(img)

    # Default note
    if note_text is None:
        note_text = """apps that actually changed my life fr:

1. that habit tracker everyone keeps talking about
   - finally sticking to my routine
   - the streaks are addicting ngl
   - been 47 days straight

2. [screenshot attached]

update: my therapist noticed the difference lol

highly recommend if ur bad at consistency like me"""

    # Draw notes lines (subtle)
    line_color = (200, 200, 180)
    line_spacing = 70
    for y in range(200, height, line_spacing):
        draw.line([(60, y), (width - 60, y)], fill=line_color, width=1)

    # Title area
    title_font = load_font(65, "bold")
    draw.text((80, 100), "life-changing apps", fill=IOS_DARK, font=title_font)

    # Date
    date_font = load_font(40)
    date_str = datetime.now().strftime("%B %d, %Y")
    draw.text((80, 180), date_str, fill=IOS_SECONDARY, font=date_font)

    # Note content
    body_font = load_font(48)
    y = 280

    for line in note_text.split('\n'):
        # Check for screenshot placeholder
        if '[screenshot' in line.lower():
            if os.path.exists(app_screenshot_path):
                app_img = Image.open(app_screenshot_path).convert('RGBA')
                # Scale
                img_width = int(width * 0.6)
                scale = img_width / app_img.width
                img_height = int(app_img.height * scale)
                app_img = app_img.resize((img_width, img_height), Image.LANCZOS)

                # Add slight rotation for "casual" feel
                app_img = app_img.rotate(-2, expand=True, fillcolor=(0, 0, 0, 0))

                x = (width - img_width) // 2
                img.paste(app_img, (x, y), app_img)
                y += img_height + 30
        else:
            draw.text((80, y), line, fill=IOS_DARK, font=body_font)
            y += 70

    img.save(output_path, quality=95)
    print(f"  Saved: {output_path}")


def create_twitter_screenshot(
    app_screenshot_path,
    output_path,
    tweet_text=None
):
    """
    Create a Twitter/X screenshot (dark mode) praising the app.
    """
    width, height = IPHONE_SIZE
    img = Image.new('RGB', (width, height), TWITTER_BG)
    draw = ImageDraw.Draw(img)

    # Default tweet
    if tweet_text is None:
        tweet_text = """okay I usually don't post about apps but this habit tracker has genuinely changed my life

been using it for 2 months and I've:
- worked out 47 days straight
- read every single day
- actually stuck to a sleep schedule

sometimes simple tools just work"""

    # Twitter header
    header_font = load_font(55, "bold")
    draw.text((80, 120), "X", fill=TWITTER_WHITE, font=header_font)

    # Profile section
    y = 280

    # Profile pic (gray circle placeholder)
    draw.ellipse([(80, y), (180, y + 100)], fill=(50, 50, 50))

    # Name and handle
    name_font = load_font(50, "bold")
    handle_font = load_font(45)
    draw.text((200, y + 5), "actual person", fill=TWITTER_WHITE, font=name_font)
    draw.text((200, y + 55), "@realperson", fill=IOS_SECONDARY, font=handle_font)

    # Tweet text
    y = 420
    body_font = load_font(52)
    max_width = width - 160

    lines = wrap_text(tweet_text, body_font, max_width, draw)
    for line in lines:
        draw.text((80, y), line, fill=TWITTER_WHITE, font=body_font)
        y += 65

    # App screenshot if exists
    y += 30
    if os.path.exists(app_screenshot_path):
        app_img = Image.open(app_screenshot_path).convert('RGBA')
        img_width = int(width * 0.85)
        scale = img_width / app_img.width
        img_height = int(app_img.height * scale)
        app_img = app_img.resize((img_width, img_height), Image.LANCZOS)

        # Rounded corners
        mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (img_width, img_height)],
                                   radius=30, fill=255)

        x = (width - img_width) // 2
        img.paste(app_img, (x, y), mask)
        y += img_height + 30

    # Engagement stats
    stats_y = min(y + 20, height - 400)
    stats_font = load_font(45)
    stats_color = IOS_SECONDARY

    draw.text((80, stats_y), "12:34 PM", fill=stats_color, font=stats_font)
    draw.text((300, stats_y), "Jan 15, 2026", fill=stats_color, font=stats_font)

    stats_y += 80
    draw.line([(80, stats_y), (width - 80, stats_y)], fill=(50, 50, 50), width=2)
    stats_y += 30

    # Retweets and likes
    bold_font = load_font(48, "bold")
    draw.text((80, stats_y), "2,847", fill=TWITTER_WHITE, font=bold_font)
    draw.text((230, stats_y), "Reposts", fill=stats_color, font=stats_font)
    draw.text((450, stats_y), "14.2K", fill=TWITTER_WHITE, font=bold_font)
    draw.text((600, stats_y), "Likes", fill=stats_color, font=stats_font)

    img.save(output_path, quality=95)
    print(f"  Saved: {output_path}")


def create_pov_tiktok_screenshot(
    app_screenshot_path,
    output_path
):
    """
    Create a TikTok-style "POV" screenshot.
    """
    width, height = IPHONE_SIZE
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load app screenshot as background (blurred/darkened)
    if os.path.exists(app_screenshot_path):
        bg = Image.open(app_screenshot_path).convert('RGB')
        bg = bg.resize((width, height), Image.LANCZOS)
        # Darken
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.4)
        img.paste(bg)
        draw = ImageDraw.Draw(img)

    # POV text at top
    pov_font = load_font(55)
    headline_font = load_font(75, "bold")

    y = 200
    draw.text((width // 2, y), "POV:", fill=IOS_WHITE, font=pov_font, anchor="mm")

    y += 100
    pov_text = "you finally found the app\nthat makes habits stick"

    for line in pov_text.split('\n'):
        draw.text((width // 2, y), line, fill=IOS_WHITE,
                 font=headline_font, anchor="mm")
        y += 90

    # App screenshot in center (smaller, floating)
    if os.path.exists(app_screenshot_path):
        app_img = Image.open(app_screenshot_path).convert('RGBA')
        img_width = int(width * 0.55)
        scale = img_width / app_img.width
        img_height = int(app_img.height * scale)
        app_img = app_img.resize((img_width, img_height), Image.LANCZOS)

        # Add glow effect
        glow = Image.new('RGBA', (img_width + 60, img_height + 60), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.rounded_rectangle(
            [(30, 30), (img_width + 30, img_height + 30)],
            radius=40,
            fill=(255, 255, 255, 50)
        )
        from PIL import ImageFilter
        glow = glow.filter(ImageFilter.GaussianBlur(radius=20))

        x = (width - img_width) // 2
        y_img = height // 2 - img_height // 4

        img.paste(glow, (x - 30, y_img - 30), glow)
        img.paste(app_img, (x, y_img), app_img)

    # TikTok-style side icons
    icon_x = width - 120
    icon_y = height - 800
    icon_font = load_font(40)

    icons = ["", "", "15.4K"]  # Heart, comment, share count
    for i, icon in enumerate(icons):
        draw.ellipse(
            [(icon_x - 35, icon_y + i * 150), (icon_x + 35, icon_y + i * 150 + 70)],
            fill=(50, 50, 50, 180)
        )

    # Caption at bottom
    caption_font = load_font(45)
    caption = "this one actually works trust"
    draw.text((80, height - 300), caption, fill=IOS_WHITE, font=caption_font)

    img.save(output_path, quality=95)
    print(f"  Saved: {output_path}")


def main():
    """Generate all Ugly Ads style screenshots."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "05_ugly_ads")

    # Get first screenshot
    raw_files = sorted([f for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])
    app_screenshot = os.path.join(raw_dir, raw_files[0]) if raw_files else ""

    print(f"\n{'='*60}")
    print("APPROACH #5: Ugly Ads / Raw Authentic Style")
    print(f"{'='*60}\n")

    print("Screenshot 1: iMessage conversation")
    create_imessage_screenshot(
        app_screenshot,
        os.path.join(output_dir, "1_6.5_inch.png")
    )

    print("\nScreenshot 2: Notes app review")
    create_notes_screenshot(
        app_screenshot,
        os.path.join(output_dir, "2_6.5_inch.png")
    )

    print("\nScreenshot 3: Twitter/X post")
    create_twitter_screenshot(
        app_screenshot,
        os.path.join(output_dir, "3_6.5_inch.png")
    )

    print("\nScreenshot 4: TikTok POV style")
    create_pov_tiktok_screenshot(
        app_screenshot,
        os.path.join(output_dir, "4_6.5_inch.png")
    )

    print(f"\nDone! Screenshots saved to: {output_dir}")


if __name__ == "__main__":
    main()
