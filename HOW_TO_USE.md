# Emoji Workshop CLI Usage Guide

## Overview

The Emoji Workshop supports comprehensive command-line configuration through an argument parser. You can customize all aspects of wallpaper generation through command-line arguments.

## Required Arguments

These arguments must always be provided:

- `--emojis` / `-e`: Comma-separated list of emojis
- `--size` / `-s`: Image dimensions in WIDTHxHEIGHT format  
- `--pattern` / `-p`: Pattern type (mosaic, lotus, stack, sprinkle, prism)
- `--color` / `-c`: Color palette (red, orange, yellow, pink, beige, ultramarine, blue, gray)

## Optional Arguments (with defaults)

- `--font-path` / `-f`: Path to emoji font (default: assets/NotoEmoji-Bold.ttf)
- `--font-size`: Base font size in pixels (default: 96)
- `--grid` / `-g`: Grid dimensions for stack pattern (default: 6x10)
- `--scale`: Scale variation factor (default: 0.7)
- `--count`: Number of emojis to place (default: 200)
- `--margin` / `-m`: Margin between emojis (default: 10)
- `--output` / `-o`: Output filename (default: wallpaper.png)

## Usage Examples

### Basic Usage
```bash
python __main__.py --emojis "🎨,🚀,💎" --size 1920x1080 --pattern mosaic --color blue
```

### Custom Configuration
```bash
python __main__.py \
  --emojis "🌟,🦄,🌈,🎯,🔥" \
  --size 2560x1440 \
  --pattern lotus \
  --color orange \
  --count 150 \
  --font-size 120 \
  --scale 0.8 \
  --margin 15 \
  --output my_wallpaper.png
```

### Stack Pattern with Custom Grid
```bash
python __main__.py \
  --emojis "🐧,🦀,🎯,🌊" \
  --size 1920x1080 \
  --pattern stack \
  --grid 8x12 \
  --color gray \
  --count 96
```

### High Resolution with Many Emojis
```bash
python __main__.py \
  --emojis "👀,✨,🦖,🐈‍⬛,🐧,🦀,🎨,🚀,💎,🌟" \
  --size 3840x2160 \
  --pattern sprinkle \
  --color ultramarine \
  --count 300 \
  --font-size 80 \
  --scale 1.2
```

## Available Options

### Patterns:
- `mosaic` - Random placement with collision avoidance
- `lotus` - Spiral pattern with multiple arms
- `stack` - Grid-based with alternating offsets  
- `sprinkle` - Random placement with rotation
- `prism` - Diamond/prism shaped layout

### Colors:
- `red`, `orange`, `yellow`, `pink`, `beige`
- `ultramarine`, `blue`, `gray`

## Validation

The argument parser includes comprehensive validation:

- Image dimensions must be positive
- Font size must be positive
- Grid dimensions must be positive
- Emoji count must be positive
- Margin cannot be negative
- Scale variation cannot be negative
- Pattern must be one of the available types
- Color must be one of the available palettes

## Error Handling

Invalid arguments will show helpful error messages:

```bash
# Missing required argument
python __main__.py --emojis "🎨,🚀"
# Error: the following arguments are required: --size, --pattern, --color

# Invalid size format  
python __main__.py --emojis "🎨,🚀" --size "invalid" --pattern mosaic --color blue
# Error: Invalid size format: invalid

# Invalid pattern
python __main__.py --emojis "🎨,🚀" --size 800x600 --pattern invalid --color blue  
# Error: argument --pattern: invalid choice: 'invalid'
```

## Help

Use `--help` to see all available options:

```bash
python __main__.py --help
```

## Demo

Run the demo script to see examples:

```bash
python demo_cli.py
```