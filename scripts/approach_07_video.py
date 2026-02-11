#!/usr/bin/env python3
"""
Approach #7: Video Preview / Animated Screenshots
=================================================
Create app preview videos/GIFs that can boost conversion by 20-40%.

Methods:
1. Slideshow from screenshots with transitions
2. Ken Burns effect (zoom/pan on static images)
3. Combine with xcrun simulator recording

Requires: ffmpeg (brew install ffmpeg)

Usage:
    python approach_07_video.py

Output: ../output/07_video_preview/
"""

import os
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IPHONE_SIZE = (1290, 2796)
VIDEO_SIZE = (886, 1920)  # App Store preview size (9:19.5 scaled)
FPS = 30
DURATION_PER_SLIDE = 3  # seconds


def check_ffmpeg():
    """Check if ffmpeg is available."""
    if shutil.which('ffmpeg'):
        return True
    print("FFmpeg not found. Install with: brew install ffmpeg")
    return False


def create_transition_frames(img1, img2, num_frames=15):
    """Create crossfade transition frames between two images."""
    frames = []
    for i in range(num_frames):
        alpha = i / (num_frames - 1)
        blended = Image.blend(img1, img2, alpha)
        frames.append(blended)
    return frames


def create_ken_burns_frames(img, num_frames, zoom_start=1.0, zoom_end=1.1, direction='in'):
    """Create Ken Burns effect (slow zoom) frames."""
    frames = []
    width, height = img.size

    for i in range(num_frames):
        t = i / (num_frames - 1)

        # Interpolate zoom
        if direction == 'in':
            zoom = zoom_start + (zoom_end - zoom_start) * t
        else:
            zoom = zoom_end - (zoom_end - zoom_start) * t

        # Calculate crop box
        new_w = int(width / zoom)
        new_h = int(height / zoom)
        left = (width - new_w) // 2
        top = (height - new_h) // 2

        # Crop and resize back
        cropped = img.crop((left, top, left + new_w, top + new_h))
        frame = cropped.resize((width, height), Image.LANCZOS)
        frames.append(frame)

    return frames


def create_marketing_frame(screenshot_path, headline, size, colors):
    """Create a single marketing frame with screenshot and text."""
    width, height = size

    # Create gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    c1 = tuple(int(colors[0].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    c2 = tuple(int(colors[1].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    for y in range(height):
        ratio = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Load and position screenshot
    if os.path.exists(screenshot_path):
        screenshot = Image.open(screenshot_path).convert('RGBA')
        target_width = int(width * 0.65)
        scale = target_width / screenshot.width
        target_height = int(screenshot.height * scale)
        screenshot = screenshot.resize((target_width, target_height), Image.LANCZOS)

        # Add rounded corners
        mask = Image.new('L', (target_width, target_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (target_width, target_height)], radius=30, fill=255)

        x = (width - target_width) // 2
        y = int(height * 0.28)
        img.paste(screenshot, (x, y), mask)

    # Add headline
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", int(width * 0.065))
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), headline, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((text_x, int(height * 0.08)), headline, fill=(255, 255, 255), font=font)

    return img


def create_slideshow_video(screenshots, headlines, output_path, colors):
    """Create a slideshow video from screenshots."""
    if not check_ffmpeg():
        return False

    # Create temp directory for frames
    temp_dir = os.path.join(os.path.dirname(output_path), "temp_frames")
    os.makedirs(temp_dir, exist_ok=True)

    frame_num = 0
    frames_per_slide = FPS * DURATION_PER_SLIDE
    transition_frames = int(FPS * 0.5)  # 0.5 second transitions

    # Generate frames for each slide
    prev_frame = None

    for i, (screenshot, headline) in enumerate(zip(screenshots, headlines)):
        print(f"  Processing slide {i+1}/{len(screenshots)}: {headline}")

        # Create the marketing frame
        color_pair = [colors[i % len(colors)], colors[(i + 1) % len(colors)]]
        frame = create_marketing_frame(screenshot, headline, VIDEO_SIZE, color_pair)

        # Add transition from previous
        if prev_frame is not None:
            trans_frames = create_transition_frames(prev_frame, frame, transition_frames)
            for tf in trans_frames:
                tf.save(os.path.join(temp_dir, f"frame_{frame_num:05d}.png"))
                frame_num += 1

        # Add Ken Burns frames
        kb_frames = create_ken_burns_frames(frame, frames_per_slide - transition_frames)
        for kf in kb_frames:
            kf.save(os.path.join(temp_dir, f"frame_{frame_num:05d}.png"))
            frame_num += 1

        prev_frame = frame

    print(f"  Generated {frame_num} frames")

    # Compile with ffmpeg
    print("  Compiling video with ffmpeg...")
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', os.path.join(temp_dir, 'frame_%05d.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'medium',
        '-crf', '18',
        output_path
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  FFmpeg error: {result.stderr}")
        return False

    # Also create GIF version
    gif_path = output_path.replace('.mp4', '.gif')
    print(f"  Creating GIF version...")

    gif_cmd = [
        'ffmpeg', '-y',
        '-i', output_path,
        '-vf', f'fps=15,scale={VIDEO_SIZE[0]//2}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
        '-loop', '0',
        gif_path
    ]
    subprocess.run(gif_cmd, capture_output=True)

    # Cleanup temp files
    shutil.rmtree(temp_dir)

    print(f"  Video saved: {output_path}")
    print(f"  GIF saved: {gif_path}")
    return True


def create_still_preview(screenshots, headlines, output_path, colors):
    """Create a still image preview if ffmpeg not available."""
    # Create a filmstrip-style preview showing all frames
    width = VIDEO_SIZE[0]
    height = len(screenshots) * VIDEO_SIZE[1] // 3

    preview = Image.new('RGB', (width, height), (0, 0, 0))

    y_offset = 0
    mini_height = height // len(screenshots)

    for i, (screenshot, headline) in enumerate(zip(screenshots, headlines)):
        color_pair = [colors[i % len(colors)], colors[(i + 1) % len(colors)]]
        frame = create_marketing_frame(screenshot, headline, VIDEO_SIZE, color_pair)

        # Scale down
        mini = frame.resize((width, mini_height), Image.LANCZOS)
        preview.paste(mini, (0, y_offset))
        y_offset += mini_height

    preview.save(output_path.replace('.mp4', '_preview.png'))
    print(f"  Preview saved: {output_path.replace('.mp4', '_preview.png')}")


def main():
    """Generate video preview."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "raw")
    output_dir = os.path.join(base_dir, "output", "07_video_preview")

    raw_files = sorted([os.path.join(raw_dir, f) for f in os.listdir(raw_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))])

    headlines = [
        "Build Habits That Stick",
        "Track Your Progress",
        "Celebrate Every Win",
        "Join 50,000+ Users",
    ]

    colors = ["#667eea", "#764ba2", "#f093fb", "#4facfe"]

    print(f"\n{'='*60}")
    print("APPROACH #7: Video Preview / Animated Screenshots")
    print(f"{'='*60}\n")

    if not raw_files:
        print("No screenshots found in raw/ folder.")
        print("Add screenshots and run again.")
        return

    # Use available screenshots
    screenshots = raw_files[:4] if len(raw_files) >= 4 else raw_files * 2

    output_path = os.path.join(output_dir, "app_preview.mp4")

    if check_ffmpeg():
        create_slideshow_video(screenshots[:4], headlines[:4], output_path, colors)
    else:
        print("Creating still preview instead...")
        create_still_preview(screenshots[:4], headlines[:4], output_path, colors)

    print(f"\nDone! Output saved to: {output_dir}")


if __name__ == "__main__":
    main()
