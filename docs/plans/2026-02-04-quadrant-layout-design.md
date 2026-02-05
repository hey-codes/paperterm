# Paperterm Quadrant Layout Design

**Date:** 2026-02-04
**Status:** Approved

## Overview

Redesign the paperterm dashboard from header/footer layout to a full-screen quadrant-based design with ASCII aesthetics.

## Screen Specifications

- **Device:** Kindle Paperwhite 11th Gen
- **Resolution:** 1236 × 1648 pixels (portrait)
- **Margins:** 30px all sides
- **Usable area:** 1176 × 1588 pixels

## Layout

```
┌──────────────────────────────────────────────────────────────────┐ ─┬─
│                                                                  │  │
│    ██   ███       ████  ██  ██                                  │  │
│   ███   █ █   ██     █  █ █  █ █                                │  │
│    ██   ███       ███   ████  ██   PM      Wednesday, Feb 4     │  │ 320px
│    ██   █ █   ██     █     █  █ █                               │  │
│    ██   ███       ████     █  █ █                    ↻ 5min     │  │
│                                                                  │ ─┴─
├────────────────────┬─────────────────────────────────────────────┤ ─┬─
│                    │                                             │  │
│     \   /          │           FEBRUARY 2026                     │  │
│      .-.    19°F   │      Su  Mo  Tu  We  Th  Fr  Sa            │  │
│   ― (   ) ―        │       1   2   3  ▓4▓  5   6   7            │  │
│      `-'    Clear  │       8   9  10  11  12  13  14            │  │ 1048px
│     /   \          │      15  16  17  18  19  20  21            │  │
│    H:21° L:16°     │      22  23  24  25  26  27  28            │  │
│                    │                                             │  │
│      350px         │                 826px                       │  │
├────────────────────┴─────────────────────────────────────────────┤ ─┴─
│  [ ] Morning routine            [ ] Check email                  │  │
│  [x] Deploy dashboard           [ ] Evening review               │  │ 220px
│                                                          04:25   │  │
└──────────────────────────────────────────────────────────────────┘ ─┴─
```

## Zone Specifications

### 1. Time Hero Zone (320px height)

**Purpose:** Large, readable clock display as the centerpiece

**Components:**
- ASCII block digits for time (HH:MM format)
- AM/PM indicator (48px bold font)
- Date line: "Wednesday, Feb 4" (36px font)
- Refresh indicator: "↻ 5min" (24px, gray)

**ASCII Digit Rendering:**
- Each digit: 80px wide × 100px tall
- Pattern: 5 columns × 7 rows grid
- Each grid cell: 16 × 14 actual pixels
- Gap between digits: 20px
- Colon: 20px wide

**Digit Patterns:**
```
 ███    █   ███  ███  █ █  ████  ███  ████ ███  ███
█   █  ██      █    █ █ █  █    █        █ █ █  █ █
█   █   █   ██   ██  ████ ███  ████    █  ███  ████
█   █   █  █       █    █    █ █   █   █  █ █     █
█   █   █  █       █    █    █ █   █  █   █ █     █
█   █   █  █    █  █    █ █  █ █   █  █   █ █  █  █
 ███   ███ ████ ███     █ ███   ███   █   ███  ███
  0     1    2    3    4    5    6     7    8    9
```

### 2. Weather Zone (350px width × 1048px height)

**Purpose:** Current conditions with ASCII art icon

**Layout (vertically centered):**
```
     \   /
      .-.
   ― (   ) ―      ← ASCII weather icon
      `-'
     /   \

      19°F        ← Temperature (72px bold)

  Mainly Clear    ← Description (36px)

   H:21° L:16°    ← High/Low (24px gray)
```

**Icon Mapping:**
| Condition | Icon Style |
|-----------|------------|
| Clear/Sunny | Sun with rays `\` `/` `―` |
| Partly Cloudy | Sun behind cloud |
| Cloudy | Cloud shape |
| Rain | Cloud with `ʻ` drops |
| Snow | Cloud with `*` asterisks |
| Thunderstorm | Cloud with `⚡` |
| Fog | Horizontal `_ -` dashes |

### 3. Calendar Zone (826px width × 1048px height)

**Purpose:** Full month view with terminal-style cursor on current date

**Layout:**
```
┌────────────────────────────────────────────────┐
│            FEBRUARY 2026                       │
├────────────────────────────────────────────────┤
│   Su    Mo    Tu    We    Th    Fr    Sa      │
│                                                │
│    1     2     3    ▓4▓    5     6     7      │
│    8     9    10    11    12    13    14      │
│   15    16    17    18    19    20    21      │
│   22    23    24    25    26    27    28      │
└────────────────────────────────────────────────┘
```

**Grid Specifications:**
- 7 columns × 118px each = 826px
- Header row + 5-6 week rows
- Row height: ~140px

**Cursor Effect (Inverted Block):**
- Current date: white text on black rectangle
- Other dates: black text on white background
- Padding around cursor: 8px

### 4. Reminders Zone (1176px width × 220px height)

**Purpose:** Quick view of daily tasks in two columns

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────┐
│   [ ] Morning routine              [ ] Check email                  │
│   [x] Deploy dashboard             [ ] Evening review               │
│   [ ] Exercise                     [ ] Read 30 mins                 │
│                                                    Last updated: 04:25│
└─────────────────────────────────────────────────────────────────────┘
```

**Specifications:**
- Left column: x=30px, width=558px
- Right column: x=618px, width=558px
- Max items: 3 per column (6 total)
- Font: Monospace 28px
- Checkbox styles: `[ ]` pending, `[x]` done, `[!]` priority
- Timestamp: bottom-right, 18px light gray

## Refresh Behavior

- **Refresh rate:** 5 minutes
- **Indicator:** "↻ 5min" shown in time zone
- **Dashboard regeneration:** GitHub Actions every 5 minutes
- **Kindle fetch:** Matches refresh rate in TRMNL.sh

## Implementation Notes

### Files to Modify
- `src/render.py` - Complete rewrite of layout logic
- `config.yml` - Add refresh_rate setting

### New Components Needed
- `src/ascii_digits.py` - ASCII digit rendering
- `src/calendar_render.py` - Calendar with cursor

### Font Requirements
- Monospace font for calendar and reminders
- Bold variant for headers and temperature
