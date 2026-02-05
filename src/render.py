"""
Main dashboard renderer for Kindle Dashboard.
Composites weather, artwork, time, and reminders into final PNG.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Error: PIL/Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

import yaml

# Import our modules
from weather import fetch_weather, WEATHER_CODES
from artwork import select_artwork, optimize_for_eink, create_placeholder_artwork


# Display constants
WIDTH = 1236
HEIGHT = 1648

# Layout zones
HEADER_HEIGHT = 200
FOOTER_HEIGHT = 350
ARTWORK_ZONE_HEIGHT = HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT

# Colors (grayscale)
BLACK = 0
DARK_GRAY = 64
MEDIUM_GRAY = 128
LIGHT_GRAY = 192
WHITE = 255


class DashboardRenderer:
    """Renders the complete dashboard image."""

    def __init__(self, config_path: str = "config.yml"):
        """Initialize renderer with configuration."""
        self.config = self._load_config(config_path)
        self.fonts = self._load_fonts()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}

    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load fonts for rendering."""
        fonts = {}

        # Try to find fonts in order of preference
        font_paths = [
            # Project fonts directory
            "fonts/",
            # System fonts (Linux)
            "/usr/share/fonts/truetype/dejavu/",
            # macOS
            "/System/Library/Fonts/",
            "/Library/Fonts/",
        ]

        font_files = {
            "regular": ["DejaVuSans.ttf", "Helvetica.ttf", "Arial.ttf"],
            "bold": ["DejaVuSans-Bold.ttf", "Helvetica-Bold.ttf", "Arial Bold.ttf"],
            "mono": ["DejaVuSansMono.ttf", "Menlo.ttc", "Courier New.ttf"],
        }

        for style, filenames in font_files.items():
            font_found = False
            for path in font_paths:
                for filename in filenames:
                    full_path = os.path.join(path, filename)
                    if os.path.exists(full_path):
                        try:
                            fonts[f"{style}_large"] = ImageFont.truetype(full_path, 72)
                            fonts[f"{style}_medium"] = ImageFont.truetype(full_path, 36)
                            fonts[f"{style}_small"] = ImageFont.truetype(full_path, 24)
                            fonts[f"{style}_tiny"] = ImageFont.truetype(full_path, 18)
                            font_found = True
                            break
                        except Exception:
                            continue
                if font_found:
                    break

            if not font_found:
                # Fallback to default
                default = ImageFont.load_default()
                fonts[f"{style}_large"] = default
                fonts[f"{style}_medium"] = default
                fonts[f"{style}_small"] = default
                fonts[f"{style}_tiny"] = default

        return fonts

    def _load_reminders(self) -> List[Dict[str, Any]]:
        """Load reminders from text file."""
        reminders_config = self.config.get("reminders", {})
        if not reminders_config.get("enabled", True):
            return []

        filepath = reminders_config.get("file", "reminders.txt")
        max_items = reminders_config.get("max_items", 5)
        reminders = []

        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # Skip completed items
                    if line.startswith('[x]') or line.startswith('[X]'):
                        continue
                    # Parse priority
                    priority = "normal"
                    text = line
                    if line.startswith('[!]'):
                        priority = "high"
                        text = line[3:].strip()
                    elif line.startswith('[ ]'):
                        text = line[3:].strip()

                    reminders.append({"text": text, "priority": priority})

                    if len(reminders) >= max_items:
                        break
        except Exception as e:
            print(f"Warning: Could not load reminders: {e}")

        return reminders

    def render_header(self, draw: ImageDraw.Draw, weather: Optional[Dict]) -> None:
        """Render the header zone with time, date, and weather."""
        # Current time
        time_config = self.config.get("time", {})
        tz_name = time_config.get("timezone", "UTC")

        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(tz_name))
        except ImportError:
            now = datetime.now()

        # Format time
        if time_config.get("format_24h", False):
            time_str = now.strftime("%H:%M")
        else:
            time_str = now.strftime("%-I:%M %p")

        # Format date
        date_format = time_config.get("date_format", "short")
        if date_format == "long":
            date_str = now.strftime("%B %-d, %Y")
        elif date_format == "iso":
            date_str = now.strftime("%Y-%m-%d")
        else:
            date_str = now.strftime("%b %-d")

        # Draw time (large, left side)
        draw.text((40, 30), time_str, font=self.fonts.get("bold_large"), fill=BLACK)

        # Draw date (below time)
        draw.text((40, 110), date_str, font=self.fonts.get("regular_medium"), fill=DARK_GRAY)

        # Draw weather (right side)
        if weather:
            current = weather["current"]
            unit = weather["unit"]

            # Temperature (large)
            temp_str = f"{current['temperature']}{unit}"
            temp_bbox = draw.textbbox((0, 0), temp_str, font=self.fonts.get("bold_large"))
            temp_width = temp_bbox[2] - temp_bbox[0]
            draw.text((WIDTH - temp_width - 40, 30), temp_str, font=self.fonts.get("bold_large"), fill=BLACK)

            # Weather description
            desc_str = current['description']
            desc_bbox = draw.textbbox((0, 0), desc_str, font=self.fonts.get("regular_medium"))
            desc_width = desc_bbox[2] - desc_bbox[0]
            draw.text((WIDTH - desc_width - 40, 110), desc_str, font=self.fonts.get("regular_medium"), fill=DARK_GRAY)

            # High/Low
            if 'high' in weather and 'low' in weather:
                hl_str = f"H:{weather['high']}° L:{weather['low']}°"
                hl_bbox = draw.textbbox((0, 0), hl_str, font=self.fonts.get("regular_small"))
                hl_width = hl_bbox[2] - hl_bbox[0]
                draw.text((WIDTH - hl_width - 40, 160), hl_str, font=self.fonts.get("regular_small"), fill=MEDIUM_GRAY)

        # Draw separator line
        draw.line([(40, HEADER_HEIGHT - 10), (WIDTH - 40, HEADER_HEIGHT - 10)], fill=LIGHT_GRAY, width=2)

    def render_artwork_zone(self, base_image: Image.Image, artwork_path: Optional[str]) -> None:
        """Render artwork in the middle zone."""
        artwork_config = self.config.get("artwork", {})

        if not artwork_config.get("enabled", True) or not artwork_path:
            return

        try:
            # Optimize artwork for the zone
            temp_path = "/tmp/dashboard_artwork_optimized.png"
            zone_height = ARTWORK_ZONE_HEIGHT
            zone_width = WIDTH - 80  # margins

            if optimize_for_eink(
                artwork_path,
                temp_path,
                width=zone_width,
                height=zone_height,
                contrast_boost=1.2,
                dither=True
            ):
                artwork = Image.open(temp_path).convert('L')

                # Center in zone
                x = (WIDTH - artwork.width) // 2
                y = HEADER_HEIGHT + (zone_height - artwork.height) // 2

                base_image.paste(artwork, (x, y))
        except Exception as e:
            print(f"Warning: Could not render artwork: {e}")

    def render_footer(self, draw: ImageDraw.Draw, reminders: List[Dict]) -> None:
        """Render the footer zone with reminders."""
        footer_y = HEIGHT - FOOTER_HEIGHT

        # Draw separator line
        draw.line([(40, footer_y + 10), (WIDTH - 40, footer_y + 10)], fill=LIGHT_GRAY, width=2)

        # "Reminders" header
        draw.text((40, footer_y + 30), "Reminders", font=self.fonts.get("bold_medium"), fill=BLACK)

        # Draw reminder items
        y_offset = footer_y + 80
        for reminder in reminders:
            # Priority indicator
            if reminder["priority"] == "high":
                prefix = "● "
                color = BLACK
            else:
                prefix = "○ "
                color = DARK_GRAY

            text = prefix + reminder["text"]

            # Truncate if too long
            max_chars = 50
            if len(text) > max_chars:
                text = text[:max_chars - 3] + "..."

            draw.text((60, y_offset), text, font=self.fonts.get("regular_small"), fill=color)
            y_offset += 40

    def render(self, output_path: str = "output/dashboard.png") -> bool:
        """
        Render the complete dashboard.

        Args:
            output_path: Where to save the final PNG

        Returns:
            True if successful
        """
        print("Rendering dashboard...")

        # Create base canvas
        image = Image.new('L', (WIDTH, HEIGHT), color=WHITE)
        draw = ImageDraw.Draw(image)

        # Fetch weather
        weather = None
        weather_config = self.config.get("weather", {})
        if weather_config:
            print("  Fetching weather...")
            weather = fetch_weather(
                latitude=weather_config.get("latitude", 32.7767),
                longitude=weather_config.get("longitude", -96.7970),
                unit=weather_config.get("unit", "fahrenheit"),
                forecast_hours=weather_config.get("forecast_hours", 12)
            )

        # Select artwork
        artwork_path = None
        artwork_config = self.config.get("artwork", {})
        if artwork_config.get("enabled", True):
            print("  Selecting artwork...")
            artwork_dir = os.path.join(os.path.dirname(__file__), "..", "artwork")
            artwork_path = select_artwork(
                artwork_dir=artwork_dir,
                categories=artwork_config.get("categories"),
                state_file="/tmp/kindle_dashboard_artwork_state.txt",
                rotation_interval=artwork_config.get("rotation_interval", 6)
            )
            if artwork_path:
                print(f"    Selected: {artwork_path.name}")

        # Load reminders
        print("  Loading reminders...")
        reminders = self._load_reminders()

        # Render zones
        print("  Rendering header...")
        self.render_header(draw, weather)

        print("  Rendering artwork zone...")
        if artwork_path:
            self.render_artwork_zone(image, str(artwork_path))

        print("  Rendering footer...")
        self.render_footer(draw, reminders)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Save final image
        print(f"  Saving to {output_path}...")
        image.save(output_path, 'PNG', optimize=True)

        print("Dashboard rendered successfully!")
        return True


def main():
    """Main entry point."""
    # Change to script directory for relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(script_dir, ".."))

    # Render dashboard
    renderer = DashboardRenderer("config.yml")
    renderer.render("output/dashboard.png")


if __name__ == "__main__":
    main()
