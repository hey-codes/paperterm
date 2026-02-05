"""
Artwork selection and processing for Kindle Dashboard.
Handles e-ink optimization, rotation, and caching.
"""

import os
import random
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL not installed. Image processing disabled.")


# E-ink display specifications
KINDLE_PW5_WIDTH = 1236
KINDLE_PW5_HEIGHT = 1648


def get_artwork_files(
    artwork_dir: str,
    categories: Optional[List[str]] = None
) -> List[Path]:
    """
    Get list of artwork files from the artwork directory.

    Args:
        artwork_dir: Path to artwork directory
        categories: Optional list of category subdirectories to include

    Returns:
        List of Path objects to image files
    """
    artwork_path = Path(artwork_dir)
    if not artwork_path.exists():
        return []

    extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    files = []

    if categories:
        # Look in specific category subdirectories
        for category in categories:
            cat_path = artwork_path / category
            if cat_path.exists():
                for f in cat_path.iterdir():
                    if f.suffix.lower() in extensions:
                        files.append(f)
    else:
        # Look in root artwork directory and all subdirectories
        for f in artwork_path.rglob('*'):
            if f.suffix.lower() in extensions:
                files.append(f)

    return sorted(files)


def select_artwork(
    artwork_dir: str,
    categories: Optional[List[str]] = None,
    state_file: Optional[str] = None,
    rotation_interval: int = 1
) -> Optional[Path]:
    """
    Select artwork for display, supporting rotation.

    Args:
        artwork_dir: Path to artwork directory
        categories: Optional list of categories to include
        state_file: Path to state file for tracking rotation
        rotation_interval: How many calls before rotating to next image

    Returns:
        Path to selected artwork file
    """
    files = get_artwork_files(artwork_dir, categories)
    if not files:
        return None

    # Load or initialize state
    current_index = 0
    call_count = 0

    if state_file:
        state_path = Path(state_file)
        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    parts = f.read().strip().split(',')
                    current_index = int(parts[0])
                    call_count = int(parts[1]) if len(parts) > 1 else 0
            except (ValueError, IOError):
                pass

    # Increment call count and potentially rotate
    call_count += 1
    if call_count >= rotation_interval:
        current_index = (current_index + 1) % len(files)
        call_count = 0

    # Save state
    if state_file:
        try:
            with open(state_file, 'w') as f:
                f.write(f"{current_index},{call_count}")
        except IOError:
            pass

    return files[current_index % len(files)]


def optimize_for_eink(
    input_path: str,
    output_path: str,
    width: int = KINDLE_PW5_WIDTH,
    height: int = KINDLE_PW5_HEIGHT,
    contrast_boost: float = 1.25,
    dither: bool = True,
    grayscale_levels: int = 16
) -> bool:
    """
    Optimize an image for e-ink display.

    Args:
        input_path: Path to input image
        output_path: Path to save optimized image
        width: Target width in pixels
        height: Target height in pixels
        contrast_boost: Contrast enhancement factor (1.0 = no change)
        dither: Apply Floyd-Steinberg dithering
        grayscale_levels: Number of grayscale levels (typically 16 for e-ink)

    Returns:
        True if successful, False otherwise
    """
    if not HAS_PIL:
        return False

    try:
        img = Image.open(input_path)

        # Convert to RGB first if necessary (handles RGBA, P, etc.)
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # Calculate scaling to fit within bounds while maintaining aspect ratio
        img_ratio = img.width / img.height
        target_ratio = width / height

        if img_ratio > target_ratio:
            # Image is wider than target - fit to width
            new_width = width
            new_height = int(width / img_ratio)
        else:
            # Image is taller than target - fit to height
            new_height = height
            new_width = int(height * img_ratio)

        # Resize with high-quality resampling
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Create canvas and paste centered
        canvas = Image.new('L', (width, height), color=255)  # White background
        x = (width - new_width) // 2
        y = (height - new_height) // 2

        # Convert to grayscale before pasting
        img_gray = img.convert('L')
        canvas.paste(img_gray, (x, y))
        img = canvas

        # Apply mild sharpening for e-ink clarity
        img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=2))

        # Boost contrast
        if contrast_boost != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_boost)

        # Apply dithering
        if dither:
            # Floyd-Steinberg dithering to limited grayscale palette
            img = img.quantize(colors=grayscale_levels, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
            img = img.convert('L')

        # Save optimized image
        img.save(output_path, 'PNG', optimize=True)
        return True

    except Exception as e:
        print(f"Error optimizing image: {e}")
        return False


def create_placeholder_artwork(
    output_path: str,
    width: int = KINDLE_PW5_WIDTH,
    height: int = KINDLE_PW5_HEIGHT,
    text: str = "No Artwork Available"
) -> bool:
    """
    Create a placeholder image when no artwork is available.

    Args:
        output_path: Path to save placeholder image
        width: Image width
        height: Image height
        text: Text to display

    Returns:
        True if successful
    """
    if not HAS_PIL:
        return False

    try:
        from PIL import ImageDraw, ImageFont

        # Create light gray canvas
        img = Image.new('L', (width, height), color=240)
        draw = ImageDraw.Draw(img)

        # Try to use a font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        except:
            font = ImageFont.load_default()

        # Draw centered text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill=128, font=font)

        img.save(output_path, 'PNG')
        return True

    except Exception as e:
        print(f"Error creating placeholder: {e}")
        return False


def get_artwork_hash(filepath: str) -> str:
    """Generate a hash of artwork file for caching."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


if __name__ == "__main__":
    # Test artwork listing
    test_dir = "../artwork"
    files = get_artwork_files(test_dir)
    print(f"Found {len(files)} artwork files")
    for f in files[:5]:
        print(f"  - {f}")

    # Test optimization
    if files and HAS_PIL:
        test_input = str(files[0])
        test_output = "/tmp/test_eink_optimized.png"
        if optimize_for_eink(test_input, test_output):
            print(f"\nOptimized: {test_input} -> {test_output}")
