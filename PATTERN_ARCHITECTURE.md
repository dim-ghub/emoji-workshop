# Emoji Workshop Pattern Architecture

## Overview

The pattern system uses a modern, type-safe enum-based architecture for maximum developer experience and compile-time safety.

## Architecture

### Core Components

- **`BasePattern`**: Abstract base class for all emoji patterns
- **`Pattern`**: Enum defining all available pattern types with their classes
- **`PatternFactory`**: Factory for creating pattern instances from enums
- **`EmojiBox`**: Collision detection for emoji placement  
- **`FontCache`**: Efficient font caching for performance optimization

### Available Patterns

- **`Pattern.MOSAIC`**: Random mosaic pattern with collision avoidance
- **`Pattern.LOTUS`**: Spiral lotus pattern with multiple arms
- **`Pattern.STACK`**: Grid-based stacked pattern
- **`Pattern.SPRINKLE`**: Randomly scattered pattern with rotation
- **`Pattern.PRISM`**: Diamond/prism pattern

## Usage

### Basic Usage

```python
from emojiworkshop.core.pattern import Pattern, PatternFactory
from emojiworkshop.core.generator import CONFIG

# Type-safe pattern selection
CONFIG["pattern"] = Pattern.MOSAIC

# Create pattern instance
pattern_config = CONFIG.copy()
pattern_config["font_color"] = CONFIG["color"].foreground

# Method 1: Factory pattern
pattern = PatternFactory.create_pattern(Pattern.LOTUS, pattern_config)

# Method 2: Direct creation (preferred)
pattern = Pattern.LOTUS.create(pattern_config)

# Apply pattern to image
pattern.generate(image, draw, font, emojis, img_size, scale_var)
```

### List Available Patterns

```python
from emojiworkshop.core.pattern import Pattern, PatternFactory

# Get all pattern enums
patterns = PatternFactory.get_available_patterns()
print("Available patterns:", [str(p) for p in patterns])

# Or iterate directly
for pattern in Pattern:
    print(f"Pattern: {pattern.name} -> {pattern}")
```

## Type Safety Features

### Compile-Time Safety
```python
# ✅ This works - IDE will autocomplete
set_pattern(Pattern.MOSAIC)

# ❌ This fails at runtime with clear error
set_pattern("mosaic")  # TypeError: pattern must be Pattern enum

# ✅ Pattern comparison is safe
if current_pattern == Pattern.LOTUS:
    print("Using lotus pattern")
```

### IDE Support
- **Autocompletion**: IDE shows all available patterns
- **Refactoring**: Safe renaming across the codebase
- **Type hints**: Full type checking support
- **Documentation**: Hover shows pattern descriptions

## Adding New Patterns

### Method 1: Extend the Pattern Enum

```python
# Add to the Pattern enum in pattern.py
class Pattern(Enum):
    MOSAIC = ("mosaic", MosaicPattern)
    LOTUS = ("lotus", LotusPattern)
    # ... existing patterns ...
    
    # Add your new pattern
    SPIRAL = ("spiral", SpiralPattern)
```

### Method 2: Create Extended Enum

```python
from emojiworkshop.core.pattern import Pattern
from enum import Enum

class ExtendedPattern(Enum):
    """Extended pattern enum with custom patterns."""
    
    # Re-export built-in patterns
    MOSAIC = ("mosaic", Pattern.MOSAIC.pattern_class)
    LOTUS = ("lotus", Pattern.LOTUS.pattern_class)
    
    # Add custom patterns
    CUSTOM = ("custom", CustomPattern)
    
    def __init__(self, pattern_name: str, pattern_class: type):
        self.pattern_name = pattern_name
        self.pattern_class = pattern_class
    
    def create(self, config: dict):
        return self.pattern_class(config)
    
    def __str__(self) -> str:
        return self.pattern_name
```

### Custom Pattern Class

```python
from emojiworkshop.core.pattern import BasePattern

class MyCustomPattern(BasePattern):
    """My custom pattern implementation."""
    
    def generate(self, image, draw, font, emojis, img_size, scale_var):
        # Pattern implementation
        for i in range(self.config["emoji_count"]):
            emoji = random.choice(emojis)
            x, y = self.calculate_position(i)
            
            current_font = self.get_font(self.config["font_size"])
            safe_pos = self.place_emoji_safely(emoji, x, y, current_font, img_size)
            
            if safe_pos:
                safe_x, safe_y = safe_pos
                self.draw_emoji_with_rotation(
                    image, draw, emoji, safe_x, safe_y, 
                    current_font, self.config["font_color"], 0)
```

## Performance Optimizations

### Font Caching
- Automatic font caching prevents repeated loading
- Cache cleared automatically or manually with `_font_cache.clear()`

### Collision Detection
- Efficient bounding-box collision detection
- Early exit optimization for faster placement
- Configurable maximum attempts per emoji

### Memory Management
- Temporary rotation images automatically cleaned up
- Pattern state reset with `pattern.reset()` for reuse

## Configuration

```python
config = {
    "font_path": "path/to/font.ttf",
    "font_size": 96,
    "emoji_count": 200,
    "font_color": (255, 255, 255),
    "margin": 10,
    "grid": (6, 10)  # For Pattern.STACK
}

pattern = Pattern.STACK.create(config)
```

## Migration from String-Based API

### Old (String-Based)
```python
# Old way - no type safety
CONFIG["pattern"] = "mosaic"
pattern = PatternFactory.create_pattern("lotus", config)
```

### New (Enum-Based)
```python
# New way - fully type-safe
CONFIG["pattern"] = Pattern.MOSAIC
pattern = Pattern.LOTUS.create(config)
```

## Benefits

1. **Type Safety**: Compile-time error checking
2. **IDE Support**: Full autocompletion and refactoring
3. **Performance**: No string lookups at runtime
4. **Maintainability**: Clear pattern definitions in one place
5. **Extensibility**: Easy to add new patterns
6. **Documentation**: Self-documenting enum values