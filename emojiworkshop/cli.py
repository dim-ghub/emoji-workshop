import argparse
import sys
from typing import List, Tuple, Dict, Any
from emojiworkshop.core.pattern import Pattern
from emojiworkshop.core.colors import ColorPalettes


def parse_emojis(emoji_string: str) -> List[str]:
    """Parse comma-separated emoji string into list."""
    return [emoji.strip() for emoji in emoji_string.split(",")]


def parse_size(size_string: str) -> Tuple[int, int]:
    """Parse 'WIDTHxHEIGHT' string into tuple."""
    try:
        parts = size_string.split("x")
        if len(parts) != 2:
            raise ValueError("Size must be in format WIDTHxHEIGHT")
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid size format: {size_string}")


def parse_grid(grid_string: str) -> Tuple[int, int]:
    """Parse 'COLSxROWS' string into tuple."""
    try:
        parts = grid_string.split("x")
        if len(parts) != 2:
            raise ValueError("Grid must be in format COLSxROWS")
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid grid format: {grid_string}")


def get_pattern_choices() -> Dict[str, Pattern]:
    """Get mapping of pattern names to Pattern enums."""
    return {pattern.pattern_name: pattern for pattern in Pattern}


def get_color_choices() -> Dict[str, Any]:
    """Get mapping of color names to ColorPalettes."""
    return {
        name.lower(): getattr(ColorPalettes, name)
        for name in dir(ColorPalettes)
        if not name.startswith('_')
    }


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="emoji-workshop",
        description="Generate emoji wallpapers with various patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --emojis "🎨,🚀,💎" --size 2560x1440 --pattern mosaic --color blue
  %(prog)s --emojis "🌟,🦄,🌈" --pattern lotus --count 150 --scale 0.8
  %(prog)s --emojis "🐧,🦀,🎯" --pattern stack --grid 8x12 --color gray
        """
    )

    # Required arguments
    required = parser.add_argument_group('required arguments')
    
    required.add_argument(
        "--emojis", "-e",
        type=parse_emojis,
        required=True,
        help="Comma-separated list of emojis (required)",
        metavar="EMOJI,EMOJI,..."
    )
    
    required.add_argument(
        "--size", "-s",
        type=parse_size,
        required=True,
        help="Image size in WIDTHxHEIGHT format (required)",
        metavar="WIDTHxHEIGHT"
    )
    
    pattern_choices = get_pattern_choices()
    required.add_argument(
        "--pattern", "-p",
        choices=list(pattern_choices.keys()),
        required=True,
        help=f"Pattern type (required). Available: {', '.join(pattern_choices.keys())}",
        metavar="PATTERN"
    )
    
    color_choices = get_color_choices()
    required.add_argument(
        "--color", "-c",
        choices=list(color_choices.keys()),
        required=True,
        help=f"Color palette (required). Available: {', '.join(color_choices.keys())}",
        metavar="COLOR"
    )

    # Optional arguments with defaults
    optional = parser.add_argument_group('optional arguments')
    
    optional.add_argument(
        "--font-path", "-f",
        type=str,
        default="assets/NotoEmoji-Bold.ttf",
        help="Path to emoji font file (default: assets/NotoEmoji-Bold.ttf)",
        metavar="PATH"
    )
    
    optional.add_argument(
        "--font-size",
        type=int,
        default=96,
        help="Base font size in pixels (default: 96)",
        metavar="SIZE"
    )
    
    optional.add_argument(
        "--grid", "-g",
        type=parse_grid,
        default=(6, 10),
        help="Grid dimensions for stack pattern as COLSxROWS (default: 6x10)",
        metavar="COLSxROWS"
    )
    
    optional.add_argument(
        "--scale", "--scale-variation",
        type=float,
        default=0.7,
        help="Scale variation factor (default: 0.7)",
        metavar="FACTOR"
    )
    
    optional.add_argument(
        "--count", "--emoji-count",
        type=int,
        default=200,
        help="Number of emojis to place (default: 200)",
        metavar="COUNT"
    )
    
    optional.add_argument(
        "--margin", "-m",
        type=int,
        default=10,
        help="Margin between emojis in pixels (default: 10)",
        metavar="PIXELS"
    )
    
    optional.add_argument(
        "--output", "-o",
        type=str,
        default="wallpaper.png",
        help="Output filename (default: wallpaper.png)",
        metavar="FILENAME"
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments and raise errors for invalid combinations."""
    # Validate font size
    if args.font_size <= 0:
        raise ValueError("Font size must be positive")
    
    # Validate image size
    if args.size[0] <= 0 or args.size[1] <= 0:
        raise ValueError("Image dimensions must be positive")
    
    # Validate grid
    if args.grid[0] <= 0 or args.grid[1] <= 0:
        raise ValueError("Grid dimensions must be positive")
    
    # Validate counts
    if args.count <= 0:
        raise ValueError("Emoji count must be positive")
    
    if args.margin < 0:
        raise ValueError("Margin cannot be negative")
    
    # Validate scale variation
    if args.scale < 0:
        raise ValueError("Scale variation cannot be negative")


def args_to_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Convert parsed arguments to configuration dictionary."""
    pattern_choices = get_pattern_choices()
    color_choices = get_color_choices()
    
    return {
        "emojis": args.emojis,
        "img_size": args.size,
        "font_path": args.font_path,
        "font_size": args.font_size,
        "grid": args.grid,
        "pattern": pattern_choices[args.pattern],
        "scale_variation": args.scale,
        "emoji_count": args.count,
        "color": color_choices[args.color],
        "margin": args.margin,
        "output_filename": args.output
    }


def parse_arguments(argv: List[str] = None) -> Dict[str, Any]:
    """
    Parse command line arguments and return configuration dictionary.
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:])
    
    Returns:
        Configuration dictionary compatible with generate_wallpaper()
    
    Raises:
        SystemExit: If argument parsing fails or validation errors occur
    """
    parser = create_parser()
    
    try:
        args = parser.parse_args(argv)
        validate_args(args)
        return args_to_config(args)
    
    except (ValueError, argparse.ArgumentTypeError) as e:
        parser.error(str(e))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_available_options():
    """Print available patterns and colors for user reference."""
    pattern_choices = get_pattern_choices()
    color_choices = get_color_choices()
    
    print("Available Patterns:")
    for name, pattern in pattern_choices.items():
        print(f"  {name:10} - {pattern}")
    
    print("\nAvailable Colors:")
    for name in color_choices.keys():
        print(f"  {name}")


if __name__ == "__main__":
    # Demo/testing
    print_available_options()
    print("\nExample usage:")
    print('python -m emojiworkshop.cli --emojis "🎨,🚀,💎" --size 1920x1080 --pattern mosaic --color blue')