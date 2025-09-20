from PIL import Image, ImageDraw, ImageFont
import random
import math

# Color palettes
COLORS = {
    "RED": ((122, 31, 30), (189, 86, 138)),
    "ORANGE": ((169, 66, 35), (216, 145, 75)),
    "YELLOW": ((202, 126, 57), (236, 157, 128)),
    "PINK": ((202, 92, 100), (244, 175, 141)),
    "BEIGE": ((183, 121, 116), (234, 185, 137)),
    "ULTRAMARINE": ((83, 95, 177), (150, 167, 245)),
    "BLUE": ((44, 70, 196), (76, 166, 249)),
    "GRAY": ((39, 39, 39), (94, 103, 102))
}

# Configuration
CONFIG = {
    "emojis": ["👀", "✨", "🦖", "🐈‍⬛", "🐧", "🦀"],
    "img_size": (1920, 1080),
    "font_path": "assets/NotoEmoji-Bold.ttf",
    "font_size": 96,
    "grid": (6, 10),
    "pattern": "mosaic",  # Options: mosaic, lotus, stack, sprinkle, prism
    "scale_variation": 0.7,
    "emoji_count": 200,
    "bg_color": COLORS["GRAY"][0],
    "font_color": COLORS["GRAY"][1],
    "margin": 10
}

class EmojiBox:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
    
    def overlaps(self, other):
        margin = CONFIG["margin"]
        return not (self.x + self.w + margin < other.x or 
                   other.x + other.w + margin < self.x or
                   self.y + self.h + margin < other.y or
                   other.y + other.h + margin < self.y)

_FONT_CACHE = {}

def get_font(size):
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(CONFIG["font_path"], size)
    return _FONT_CACHE[size]

