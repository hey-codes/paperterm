"""
Calendar rendering module for terminal-style display.

Renders a full month calendar with box-drawing borders and an inverted
cursor highlighting the current date (white text on black background).
"""

import calendar
from datetime import datetime
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


def get_month_grid(year: int, month: int) -> list[list[Optional[int]]]:
    """
    Return a 6x7 grid of day numbers for the given month.

    Each row represents a week (Sunday to Saturday).
    Empty cells are represented as None.

    Args:
        year: The year (e.g., 2026)
        month: The month (1-12)

    Returns:
        A 6x7 grid where each cell is either a day number (1-31) or None
    """
    # Get the first day of the month (0=Monday, 6=Sunday in calendar module)
    # and the number of days in the month
    cal = calendar.Calendar(firstweekday=6)  # Start weeks on Sunday

    # Get all days in the month, including leading/trailing days from other months
    month_days = cal.monthdayscalendar(year, month)

    # Convert zeros to None and ensure we have exactly 6 rows
    grid: list[list[Optional[int]]] = []
    for week in month_days:
        row: list[Optional[int]] = []
        for day in week:
            row.append(day if day != 0 else None)
        grid.append(row)

    # Pad to 6 rows if needed
    while len(grid) < 6:
        grid.append([None] * 7)

    return grid


def render_calendar(
    draw: ImageDraw.ImageDraw,
    image: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    year: int,
    month: int,
    today: int,
    font_header: ImageFont.FreeTypeFont,
    font_days: ImageFont.FreeTypeFont,
    fill: int = 0,
    bg: int = 255
) -> None:
    """
    Render a full month calendar with cursor on today.

    Draws a terminal-style calendar with box-drawing borders, centered
    month/year header, day-of-week headers, and an inverted cursor
    (white text on black rectangle) highlighting the specified day.

    Args:
        draw: PIL ImageDraw object for drawing
        image: PIL Image (needed for cursor rectangle operations)
        x: Left edge x-coordinate
        y: Top edge y-coordinate
        width: Total width of calendar bounding box
        height: Total height of calendar bounding box
        year: Year to display (e.g., 2026)
        month: Month to display (1-12)
        today: Day number to highlight with inverted cursor (1-31)
        font_header: Font for month name and day-of-week headers
        font_days: Font for day numbers
        fill: Text/border color (default 0 = black)
        bg: Background color (default 255 = white)
    """
    # Box-drawing characters (double-line for outer border, single for inner)
    # Double-line characters for outer border
    D_TOP_LEFT = "\u2554"     # ╔
    D_TOP_RIGHT = "\u2557"    # ╗
    D_BOTTOM_LEFT = "\u255a"  # ╚
    D_BOTTOM_RIGHT = "\u255d" # ╝
    D_HORIZONTAL = "\u2550"   # ═
    D_VERTICAL = "\u2551"     # ║
    D_T_RIGHT = "\u2560"      # ╠
    D_T_LEFT = "\u2563"       # ╣

    # Single-line characters (for internal separators if needed)
    TOP_LEFT = "\u250c"
    TOP_RIGHT = "\u2510"
    BOTTOM_LEFT = "\u2514"
    BOTTOM_RIGHT = "\u2518"
    HORIZONTAL = "\u2500"
    VERTICAL = "\u2502"
    T_DOWN = "\u252c"
    T_UP = "\u2534"
    T_RIGHT = "\u251c"
    T_LEFT = "\u2524"

    # Layout constants
    col_width = width // 7  # ~118px per column
    header_height = 50  # Height for month/year header
    dow_height = 40  # Height for day-of-week row
    border_thickness = 3  # Thicker border for visibility
    cursor_padding = 8

    # Calculate row height for day grid (6 rows of days)
    grid_top = y + header_height + dow_height
    remaining_height = height - header_height - dow_height
    row_height = remaining_height // 6

    # Day of week labels
    dow_labels = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

    # Get month name
    month_name = calendar.month_name[month].upper()
    header_text = f"{month_name} {year}"

    # Draw outer border using PIL lines for reliability, then overlay corner characters
    # Calculate character dimensions for corner characters
    char_bbox = draw.textbbox((0, 0), D_HORIZONTAL, font=font_header)
    char_w = char_bbox[2] - char_bbox[0]
    char_h = char_bbox[3] - char_bbox[1]

    # Border line thickness (double-line style = 3 pixels)
    border_line_width = 3

    # Calculate the rectangle coordinates (inset slightly for the lines)
    # The border should be drawn at half the line width inset to align with corners
    border_x1 = x + char_w // 2
    border_y1 = y + char_h // 2
    border_x2 = x + width - char_w // 2
    border_y2 = y + height - char_h // 2

    # Draw the rectangle border using lines
    # Top line
    draw.line([(border_x1, border_y1), (border_x2, border_y1)], fill=fill, width=border_line_width)
    # Bottom line
    draw.line([(border_x1, border_y2), (border_x2, border_y2)], fill=fill, width=border_line_width)
    # Left line
    draw.line([(border_x1, border_y1), (border_x1, border_y2)], fill=fill, width=border_line_width)
    # Right line
    draw.line([(border_x2, border_y1), (border_x2, border_y2)], fill=fill, width=border_line_width)

    # Overlay corner characters for the box-drawing aesthetic
    # Top-left corner
    draw.text((x, y), D_TOP_LEFT, font=font_header, fill=fill)
    # Top-right corner
    draw.text((x + width - char_w, y), D_TOP_RIGHT, font=font_header, fill=fill)
    # Bottom-left corner
    draw.text((x, y + height - char_h), D_BOTTOM_LEFT, font=font_header, fill=fill)
    # Bottom-right corner
    draw.text((x + width - char_w, y + height - char_h), D_BOTTOM_RIGHT, font=font_header, fill=fill)

    # Draw header separator line (thicker)
    header_sep_y = y + header_height
    draw.line([(x, header_sep_y), (x + width, header_sep_y)], fill=fill, width=border_thickness)

    # Draw styled "CALENDAR" header with decorative elements
    calendar_label = f"{D_T_RIGHT} {month_name} {year} {D_T_LEFT}"
    header_bbox = draw.textbbox((0, 0), calendar_label, font=font_header)
    header_text_width = header_bbox[2] - header_bbox[0]
    header_text_height = header_bbox[3] - header_bbox[1]
    header_x = x + (width - header_text_width) // 2
    header_y = y + (header_height - header_text_height) // 2 + char_h // 2
    draw.text((header_x, header_y), calendar_label, font=font_header, fill=fill)

    # Draw day-of-week headers
    for i, dow in enumerate(dow_labels):
        dow_bbox = draw.textbbox((0, 0), dow, font=font_header)
        dow_text_width = dow_bbox[2] - dow_bbox[0]
        dow_text_height = dow_bbox[3] - dow_bbox[1]
        col_center_x = x + i * col_width + col_width // 2
        dow_x = col_center_x - dow_text_width // 2
        dow_y = header_sep_y + (dow_height - dow_text_height) // 2
        draw.text((dow_x, dow_y), dow, font=font_header, fill=fill)

    # Get the month grid
    grid = get_month_grid(year, month)

    # Draw day numbers
    for row_idx, week in enumerate(grid):
        for col_idx, day in enumerate(week):
            if day is None:
                continue

            # Calculate cell center
            cell_x = x + col_idx * col_width + col_width // 2
            cell_y = grid_top + row_idx * row_height + row_height // 2

            # Get text dimensions
            day_text = str(day)
            day_bbox = draw.textbbox((0, 0), day_text, font=font_days)
            day_text_width = day_bbox[2] - day_bbox[0]
            day_text_height = day_bbox[3] - day_bbox[1]

            # Text position (centered in cell)
            text_x = cell_x - day_text_width // 2
            text_y = cell_y - day_text_height // 2

            if day == today:
                # Draw inverted cursor (black rectangle with white text)
                rect_x1 = text_x - cursor_padding
                rect_y1 = text_y - cursor_padding
                rect_x2 = text_x + day_text_width + cursor_padding
                rect_y2 = text_y + day_text_height + cursor_padding

                # Draw filled black rectangle
                draw.rectangle(
                    [(rect_x1, rect_y1), (rect_x2, rect_y2)],
                    fill=fill  # Black fill
                )

                # Draw white text on top
                draw.text((text_x, text_y), day_text, font=font_days, fill=bg)
            else:
                # Normal day - black text
                draw.text((text_x, text_y), day_text, font=font_days, fill=fill)


