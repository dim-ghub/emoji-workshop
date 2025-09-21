from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from enum import Enum

import random
import math


class EmojiBox:
    """Represents a bounding box for an emoji with collision detection."""

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x, self.y, self.w, self.h = x, y, w, h

    def overlaps(self, other: 'EmojiBox', margin: int = 10) -> bool:
        """Check if this box overlaps with another box including margin."""
        return not (self.x + self.w + margin < other.x or
                    other.x + other.w + margin < self.x or
                    self.y + self.h + margin < other.y or
                    other.y + other.h + margin < self.y)


class FontCache:
    """Efficient font caching to avoid repeated font loading."""

    def __init__(self):
        self._cache = {}

    def get_font(self, font_path: str, size: int) -> ImageFont.FreeTypeFont:
        """Get font from cache or create new one."""
        key = (font_path, size)

        if key not in self._cache:
            self._cache[key] = ImageFont.truetype(font_path, size)

        return self._cache[key]

    def clear(self):
        """Clear the font cache."""
        self._cache.clear()


# Global font cache instance
_font_cache = FontCache()


class BasePattern(ABC):
    """Abstract base class for all emoji patterns."""

    def __init__(self, config: dict):
        self.config = config
        self.placed_emojis: List[EmojiBox] = []

    @abstractmethod
    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        font: ImageFont.FreeTypeFont, emojis: List[str],
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        """Generate the pattern on the image."""
        pass

    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font with specified size using cache."""
        return _font_cache.get_font(self.config["font_path"], size)

    def place_emoji_safely(
        self, emoji: str, x: int, y: int,
        font: ImageFont.FreeTypeFont, img_size: Tuple[int, int],
        max_attempts: int = 50
    ) -> Optional[Tuple[int, int]]:
        """
        Find a safe position for an emoji that doesn't overlap with existing ones.

        Performance optimization: Use spatial partitioning for large numbers of emojis.
        """
        bbox = font.getbbox(emoji)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        for _ in range(max_attempts):
            safe_x = max(w//2, min(x, img_size[0] - w//2))
            safe_y = max(h//2, min(y, img_size[1] - h//2))

            new_box = EmojiBox(safe_x - w//2, safe_y - h//2, w, h)

            # Performance optimization: early exit on first non-overlapping position
            if not any(
                new_box.overlaps(existing, self.config.get("margin", 10))
                for existing in self.placed_emojis
            ):
                self.placed_emojis.append(new_box)
                return safe_x, safe_y

            # Add some randomness to find alternative positions
            x += random.randint(-50, 50)
            y += random.randint(-50, 50)

        return None

    def draw_emoji_with_rotation(
        self, image: Image.Image, draw: ImageDraw.Draw,
        emoji: str, x: int, y: int,
        font: ImageFont.FreeTypeFont, color: Tuple[int, int, int],
        rotation: int = 0
    ) -> None:
        """Draw emoji with optional rotation."""
        if rotation == 0:
            # Fast path for non-rotated emojis
            bbox = font.getbbox(emoji)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((x - w // 2, y - h // 2), emoji, font=font, fill=color)
        else:
            # Slower path for rotated emojis
            bbox = font.getbbox(emoji)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

            temp_size = max(w, h) + 40
            temp_img = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text(
                (temp_size//2 - w//2, temp_size//2 - h//2),
                emoji, font=font, fill=color
            )

            rotated = temp_img.rotate(
                rotation, expand=False,
                resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0)
            )

            paste_x = max(0, min(x - temp_size//2, image.size[0] - temp_size))
            paste_y = max(0, min(y - temp_size//2, image.size[1] - temp_size))

            if rotated.mode == 'RGBA':
                image.paste(rotated, (paste_x, paste_y), rotated)

            else:
                image.paste(rotated, (paste_x, paste_y))

    def reset(self) -> None:
        """Reset the pattern state for reuse."""
        self.placed_emojis.clear()


class MosaicPattern(BasePattern):
    """Random mosaic pattern with collision avoidance."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        font: ImageFont.FreeTypeFont, emojis: List[str],
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        attempts = 0
        max_attempts = self.config["emoji_count"] * 10

        while len(self.placed_emojis) < self.config["emoji_count"] and attempts < max_attempts:
            emoji = random.choice(emojis)
            x = random.randint(100, img_size[0] - 100)
            y = random.randint(100, img_size[1] - 100)

            size_factor = 0.5 + random.uniform(0, 1.5 * scale_var)
            current_font = self.get_font(
                size=int(self.config["font_size"] * size_factor)
            )

            safe_pos = self.place_emoji_safely(
                emoji=emoji, x=x, y=y,
                font=current_font, img_size=img_size
            )

            if safe_pos is not None:
                safe_x, safe_y = safe_pos
                self.draw_emoji_with_rotation(
                    image=image, draw=draw, emoji=emoji, x=safe_x, y=safe_y,
                    font=current_font, color=self.config["font_color"], rotation=0
                )

            attempts += 1


