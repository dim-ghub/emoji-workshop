# Emoji Workshop

A powerful Python-based wallpaper generator that creates stunning emoji patterns with sophisticated collision detection and multiple artistic layouts.

**Emoji Workshop** is a desktop port/clone of Google's popular "Emoji Workshop Wallpaper" Android app, bringing the same creative emoji pattern generation to your desktop with enhanced features and customization options.

## ✨ Features

- **5 Unique Patterns**: Mosaic, Lotus, Stack, Sprinkle, and Prism layouts
- **Smart Collision Detection**: Prevents emoji overlap with intelligent placement algorithms
- **Rotation Support**: Full 360° emoji rotation with anti-aliasing
- **Font Caching**: Optimized performance for fast generation (~1 second)
- **Configurable Parameters**: Easily adjust colors, sizes, counts, and variations
- **High Resolution**: Generate wallpapers up to 1920x1080 and beyond

## 🚀 Quick Start

### Prerequisites

```bash
pip install Pillow
```

### Basic Usage

```bash
python main.py
```

This generates a `wallpaper.png` file with the default mosaic pattern.

## 🎨 Pattern Types

### Mosaic
Random placement with varying sizes - perfect for organic, natural looks.

### Lotus
Curved spiral arms emanating from center - creates flowing, organic patterns.

### Stack
Brick-like offset grid pattern - structured and architectural.

### Sprinkle
Scattered placement with full rotation - chaotic but balanced distribution.

### Prism
Diamond formation with subtle rotations - geometric and crystalline.

## ⚙️ Configuration

Edit the `CONFIG` dictionary in `main.py` to customize:

```python
CONFIG = {
    "emojis": ["👀", "✨", "🦖", "🐈‍⬛", "🐧", "🦀"],
    "img_size": (1920, 1080),
    "pattern": "mosaic",  # mosaic, lotus, stack, sprinkle, prism
    "scale_variation": 0.7,  # 0.0 = uniform, 1.0 = maximum variation
    "emoji_count": 200,
    "bg_color": (39, 39, 39),
    "font_color": (94, 103, 102)
}
```

### Available Colors

Choose from predefined color palettes:
- `GRAY`, `RED`, `ORANGE`, `YELLOW`, `PINK`, `BEIGE`, `ULTRAMARINE`, `BLUE`

## 🏗️ Architecture

### Core Components

- **EmojiBox**: Collision detection system with optimized overlap algorithms
- **Pattern Functions**: Modular pattern generators for easy extension
- **Font Caching**: Performance optimization preventing redundant font loading
- **Rotation Engine**: Anti-aliased emoji rotation with alpha compositing

### Performance Features

- **Smart Placement**: Maximum attempt limits prevent infinite loops
- **Cached Fonts**: Single font loading per size
- **Optimized Collision**: Early exit collision detection
- **Memory Efficient**: Minimal temporary image creation

## 📁 Project Structure

```
emoji-workshop-wallpaper/
├── main.py              # Main application
├── assets/
│   └── NotoEmoji-Bold.ttf   # Emoji font file
├── wallpaper.png        # Generated output
└── README.md            # This file
```

## 🛠️ Advanced Usage

### Custom Emoji Sets

```python
CONFIG["emojis"] = ["🌟", "🎨", "🔥", "💎", "🚀"]
```

### Custom Resolutions

```python
CONFIG["img_size"] = (3840, 2160)  # 4K resolution
```

### Pattern-Specific Settings

```python
CONFIG["pattern"] = "lotus"
CONFIG["scale_variation"] = 0.3  # Subtle size variations
CONFIG["emoji_count"] = 150      # Fewer emojis for cleaner look
```

## 🎯 Technical Details

### Collision Detection Algorithm

Uses bounding box overlap detection with configurable margins:
- O(n) placement attempts per emoji
- Configurable retry limits prevent hanging
- Spatial optimization for large emoji counts

### Rotation Implementation

- Temporary RGBA canvas for each rotated emoji
- BICUBIC resampling for smooth edges
- Alpha compositing preserves transparency
- Boundary checking prevents clipping

### Font System

- TrueType font loading with size caching
- NotoEmoji-Bold for consistent cross-platform rendering
- Automatic bbox calculation for precise positioning

## 🔧 Extending Patterns

Add new patterns by implementing a pattern function:

```python
def my_pattern(image, draw, font, emojis, img_size, scale_var):
    # Your pattern logic here
    pass

# Register the pattern
PATTERNS["my_pattern"] = my_pattern
```

## 📋 Requirements

- Python 3.7+
- Pillow (PIL) 8.0+
- NotoEmoji-Bold.ttf font file

## 🐛 Troubleshooting

### Font Issues
Ensure `NotoEmoji-Bold.ttf` is in the `assets/` directory.

### Performance Issues
Reduce `emoji_count` or `scale_variation` for faster generation.

### Memory Issues
Lower `img_size` or reduce `max_attempts` in placement functions.

## 📄 License

MIT License - Feel free to use, modify, and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your pattern or optimization
4. Submit a pull request

---

**Emoji Workshop** - Where patterns meet creativity. ✨