def place_emoji_safely(placed_emojis, emoji, x, y, font, img_size, max_attempts=50):
    bbox = font.getbbox(emoji)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    for _ in range(max_attempts):
        safe_x = max(w//2, min(x, img_size[0] - w//2))
        safe_y = max(h//2, min(y, img_size[1] - h//2))
        
        new_box = EmojiBox(safe_x - w//2, safe_y - h//2, w, h)
        
        if not any(new_box.overlaps(existing) for existing in placed_emojis):
            placed_emojis.append(new_box)
            return safe_x, safe_y
        
        x += random.randint(-50, 50)
        y += random.randint(-50, 50)
    
    return None, None

def draw_emoji_with_rotation(image, draw, emoji, x, y, font, color, rotation=0):
    if rotation == 0:
        bbox = font.getbbox(emoji)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x - w // 2, y - h // 2), emoji, font=font, fill=color)
    else:
        bbox = font.getbbox(emoji)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        temp_size = max(w, h) + 40
        temp_img = Image.new('RGBA', (temp_size, temp_size), (0,0,0,0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((temp_size//2 - w//2, temp_size//2 - h//2), emoji, font=font, fill=color)
        
        rotated = temp_img.rotate(rotation, expand=False, resample=Image.BICUBIC, fillcolor=(0,0,0,0))
        paste_x = max(0, min(x - temp_size//2, image.size[0] - temp_size))
        paste_y = max(0, min(y - temp_size//2, image.size[1] - temp_size))
        
        if rotated.mode == 'RGBA':
            image.paste(rotated, (paste_x, paste_y), rotated)
        else:
            image.paste(rotated, (paste_x, paste_y))

def mosaic_pattern(image, draw, font, emojis, img_size, scale_var):
    placed_emojis = []
    attempts = 0
    max_attempts = CONFIG["emoji_count"] * 10
    
    while len(placed_emojis) < CONFIG["emoji_count"] and attempts < max_attempts:
        emoji = random.choice(emojis)
        x = random.randint(100, img_size[0] - 100)
        y = random.randint(100, img_size[1] - 100)
        
        size_factor = 0.5 + random.uniform(0, 1.5 * scale_var)
        current_font = get_font(int(CONFIG["font_size"] * size_factor))
        
        safe_x, safe_y = place_emoji_safely(placed_emojis, emoji, x, y, current_font, img_size)
        if safe_x is not None:
            draw_emoji_with_rotation(image, draw, emoji, safe_x, safe_y, current_font, CONFIG["font_color"], 0)
        
        attempts += 1

def lotus_pattern(image, draw, font, emojis, img_size, scale_var):
    placed_emojis = []
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
                size_factor = max(0.4, 1.2 - (i * 0.03)) + random.uniform(-scale_var*0.5, scale_var*0.5)
                current_font = get_font(int(CONFIG["font_size"] * size_factor))
                
                safe_x, safe_y = place_emoji_safely(placed_emojis, emoji, int(x), int(y), current_font, img_size, 15)
                if safe_x is not None:
                    draw_emoji_with_rotation(image, draw, emoji, safe_x, safe_y, current_font, CONFIG["font_color"], 0)

def stack_pattern(image, draw, font, emojis, img_size, scale_var):
    cols, rows = CONFIG["grid"]
    cell_w, cell_h = img_size[0] // cols, img_size[1] // rows
    
    for row in range(rows):
        for col in range(cols):
            emoji = random.choice(emojis)
            
            base_x = col * cell_w + cell_w // 2
            base_y = row * cell_h + cell_h // 2
            
            if row % 2 == 1:
                offset_x = base_x + cell_w // 2
                x = offset_x if offset_x < img_size[0] - cell_w // 2 else base_x - cell_w // 2
            else:
                x = base_x
            
            size_factor = 1.0 + random.uniform(-scale_var * 0.3, scale_var * 0.3)
            current_font = get_font(int(CONFIG["font_size"] * size_factor))
            draw_emoji_with_rotation(image, draw, emoji, x, base_y, current_font, CONFIG["font_color"], 0)

def sprinkle_pattern(image, draw, font, emojis, img_size, scale_var):
    placed_emojis = []
    attempts = 0
    max_attempts = CONFIG["emoji_count"] * 15
    
    while len(placed_emojis) < CONFIG["emoji_count"] and attempts < max_attempts:
        emoji = random.choice(emojis)
        x = random.randint(80, img_size[0] - 80)
        y = random.randint(80, img_size[1] - 80)
        
        size_factor = 0.6 + random.uniform(0, 1.0 + scale_var)
        current_font = get_font(int(CONFIG["font_size"] * size_factor))
        
        safe_x, safe_y = place_emoji_safely(placed_emojis, emoji, x, y, current_font, img_size)
        if safe_x is not None:
            rotation = random.randint(0, 360)
            draw_emoji_with_rotation(image, draw, emoji, safe_x, safe_y, current_font, CONFIG["font_color"], rotation)
        
        attempts += 1

def prism_pattern(image, draw, font, emojis, img_size, scale_var):
    placed_emojis = []
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
            current_font = get_font(int(CONFIG["font_size"] * size_factor))
            
            safe_x, safe_y = place_emoji_safely(placed_emojis, emoji, x, y, current_font, img_size, 15)
            if safe_x is not None:
                rotation = random.randint(-30, 30)
                draw_emoji_with_rotation(image, draw, emoji, safe_x, safe_y, current_font, CONFIG["font_color"], rotation)

PATTERNS = {
    "mosaic": mosaic_pattern,
    "lotus": lotus_pattern,
    "stack": stack_pattern,
    "sprinkle": sprinkle_pattern,
    "prism": prism_pattern
}

def generate_wallpaper():
    img = Image.new("RGB", CONFIG["img_size"], CONFIG["bg_color"])
    draw = ImageDraw.Draw(img)
    font = get_font(CONFIG["font_size"])

    pattern_func = PATTERNS.get(CONFIG["pattern"], mosaic_pattern)
    pattern_func(img, draw, font, CONFIG["emojis"], CONFIG["img_size"], CONFIG["scale_variation"])

    img.save("wallpaper.png")
    print(f"Wallpaper with {CONFIG['pattern']} pattern saved as wallpaper.png")

