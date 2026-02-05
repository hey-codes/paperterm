# E-Ink Display Research

Compiled research on e-ink technology, optimization techniques, and best practices.

## E-Ink Technology Overview

### How E-Ink Works
- **Electrophoretic display**: Tiny capsules contain black and white particles
- **Bistable**: Maintains image without power (only needs power to change)
- **Reflective**: Uses ambient light like paper (no backlight needed, though frontlight available)
- **Slow refresh**: 0.5-2 seconds for full refresh

### Kindle Paperwhite 11th Gen Specifications
| Property | Value |
|----------|-------|
| Screen Size | 6.8 inches |
| Resolution | 1236 × 1648 pixels |
| Pixel Density | 300 PPI |
| Color Depth | 16 levels of grayscale |
| Technology | E Ink Carta 1200 |
| Frontlight | Adjustable warm light |

## Image Optimization Techniques

### Pre-Processing Pipeline
1. **Resize** to exact display dimensions
2. **Convert to grayscale** (8-bit)
3. **Boost contrast** by 20-30%
4. **Apply gamma correction** (1.8-2.2)
5. **Apply dithering** (Floyd-Steinberg recommended)
6. **Save as PNG** (lossless compression)

### Dithering Algorithms

#### Floyd-Steinberg (Recommended)
- Best for photographs and continuous-tone images
- Distributes quantization error to neighboring pixels
- Creates natural-looking grain pattern
- Good edge preservation

#### Atkinson
- Lighter, more stylized appearance
- Only distributes 75% of error (discards 25%)
- Classic "Mac" aesthetic
- Better for line art and illustrations

#### Ordered/Bayer
- Uses fixed threshold matrix
- Creates regular dot pattern
- Faster to compute
- Less natural appearance

### Contrast Enhancement
```python
# Recommended contrast boost: 1.2-1.3 (20-30% increase)
from PIL import ImageEnhance
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(1.25)
```

### Sharpening for E-Ink
```python
# Mild unsharp mask improves clarity
from PIL import ImageFilter
img = img.filter(ImageFilter.UnsharpMask(
    radius=0.5,      # Small radius
    percent=50,      # Moderate amount
    threshold=2      # Avoid noise amplification
))
```

## Display Refresh Modes

### Full Refresh (GC16)
- Complete screen clear and redraw
- Eliminates ghosting
- Visible flash (black-white-black)
- ~1 second

### Partial Refresh (DU)
- Only updates changed pixels
- Faster (~250ms)
- Can accumulate ghosting
- Good for text/UI updates

### A2 Mode (Fast)
- Binary (black/white only)
- Very fast (~120ms)
- No grayscale
- Significant ghosting

## Ghosting Mitigation

### Causes
- Incomplete particle movement during refresh
- Accumulation from partial refreshes
- Temperature variations
- Age of display

### Solutions
- Periodic full refresh (every N partial refreshes)
- Higher contrast images reduce visibility of ghosts
- Avoid large solid gray areas
- Use patterns instead of solid fills when possible

## Power Consumption

### Display States
- **Static image**: Near zero (bistable)
- **Refresh**: Brief spike during update
- **Frontlight**: Continuous draw when enabled

### Optimization
- Minimize refresh frequency
- Use partial refreshes when possible
- Batch updates together
- Consider frontlight usage

## Temperature Effects

E-ink refresh speed varies with temperature:
- **Cold (<10°C)**: Slower refresh, may need multiple passes
- **Normal (15-25°C)**: Optimal performance
- **Hot (>35°C)**: Faster but may affect longevity

## References

### Technical Documentation
- [E Ink Corporation](https://www.eink.com/) - Official technology info
- [Preparing Graphics for E-Ink Displays](https://cdn-learn.adafruit.com/downloads/pdf/preparing-graphics-for-e-ink-displays.pdf) - Adafruit Guide
- [GooDisplay Dithering Guide](https://www.good-display.com/news/194.html)

### Community Resources
- [MobileRead Forums](https://www.mobileread.com/forums/) - Kindle hacking community
- [KindleModding.org](https://kindlemodding.org/) - Jailbreak documentation
- [r/kindlescreensavers](https://reddit.com/r/kindlescreensavers) - Wallpaper community

### Tools
- [eink-wallpaper-generator](https://github.com/whitelips/eink-wallpaper-generator) - Web-based with device presets
- [ImageMagick](https://imagemagick.org/) - Command-line image processing
- [Pillow](https://pillow.readthedocs.io/) - Python imaging library
