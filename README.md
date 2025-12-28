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
python __main__.py
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

## 📁 Project Structure

```
emoji-workshop-wallpaper/
├── main.py              # Main application
├── assets/
│   └── NotoEmoji-Bold.ttf   # Emoji font file
├── wallpaper.png        # Generated output
└── README.md            # This file
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

- Python 3.11+
- Pillow (PIL) 12.0+
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
