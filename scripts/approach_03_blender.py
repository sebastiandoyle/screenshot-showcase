#!/usr/bin/env python3
"""
Approach #3: Blender 3D Mockup Automation
=========================================
Uses Blender's Python API to render photorealistic 3D iPhone mockups.

REQUIREMENTS:
1. Install Blender: brew install --cask blender
2. Download iPhone 3D model:
   - Free: https://mockupz.design/ (Blender files included)
   - Free: https://www.blenderkit.com/ (search "iPhone")
   - Paid ($5): https://simuradi.gumroad.com/l/iPhone14pro

3. Save model to: ~/Developer/screenshot-showcase/assets/iphone_mockup.blend

The .blend file should have:
- An image texture node named "ScreenTexture" for the phone screen
- A camera set up at desired angle
- Proper lighting

Usage:
    blender --background assets/iphone_mockup.blend --python scripts/approach_03_blender.py

Output: ./output/03_blender_3d/
"""

import os
import sys

# Check if running inside Blender
try:
    import bpy
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


def render_in_blender():
    """Render screenshots using Blender."""
    # Get paths
    blend_dir = os.path.dirname(bpy.data.filepath)
    base_dir = os.path.dirname(blend_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "03_blender_3d")

    os.makedirs(output_dir, exist_ok=True)

    # Find screenshots
    screenshots = sorted([f for f in os.listdir(raw_dir)
                         if f.endswith(('.png', '.jpg', '.jpeg'))])

    if not screenshots:
        print("No screenshots found in raw/ folder")
        return

    # Find the screen texture
    screen_tex = None
    for img in bpy.data.images:
        if "screen" in img.name.lower() or "texture" in img.name.lower():
            screen_tex = img
            break

    if not screen_tex:
        print("Could not find screen texture. Looking for image named 'ScreenTexture'...")
        print("Available images:", [img.name for img in bpy.data.images])
        return

    # Set render settings
    scene = bpy.context.scene
    scene.render.resolution_x = 1290
    scene.render.resolution_y = 2796
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # Render each screenshot
    for i, screenshot in enumerate(screenshots[:5]):
        print(f"\nRendering {i+1}/{len(screenshots)}: {screenshot}")

        # Update screen texture
        screen_path = os.path.join(raw_dir, screenshot)
        screen_tex.filepath = screen_path
        screen_tex.reload()

        # Set output path
        output_path = os.path.join(output_dir, f"{i+1}_6.5_inch.png")
        scene.render.filepath = output_path

        # Render
        bpy.ops.render.render(write_still=True)
        print(f"Saved: {output_path}")

    print(f"\nDone! Renders saved to: {output_dir}")


def show_instructions():
    """Show setup instructions when not running in Blender."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           APPROACH #3: Blender 3D Mockup Automation              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  This approach requires Blender and an iPhone 3D model.          ║
║                                                                  ║
║  SETUP STEPS:                                                    ║
║                                                                  ║
║  1. Install Blender:                                             ║
║     brew install --cask blender                                  ║
║                                                                  ║
║  2. Download a free iPhone mockup:                               ║
║     https://mockupz.design/ (has Blender files)                  ║
║     https://www.blenderkit.com/ (search "iPhone")                ║
║                                                                  ║
║  3. Open the .blend file in Blender and:                         ║
║     - Ensure the phone screen has an Image Texture node          ║
║     - Name the texture "ScreenTexture"                           ║
║     - Set up camera at desired angle                             ║
║     - Save as: assets/iphone_mockup.blend                        ║
║                                                                  ║
║  4. Run with:                                                    ║
║     blender --background assets/iphone_mockup.blend \\            ║
║             --python scripts/approach_03_blender.py              ║
║                                                                  ║
║  WHY USE BLENDER?                                                ║
║  - Photorealistic renders with ray-traced lighting               ║
║  - Any camera angle (isometric, dramatic, floating)              ║
║  - Multiple devices in one scene (iPhone + iPad + Watch)         ║
║  - Depth of field, reflections, custom environments              ║
║  - Completely unique look no template tool can match             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    if IN_BLENDER:
        render_in_blender()
    else:
        show_instructions()
