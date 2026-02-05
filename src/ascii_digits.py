"""
ASCII Block Digits Renderer for E-Ink Display

This module renders time as large ASCII block digits suitable for e-ink displays.
Each digit is rendered on a 5x7 grid pattern, scaled to 80x100 pixels.
"""

from PIL import Image, ImageDraw

# Digit dimensions
DIGIT_WIDTH = 80      # Total width of each digit in pixels
DIGIT_HEIGHT = 100    # Total height of each digit in pixels
GRID_COLS = 5         # Number of columns in the digit grid
GRID_ROWS = 7         # Number of rows in the digit grid
CELL_WIDTH = 16       # Width of each grid cell (80 / 5 = 16)
CELL_HEIGHT = 14      # Height of each grid cell (100 / 7 ≈ 14)
DIGIT_GAP = 20        # Gap between digits in pixels
COLON_WIDTH = 20      # Width of the colon separator

# Digit patterns: 5 columns × 7 rows grid (1=filled, 0=empty)
DIGIT_PATTERNS = {
    '0': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '1': [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
    ],
    '2': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
    ],
    '3': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '4': [
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
    ],
    '5': [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0],
    ],
    '6': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '7': [
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
    ],
    '8': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
    '9': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
    ],
}


def render_digit(draw: ImageDraw.ImageDraw, digit: str, x: int, y: int, fill: int = 0) -> int:
    """
    Render a single ASCII block digit at the specified position.

    Args:
        draw: PIL ImageDraw object to render onto
        digit: Single digit character ('0'-'9')
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner
        fill: Grayscale fill color (0=black, 255=white)

    Returns:
        Width consumed by the digit in pixels
    """
    if digit not in DIGIT_PATTERNS:
        raise ValueError(f"Invalid digit: {digit}. Must be '0'-'9'.")

    pattern = DIGIT_PATTERNS[digit]

    for row_idx, row in enumerate(pattern):
        for col_idx, cell in enumerate(row):
            if cell == 1:
                # Calculate cell position
                cell_x = x + (col_idx * CELL_WIDTH)
                cell_y = y + (row_idx * CELL_HEIGHT)

                # Draw filled rectangle for this cell
                draw.rectangle(
                    [cell_x, cell_y, cell_x + CELL_WIDTH - 1, cell_y + CELL_HEIGHT - 1],
                    fill=fill
                )

    return DIGIT_WIDTH


def render_colon(draw: ImageDraw.ImageDraw, x: int, y: int, fill: int = 0) -> int:
    """
    Render a colon separator at the specified position.

    The colon consists of two square dots positioned at rows 2 and 5
    of the 7-row grid, centered within the 20px wide colon area.

    Args:
        draw: PIL ImageDraw object to render onto
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner
        fill: Grayscale fill color (0=black, 255=white)

    Returns:
        Width consumed by the colon in pixels
    """
    # Dot size (square dots)
    dot_size = CELL_HEIGHT

    # Center the dots horizontally within the colon width
    dot_x = x + (COLON_WIDTH - dot_size) // 2

    # Position dots at row 2 (index 1) and row 5 (index 4) of the 7-row grid
    top_dot_y = y + (1 * CELL_HEIGHT) + (CELL_HEIGHT - dot_size) // 2
    bottom_dot_y = y + (4 * CELL_HEIGHT) + (CELL_HEIGHT - dot_size) // 2

    # Draw top dot
    draw.rectangle(
        [dot_x, top_dot_y, dot_x + dot_size - 1, top_dot_y + dot_size - 1],
        fill=fill
    )

    # Draw bottom dot
    draw.rectangle(
        [dot_x, bottom_dot_y, dot_x + dot_size - 1, bottom_dot_y + dot_size - 1],
        fill=fill
    )

    return COLON_WIDTH


def render_time(
    draw: ImageDraw.ImageDraw,
    hour: int,
    minute: int,
    x: int,
    y: int,
    twelve_hour: bool = True,
    fill: int = 0
) -> tuple[int, str]:
    """
    Render a full time display as ASCII block digits.

    Renders the time in format "HH:MM" with optional 12-hour conversion.

    Args:
        draw: PIL ImageDraw object to render onto
        hour: Hour value (0-23)
        minute: Minute value (0-59)
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner
        twelve_hour: If True, convert to 12-hour format and return AM/PM
        fill: Grayscale fill color (0=black, 255=white)

    Returns:
        Tuple of (total_width, am_pm_string)
        - total_width: Total width consumed in pixels
        - am_pm_string: "AM", "PM", or "" (empty if twelve_hour is False)
    """
    # Handle 12-hour conversion
    am_pm = ""
    display_hour = hour

    if twelve_hour:
        if hour == 0:
            display_hour = 12
            am_pm = "AM"
        elif hour < 12:
            display_hour = hour
            am_pm = "AM"
        elif hour == 12:
            display_hour = 12
            am_pm = "PM"
        else:
            display_hour = hour - 12
            am_pm = "PM"

    # Format hour and minute as strings
    hour_str = f"{display_hour:02d}"
    minute_str = f"{minute:02d}"

    current_x = x

    # Render hour digits
    for digit in hour_str:
        render_digit(draw, digit, current_x, y, fill)
        current_x += DIGIT_WIDTH + DIGIT_GAP

    # Remove the last gap before colon (we'll add colon directly)
    current_x -= DIGIT_GAP

    # Render colon
    render_colon(draw, current_x, y, fill)
    current_x += COLON_WIDTH

    # Render minute digits
    for i, digit in enumerate(minute_str):
        render_digit(draw, digit, current_x, y, fill)
        current_x += DIGIT_WIDTH
        if i < len(minute_str) - 1:
            current_x += DIGIT_GAP

    total_width = current_x - x

    return (total_width, am_pm)


if __name__ == "__main__":
    # Test: Create an image showing "10:34"

    # Calculate image dimensions with some padding
    padding = 40
    # Width: 4 digits (80px each) + 3 gaps (20px) + 1 colon (20px) + padding
    img_width = (4 * DIGIT_WIDTH) + (2 * DIGIT_GAP) + COLON_WIDTH + (2 * padding)
    # Height: digit height + padding
    img_height = DIGIT_HEIGHT + (2 * padding)

    # Create grayscale image with white background
    img = Image.new('L', (img_width, img_height), 255)
    draw = ImageDraw.Draw(img)

    # Render "10:34" (representing 10:34 AM)
    hour = 10
    minute = 34

    total_width, am_pm = render_time(draw, hour, minute, padding, padding, twelve_hour=True, fill=0)

    print(f"Test: Rendering time {hour:02d}:{minute:02d}")
    print(f"Total width: {total_width}px")
    print(f"AM/PM: {am_pm}")
    print(f"Image size: {img_width}x{img_height}px")

    # Save test image
    output_path = "/Users/cody-mbp/Codex/Projects/kindle-jail-break/paperterm/src/test_ascii_digits.png"
    img.save(output_path)
    print(f"Test image saved to: {output_path}")
