from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageEnhance
from enum import Enum
import random
import math
import cairosvg
import io


class SvgBox:
    """Represents a bounding box for an SVG with collision detection."""

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x, self.y, self.w, self.h = x, y, w, h

    def overlaps(self, other: 'SvgBox', margin: int = 10) -> bool:
        """Check if this box overlaps with another box including margin."""
        return not (self.x + self.w + margin < other.x or
                    other.x + other.w + margin < self.x or
                    self.y + self.h + margin < other.y or
                    other.y + other.h + margin < self.y)


class SvgCache:
    """Efficient SVG caching to avoid repeated rendering."""

    def __init__(self):
        self._cache = {}

    def get_svg(self, svg_path: str, size: int) -> Image.Image:
        """Get SVG rendered at specified size from cache or create new."""
        key = (svg_path, size)
        if key not in self._cache:
            png_data = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
            self._cache[key] = Image.open(io.BytesIO(png_data)).convert("RGBA")
        return self._cache[key].copy()

    def clear(self):
        """Clear the SVG cache."""
        self._cache.clear()


_svg_cache = SvgCache()


def tint_image(img: Image.Image, color: Tuple[int, int, int]) -> Image.Image:
    """Replace all non-transparent pixels with the specified color."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    r, g, b = color
    pixels = img.load()
    width, height = img.size
    
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if pixel[3] > 0:
                pixels[x, y] = (r, g, b, pixel[3])
    
    return img


def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    """Interpolate between two colors."""
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    return (r, g, b)


class BasePattern(ABC):
    """Abstract base class for all SVG patterns."""

    def __init__(self, config: dict):
        self.config = config
        self.placed_svgs: List[SvgBox] = []

    @abstractmethod
    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        svg_path: str, svg_count: int,
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        """Generate the pattern on the image."""
        pass

    def get_svg(self, size: int, tint: Tuple[int, int, int] = None) -> Image.Image:
        """Get SVG with specified size, optionally tinted."""
        svg_img = _svg_cache.get_svg(self.config["svg_path"], size)
        if tint:
            return tint_image(svg_img, tint)
        return svg_img

    def get_tint_color(self, x: int, y: int, img_size: Tuple[int, int]) -> Optional[Tuple[int, int, int]]:
        """Get tint color for position, supporting gradients."""
        tint = self.config.get("tint_color")
        svg_gradient = self.config.get("svg_gradient")
        
        if svg_gradient and len(svg_gradient) >= 2:
            ratio = (x / img_size[0] + y / img_size[1]) / 2
            return interpolate_color(svg_gradient[0], svg_gradient[1], ratio)
        elif tint:
            return tint
        return None

    def place_svg_safely(
        self, x: int, y: int,
        svg_size: int, img_size: Tuple[int, int],
        max_attempts: int = 50
    ) -> Optional[Tuple[int, int]]:
        """
        Find a safe position for an SVG that doesn't overlap with existing ones.
        """
        w, h = svg_size, svg_size
        for _ in range(max_attempts):
            safe_x = max(w//2, min(x, img_size[0] - w//2))
            safe_y = max(h//2, min(y, img_size[1] - h//2))

            new_box = SvgBox(safe_x - w//2, safe_y - h//2, w, h)

            if not any(
                new_box.overlaps(existing, self.config.get("margin", 10))
                for existing in self.placed_svgs
            ):
                self.placed_svgs.append(new_box)
                return safe_x, safe_y

            x += random.randint(-50, 50)
            y += random.randint(-50, 50)

        return None

    def draw_svg_with_rotation(
        self, image: Image.Image,
        svg: Image.Image, x: int, y: int,
        rotation: int = 0
    ) -> None:
        """Draw SVG with optional rotation."""
        if rotation == 0:
            w, h = svg.size
            paste_x = max(0, min(x - w//2, image.size[0] - w))
            paste_y = max(0, min(y - h//2, image.size[1] - h))
            if svg.mode == 'RGBA':
                image.paste(svg, (paste_x, paste_y), svg)
            else:
                image.paste(svg, (paste_x, paste_y))
        else:
            w, h = svg.size
            rotated = svg.rotate(rotation, expand=False, resample=Image.BICUBIC)
            paste_x = max(0, min(x - rotated.size[0]//2, image.size[0] - rotated.size[0]))
            paste_y = max(0, min(y - rotated.size[1]//2, image.size[1] - rotated.size[1]))
            if rotated.mode == 'RGBA':
                image.paste(rotated, (paste_x, paste_y), rotated)
            else:
                image.paste(rotated, (paste_x, paste_y))

    def reset(self) -> None:
        """Reset the pattern state for reuse."""
        self.placed_svgs.clear()


class MosaicPattern(BasePattern):
    """Random mosaic pattern with collision avoidance."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        svg_path: str, svg_count: int,
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        attempts = 0
        max_attempts = max(svg_count * 10, 1)

        while len(self.placed_svgs) < svg_count and attempts < max_attempts:
            margin = min(50, img_size[0] // 4, img_size[1] // 4)
            x = random.randint(margin, img_size[0] - margin)
            y = random.randint(margin, img_size[1] - margin)

            size_factor = 0.5 + random.uniform(0, 1.5 * scale_var)
            size = int(self.config["svg_size"] * size_factor)
            tint = self.get_tint_color(x, y, img_size)
            svg_img = self.get_svg(size, tint)

            safe_pos = self.place_svg_safely(x, y, size, img_size)

            if safe_pos is not None:
                safe_x, safe_y = safe_pos
                self.draw_svg_with_rotation(image, svg_img, safe_x, safe_y, 0)

            attempts += 1


class LotusPattern(BasePattern):
    """Spiral lotus pattern with multiple arms."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        svg_path: str, svg_count: int,
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
                    size_factor = max(0.4, 1.2 - (i * 0.03)) + \
                        random.uniform(-scale_var*0.5, scale_var*0.5)
                    size = int(self.config["svg_size"] * size_factor)
                    tint = self.get_tint_color(int(x), int(y), img_size)
                    svg_img = self.get_svg(size, tint)

                    safe_pos = self.place_svg_safely(int(x), int(y), size, img_size)

                    if safe_pos is not None:
                        safe_x, safe_y = safe_pos
                        self.draw_svg_with_rotation(image, svg_img, safe_x, safe_y, 0)


class StackPattern(BasePattern):
    """Grid-based stacked pattern with alternating offsets."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        svg_path: str, svg_count: int,
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        cols, rows = self.config["grid"]
        cell_w, cell_h = img_size[0] // cols, img_size[1] // rows

        for row in range(rows):
            for col in range(cols):
                base_x = col * cell_w + cell_w // 2
                base_y = row * cell_h + cell_h // 2

                if row % 2 == 1:
                    offset_x = base_x + cell_w // 2
                    x = offset_x if offset_x < img_size[0] - cell_w // 2 else base_x - cell_w // 2
                else:
                    x = base_x

                size_factor = 1.0 + random.uniform(-scale_var * 0.3, scale_var * 0.3)
                size = int(self.config["svg_size"] * size_factor)
                tint = self.get_tint_color(int(x), int(base_y), img_size)
                svg_img = self.get_svg(size, tint)

                self.draw_svg_with_rotation(image, svg_img, x, base_y, 0)


class SprinklePattern(BasePattern):
    """Random sprinkled pattern with rotation."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        svg_path: str, svg_count: int,
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        attempts = 0
        max_attempts = max(svg_count * 15, 1)

        while len(self.placed_svgs) < svg_count and attempts < max_attempts:
            margin = min(40, img_size[0] // 5, img_size[1] // 5)
            x = random.randint(margin, img_size[0] - margin)
            y = random.randint(margin, img_size[1] - margin)

            size_factor = 0.6 + random.uniform(0, 1.0 + scale_var)
            size = int(self.config["svg_size"] * size_factor)
            tint = self.get_tint_color(x, y, img_size)
            svg_img = self.get_svg(size, tint)

            safe_pos = self.place_svg_safely(x, y, size, img_size)

            if safe_pos is not None:
                safe_x, safe_y = safe_pos
                rotation = random.randint(0, 360)
                self.draw_svg_with_rotation(image, svg_img, safe_x, safe_y, rotation)

            attempts += 1


class PrismPattern(BasePattern):
    """Diamond/prism shaped pattern."""

    def generate(
        self, image: Image.Image, draw: ImageDraw.Draw,
        svg_path: str, svg_count: int,
        img_size: Tuple[int, int], scale_var: float
    ) -> None:
        rows = 7

        for row in range(rows):
            svg_count_row = row + 2 if row <= rows // 2 else rows - row + 1
            row_width = svg_count_row * 140
            start_x = (img_size[0] - row_width) // 2
            y = 120 + row * 130

            for col in range(svg_count_row):
                x = start_x + col * 140 + 70

                size_factor = 0.8 + random.uniform(-scale_var, scale_var)
                size = int(self.config["svg_size"] * size_factor)
                tint = self.get_tint_color(int(x), int(y), img_size)
                svg_img = self.get_svg(size, tint)

                safe_pos = self.place_svg_safely(x, y, size, img_size)

                if safe_pos is not None:
                    safe_x, safe_y = safe_pos
                    rotation = random.randint(-30, 30)
                    self.draw_svg_with_rotation(image, svg_img, safe_x, safe_y, rotation)


class PatternFactory:
    """Factory for creating pattern instances."""

    @classmethod
    def create_pattern(cls, pattern: 'Pattern', config: dict) -> BasePattern:
        """Create a pattern instance from Pattern enum."""
        if not isinstance(pattern, Pattern):
            raise TypeError(f"pattern must be Pattern enum, got {type(pattern)}")
        return pattern.create(config)

    @classmethod
    def get_available_patterns(cls) -> List['Pattern']:
        """Get list of available Pattern enums."""
        return list(Pattern)


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