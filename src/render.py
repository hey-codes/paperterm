"""
Main dashboard renderer for Kindle Dashboard.
Composites time, weather, calendar, and reminders into final PNG using quadrant layout.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Error: PIL/Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

import yaml

# Import our modules
from weather import fetch_weather, WEATHER_CODES
from ascii_digits import render_time
from calendar_render import render_calendar
from weather_render import render_weather_zone


# Display constants
WIDTH = 1236
HEIGHT = 1648
MARGIN = 30

# Layout zone heights (as per design doc)
TIME_ZONE_HEIGHT = 320
MIDDLE_ZONE_HEIGHT = 1048  # Weather + Calendar
REMINDERS_ZONE_HEIGHT = 220

# Layout zone widths
WEATHER_ZONE_WIDTH = 350
CALENDAR_ZONE_WIDTH = WIDTH - (2 * MARGIN) - WEATHER_ZONE_WIDTH  # 826px

# Colors (grayscale)
BLACK = 0
DARK_GRAY = 64
MEDIUM_GRAY = 128
LIGHT_GRAY = 192
WHITE = 255


class DashboardRenderer:
    """Renders the complete dashboard image with quadrant layout."""

    def _draw_ascii_border(self, draw: ImageDraw.Draw, x: int, y: int, width: int, height: int, title: str = None) -> None:
        """Draw an ASCII-style box border with optional title."""
        font = self.fonts.get("mono_16")

        # Box drawing characters
        TL, TR, BL, BR = '\u250c', '\u2510', '\u2514', '\u2518'
        H, V = '\u2500', '\u2502'
        LT, RT = '\u251c', '\u2524'

        # Calculate character dimensions
        char_bbox = draw.textbbox((0, 0), H, font=font)
        char_w = char_bbox[2] - char_bbox[0]
        char_h = char_bbox[3] - char_bbox[1]

        # Number of horizontal chars needed
        h_count = (width - 2 * char_w) // char_w

        # Top border
        top_line = TL + (H * h_count) + TR
        draw.text((x, y), top_line, font=font, fill=DARK_GRAY)

        # If title, draw title bar
        if title:
            title_y = y + char_h + 5
            title_str = f"{LT} {title} {RT}"
            # Center the title
            title_x = x + (width - len(title_str) * char_w) // 2
            draw.text((title_x, title_y), title_str, font=font, fill=BLACK)

        # Bottom border
        bottom_y = y + height - char_h
        bottom_line = BL + (H * h_count) + BR
        draw.text((x, bottom_y), bottom_line, font=font, fill=DARK_GRAY)

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
                            # Load various sizes
                            fonts[f"{style}_large"] = ImageFont.truetype(full_path, 72)
                            fonts[f"{style}_medium"] = ImageFont.truetype(full_path, 36)
                            fonts[f"{style}_small"] = ImageFont.truetype(full_path, 24)
                            fonts[f"{style}_tiny"] = ImageFont.truetype(full_path, 18)
                            # Additional sizes for specific uses
                            fonts[f"{style}_48"] = ImageFont.truetype(full_path, 48)
                            fonts[f"{style}_28"] = ImageFont.truetype(full_path, 28)
                            fonts[f"{style}_32"] = ImageFont.truetype(full_path, 32)
                            fonts[f"{style}_16"] = ImageFont.truetype(full_path, 16)
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
                fonts[f"{style}_48"] = default
                fonts[f"{style}_28"] = default
                fonts[f"{style}_32"] = default
                fonts[f"{style}_16"] = default

        return fonts

    def _load_reminders(self) -> List[Dict[str, Any]]:
        """Load reminders from text file."""
        reminders_config = self.config.get("reminders", {})
        if not reminders_config.get("enabled", True):
            return []

        filepath = reminders_config.get("file", "reminders.txt")
        max_items = reminders_config.get("max_items", 6)
        reminders = []

        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue

                    # Parse status and priority
                    status = "pending"
                    priority = "normal"
                    text = line

                    if line.startswith('[x]') or line.startswith('[X]'):
                        status = "done"
                        text = line[3:].strip()
                    elif line.startswith('[!]'):
                        priority = "high"
                        text = line[3:].strip()
                    elif line.startswith('[ ]'):
                        text = line[3:].strip()

                    reminders.append({
                        "text": text,
                        "priority": priority,
                        "status": status
                    })

                    if len(reminders) >= max_items:
                        break
        except Exception as e:
            print(f"Warning: Could not load reminders: {e}")

        return reminders

    def _get_current_time(self) -> datetime:
        """Get current time in configured timezone."""
        time_config = self.config.get("time", {})
        tz_name = time_config.get("timezone", "UTC")

        try:
            from zoneinfo import ZoneInfo
            return datetime.now(ZoneInfo(tz_name))
        except ImportError:
            return datetime.now()

    def render_time_zone(self, draw: ImageDraw.Draw, image: Image.Image) -> None:
        """
        Render the time hero zone (top section).

        Contains:
        - ASCII block digits for HH:MM
        - AM/PM indicator (48px bold)
        - Date: "Wednesday, Feb 4" (36px)
        - Refresh indicator: "circled 5min" (24px gray, bottom-right)
        """
        now = self._get_current_time()
        time_config = self.config.get("time", {})
        use_24h = time_config.get("format_24h", False)

        # Zone coordinates
        zone_x = MARGIN
        zone_y = MARGIN
        zone_width = WIDTH - (2 * MARGIN)
        zone_height = TIME_ZONE_HEIGHT

        # Render ASCII digits for time
        # Center the time display vertically and position left-of-center
        digits_y = zone_y + 60  # Positioned toward top of zone

        # Render time using ascii_digits module
        total_width, am_pm = render_time(
            draw=draw,
            hour=now.hour,
            minute=now.minute,
            x=zone_x + 50,
            y=digits_y,
            twelve_hour=not use_24h,
            fill=BLACK
        )

        # Draw AM/PM indicator (48px bold, to the right of digits)
        if am_pm:
            am_pm_x = zone_x + 50 + total_width + 30
            am_pm_y = digits_y + 30  # Vertically centered with digits
            draw.text(
                (am_pm_x, am_pm_y),
                am_pm,
                font=self.fonts.get("bold_48"),
                fill=BLACK
            )

        # Draw date: "Wednesday, Feb 4" (36px, to right of AM/PM)
        date_str = now.strftime("%A, %b %-d")
        date_x = zone_x + 50 + total_width + 150  # Right of AM/PM
        date_y = digits_y + 35
        draw.text(
            (date_x, date_y),
            date_str,
            font=self.fonts.get("regular_medium"),
            fill=DARK_GRAY
        )

        # Draw refresh indicator (bottom-right of time zone)
        refresh_rate = self.config.get("refresh_rate", 5)
        refresh_str = f"\u21bb {refresh_rate}min"
        refresh_font = self.fonts.get("regular_small")

        # Calculate position for bottom-right
        refresh_bbox = draw.textbbox((0, 0), refresh_str, font=refresh_font)
        refresh_width = refresh_bbox[2] - refresh_bbox[0]
        refresh_x = zone_x + zone_width - refresh_width - 20
        refresh_y = zone_y + zone_height - 50
        draw.text(
            (refresh_x, refresh_y),
            refresh_str,
            font=refresh_font,
            fill=MEDIUM_GRAY
        )

    def render_weather_zone_wrapper(self, draw: ImageDraw.Draw, weather: Optional[Dict]) -> None:
        """
        Render the weather zone (left middle section).

        Uses the weather_render module to display:
        - ASCII weather icon
        - Temperature
        - Condition
        - High/Low
        """
        # Zone coordinates
        zone_x = MARGIN
        zone_y = MARGIN + TIME_ZONE_HEIGHT
        zone_width = WEATHER_ZONE_WIDTH
        zone_height = MIDDLE_ZONE_HEIGHT

        if not weather:
            # Draw placeholder if no weather data
            draw.text(
                (zone_x + 50, zone_y + zone_height // 2),
                "Weather\nunavailable",
                font=self.fonts.get("regular_medium"),
                fill=MEDIUM_GRAY
            )
            return

        # Prepare fonts dict for weather_render module
        weather_fonts = {
            'large': self.fonts.get("bold_large"),
            'medium': self.fonts.get("regular_medium"),
            'small': self.fonts.get("regular_small"),
            'mono': self.fonts.get("mono_16"),
        }

        # Get weather data
        current = weather["current"]
        unit = weather["unit"]
        high = weather.get("high", current["temperature"])
        low = weather.get("low", current["temperature"])

        # Get city from config
        city = self.config.get("weather", {}).get("city", "")

        # Get additional weather data
        sunrise = weather.get("sunrise")
        sunset = weather.get("sunset")
        wind_speed = weather.get("wind_speed_max")
        precip_chance = weather.get("precip_chance")

        # Call weather_render module
        render_weather_zone(
            draw=draw,
            x=zone_x,
            y=zone_y,
            width=zone_width,
            height=zone_height,
            temperature=current["temperature"],
            unit=unit,
            condition=current["description"],
            high=high,
            low=low,
            fonts=weather_fonts,
            city=city,
            sunrise=sunrise,
            sunset=sunset,
            wind_speed=wind_speed,
            precip_chance=precip_chance
        )

    def render_calendar_zone(self, draw: ImageDraw.Draw, image: Image.Image) -> None:
        """
        Render the calendar zone (right middle section).

        Uses the calendar_render module to display:
        - Full month grid
        - Inverted cursor on today
        """
        now = self._get_current_time()

        # Zone coordinates (right of weather zone)
        zone_x = MARGIN + WEATHER_ZONE_WIDTH
        zone_y = MARGIN + TIME_ZONE_HEIGHT
        zone_width = CALENDAR_ZONE_WIDTH
        zone_height = MIDDLE_ZONE_HEIGHT

        # Prepare fonts for calendar
        font_header = self.fonts.get("mono_28")
        font_days = self.fonts.get("mono_32")

        # Call calendar_render module
        render_calendar(
            draw=draw,
            image=image,
            x=zone_x,
            y=zone_y,
            width=zone_width,
            height=zone_height,
            year=now.year,
            month=now.month,
            today=now.day,
            font_header=font_header,
            font_days=font_days,
            fill=BLACK,
            bg=WHITE
        )

    def render_reminders_zone(self, draw: ImageDraw.Draw, reminders: List[Dict]) -> None:
        """
        Render the reminders zone (bottom section).

        Two-column layout:
        - Left column: x=30, width=558
        - Right column: x=618, width=558
        - Max 3 items per column
        - Timestamp bottom-right
        """
        now = self._get_current_time()

        # Zone coordinates
        zone_x = MARGIN
        zone_y = MARGIN + TIME_ZONE_HEIGHT + MIDDLE_ZONE_HEIGHT
        zone_width = WIDTH - (2 * MARGIN)
        zone_height = REMINDERS_ZONE_HEIGHT

        # Column specifications
        left_col_x = MARGIN + 20  # Offset from border
        right_col_x = MARGIN + 588  # ~618 from left edge
        col_width = 558
        max_per_column = 3

        # Draw ASCII border around reminders zone with title
        self._draw_ascii_border(draw, zone_x, zone_y, zone_width, zone_height, title="REMINDERS")

        # Font for reminders
        reminder_font = self.fonts.get("mono_28")
        line_height = 50

        # Split reminders into two columns
        left_reminders = reminders[:max_per_column]
        right_reminders = reminders[max_per_column:max_per_column * 2]

        # Starting y position for items (offset for border and title)
        items_y = zone_y + 45

        # Render left column
        for i, reminder in enumerate(left_reminders):
            y_pos = items_y + (i * line_height)

            # Determine checkbox style
            if reminder["status"] == "done":
                prefix = "[x]"
            elif reminder["priority"] == "high":
                prefix = "[!]"
            else:
                prefix = "[ ]"

            text = f"{prefix} {reminder['text']}"

            # Truncate if too long
            max_chars = 35
            if len(text) > max_chars:
                text = text[:max_chars - 3] + "..."

            # Choose color based on status/priority
            if reminder["status"] == "done":
                color = MEDIUM_GRAY
            elif reminder["priority"] == "high":
                color = BLACK
            else:
                color = DARK_GRAY

            draw.text((left_col_x, y_pos), text, font=reminder_font, fill=color)

        # Render right column
        for i, reminder in enumerate(right_reminders):
            y_pos = items_y + (i * line_height)

            # Determine checkbox style
            if reminder["status"] == "done":
                prefix = "[x]"
            elif reminder["priority"] == "high":
                prefix = "[!]"
            else:
                prefix = "[ ]"

            text = f"{prefix} {reminder['text']}"

            # Truncate if too long
            max_chars = 35
            if len(text) > max_chars:
                text = text[:max_chars - 3] + "..."

            # Choose color based on status/priority
            if reminder["status"] == "done":
                color = MEDIUM_GRAY
            elif reminder["priority"] == "high":
                color = BLACK
            else:
                color = DARK_GRAY

            draw.text((right_col_x, y_pos), text, font=reminder_font, fill=color)

        # If no reminders, show placeholder
        if not reminders:
            placeholder_text = "[ ] No reminders set"
            draw.text(
                (left_col_x, items_y),
                placeholder_text,
                font=reminder_font,
                fill=MEDIUM_GRAY
            )

        # Draw timestamp (bottom-right of zone)
        timestamp_str = now.strftime("%H:%M")
        timestamp_font = self.fonts.get("mono_tiny")
        ts_bbox = draw.textbbox((0, 0), timestamp_str, font=timestamp_font)
        ts_width = ts_bbox[2] - ts_bbox[0]
        ts_x = WIDTH - MARGIN - ts_width - 10
        ts_y = zone_y + zone_height - 40
        draw.text((ts_x, ts_y), timestamp_str, font=timestamp_font, fill=LIGHT_GRAY)

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

        # Load reminders
        print("  Loading reminders...")
        reminders = self._load_reminders()

        # Render zones
        print("  Rendering time zone...")
        self.render_time_zone(draw, image)

        print("  Rendering weather zone...")
        self.render_weather_zone_wrapper(draw, weather)

        print("  Rendering calendar zone...")
        self.render_calendar_zone(draw, image)

        print("  Rendering reminders zone...")
        self.render_reminders_zone(draw, reminders)

        # Draw exit indicator
        exit_text = "[ TAP HERE TO EXIT ]"
        exit_font = self.fonts.get("mono_tiny")
        exit_bbox = draw.textbbox((0, 0), exit_text, font=exit_font)
        exit_width = exit_bbox[2] - exit_bbox[0]
        exit_x = WIDTH - exit_width - 20
        exit_y = HEIGHT - 30
        draw.text((exit_x, exit_y), exit_text, font=exit_font, fill=MEDIUM_GRAY)

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
