# Screenshot Showcase

10 different approaches to generating App Store screenshots — from pure Python gradients to 3D Blender renders to fake iMessage conversations. A framework for testing which screenshot style converts best.

## Approaches

| # | Name | Auto | Description |
|---|------|------|-------------|
| 1 | PIL + Mesh Gradients | Yes | Programmatic gradients with PIL |
| 2 | HTML/CSS to Image | Yes | Modern CSS effects via Playwright |
| 3 | Blender 3D | Semi | Photorealistic 3D device renders |
| 4 | AI Backgrounds | Semi | Midjourney/DALL-E scene backgrounds |
| 5 | Ugly Ads | Yes | iMessage/Notes/Twitter mockup style |
| 6 | Screenshots Pro | Semi | Commercial API integration |
| 7 | Video Preview | Yes | Animated slideshows for app previews |
| 8 | Storytelling | Yes | Connected narrative carousel across 5 frames |
| 9 | Figma Export | Semi | Design in Figma, export via API |
| 10 | Hybrid Engine | Yes | Config-driven, combines multiple styles |

## Tech Stack

- Python 3 (PIL, NumPy)
- Playwright (HTML/CSS rendering)
- Blender Python API (3D mockups)
- ffmpeg (video generation)

## Quick Start

```bash
# 1. Add your raw screenshots
cp your_screenshots/*.png raw/

# 2. Run all automated approaches
python run_all.py

# 3. Check output
open output/
```

## Output Sizes

- iPhone 6.7": 1290 x 2796 px
- iPad 13": 2048 x 2732 px

## Run Specific Approach

```bash
python run_all.py --approach 5  # Run only Ugly Ads
python run_all.py --list        # List all approaches
```

## Project Structure

```
screenshot-showcase/
├── raw/                    # Your app screenshots (input)
├── output/                 # Generated screenshots
│   ├── 01_pil_mesh/
│   ├── 02_html_css/
│   ├── 05_ugly_ads/
│   └── ...
├── scripts/                # Generator scripts
├── gradients/              # For AI backgrounds (#4)
└── run_all.py              # Master runner
```

## Why 10 Approaches?

Because nobody knows which screenshot style actually converts until you test it. Approach 5 (fake iMessage conversations) consistently outperforms the "professional" approaches, which says something about the App Store.

## License

MIT
