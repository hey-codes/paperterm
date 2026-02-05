# ASCII Artwork Agent

A helper for generating terminal-inspired, ASCII-aesthetic artwork optimized for e-ink displays.

## How to Use This File

When working with Claude Code on artwork generation, reference this file:
```
"Use the ASCII_ARTWORK_AGENT.md guidelines to help me create artwork for my paperterm dashboard"
```

---

## Quick Prompts

### Generate ASCII Art Directly in Claude

Ask Claude to create text-based ASCII art:

```
Create ASCII art of [SUBJECT] using only these characters:
/ \ | _ - = + * . : ' " ~ ^
Make it approximately 60 characters wide and 40 lines tall.
High contrast, suitable for e-ink display.
```

**Good subjects for ASCII art:**
- Mountains and landscapes
- Trees (pine, oak, willow)
- Animals (owl, cat, wolf, fox)
- Geometric patterns
- City skylines
- Weather symbols (sun, cloud, rain)
- Clocks and timepieces
- Abstract patterns

### Example Request

```
Create ASCII art of a mountain landscape with pine trees and a moon.
Use characters: /\|_-=.:'*
60 characters wide, 35 lines tall.
Include some stars in the sky using . and *
```

---

## AI Image Generator Prompts

For Midjourney, DALL-E, Stable Diffusion, or Claude's image generation:

### Template A: Classic Terminal
```
[SUBJECT] displayed on a vintage computer terminal screen,
green phosphor text on black background,
ASCII art style made of text characters,
CRT screen with subtle scanlines,
1980s computing aesthetic,
high contrast monochrome
```

### Template B: Pure ASCII
```
ASCII art illustration of [SUBJECT],
made entirely of keyboard characters,
white background with black text characters,
pixel-perfect alignment,
retro BBS bulletin board art style,
clean edges, high contrast
```

### Template C: Matrix/Hacker
```
[SUBJECT] emerging from falling digital rain,
green characters cascading down black background,
Matrix movie inspired aesthetic,
cyberpunk atmosphere,
high contrast for e-ink display
```

### Template D: Minimalist Pattern
```
Repeating geometric pattern using ASCII characters,
[PATTERN DESCRIPTION],
black on white or white on black,
op-art inspired optical effect,
mathematically precise alignment,
suitable for e-ink display
```

---

## Subject Ideas by Category

### Nature
- Mountain range with snow caps
- Single gnarled tree
- Forest of pine trees
- Ocean waves
- Desert with cactus
- Moon phases
- Starfield/constellation

### Animals
- Owl on branch
- Cat silhouette
- Wolf howling
- Fish/koi
- Bird in flight
- Deer/stag

### Urban/Architecture
- City skyline
- Single building/tower
- Bridge structure
- Window with view
- Staircase

### Abstract/Geometric
- Spiraling pattern
- Concentric circles
- Chevron waves
- Maze/labyrinth
- Tessellation
- Mandala

### Weather/Time
- Sun with rays
- Rain clouds
- Lightning bolt
- Snowflake
- Clock face
- Hourglass

### Typography/Quotes
- Single large letter
- Word as art
- Quote with decorative border
- Calendar grid
- Numbers/digits

---

## Character Palette Reference

### Line Drawing
```
Horizontal:  ─ ━ ═ - _
Vertical:    │ ┃ ║ |
Corners:     ┌ ┐ └ ┘ ╔ ╗ ╚ ╝
T-joints:    ├ ┤ ┬ ┴ ╠ ╣ ╦ ╩
Cross:       ┼ ╬
```

### Shading (light to dark)
```
. · : ; = # @ █
░ ▒ ▓ █
```

### Shapes
```
○ ● ◯ ◉ ◎
□ ■ ▢ ▣
△ ▲ ▽ ▼
◇ ◆ ◊
```

### Decorative
```
★ ☆ ✦ ✧ ⋆
♠ ♣ ♥ ♦
→ ← ↑ ↓ ↔
« » ‹ ›
```

### Basic ASCII (most compatible)
```
/ \ | - _ = + * . : ' " ~ ^ < > [ ] { } ( )
```

---

## Post-Processing Checklist

After generating artwork:

1. **Convert to image** (if text-based)
   - Use monospace font
   - White background, black text (or inverse)
   - Anti-aliasing OFF for crisp edges

2. **Resize to 1236 × 1648 pixels**
   - Kindle PW 11th gen resolution
   - Maintain aspect ratio, add margins if needed

3. **Convert to grayscale**
   - 8-bit grayscale
   - Remove any color

4. **Boost contrast**
   - Increase by 20-30%
   - Ensure pure blacks and whites

5. **Apply dithering** (if gradients present)
   - Floyd-Steinberg recommended
   - 16 color levels

6. **Save as PNG**
   - Lossless compression
   - Place in `artwork/` folder

---

## Sample ASCII Art

### Simple Mountain
```
                    /\
                   /  \
                  /    \
                 /      \
            /\  /   /\   \  /\
           /  \/   /  \   \/  \
          /       /    \       \
    /\   /       /      \       \   /\
   /  \ /       /        \       \ /  \
  /    \       /          \       \    \
 /______\_____/____________\_____/______\
```

### Moon
```
       _..._
     .:::::::.
    :::::::::::
    :::::::::::
    `:::::::::'
      `':::''
```

### Tree
```
        *
       /|\
      /*|O\
     /*/|\*\
    /X/O|*\X\
   /*/X/|\X\*\
  /O/*/X|O\*\O\
 /X/O/*/|\*\O\X\
        |
       |||
```

---

## Workflow Integration

### For paperterm dashboard:

1. Generate or find ASCII art
2. Save as PNG in `paperterm/artwork/` subfolder
3. Art will automatically rotate based on `config.yml` settings
4. Test locally: `cd src && python render.py`
5. Commit and push to trigger GitHub Actions

### Folder Organization
```
artwork/
├── nature/         # Landscapes, trees, animals
├── typography/     # Quotes, letters, words
├── illustrations/  # Detailed drawings
├── abstract/       # Patterns, geometric
└── terminal/       # ASCII, retro computing themes
```

---

## Resources

### ASCII Art Archives
- [ASCII Art Archive](https://www.asciiart.eu/)
- [Christopher Johnson's ASCII Art](https://asciiart.website/)
- [ASCII Art Dictionary](https://www.asciiartfarts.com/ascii.html)

### Text-to-ASCII Tools
- [Text to ASCII Art Generator](https://patorjk.com/software/taag/)
- [ASCII Banner Generator](https://manytools.org/hacker-tools/ascii-banner/)
- [Figlet](http://www.figlet.org/)

### Image-to-ASCII Converters
- [Image to ASCII Art](https://www.text-image.com/convert/ascii.html)
- [ASCII Art Studio](https://www.ascii-art-generator.org/)
