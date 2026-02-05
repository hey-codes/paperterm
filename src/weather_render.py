"""
Weather rendering module with ASCII art icons.

Renders weather information in a 350px wide vertical zone with:
- ASCII weather icon at top
- Large temperature display (72px)
- Description text (36px)
- High/Low temps (24px, gray)
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Optional


# ASCII art weather icons
WEATHER_ICONS = {
    "clear": '''
   \\   /
    .-.
 ― (   ) ―
    `-'
   /   \\
''',
    "partly_cloudy": '''
   \\  /
 _ /"".-.
   \\_(   ).
   /(___(__)
''',
    "cloudy": '''
     .--.
  .-(    ).
 (___.__)__)
''',
    "rain": '''
     .-.
    (   ).
   (___(__)
    ʻ ʻ ʻ ʻ
   ʻ ʻ ʻ ʻ
''',
    "snow": '''
     .-.
    (   ).
   (___(__)
    * * * *
   * * * *
''',
    "thunderstorm": '''
     .-.
    (   ).
   (___(__)
   ⚡ʻ ⚡ʻ
''',
    "fog": '''
 _ - _ - _ -
  _ - _ - _
 _ - _ - _ -
'''
}


# Mapping of weather condition keywords to icon keys
CONDITION_MAPPINGS = {
    # Clear conditions
    "clear": "clear",
    "sunny": "clear",
    "fair": "clear",

    # Partly cloudy
    "partly cloudy": "partly_cloudy",
    "partly sunny": "partly_cloudy",
    "mostly sunny": "partly_cloudy",
    "mostly clear": "partly_cloudy",
    "mainly clear": "partly_cloudy",

    # Cloudy conditions
    "cloudy": "cloudy",
    "overcast": "cloudy",
    "mostly cloudy": "cloudy",

    # Rain conditions
    "rain": "rain",
    "rainy": "rain",
    "drizzle": "rain",
    "showers": "rain",
    "light rain": "rain",
    "heavy rain": "rain",
    "moderate rain": "rain",

    # Snow conditions
    "snow": "snow",
    "snowy": "snow",
    "flurries": "snow",
    "light snow": "snow",
    "heavy snow": "snow",
    "sleet": "snow",
    "ice": "snow",

    # Thunderstorm conditions
    "thunderstorm": "thunderstorm",
    "thunder": "thunderstorm",
    "lightning": "thunderstorm",
    "storm": "thunderstorm",

    # Fog conditions
    "fog": "fog",
    "foggy": "fog",
    "mist": "fog",
    "misty": "fog",
    "haze": "fog",
    "hazy": "fog",
}


def get_weather_icon(condition: str) -> str:
    """
    Map weather condition string to icon key.

    Args:
        condition: Weather description from API (e.g., "Mainly Clear", "Light rain")

    Returns:
        Icon key string (e.g., "clear", "rain", "cloudy")
    """
    if not condition:
        return "clear"

    condition_lower = condition.lower().strip()

    # Check for exact match first
    if condition_lower in CONDITION_MAPPINGS:
        return CONDITION_MAPPINGS[condition_lower]

    # Check for partial matches (keyword in condition)
    for keyword, icon_key in CONDITION_MAPPINGS.items():
        if keyword in condition_lower:
            return icon_key

    # Default to cloudy if no match found
    return "cloudy"


def _get_icon_text(icon_key: str) -> str:
    """
    Get the ASCII art text for an icon key.

    Args:
        icon_key: Key into WEATHER_ICONS dict

    Returns:
        ASCII art string, stripped of leading/trailing whitespace
    """
    return WEATHER_ICONS.get(icon_key, WEATHER_ICONS["cloudy"]).strip()


def _center_text(draw: ImageDraw, text: str, x: int, width: int,
                 y: int, font: ImageFont, fill: str = "black") -> int:
    """
    Draw centered text and return the y position after the text.

    Args:
        draw: PIL ImageDraw object
        text: Text to draw
        x: Left edge of zone
        width: Width of zone
        y: Y position to draw at
        font: Font to use
        fill: Text color

    Returns:
        Y position after the drawn text
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = x + (width - text_width) // 2
    draw.text((text_x, y), text, font=font, fill=fill)

    return y + text_height


def _draw_multiline_centered(draw: ImageDraw, text: str, x: int, width: int,
                             y: int, font: ImageFont, fill: str = "black") -> int:
    """
    Draw multiline text with each line centered.

    Args:
        draw: PIL ImageDraw object
        text: Multiline text to draw
        x: Left edge of zone
        width: Width of zone
        y: Starting Y position
        font: Font to use
        fill: Text color

    Returns:
        Y position after all lines
    """
    lines = text.split('\n')
    current_y = y

    for line in lines:
        if line:  # Only draw non-empty lines
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]

            text_x = x + (width - text_width) // 2
            draw.text((text_x, current_y), line, font=font, fill=fill)
            current_y += line_height + 2  # Small line spacing
        else:
            # Empty line - add some spacing
            current_y += 10

    return current_y


