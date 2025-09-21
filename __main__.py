#!/usr/bin/env python3
"""
Emoji Workshop Wallpaper Generator

Generate beautiful emoji wallpapers with various patterns and color schemes.
"""

import sys
from emojiworkshop.cli import parse_arguments
from emojiworkshop.core.generator import generate_wallpaper_with_config


def main():
    """Main entry point for the application."""
    try:
        # Parse command line arguments
        config = parse_arguments()
        
        # Generate wallpaper with parsed configuration
        generate_wallpaper_with_config(config)
        
        print(f"✅ Wallpaper generated successfully: {config['output_filename']}")
        print(f"   Pattern: {config['pattern']}")
        print(f"   Size: {config['img_size'][0]}x{config['img_size'][1]}")
        print(f"   Emojis: {len(config['emojis'])} different emojis")
        print(f"   Count: {config['emoji_count']} placed emojis")
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()