#!/usr/bin/env python3
"""
Emoji Workshop GUI Launcher

Launch the desktop GUI application for creating emoji wallpapers.
"""

import sys
import os

# Add the parent directory to the path so we can import emojiworkshop
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from emojiworkshop.gui.app import WorkshopGUI
except ImportError as e:
    print(f"❌ Failed to import GUI components: {e}")
    print("Make sure customtkinter is installed: pip install customtkinter")
    sys.exit(1)


def main():
    """Launch the GUI application."""
    try:
        app = WorkshopGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 GUI application closed by user")
    except Exception as e:
        print(f"❌ GUI Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()