def render_weather_zone(draw: ImageDraw, x: int, y: int,
                        width: int, height: int,
                        temperature: int, unit: str,
                        condition: str, high: int, low: int,
                        fonts: dict, city: Optional[str] = None) -> None:
    """
    Render weather display with ASCII icon and box border.

    Renders a vertically centered weather display containing:
    - ASCII-style box border
    - City name header (if provided)
    - ASCII art weather icon
    - Large temperature display
    - Weather condition description
    - High/Low temperature line

    Args:
        draw: PIL ImageDraw object
        x: X coordinate of top-left of zone
        y: Y coordinate of top-left of zone
        width: Width of zone (typically 350px)
        height: Height of zone
        temperature: Current temperature value
        unit: Temperature unit ("°F" or "°C")
        condition: Weather description from API (e.g., "Mainly Clear")
        high: Daily high temperature
        low: Daily low temperature
        fonts: Dict with font keys:
            - 'large': For temperature (72px)
            - 'medium': For condition text (36px)
            - 'small': For high/low (24px)
            - 'mono': For ASCII art icon
        city: Optional city name to display at top
    """
    # Get the icon for this condition
    icon_key = get_weather_icon(condition)
    icon_text = _get_icon_text(icon_key)

    # Get fonts with fallbacks
    font_large = fonts.get('large')
    font_medium = fonts.get('medium')
    font_small = fonts.get('small')
    font_mono = fonts.get('mono')

    # Box drawing characters
    BOX_TOP_LEFT = "\u250c"      # ┌
    BOX_TOP_RIGHT = "\u2510"     # ┐
    BOX_BOTTOM_LEFT = "\u2514"   # └
    BOX_BOTTOM_RIGHT = "\u2518"  # ┘
    BOX_HORIZONTAL = "\u2500"    # ─
    BOX_VERTICAL = "\u2502"      # │
    BOX_T_LEFT = "\u251c"        # ├
    BOX_T_RIGHT = "\u2524"       # ┤

    # Box dimensions and padding
    box_padding = 20
    box_x = x + box_padding
    box_width = width - (2 * box_padding)

    # Calculate content heights
    # City header height
    city_height = 0
    if city and font_medium:
        city_bbox = draw.textbbox((0, 0), city.upper(), font=font_medium)
        city_height = city_bbox[3] - city_bbox[1] + 20  # Extra padding for separator

    # Icon height
    icon_lines = icon_text.split('\n')
    if font_mono:
        icon_bbox = draw.textbbox((0, 0), icon_text, font=font_mono)
        icon_height = icon_bbox[3] - icon_bbox[1]
    else:
        icon_height = len(icon_lines) * 16  # Estimate

    # Temperature text
    temp_text = f"{temperature}{unit}"
    if font_large:
        temp_bbox = draw.textbbox((0, 0), temp_text, font=font_large)
        temp_height = temp_bbox[3] - temp_bbox[1]
    else:
        temp_height = 72

    # Condition text height
    if font_medium:
        cond_bbox = draw.textbbox((0, 0), condition, font=font_medium)
        cond_height = cond_bbox[3] - cond_bbox[1]
    else:
        cond_height = 36

    # High/Low text
    highlow_text = f"H:{high}{unit} L:{low}{unit}"
    if font_small:
        hl_bbox = draw.textbbox((0, 0), highlow_text, font=font_small)
        hl_height = hl_bbox[3] - hl_bbox[1]
    else:
        hl_height = 24

    # Spacing between elements
    spacing = 20
    box_inner_padding = 15

    # Total content height (inside box)
    content_height = city_height + icon_height + spacing + temp_height + spacing + cond_height + spacing + hl_height + (2 * box_inner_padding)

    # Calculate box Y position to center in zone
    box_y = y + (height - content_height) // 2
    box_height = content_height

    # Draw box border using mono font
    if font_mono:
        # Calculate how many horizontal chars fit
        char_bbox = draw.textbbox((0, 0), BOX_HORIZONTAL, font=font_mono)
        char_width = char_bbox[2] - char_bbox[0]
        num_chars = (box_width - 2 * char_width) // char_width

        # Top border
        top_border = BOX_TOP_LEFT + (BOX_HORIZONTAL * num_chars) + BOX_TOP_RIGHT
        draw.text((box_x, box_y), top_border, font=font_mono, fill="black")

        # Get border line height
        border_height = char_bbox[3] - char_bbox[1]
        current_y = box_y + border_height + 5

        # Draw city name if provided
        if city:
            # Draw left vertical bar
            draw.text((box_x, current_y), BOX_VERTICAL, font=font_mono, fill="black")
            # Draw right vertical bar
            draw.text((box_x + box_width - char_width, current_y), BOX_VERTICAL, font=font_mono, fill="black")

            # Draw centered city name
            city_text = city.upper()
            if font_medium:
                _center_text(draw, city_text, box_x + char_width, box_width - 2 * char_width,
                            current_y, font_medium, fill="black")
                city_bbox = draw.textbbox((0, 0), city_text, font=font_medium)
                current_y += city_bbox[3] - city_bbox[1] + 10

            # Draw separator line
            separator = BOX_T_LEFT + (BOX_HORIZONTAL * num_chars) + BOX_T_RIGHT
            draw.text((box_x, current_y), separator, font=font_mono, fill="black")
            current_y += border_height + 10

        # Content area - draw vertical bars on sides for each content line
        content_start_y = current_y
        content_end_y = box_y + box_height - border_height - 5

        # Draw left and right vertical bars for content area
        # We'll draw them at intervals
        bar_y = content_start_y
        while bar_y < content_end_y:
            draw.text((box_x, bar_y), BOX_VERTICAL, font=font_mono, fill="black")
            draw.text((box_x + box_width - char_width, bar_y), BOX_VERTICAL, font=font_mono, fill="black")
            bar_y += border_height + 2

        # Inner content area boundaries
        inner_x = box_x + char_width + 5
        inner_width = box_width - 2 * char_width - 10

        current_y = content_start_y + box_inner_padding

        # Draw ASCII icon (centered in inner area)
        current_y = _draw_multiline_centered(draw, icon_text, inner_x, inner_width,
                                             current_y, font_mono, fill="black")
        current_y += spacing

        # Draw temperature (large, centered)
        if font_large:
            current_y = _center_text(draw, temp_text, inner_x, inner_width, current_y,
                                     font_large, fill="black")
        else:
            draw.text((inner_x + inner_width // 2 - 50, current_y), temp_text, fill="black")
            current_y += temp_height
        current_y += spacing

        # Draw condition description (medium, centered)
        if font_medium:
            current_y = _center_text(draw, condition, inner_x, inner_width, current_y,
                                     font_medium, fill="black")
        else:
            draw.text((inner_x + inner_width // 2 - 60, current_y), condition, fill="black")
            current_y += cond_height
        current_y += spacing

        # Draw high/low (small, gray, centered)
        if font_small:
            _center_text(draw, highlow_text, inner_x, inner_width, current_y,
                         font_small, fill="gray")
        else:
            draw.text((inner_x + inner_width // 2 - 50, current_y), highlow_text, fill="gray")

        # Bottom border
        bottom_border = BOX_BOTTOM_LEFT + (BOX_HORIZONTAL * num_chars) + BOX_BOTTOM_RIGHT
        draw.text((box_x, box_y + box_height - border_height), bottom_border, font=font_mono, fill="black")

    else:
        # Fallback without mono font - just draw content without border
        current_y = y + (height - content_height) // 2

        # Draw ASCII icon
        for line in icon_lines:
            if line:
                draw.text((x + 100, current_y), line, fill="black")
                current_y += 16
        current_y += spacing

        # Draw temperature
        draw.text((x + width // 2 - 50, current_y), temp_text, fill="black")
        current_y += temp_height + spacing

        # Draw condition
        draw.text((x + width // 2 - 60, current_y), condition, fill="black")
        current_y += cond_height + spacing

        # Draw high/low
        draw.text((x + width // 2 - 50, current_y), highlow_text, fill="gray")


if __name__ == "__main__":
    """Test the weather rendering module."""

    # Create a test image
    img_width = 400
    img_height = 600
    image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(image)

    # Try to load fonts, fall back to default if not available
    fonts = {}

    try:
        # Try to load system fonts
        fonts['large'] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        fonts['medium'] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        fonts['small'] = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        fonts['mono'] = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    except (OSError, IOError):
        try:
            # Try DejaVu fonts (common on Linux)
            fonts['large'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 72)
            fonts['medium'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            fonts['small'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            fonts['mono'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
        except (OSError, IOError):
            # Fall back to default font
            print("Warning: Could not load TrueType fonts, using default")
            default_font = ImageFont.load_default()
            fonts['large'] = default_font
            fonts['medium'] = default_font
            fonts['small'] = default_font
            fonts['mono'] = default_font

    # Test zone dimensions
    zone_x = 25
    zone_y = 20
    zone_width = 350
    zone_height = 560

    # Draw zone boundary for visualization
    draw.rectangle([zone_x, zone_y, zone_x + zone_width, zone_y + zone_height],
                   outline="lightgray", width=1)

    # Render weather
    render_weather_zone(
        draw=draw,
        x=zone_x,
        y=zone_y,
        width=zone_width,
        height=zone_height,
        temperature=19,
        unit="°F",
        condition="Mainly Clear",
        high=21,
        low=16,
        fonts=fonts
    )

    # Save test image
    output_path = "/Users/cody-mbp/Codex/Projects/kindle-jail-break/paperterm/src/weather_test.png"
    image.save(output_path)
    print(f"Test image saved to: {output_path}")

    # Test condition mapping
    print("\nCondition mapping tests:")
    test_conditions = [
        "Clear",
        "Mainly Clear",
        "Partly cloudy",
        "Overcast",
        "Light rain",
        "Heavy snow",
        "Thunderstorm",
        "Foggy",
        "Unknown condition"
    ]

    for cond in test_conditions:
        icon = get_weather_icon(cond)
        print(f"  '{cond}' -> '{icon}'")
