#!/usr/bin/env python3
"""
Approach #9: Figma Template + Export Automation
===============================================
Design in Figma (visual iteration), automate export with Figma API.

WORKFLOW:
1. Create/import a screenshot template in Figma
2. Set up your Figma Personal Access Token
3. Export frames via API

TEMPLATE RESOURCES:
- 500+ Free Templates: https://www.figma.com/community/file/1471925742378558731/
- ASO.dev Plugin: https://aso.dev/ (localization + export)
- Screeny Plugin: https://www.figma.com/community/plugin/1438365234530795949/

SETUP:
1. Create a Figma account
2. Generate Personal Access Token: Figma > Settings > Account > Personal access tokens
3. Set environment variable: export FIGMA_TOKEN=your_token
4. Get file key from Figma URL: figma.com/file/[FILE_KEY]/...
5. Set environment variable: export FIGMA_FILE_KEY=your_file_key

Usage:
    python approach_09_figma.py

Output: ./output/09_figma_export/
"""

import os
import json
import urllib.request
import urllib.error

FIGMA_API = "https://api.figma.com/v1"


def get_figma_credentials():
    """Get Figma token and file key from environment."""
    token = os.environ.get('FIGMA_TOKEN')
    file_key = os.environ.get('FIGMA_FILE_KEY')
    return token, file_key


def get_file_frames(token, file_key):
    """Get all frames from a Figma file."""
    req = urllib.request.Request(
        f"{FIGMA_API}/files/{file_key}",
        headers={"X-Figma-Token": token}
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code}")
        return None


def export_frames(token, file_key, frame_ids, output_dir):
    """Export specific frames as PNG."""
    ids_param = ",".join(frame_ids)

    req = urllib.request.Request(
        f"{FIGMA_API}/images/{file_key}?ids={ids_param}&format=png&scale=2",
        headers={"X-Figma-Token": token}
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

            for i, (frame_id, url) in enumerate(data.get('images', {}).items()):
                if url:
                    output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")
                    urllib.request.urlretrieve(url, output_path)
                    print(f"  Saved: {output_path}")

            return True

    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code}")
        return False


def find_screenshot_frames(file_data):
    """Find frames that look like app screenshots."""
    frames = []

    def search_children(node):
        if node.get('type') == 'FRAME':
            name = node.get('name', '').lower()
            # Look for frames named like screenshots
            if any(term in name for term in ['screenshot', 'screen', '6.5', 'iphone', 'mockup']):
                frames.append(node['id'])
        for child in node.get('children', []):
            search_children(child)

    document = file_data.get('document', {})
    search_children(document)

    return frames


def show_instructions():
    """Show setup instructions."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║            APPROACH #9: Figma Template + Export                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Design in Figma, automate export with the Figma API.            ║
║                                                                  ║
║  TEMPLATE RESOURCES (FREE):                                      ║
║  - 500+ Templates:                                               ║
║    figma.com/community/file/1471925742378558731/                 ║
║  - ASO.dev Plugin: aso.dev (localization + export)               ║
║  - Screeny Plugin: Direct App Store export                       ║
║                                                                  ║
║  SETUP STEPS:                                                    ║
║                                                                  ║
║  1. Create/duplicate a template in Figma                         ║
║  2. Name your screenshot frames: "Screenshot 1", "Screenshot 2"  ║
║  3. Generate Personal Access Token:                              ║
║     Figma > Settings > Account > Personal access tokens          ║
║  4. Get file key from URL: figma.com/file/[FILE_KEY]/...         ║
║  5. Set environment variables:                                   ║
║     export FIGMA_TOKEN=your_token                                ║
║     export FIGMA_FILE_KEY=your_file_key                          ║
║  6. Run this script                                              ║
║                                                                  ║
║  WHY USE FIGMA?                                                  ║
║  - Visual design iteration (faster than code)                    ║
║  - Component system (update once, propagates)                    ║
║  - Huge template library                                         ║
║  - Real-time collaboration                                       ║
║  - Export automation via API                                     ║
║                                                                  ║
║  TIPS:                                                           ║
║  - Use Components for device frames                              ║
║  - Use Auto Layout for text                                      ║
║  - Create Variants for different color schemes                   ║
║  - Use the Screeny plugin for quick exports                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(base_dir, "output", "09_figma_export")

    print(f"\n{'='*60}")
    print("APPROACH #9: Figma Template + Export")
    print(f"{'='*60}\n")

    token, file_key = get_figma_credentials()

    if not token or not file_key:
        show_instructions()
        return

    print("Fetching Figma file...")
    file_data = get_file_frames(token, file_key)

    if not file_data:
        print("Could not fetch Figma file. Check your credentials.")
        return

    print(f"File: {file_data.get('name', 'Unknown')}")

    # Find screenshot frames
    frames = find_screenshot_frames(file_data)

    if not frames:
        print("\nNo screenshot frames found.")
        print("Make sure your frames are named with 'screenshot', 'screen', or 'iPhone'")
        return

    print(f"Found {len(frames)} screenshot frames")
    print("Exporting...")

    export_frames(token, file_key, frames[:5], output_dir)

    print(f"\nDone! Screenshots saved to: {output_dir}")


if __name__ == "__main__":
    main()