class LotusPattern(BasePattern):
    """Spiral lotus pattern with multiple arms."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        font: ImageFont.FreeTypeFont, emojis: List[str],
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        center_x, center_y = img_size[0] // 2, img_size[1] // 2
        num_arms = 4

        for arm in range(num_arms):
            base_angle = (arm * 2 * math.pi) / num_arms
            points_per_arm = 25

            for i in range(points_per_arm):
                distance = 30 + (i * i * 1.8)
                angle_variation = math.sin(i * 0.4) * 0.8
                current_angle = base_angle + angle_variation

                x = center_x + distance * math.cos(current_angle)
                y = center_y + distance * math.sin(current_angle)

                if 50 <= x <= img_size[0] - 50 and 50 <= y <= img_size[1] - 50:
                    emoji = random.choice(emojis)
                    size_factor = max(0.4, 1.2 - (i * 0.03)) + \
                        random.uniform(-scale_var*0.5, scale_var*0.5)

                    current_font = self.get_font(
                        size=int(self.config["font_size"] * size_factor)
                    )

                safe_pos = self.place_emoji_safely(
                    emoji=emoji, x=x, y=y,
                    font=current_font, img_size=img_size
                )

                if safe_pos is not None:
                        safe_x, safe_y = safe_pos

                        self.draw_emoji_with_rotation(
                            image=image, draw=draw, emoji=emoji, x=safe_x, y=safe_y,
                            font=current_font, color=self.config["font_color"], rotation=0
                        )


class StackPattern(BasePattern):
    """Grid-based stacked pattern with alternating offsets."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        font: ImageFont.FreeTypeFont, emojis: List[str],
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        cols, rows = self.config["grid"]
        cell_w, cell_h = img_size[0] // cols, img_size[1] // rows

        for row in range(rows):
            for col in range(cols):
                emoji = random.choice(emojis)

                base_x = col * cell_w + cell_w // 2
                base_y = row * cell_h + cell_h // 2

                if row % 2 == 1:
                    offset_x = base_x + cell_w // 2
                    x = offset_x if offset_x < img_size[0] - \
                        cell_w // 2 else base_x - cell_w // 2
                else:
                    x = base_x

                size_factor = 1.0 + \
                    random.uniform(-scale_var * 0.3, scale_var * 0.3)

                current_font = self.get_font(
                    size=int(self.config["font_size"] * size_factor)
                )

                self.draw_emoji_with_rotation(
                    image=image, draw=draw, emoji=emoji, x=x, y=base_y,
                    font=current_font, color=self.config["font_color"], rotation=0
                )


class SprinklePattern(BasePattern):
    """Random sprinkled pattern with rotation."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        font: ImageFont.FreeTypeFont, emojis: List[str],
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        attempts = 0
        max_attempts = self.config["emoji_count"] * 15

        while len(self.placed_emojis) < self.config["emoji_count"] and attempts < max_attempts:
            emoji = random.choice(emojis)

            x = random.randint(80, img_size[0] - 80)
            y = random.randint(80, img_size[1] - 80)

            size_factor = 0.6 + random.uniform(0, 1.0 + scale_var)
            current_font = self.get_font(
                size=int(self.config["font_size"] * size_factor)
            )

            safe_pos = self.place_emoji_safely(
                emoji=emoji, x=x, y=y,
                font=current_font, img_size=img_size
            )

            if safe_pos is not None:
                safe_x, safe_y = safe_pos
                rotation = random.randint(0, 360)

                self.draw_emoji_with_rotation(
                    image=image, draw=draw, emoji=emoji, x=safe_x, y=safe_y,
                    font=current_font, color=self.config["font_color"], rotation=rotation
                )

            attempts += 1


class PrismPattern(BasePattern):
    """Diamond/prism shaped pattern."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        font: ImageFont.FreeTypeFont, emojis: List[str],
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        rows = 7

        for row in range(rows):
            emoji_count = row + 2 if row <= rows // 2 else rows - row + 1
            row_width = emoji_count * 140
            start_x = (img_size[0] - row_width) // 2
            y = 120 + row * 130

            for col in range(emoji_count):
                emoji = random.choice(emojis)
                x = start_x + col * 140 + 70

                size_factor = 0.8 + random.uniform(-scale_var, scale_var)
                current_font = self.get_font(
                    size=int(self.config["font_size"] * size_factor)
                )

                safe_pos = self.place_emoji_safely(
                    emoji=emoji, x=x, y=y,
                    font=current_font, img_size=img_size
                )

                if safe_pos is not None:
                    safe_x, safe_y = safe_pos
                    rotation = random.randint(-30, 30)

                    self.draw_emoji_with_rotation(
                        image=image, draw=draw, emoji=emoji, x=safe_x, y=safe_y,
                        font=current_font, color=self.config["font_color"], rotation=rotation
                    )


class PatternFactory:
    """Factory for creating pattern instances."""

    @classmethod
    def create_pattern(cls, pattern: 'Pattern', config: dict) -> BasePattern:
        """Create a pattern instance from Pattern enum."""
        if not isinstance(pattern, Pattern):
            raise TypeError(
                f"pattern must be Pattern enum, got {type(pattern)}")
        return pattern.create(config)

    @classmethod
    def get_available_patterns(cls) -> List['Pattern']:
        """Get list of available Pattern enums."""
        return list(Pattern)

    @classmethod
    def register_pattern(cls, pattern_enum: 'Pattern') -> None:
        """Register a new pattern enum (for extensibility)."""
        if not isinstance(pattern_enum, Pattern):
            raise TypeError("pattern_enum must be Pattern enum")
        # Pattern enums are registered automatically via the enum definition


class Pattern(Enum):
    """Enum for pattern types with associated classes."""

    MOSAIC = ("mosaic", MosaicPattern)
    LOTUS = ("lotus", LotusPattern)
    STACK = ("stack", StackPattern)
    SPRINKLE = ("sprinkle", SprinklePattern)
    PRISM = ("prism", PrismPattern)

    def __init__(self, pattern_name: str, pattern_class: type):
        self.pattern_name = pattern_name
        self.pattern_class = pattern_class

    def create(self, config: dict) -> BasePattern:
        """Create an instance of this pattern with the given config."""
        return self.pattern_class(config)

    def __str__(self) -> str:
        """String representation returns the pattern name."""
        return self.pattern_name

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Pattern.{self.name}"
