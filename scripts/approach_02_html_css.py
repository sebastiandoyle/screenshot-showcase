#!/usr/bin/env python3
"""
Approach #2: HTML/CSS → Image (Playwright)
==========================================
Design screenshots as HTML/CSS templates, render to PNG with headless Chrome.
Supports glassmorphism, backdrop-blur, any modern CSS effect.

Requires: playwright
Install: pip install playwright && playwright install chromium

Usage:
    python approach_02_html_css.py

Output: ../output/02_html_css/
"""

import os
import base64
import asyncio

# Try to import playwright, provide helpful error if not installed
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with:")
    print("  pip install playwright && playwright install chromium")


IPHONE_SIZE = (1290, 2796)

# Headlines and config
SCREENSHOTS_CONFIG = [
    {
        "headline": "Build Habits That Stick",
        "subtitle": "Simple tracking, lasting results",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "glass_color": "rgba(255, 255, 255, 0.15)",
    },
    {
        "headline": "Track Your Progress",
        "subtitle": "Watch your streaks grow daily",
        "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "glass_color": "rgba(255, 255, 255, 0.12)",
    },
    {
        "headline": "Celebrate Every Win",
        "subtitle": "Small wins lead to big changes",
        "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "glass_color": "rgba(255, 255, 255, 0.18)",
    },
    {
        "headline": "Stay Motivated",
        "subtitle": "Join 50,000+ users building better habits",
        "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "glass_color": "rgba(255, 255, 255, 0.14)",
    },
]


def generate_html_template(config, screenshot_base64, width, height):
    """Generate an HTML template for a screenshot."""

    # If no screenshot, use placeholder
    if screenshot_base64:
        img_src = f"data:image/png;base64,{screenshot_base64}"
    else:
        img_src = ""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            width: {width}px;
            height: {height}px;
            background: {config['gradient']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: hidden;
            position: relative;
        }}

        /* Animated gradient orbs for depth */
        .orb {{
            position: absolute;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.6;
        }}

        .orb-1 {{
            width: 600px;
            height: 600px;
            background: rgba(255, 255, 255, 0.3);
            top: -200px;
            left: -100px;
        }}

        .orb-2 {{
            width: 500px;
            height: 500px;
            background: rgba(255, 255, 255, 0.2);
            bottom: 200px;
            right: -150px;
        }}

        .orb-3 {{
            width: 400px;
            height: 400px;
            background: rgba(0, 0, 0, 0.15);
            bottom: -100px;
            left: 100px;
        }}

        .content {{
            position: relative;
            z-index: 10;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 120px 80px;
        }}

        .headline {{
            font-size: 95px;
            font-weight: 800;
            color: white;
            text-align: center;
            text-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
            line-height: 1.1;
        }}

        .subtitle {{
            font-size: 48px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            margin-bottom: 80px;
        }}

        .phone-container {{
            position: relative;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        /* Glassmorphism card behind screenshot */
        .glass-card {{
            position: absolute;
            width: 90%;
            height: 80%;
            background: {config['glass_color']};
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 50px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow:
                0 25px 50px rgba(0, 0, 0, 0.15),
                inset 0 0 60px rgba(255, 255, 255, 0.05);
        }}

        .screenshot {{
            position: relative;
            max-width: 75%;
            max-height: 85%;
            border-radius: 45px;
            box-shadow:
                0 50px 100px rgba(0, 0, 0, 0.3),
                0 15px 35px rgba(0, 0, 0, 0.2);
            transform: perspective(1000px) rotateX(2deg);
        }}

        .screenshot img {{
            width: 100%;
            height: auto;
            border-radius: 45px;
            display: block;
        }}

        /* Placeholder if no image */
        .placeholder {{
            width: 700px;
            height: 1400px;
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255, 255, 255, 0.3);
            font-size: 40px;
        }}

        /* Floating badges */
        .badge {{
            position: absolute;
            background: rgba(255, 255, 255, 0.95);
            padding: 20px 35px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 36px;
            color: #333;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }}

        .badge-rating {{
            top: 30%;
            right: 5%;
        }}

        .badge-streak {{
            bottom: 25%;
            left: 5%;
        }}
    </style>
</head>
<body>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <div class="content">
        <h1 class="headline">{config['headline']}</h1>
        <p class="subtitle">{config['subtitle']}</p>

        <div class="phone-container">
            <div class="glass-card"></div>
            <div class="screenshot">
                {"<img src='" + img_src + "' />" if img_src else '<div class="placeholder">App Screenshot</div>'}
            </div>

            <div class="badge badge-rating">4.9</div>
            <div class="badge badge-streak">47 day streak</div>
        </div>
    </div>
</body>
</html>
"""
    return html


async def render_screenshot(html_content, output_path, width, height):
    """Render HTML to PNG using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})

        await page.set_content(html_content, wait_until="networkidle")

        # Wait for fonts to load
        await page.wait_for_timeout(500)

        await page.screenshot(path=output_path, type="png")
        await browser.close()

    print(f"  Saved: {output_path}")


def image_to_base64(image_path):
    """Convert an image file to base64 string."""
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def main_async():
    """Generate all HTML/CSS screenshots."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "02_html_css")

    raw_files = sorted([f for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    print(f"\n{'='*60}")
    print("APPROACH #2: HTML/CSS -> Image (Playwright)")
    print(f"{'='*60}\n")

    width, height = IPHONE_SIZE

    for i, config in enumerate(SCREENSHOTS_CONFIG):
        print(f"Screenshot {i+1}: {config['headline']}")

        # Get raw screenshot
        raw_path = os.path.join(raw_dir, raw_files[i % len(raw_files)]) if raw_files else ""
        screenshot_b64 = image_to_base64(raw_path)

        # Generate HTML
        html = generate_html_template(config, screenshot_b64, width, height)

        # Render
        output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")
        await render_screenshot(html, output_path, width, height)
        print()

    print(f"Done! Screenshots saved to: {output_dir}")


def main():
    """Entry point."""
    if not PLAYWRIGHT_AVAILABLE:
        print("\nCannot run without Playwright. Skipping...")
        return

    asyncio.run(main_async())


if __name__ == "__main__":
    main()
