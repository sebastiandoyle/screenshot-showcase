#!/usr/bin/env python3
"""
Approach #6: Screenshots Pro API
================================
Commercial API-based screenshot generation with built-in 3D device frames.

Website: https://screenshots.pro/

SETUP:
1. Sign up at screenshots.pro
2. Get your API key
3. Set environment variable: export SCREENSHOTS_PRO_API_KEY=your_key
4. Run this script

Features:
- 3D perspective device frames
- All App Store + Google Play sizes
- CI/CD integration
- Direct fastlane integration

Usage:
    python approach_06_api.py

Output: ./output/06_screenshots_pro/
"""

import os
import json
import base64
import urllib.request
import urllib.error

API_BASE = "https://api.screenshots.pro"
IPHONE_SIZE = (1290, 2796)

HEADLINES = [
    "Build Habits That Stick",
    "Track Your Progress",
    "Celebrate Every Win",
    "Stay Motivated",
]


def get_api_key():
    """Get API key from environment."""
    key = os.environ.get('SCREENSHOTS_PRO_API_KEY')
    if not key:
        return None
    return key


def image_to_base64(path):
    """Convert image to base64."""
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def generate_screenshot_api(api_key, screenshot_path, headline, output_path):
    """Generate screenshot using API."""

    # API payload
    payload = {
        "screenshot": image_to_base64(screenshot_path),
        "device": "iphone15pro",
        "angle": "perspective",
        "headline": headline,
        "background": "gradient",
        "gradient_colors": ["#667eea", "#764ba2"],
        "output_size": {
            "width": IPHONE_SIZE[0],
            "height": IPHONE_SIZE[1]
        }
    }

    # Make request
    req = urllib.request.Request(
        f"{API_BASE}/v1/generate",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))

            # Decode and save result
            img_data = base64.b64decode(result['image'])
            with open(output_path, 'wb') as f:
                f.write(img_data)

            print(f"  Saved: {output_path}")
            return True

    except urllib.error.HTTPError as e:
        print(f"  API Error: {e.code} - {e.reason}")
        return False


def show_instructions():
    """Show setup instructions."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║             APPROACH #6: Screenshots Pro API                     ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  This approach uses the Screenshots Pro commercial API.          ║
║                                                                  ║
║  SETUP:                                                          ║
║  1. Sign up at https://screenshots.pro/                          ║
║  2. Get your API key from the dashboard                          ║
║  3. Set environment variable:                                    ║
║     export SCREENSHOTS_PRO_API_KEY=your_key_here                 ║
║  4. Run this script again                                        ║
║                                                                  ║
║  FEATURES:                                                       ║
║  - 3D perspective device frames                                  ║
║  - All App Store + Google Play sizes in one call                 ║
║  - CI/CD pipeline integration                                    ║
║  - Direct fastlane integration                                   ║
║  - Multiple device types (iPhone, iPad, Android)                 ║
║                                                                  ║
║  PRICING:                                                        ║
║  - Check screenshots.pro for current pricing                     ║
║  - Usually subscription-based with volume tiers                  ║
║                                                                  ║
║  WHY USE THIS?                                                   ║
║  - Enterprise-grade reliability                                  ║
║  - No local rendering resources needed                           ║
║  - Consistent output across all devices                          ║
║  - Perfect for CI/CD automation                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "06_screenshots_pro")

    print(f"\n{'='*60}")
    print("APPROACH #6: Screenshots Pro API")
    print(f"{'='*60}\n")

    api_key = get_api_key()

    if not api_key:
        show_instructions()
        return

    raw_files = sorted([f for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    if not raw_files:
        print("No screenshots found in raw/ folder")
        return

    for i, (raw_file, headline) in enumerate(zip(raw_files[:4], HEADLINES)):
        print(f"Screenshot {i+1}: {headline}")
        raw_path = os.path.join(raw_dir, raw_file)
        output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")
        generate_screenshot_api(api_key, raw_path, headline, output_path)

    print(f"\nDone! Screenshots saved to: {output_dir}")


if __name__ == "__main__":
    main()
