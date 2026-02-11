# App Store Screenshot Showcase

Generate stunning app store screenshots using 10 different approaches.

## Quick Start

```bash
# 1. Add your raw screenshots
cp your_screenshots/*.png raw/

# 2. Run all automated approaches
python run_all.py

# 3. Check output
open output/
```

## Approaches

| # | Name | Auto | Description |
|---|------|------|-------------|
| 1 | PIL + Mesh Gradients | ✅ | Programmatic gradients with PIL |
| 2 | HTML/CSS → Image | ✅ | Modern CSS effects via Playwright |
| 3 | Blender 3D | ⚠️ | Photorealistic 3D renders |
| 4 | AI Backgrounds | ⚠️ | Midjourney/DALL-E backgrounds |
| 5 | Ugly Ads | ✅ | iMessage/Notes/Twitter style |
| 6 | Screenshots Pro | ⚠️ | Commercial API |
| 7 | Video Preview | ✅ | Animated slideshows |
| 8 | Storytelling | ✅ | Connected narrative carousel |
| 9 | Figma Export | ⚠️ | Design in Figma, export via API |
| 10 | Hybrid Engine | ✅ | Config-driven, all styles |

✅ = Fully automated (just add screenshots)
⚠️ = Requires external setup

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
