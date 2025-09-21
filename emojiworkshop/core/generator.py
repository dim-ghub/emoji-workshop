from PIL import Image, ImageDraw
from typing import Dict, Any
from emojiworkshop.core.colors import ColorPalettes
from emojiworkshop.core.pattern import PatternFactory, Pattern


# Default configuration
DEFAULT_CONFIG = {
    "emojis": ["👀", "✨", "🦖", "🐈‍⬛", "🐧", "🦀"],
    "img_size": (1920, 1080),
    "font_path": "assets/NotoEmoji-Bold.ttf",
    "font_size": 96,
    "grid": (6, 10),
    "pattern": Pattern.MOSAIC,
    "scale_variation": 0.7,
    "emoji_count": 200,
    "color": ColorPalettes.GRAY,
    "margin": 10,
    "output_filename": "wallpaper.png"
}


def generate_wallpaper_with_config(config: Dict[str, Any]):
    """Generate wallpaper using the provided configuration."""
    img = Image.new("RGB", config["img_size"], config["color"].background)
    draw = ImageDraw.Draw(img)

    # Create pattern configuration with proper font_color
    pattern_config = config.copy()
    pattern_config["font_color"] = config["color"].foreground
    pattern_config["bg_color"] = config["color"].background

    # Create pattern instance using factory
    pattern = PatternFactory.create_pattern(config["pattern"], pattern_config)

    # Generate the pattern
    pattern.generate(img, draw, None, config["emojis"],
                     config["img_size"], config["scale_variation"])

    # Save with specified filename
    output_file = config.get("output_filename", "wallpaper.png")
    img.save(output_file)
    print(f"Wallpaper with {config['pattern']} pattern saved as {output_file}")


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