if __name__ == "__main__":
    # Test: render current month calendar
    from pathlib import Path

    # Image dimensions
    IMG_WIDTH = 826
    IMG_HEIGHT = 700

    # Create white image
    img = Image.new("L", (IMG_WIDTH, IMG_HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # Try to load fonts, fall back to default if not available
    try:
        # Try common system font paths
        font_paths = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        ]
        font_header = None
        font_days = None

        for font_path in font_paths:
            if Path(font_path).exists():
                font_header = ImageFont.truetype(font_path, 28)
                font_days = ImageFont.truetype(font_path, 32)
                print(f"Using font: {font_path}")
                break

        if font_header is None:
            print("No system fonts found, using default font")
            font_header = ImageFont.load_default()
            font_days = ImageFont.load_default()

    except Exception as e:
        print(f"Font loading error: {e}, using default font")
        font_header = ImageFont.load_default()
        font_days = ImageFont.load_default()

    # Get current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day

    # Render calendar with some padding
    padding = 20
    render_calendar(
        draw=draw,
        image=img,
        x=padding,
        y=padding,
        width=IMG_WIDTH - 2 * padding,
        height=IMG_HEIGHT - 2 * padding,
        year=current_year,
        month=current_month,
        today=current_day,
        font_header=font_header,
        font_days=font_days,
        fill=0,
        bg=255
    )

    # Save test image
    output_path = Path(__file__).parent.parent / "test_calendar.png"
    img.save(output_path)
    print(f"Test calendar saved to: {output_path}")
    print(f"Rendered: {calendar.month_name[current_month]} {current_year}, today={current_day}")
