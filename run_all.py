#!/usr/bin/env python3
"""
Master Runner: Generate All Screenshot Approaches
==================================================
Runs all 10 screenshot approaches and generates comparison output.

Usage:
    python run_all.py              # Run all available approaches
    python run_all.py --approach 1 # Run specific approach (1-10)
    python run_all.py --list       # List all approaches

Output: ./output/[approach_folder]/
"""

import os
import sys
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "scripts")
RAW_DIR = os.path.join(SCRIPT_DIR, "raw")

APPROACHES = [
    {
        "num": 1,
        "name": "PIL + Mesh Gradients",
        "script": "approach_01_pil_mesh.py",
        "requires": ["PIL"],
        "auto": True,
    },
    {
        "num": 2,
        "name": "HTML/CSS → Image (Playwright)",
        "script": "approach_02_html_css.py",
        "requires": ["playwright"],
        "auto": True,
    },
    {
        "num": 3,
        "name": "Blender 3D Mockup",
        "script": "approach_03_blender.py",
        "requires": ["Blender", "iPhone 3D model"],
        "auto": False,
    },
    {
        "num": 4,
        "name": "AI-Generated Backgrounds",
        "script": "approach_04_ai_bg.py",
        "requires": ["Pre-generated Midjourney/DALL-E backgrounds"],
        "auto": False,
    },
    {
        "num": 5,
        "name": "Ugly Ads (iMessage/Notes/Twitter)",
        "script": "approach_05_ugly_ads.py",
        "requires": ["PIL"],
        "auto": True,
    },
    {
        "num": 6,
        "name": "Screenshots Pro API",
        "script": "approach_06_api.py",
        "requires": ["API key from screenshots.pro"],
        "auto": False,
    },
    {
        "num": 7,
        "name": "Video Preview",
        "script": "approach_07_video.py",
        "requires": ["PIL", "ffmpeg (optional)"],
        "auto": True,
    },
    {
        "num": 8,
        "name": "Storytelling Carousel",
        "script": "approach_08_storytelling.py",
        "requires": ["PIL"],
        "auto": True,
    },
    {
        "num": 9,
        "name": "Figma Template Export",
        "script": "approach_09_figma.py",
        "requires": ["Figma account", "Template design"],
        "auto": False,
    },
    {
        "num": 10,
        "name": "Hybrid Engine",
        "script": "approach_10_hybrid.py",
        "requires": ["PIL"],
        "auto": True,
    },
]


def check_raw_screenshots():
    """Check if raw screenshots exist."""
    if not os.path.exists(RAW_DIR):
        return []
    files = [f for f in os.listdir(RAW_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return sorted(files)


def run_approach(approach):
    """Run a single approach script."""
    script_path = os.path.join(SCRIPTS_DIR, approach["script"])

    if not os.path.exists(script_path):
        print(f"  Script not found: {approach['script']}")
        return False

    print(f"\n{'='*60}")
    print(f"APPROACH #{approach['num']}: {approach['name']}")
    print(f"{'='*60}")

    start = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=SCRIPT_DIR,
        capture_output=False
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n Completed in {elapsed:.1f}s")
        return True
    else:
        print(f"\n Failed (exit code {result.returncode})")
        return False


def list_approaches():
    """List all approaches with their status."""
    raw_files = check_raw_screenshots()

    print("\n" + "="*70)
    print("APP STORE SCREENSHOT APPROACHES")
    print("="*70)
    print(f"\nRaw screenshots found: {len(raw_files)}")
    if raw_files:
        for f in raw_files[:5]:
            print(f"  - {f}")
        if len(raw_files) > 5:
            print(f"  ... and {len(raw_files) - 5} more")

    print("\n" + "-"*70)
    print(f"{'#':<4} {'Approach':<40} {'Auto':<6} {'Requirements'}")
    print("-"*70)

    for a in APPROACHES:
        auto = "" if a["auto"] else ""
        reqs = ", ".join(a["requires"][:2])
        if len(a["requires"]) > 2:
            reqs += f" +{len(a['requires'])-2} more"
        print(f"{a['num']:<4} {a['name']:<40} {auto:<6} {reqs}")

    print("-"*70)
    print("\n = Fully automated (just add screenshots)")
    print(" = Requires external resources\n")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if '--list' in args or '-l' in args:
        list_approaches()
        return

    if '--approach' in args or '-a' in args:
        try:
            idx = args.index('--approach') if '--approach' in args else args.index('-a')
            num = int(args[idx + 1])
            approach = next((a for a in APPROACHES if a['num'] == num), None)
            if approach:
                run_approach(approach)
            else:
                print(f"Approach {num} not found. Use --list to see available approaches.")
        except (IndexError, ValueError):
            print("Usage: python run_all.py --approach [1-10]")
        return

    # Run all automated approaches
    raw_files = check_raw_screenshots()

    if not raw_files:
        print("\n" + "!"*60)
        print("NO SCREENSHOTS FOUND!")
        print("!"*60)
        print(f"\nPlease add your app screenshots to:")
        print(f"  {RAW_DIR}/")
        print("\nExpected files: 1.png, 2.png, 3.png, 4.png (or any .png/.jpg)")
        print("\nThen run this script again.")
        return

    print("\n" + "="*70)
    print("RUNNING ALL AUTOMATED APPROACHES")
    print("="*70)
    print(f"\nFound {len(raw_files)} screenshots in raw/")

    results = []

    for approach in APPROACHES:
        if approach["auto"]:
            success = run_approach(approach)
            results.append((approach["num"], approach["name"], success))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for num, name, success in results:
        status = "" if success else ""
        print(f"  {status} Approach #{num}: {name}")

    print("\n" + "-"*70)
    print("Output folders:")
    output_dir = os.path.join(SCRIPT_DIR, "output")
    for folder in sorted(os.listdir(output_dir)):
        path = os.path.join(output_dir, folder)
        if os.path.isdir(path):
            files = len([f for f in os.listdir(path) if f.endswith('.png')])
            print(f"  {folder}/ ({files} images)")

    print("\nDone!")


if __name__ == "__main__":
    main()
