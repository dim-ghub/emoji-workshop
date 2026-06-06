from PIL import Image, ImageDraw
from typing import Dict, Any, Tuple, Optional, List
from emojiworkshop.core.colors import ColorPalettes
from emojiworkshop.core.pattern import PatternFactory, Pattern
import math


DEFAULT_CONFIG = {
    "svg_path": "assets/caelestia.svg",
    "svg_size": 96,
    "img_size": (1920, 1080),
    "grid": (6, 10),
    "pattern": Pattern.MOSAIC,
    "scale_variation": 0.7,
    "svg_count": 200,
    "color": ColorPalettes.GRAY,
    "tint_color": None,
    "bg_gradient": None,
    "bg_gradient_direction": "vertical",
    "svg_gradient": None,
    "margin": 10,
    "output_filename": "wallpaper.png"
}


def generate_wallpaper_with_config(config: Dict[str, Any]):
    """Generate wallpaper using the provided configuration."""
    bg_gradient = config.get("bg_gradient")
    
    if bg_gradient:
        img = Image.new("RGB", config["img_size"], bg_gradient[0])
        draw = ImageDraw.Draw(img)
        direction = config.get("bg_gradient_direction", "vertical")
        draw_gradient(draw, config["img_size"], bg_gradient, direction)
    else:
        img = Image.new("RGB", config["img_size"], config["color"].background)
        draw = ImageDraw.Draw(img)

    pattern_config = config.copy()
    pattern_config["bg_color"] = bg_gradient[1] if bg_gradient else config["color"].background
    pattern_config["tint_color"] = config.get("tint_color")
    pattern_config["svg_gradient"] = config.get("svg_gradient")

    pattern = PatternFactory.create_pattern(config["pattern"], pattern_config)

    pattern.generate(img, draw, config["svg_path"], config["svg_count"],
                     config["img_size"], config["scale_variation"])

    output_file = config.get("output_filename", "wallpaper.png")
    img.save(output_file)
    print(f"Wallpaper with {config['pattern']} pattern saved as {output_file}")


def draw_gradient(draw: ImageDraw.Draw, size: Tuple[int, int], gradient: List[Tuple[int, int, int]], direction: str = "vertical"):
    """Draw a gradient on the image."""
    w, h = size
    colors = gradient if len(gradient) == 2 else [gradient[0], gradient[-1]]
    
    if direction == "vertical":
        for y in range(h):
            ratio = y / (h - 1) if h > 1 else 0
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
    elif direction == "horizontal":
        for x in range(w):
            ratio = x / (w - 1) if w > 1 else 0
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(x, 0), (x, h)], fill=(r, g, b))
    elif direction == "diagonal":
        for y in range(h):
            for x in range(w):
                ratio = (x / (w - 1) + y / (h - 1)) / 2 if w > 1 and h > 1 else 0
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                draw.point((x, y), fill=(r, g, b))


def generate_wallpaper():
    """Generate wallpaper using the default configuration."""
    generate_wallpaper_with_config(DEFAULT_CONFIG)


def get_available_patterns():
    """Get list of available patterns."""
    return PatternFactory.get_available_patterns()


def set_pattern(pattern: Pattern):
    """Set the active pattern using Pattern enum."""
    if not isinstance(pattern, Pattern):
        raise TypeError("pattern must be Pattern enum")
    DEFAULT_CONFIG["pattern"] = pattern


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))