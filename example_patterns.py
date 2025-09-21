"""
Example of custom patterns.
This example shows how easily new patterns can be added to the Emoji Workshop.
"""

from emojiworkshop.core.pattern import BasePattern, Pattern
from enum import Enum
import random
import math


class CircularPattern(BasePattern):
    """An example pattern that arranges emojis in concentric circles."""

    def generate(self, image, draw, font, emojis, img_size, scale_var):
        """Generate concentric circles of emojis."""
        center_x, center_y = img_size[0] // 2, img_size[1] // 2
        max_radius = min(img_size[0], img_size[1]) // 2 - 100

        # Number of circles based on desired emoji count
        num_circles = int(math.sqrt(self.config["emoji_count"] / 8))

        for circle in range(num_circles):
            radius = (circle + 1) * (max_radius / num_circles)
            circumference = 2 * math.pi * radius

            # Number of emojis per circle based on circumference
            emojis_in_circle = max(8, int(circumference / 80))

            for i in range(emojis_in_circle):
                angle = (2 * math.pi * i) / emojis_in_circle

                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)

                # Small random variation for more organic look
                x += random.randint(-20, 20)
                y += random.randint(-20, 20)

                # Size based on radius (inner circles larger)
                size_factor = (1.2 - (circle * 0.2)) + \
                    random.uniform(-scale_var*0.3, scale_var*0.3)
                size_factor = max(0.4, size_factor)

                emoji = random.choice(emojis)
                current_font = self.get_font(
                    int(self.config["font_size"] * size_factor))

                safe_pos = self.place_emoji_safely(
                    emoji, int(x), int(y), current_font, img_size, 30)
                if safe_pos is not None:
                    safe_x, safe_y = safe_pos
                    rotation = random.randint(-15, 15)  # Slight rotation
                    self.draw_emoji_with_rotation(
                        image, draw, emoji, safe_x, safe_y, current_font,
                        self.config["font_color"], rotation)


class WavePattern(BasePattern):
    """A wave pattern that arranges emojis in sine waves."""

    def generate(self, image, draw, font, emojis, img_size, scale_var):
        """Generate emoji waves."""
        num_waves = 3
        wave_height = img_size[1] // (num_waves + 1)

        emojis_per_wave = self.config["emoji_count"] // num_waves

        for wave in range(num_waves):
            base_y = (wave + 1) * wave_height

            for i in range(emojis_per_wave):
                # X position evenly distributed across width
                x = (i * img_size[0]) / (emojis_per_wave -
                                         1) if emojis_per_wave > 1 else img_size[0] // 2

                # Y position as sine wave
                wave_amplitude = 100 + (wave * 30)  # Different amplitudes
                wave_frequency = 0.02 + (wave * 0.01)  # Different frequencies
                y = base_y + wave_amplitude * math.sin(x * wave_frequency)

                # Size variation based on wave height
                wave_factor = abs(math.sin(x * wave_frequency))
                size_factor = (0.7 + wave_factor * 0.5) + \
                    random.uniform(-scale_var*0.2, scale_var*0.2)

                emoji = random.choice(emojis)
                current_font = self.get_font(
                    int(self.config["font_size"] * size_factor))

                safe_pos = self.place_emoji_safely(
                    emoji, int(x), int(y), current_font, img_size, 25)
                if safe_pos is not None:
                    safe_x, safe_y = safe_pos
                    # Rotation based on wave slope
                    slope = wave_amplitude * wave_frequency * \
                        math.cos(x * wave_frequency)
                    rotation = int(math.degrees(math.atan(slope / 10)))
                    self.draw_emoji_with_rotation(
                        image, draw, emoji, safe_x, safe_y, current_font,
                        self.config["font_color"], rotation)


# Extended Pattern enum with custom patterns
class ExtendedPattern(Enum):
    """Extended pattern enum including custom patterns."""
    
    # Built-in patterns
    MOSAIC = ("mosaic", Pattern.MOSAIC.pattern_class)
    LOTUS = ("lotus", Pattern.LOTUS.pattern_class) 
    STACK = ("stack", Pattern.STACK.pattern_class)
    SPRINKLE = ("sprinkle", Pattern.SPRINKLE.pattern_class)
    PRISM = ("prism", Pattern.PRISM.pattern_class)
    
    # Custom patterns
    CIRCULAR = ("circular", CircularPattern)
    WAVE = ("wave", WavePattern)
    
    def __init__(self, pattern_name: str, pattern_class: type):
        self.pattern_name = pattern_name
        self.pattern_class = pattern_class
    
    def create(self, config: dict):
        """Create an instance of this pattern with the given config."""
        return self.pattern_class(config)
    
    def __str__(self) -> str:
        return self.pattern_name


if __name__ == "__main__":
    # Demonstration of example patterns
    from emojiworkshop.core.generator import CONFIG, generate_wallpaper, set_pattern

    print("Available built-in patterns:", [p.name for p in Pattern])
    print("Available extended patterns:", [p.name for p in ExtendedPattern])

    # Test built-in patterns using enum
    set_pattern(Pattern.LOTUS)
    CONFIG["emoji_count"] = 80
    print(f"Generating wallpaper with {Pattern.LOTUS} pattern...")
    generate_wallpaper()

    # For custom patterns, we would need to modify the generator
    # to work with ExtendedPattern or create a custom generator
    print("\nNote: Custom patterns (CIRCULAR, WAVE) would require")
    print("extending the main Pattern enum or using a custom generator.")
