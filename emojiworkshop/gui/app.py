#!/usr/bin/env python3
"""
Emoji Workshop Advanced GUI with Improvements

Advanced GUI with sidebar layout plus the requested improvements:
- Scrollable sidebar for small windows
- Direct emoji editing without button
- Proper fonts (NotoEmoji-Bold for emojis, GoogleSansCode for UI)
- Custom resolution support
- Improved preview quality
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import random
import threading
import os
from typing import Tuple
import time
import re

from emojiworkshop.core.pattern import Pattern
from emojiworkshop.core.colors import ColorPalettes
from emojiworkshop.core.generator import generate_wallpaper_with_config


# Set appearance mode and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Font paths
EMOJI_FONT_PATH = "assets/NotoEmoji-Bold.ttf"
UI_FONT_PATH = "assets/GoogleSansCode-Regular.ttf"


class WorkshopGUI:
    """Advanced GUI with sidebar layout and improvements."""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Emoji Workshop - Advanced GUI")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Application state
        self.selected_emojis = ["👀", "✨", "🦖", "🐈‍⬛", "🐧", "🦀"]
        self.selected_pattern = Pattern.MOSAIC
        self.selected_color = ColorPalettes.GRAY
        self.current_config = None
        self.generation_in_progress = False
        
        # Settings
        self.count_var = ctk.IntVar(value=200)
        self.scale_var = ctk.DoubleVar(value=0.7)
        self.font_size_var = ctk.IntVar(value=96)
        self.resolution_var = ctk.StringVar(value="1920x1080")
        self.custom_width_var = ctk.IntVar(value=1920)
        self.custom_height_var = ctk.IntVar(value=1080)
        self.use_custom_resolution = ctk.BooleanVar(value=False)
        
        self.color_options = {
            "Gray": ColorPalettes.GRAY,
            "Blue": ColorPalettes.BLUE,
            "Ultramarine": ColorPalettes.ULTRAMARINE,
            "Red": ColorPalettes.RED,
            "Orange": ColorPalettes.ORANGE,
            "Yellow": ColorPalettes.YELLOW,
            "Pink": ColorPalettes.PINK,
            "Beige": ColorPalettes.BEIGE,
        }
        
        # Pattern previews
        self.pattern_buttons = {}
        self.color_buttons = {}
        
        self.setup_ui()
        self.create_pattern_previews()
        self.update_background()
    
    def setup_ui(self):
        """Set up the advanced user interface with sidebar."""
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create scrollable sidebar
        self.setup_scrollable_sidebar()
        
        # Main preview area
        self.setup_main_area()
        
        # Status bar
        self.setup_status_bar()
        
        # Bind events
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_scrollable_sidebar(self):
        """Set up scrollable sidebar container with mouse wheel support."""
        # Create sidebar frame with shadow effect
        self.sidebar_container = ctk.CTkFrame(
            self.root, 
            width=320, 
            corner_radius=0,
            fg_color=("gray92", "gray14"),
            border_width=2,
            border_color=("gray80", "gray25")
        )
        self.sidebar_container.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_container.grid_propagate(False)
        self.sidebar_container.grid_columnconfigure(0, weight=1)
        self.sidebar_container.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame with improved styling
        self.sidebar_scroll = ctk.CTkScrollableFrame(
            self.sidebar_container,
            width=300,
            corner_radius=8,
            fg_color=("gray95", "gray11"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.sidebar_scroll.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.sidebar_scroll.grid_columnconfigure(0, weight=1)
        
        # Enable mouse wheel scrolling
        self.enable_mouse_wheel_scrolling()
        
        self.sidebar = self.sidebar_scroll  # Reference for compatibility
        
        # Setup sidebar content
        self.setup_sidebar_content()
    
    def enable_mouse_wheel_scrolling(self):
        """Enable mouse wheel scrolling for the sidebar."""
        def on_mouse_wheel(event):
            # Check if mouse is over sidebar area
            try:
                widget_under_mouse = self.root.winfo_containing(event.x_root, event.y_root)
                if widget_under_mouse and self.is_widget_in_sidebar(widget_under_mouse):
                    # Scroll the sidebar
                    self.sidebar_scroll._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass  # Ignore errors during scrolling
        
        def on_mouse_wheel_linux_up(event):
            try:
                widget_under_mouse = self.root.winfo_containing(event.x_root, event.y_root)
                if widget_under_mouse and self.is_widget_in_sidebar(widget_under_mouse):
                    self.sidebar_scroll._parent_canvas.yview_scroll(-1, "units")
            except Exception:
                pass
        
        def on_mouse_wheel_linux_down(event):
            try:
                widget_under_mouse = self.root.winfo_containing(event.x_root, event.y_root)
                if widget_under_mouse and self.is_widget_in_sidebar(widget_under_mouse):
                    self.sidebar_scroll._parent_canvas.yview_scroll(1, "units")
            except Exception:
                pass
        
        # Bind mouse wheel events
        self.root.bind("<MouseWheel>", on_mouse_wheel)  # Windows/Mac
        self.root.bind("<Button-4>", on_mouse_wheel_linux_up)  # Linux scroll up
        self.root.bind("<Button-5>", on_mouse_wheel_linux_down)  # Linux scroll down
    
    def is_widget_in_sidebar(self, widget):
        """Check if a widget is inside the sidebar."""
        try:
            # Walk up the widget hierarchy to check if it's in sidebar
            current = widget
            while current:
                if current == self.sidebar_scroll or current == self.sidebar_container:
                    return True
                try:
                    current = current.master
                except AttributeError:
                    break
            return False
        except Exception:
            return False
    
    def setup_sidebar_content(self):
        """Set up the content of the scrollable sidebar."""
        
        # Logo/Title
        try:
            ui_font = ctk.CTkFont(family="GoogleSansCode", size=20, weight="bold")
        except Exception:
            ui_font = ctk.CTkFont(size=20, weight="bold")
            
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="🎨 Emoji Workshop",
            font=ui_font
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Quick actions
        self.setup_quick_actions()
        
        # Emoji selection
        self.setup_emoji_section()
        
        # Pattern selection
        self.setup_pattern_section()
        
        # Color selection
        self.setup_color_section()
        
        # Advanced settings
        self.setup_advanced_settings()
    
    def setup_quick_actions(self):
        """Set up quick action buttons with enhanced styling."""
        actions_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=("gray88", "gray17"),
            corner_radius=12,
            border_width=1,
            border_color=("gray75", "gray28")
        )
        actions_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=10)
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.randomize_btn = ctk.CTkButton(
            actions_frame,
            text="🎲 Random",
            command=self.randomize_selection,
            font=ctk.CTkFont(weight="bold"),
            height=40,
            corner_radius=10,
            fg_color=("gray70", "gray35"),
            hover_color=("gray60", "gray45"),
            border_width=2,
            border_color=("gray60", "gray40")
        )
        self.randomize_btn.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        
        self.generate_btn = ctk.CTkButton(
            actions_frame,
            text="✨ Generate",
            command=self.generate_wallpaper,
            font=ctk.CTkFont(weight="bold"),
            height=40,
            corner_radius=10,
            fg_color=("#2E7D32", "#4CAF50"),
            hover_color=("#1B5E20", "#66BB6A"),
            border_width=2,
            border_color=("#388E3C", "#4CAF50")
        )
        self.generate_btn.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
    
    def setup_emoji_section(self):
        """Set up direct emoji editing with enhanced styling."""
        try:
            ui_font = ctk.CTkFont(family="GoogleSansCode", size=16, weight="bold")
        except Exception:
            ui_font = ctk.CTkFont(size=16, weight="bold")
            
        emoji_label = ctk.CTkLabel(
            self.sidebar,
            text="🎯 Emojis",
            font=ui_font,
            text_color=("gray20", "gray80")
        )
        emoji_label.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # Enhanced emoji input frame with depth
        emoji_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=("gray88", "gray17"),
            corner_radius=12,
            border_width=2,
            border_color=("gray75", "gray28")
        )
        emoji_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=5)
        emoji_frame.grid_columnconfigure(0, weight=1)
        
        # Instructions with better styling
        try:
            instruction_font = ctk.CTkFont(family="GoogleSansCode", size=10)
        except Exception:
            instruction_font = ctk.CTkFont(size=10)
            
        instruction_label = ctk.CTkLabel(
            emoji_frame,
            text="📝 Enter emojis (Win+. / Cmd+Space / Ctrl+.)",
            font=instruction_font,
            text_color=("gray50", "gray60")
        )
        instruction_label.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")
        
        # Enhanced emoji input textbox
        self.emoji_input = ctk.CTkTextbox(
            emoji_frame,
            height=70,
            width=280,
            font=ctk.CTkFont(size=16),
            corner_radius=8,
            border_width=2,
            border_color=("gray70", "gray35"),
            fg_color=("white", "gray20")
        )
        self.emoji_input.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        
        # Set initial content
        current_text = " ".join(self.selected_emojis)
        self.emoji_input.insert("1.0", current_text)
        
        # Bind to update on text change
        self.emoji_input.bind("<KeyRelease>", self.on_emoji_text_change)
        self.emoji_input.bind("<Button-1>", self.on_emoji_text_change)
        self.emoji_input.bind("<FocusOut>", self.on_emoji_text_change)
        
        # Enhanced count display
        self.emoji_count_label = ctk.CTkLabel(
            emoji_frame,
            text=f"✅ {len(self.selected_emojis)} emojis selected",
            font=instruction_font,
            text_color=("gray50", "gray60")
        )
        self.emoji_count_label.grid(row=2, column=0, padx=15, pady=(8, 15), sticky="w")
    
    def setup_pattern_section(self):
        """Set up pattern selection with previews and enhanced styling."""
        try:
            ui_font = ctk.CTkFont(family="GoogleSansCode", size=16, weight="bold")
        except Exception:
            ui_font = ctk.CTkFont(size=16, weight="bold")
            
        pattern_label = ctk.CTkLabel(
            self.sidebar,
            text="🎨 Patterns",
            font=ui_font,
            text_color=("gray20", "gray80")
        )
        pattern_label.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # Enhanced patterns frame with depth
        patterns_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=("gray88", "gray17"),
            corner_radius=12,
            border_width=2,
            border_color=("gray75", "gray28")
        )
        patterns_frame.grid(row=5, column=0, sticky="ew", padx=15, pady=5)
        patterns_frame.grid_columnconfigure((0, 1), weight=1)
        
        patterns = [
            (Pattern.MOSAIC, "Mosaic"),
            (Pattern.LOTUS, "Lotus"),
            (Pattern.STACK, "Stack"),
            (Pattern.SPRINKLE, "Sprinkle")
        ]
        
        for i, (pattern, name) in enumerate(patterns):
            row, col = divmod(i, 2)
            
            # Enhanced pattern frame with shadow effect
            pattern_frame = ctk.CTkFrame(
                patterns_frame,
                corner_radius=10,
                fg_color=("white", "gray20"),
                border_width=2,
                border_color=("gray70", "gray35")
            )
            pattern_frame.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
            pattern_frame.grid_columnconfigure(0, weight=1)
            
            # High-quality preview with better styling
            preview_label = ctk.CTkLabel(
                pattern_frame,
                text="⏳",  # Loading indicator
                width=135,
                height=85,
                fg_color=("gray95", "gray25"),
                corner_radius=8,
                font=ctk.CTkFont(size=24)
            )
            preview_label.grid(row=0, column=0, padx=8, pady=(8, 4))
            
            # Enhanced pattern button
            try:
                btn_font = ctk.CTkFont(family="GoogleSansCode", size=11, weight="bold")
            except Exception:
                btn_font = ctk.CTkFont(size=11, weight="bold")
                
            btn = ctk.CTkButton(
                pattern_frame,
                text=name,
                command=lambda p=pattern: self.select_pattern(p),
                height=32,
                corner_radius=8,
                font=btn_font,
                fg_color=("gray75", "gray30"),
                hover_color=("gray65", "gray40"),
                border_width=1,
                border_color=("gray60", "gray35")
            )
            btn.grid(row=1, column=0, padx=8, pady=(4, 8), sticky="ew")
            
            self.pattern_buttons[pattern] = {"button": btn, "preview": preview_label}
        
        self.update_pattern_buttons()
    
    def setup_color_section(self):
        """Set up color selection with emoji previews."""
        try:
            ui_font = ctk.CTkFont(family="GoogleSansCode", size=16, weight="bold")
        except Exception:
            ui_font = ctk.CTkFont(size=16, weight="bold")
            
        color_label = ctk.CTkLabel(
            self.sidebar,
            text="Colors",
            font=ui_font
        )
        color_label.grid(row=6, column=0, padx=20, pady=(20, 5), sticky="w")
        
        colors_frame = ctk.CTkFrame(self.sidebar)
        colors_frame.grid(row=7, column=0, sticky="ew", padx=15, pady=5)
        colors_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        preview_emoji = "😊"
        for i, (name, palette) in enumerate(self.color_options.items()):
            row, col = divmod(i, 4)
            
            bg_color = self.rgb_to_hex(palette.background)
            fg_color = self.rgb_to_hex(palette.foreground)
            
            btn = ctk.CTkButton(
                colors_frame,
                text=preview_emoji,
                command=lambda p=palette: self.select_color(p),
                width=60,
                height=60,
                corner_radius=30,
                fg_color=bg_color,
                hover_color=self.adjust_color_brightness(bg_color, 0.8),
                border_width=3,
                border_color=fg_color,
                text_color=fg_color,
                font=ctk.CTkFont(size=18)
            )
            btn.grid(row=row, column=col, padx=3, pady=3)
            
            # Color name with UI font
            if row == 0 or (row == 1 and col < len(self.color_options) % 4):
                try:
                    name_font = ctk.CTkFont(family="GoogleSansCode", size=8)
                except Exception:
                    name_font = ctk.CTkFont(size=8)
                    
                name_label = ctk.CTkLabel(
                    colors_frame,
                    text=name,
                    font=name_font
                )
                name_label.grid(row=row*2+1, column=col, pady=(0, 5))
            
            self.color_buttons[palette] = btn
        
        self.update_color_buttons()
    
    def setup_advanced_settings(self):
        """Set up advanced settings section with custom resolution."""
        try:
            ui_font = ctk.CTkFont(family="GoogleSansCode", size=16, weight="bold")
            label_font = ctk.CTkFont(family="GoogleSansCode", size=12)
            value_font = ctk.CTkFont(family="GoogleSansCode", size=11)
        except Exception:
            ui_font = ctk.CTkFont(size=16, weight="bold")
            label_font = ctk.CTkFont(size=12)
            value_font = ctk.CTkFont(size=11)
            
        settings_label = ctk.CTkLabel(
            self.sidebar,
            text="Settings",
            font=ui_font
        )
        settings_label.grid(row=8, column=0, padx=20, pady=(20, 5), sticky="w")
        
        settings_frame = ctk.CTkFrame(self.sidebar)
        settings_frame.grid(row=9, column=0, sticky="ew", padx=15, pady=5)
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Emoji count
        count_label = ctk.CTkLabel(settings_frame, text="Count:", font=label_font)
        count_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.count_slider = ctk.CTkSlider(
            settings_frame,
            from_=50,
            to=500,
            number_of_steps=45,
            variable=self.count_var,
            command=self.on_setting_change
        )
        self.count_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.count_value_label = ctk.CTkLabel(settings_frame, text="200", font=value_font)
        self.count_value_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Scale variation
        scale_label = ctk.CTkLabel(settings_frame, text="Scale:", font=label_font)
        scale_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.scale_slider = ctk.CTkSlider(
            settings_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19,
            variable=self.scale_var,
            command=self.on_setting_change
        )
        self.scale_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        self.scale_value_label = ctk.CTkLabel(settings_frame, text="0.7", font=value_font)
        self.scale_value_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Font size
        font_label = ctk.CTkLabel(settings_frame, text="Font:", font=label_font)
        font_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.font_slider = ctk.CTkSlider(
            settings_frame,
            from_=24,
            to=200,
            number_of_steps=44,
            variable=self.font_size_var,
            command=self.on_setting_change
        )
        self.font_slider.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        self.font_value_label = ctk.CTkLabel(settings_frame, text="96", font=value_font)
        self.font_value_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Resolution section
        res_label = ctk.CTkLabel(settings_frame, text="Resolution:", font=label_font)
        res_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        # Preset resolution dropdown
        self.resolution_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["1920x1080", "2560x1440", "3840x2160", "1366x768", "Custom"],
            variable=self.resolution_var,
            command=self.on_resolution_change,
            width=120,
            height=25,
            font=value_font
        )
        self.resolution_menu.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Custom resolution frame (initially hidden)
        self.custom_res_frame = ctk.CTkFrame(settings_frame)
        self.custom_res_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        self.custom_res_frame.grid_columnconfigure((1, 3), weight=1)
        self.custom_res_frame.grid_remove()  # Hide initially
        
        width_label = ctk.CTkLabel(self.custom_res_frame, text="W:", font=value_font)
        width_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.width_entry = ctk.CTkEntry(
            self.custom_res_frame, 
            textvariable=self.custom_width_var,
            width=80,
            font=value_font
        )
        self.width_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        height_label = ctk.CTkLabel(self.custom_res_frame, text="H:", font=value_font)
        height_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.height_entry = ctk.CTkEntry(
            self.custom_res_frame,
            textvariable=self.custom_height_var, 
            width=80,
            font=value_font
        )
        self.height_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Bind custom resolution changes
        self.width_entry.bind("<KeyRelease>", self.on_custom_resolution_change)
        self.height_entry.bind("<KeyRelease>", self.on_custom_resolution_change)
    
    def setup_main_area(self):
        """Set up the main preview area with enhanced styling."""
        # Enhanced main frame with depth
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            fg_color=("gray90", "gray15"),
            border_width=2,
            border_color=("gray75", "gray25")
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Enhanced preview area with shadow effect
        self.preview_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=12,
            fg_color=("white", "gray10"),
            border_width=3,
            border_color=("gray70", "gray30")
        )
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)
        
        # Canvas for background with better styling
        self.canvas = ctk.CTkCanvas(
            self.preview_frame,
            highlightthickness=0,
            bg=("white" if ctk.get_appearance_mode() == "Light" else "#1a1a1a")
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        
        # Enhanced loading overlay
        self.loading_frame = ctk.CTkFrame(
            self.preview_frame, 
            fg_color=("gray92", "gray18"),
            corner_radius=10,
            border_width=2,
            border_color=("gray80", "gray25")
        )
        self.loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="🎨 Generating Preview...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray30", "gray70")
        )
        self.loading_label.pack(pady=25, padx=25)
        self.loading_frame.place_forget()
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.status_frame.grid(row=1, column=1, sticky="ew", padx=0, pady=0)
        self.status_frame.grid_propagate(False)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.progress_bar.set(0)
    
    def create_pattern_previews(self):
        """Create high-quality preview thumbnails for each pattern with better error handling."""
        preview_emojis = ["🔵", "🟢", "🟡"]
        
        for pattern in Pattern:
            try:
                # Higher resolution preview for better quality with fixed paths
                preview_config = {
                    "emojis": preview_emojis,
                    "img_size": (270, 170),  # Higher resolution for crisp previews
                    "font_path": EMOJI_FONT_PATH,
                    "font_size": 28,
                    "grid": (7, 5),
                    "pattern": pattern,
                    "scale_variation": 0.3,
                    "emoji_count": 20,
                    "color": ColorPalettes.GRAY,
                    "margin": 3,
                    "output_filename": f"preview_{pattern.pattern_name}_{id(self)}.png"  # Unique filename
                }
                
                def create_preview(config, pat):
                    try:
                        # Add delay to avoid race conditions
                        time.sleep(random.uniform(0.1, 0.3))
                        generate_wallpaper_with_config(config)
                        # Schedule loading on main thread
                        self.root.after(100, lambda p=pat, f=config["output_filename"]: self.load_pattern_preview(p, f))
                    except Exception as e:
                        print(f"Preview generation failed for {pat}: {e}")
                        # Set error state on main thread
                        self.root.after(0, lambda p=pat: self.set_pattern_preview_error(p))
                
                # Start generation in background
                threading.Thread(
                    target=create_preview, 
                    args=(preview_config, pattern), 
                    daemon=True
                ).start()
                
            except Exception as e:
                print(f"Failed to create preview for {pattern}: {e}")
                self.set_pattern_preview_error(pattern)
    
    def set_pattern_preview_error(self, pattern: Pattern):
        """Set error state for pattern preview."""
        try:
            if pattern in self.pattern_buttons:
                preview_label = self.pattern_buttons[pattern]["preview"]
                preview_label.configure(text="❌", font=ctk.CTkFont(size=20))
        except Exception as e:
            print(f"Failed to set error state for {pattern}: {e}")
    
    def load_pattern_preview(self, pattern: Pattern, filename: str):
        """Load a pattern preview image with improved error handling."""
        try:
            if not os.path.exists(filename):
                print(f"Preview file not found: {filename}")
                self.set_pattern_preview_error(pattern)
                return
                
            if pattern not in self.pattern_buttons:
                print(f"Pattern button not found: {pattern}")
                return
            
            # Load and process image
            image = Image.open(filename)
            # Use high-quality resampling with proper size
            image = image.resize((135, 85), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Update preview label
            preview_label = self.pattern_buttons[pattern]["preview"]
            preview_label.configure(image=photo, text="")
            preview_label.image = photo  # Keep reference to prevent garbage collection
            
            # Clean up file
            try:
                os.remove(filename)
            except Exception as cleanup_error:
                print(f"Failed to cleanup preview file {filename}: {cleanup_error}")
                
        except Exception as e:
            print(f"Failed to load preview for {pattern}: {e}")
            self.set_pattern_preview_error(pattern)
    
    def on_emoji_text_change(self, event=None):
        """Handle emoji text changes in real-time."""
        if hasattr(self, '_emoji_update_timer'):
            self.root.after_cancel(self._emoji_update_timer)
        
        self._emoji_update_timer = self.root.after(500, self.update_emojis_from_text)
    
    def update_emojis_from_text(self):
        """Update emoji selection from text input."""
        try:
            text_content = self.emoji_input.get("1.0", "end-1c")
            
            # Enhanced emoji pattern matching
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map
                "\U0001F1E0-\U0001F1FF"  # flags
                "\U00002702-\U000027B0"  # dingbats
                "\U000024C2-\U0001F251"  # enclosed chars
                "\U0001F900-\U0001F9FF"  # supplemental symbols
                "\U0001FA70-\U0001FAFF"  # extended pictographs
                "]+", 
                flags=re.UNICODE
            )
            
            emojis = emoji_pattern.findall(text_content)
            
            # Also check for individual characters that might be emojis
            words = text_content.split()
            for word in words:
                if len(word) == 1 and ord(word) > 127:
                    if word not in emojis:
                        emojis.append(word)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_emojis = []
            for emoji in emojis:
                if emoji not in seen:
                    seen.add(emoji)
                    unique_emojis.append(emoji)
            
            # Limit to 30 emojis
            if len(unique_emojis) > 30:
                unique_emojis = unique_emojis[:30]
            
            if unique_emojis and unique_emojis != self.selected_emojis:
                self.selected_emojis = unique_emojis
                self.emoji_count_label.configure(text=f"✅ {len(self.selected_emojis)} emojis selected")
                self.schedule_background_update()
            elif not unique_emojis and self.selected_emojis:
                # Keep at least one emoji to avoid errors
                pass
                
        except Exception as e:
            print(f"Failed to update emojis from text: {e}")
            # Don't change emojis if there's an error
    
    def on_resolution_change(self, value):
        """Handle resolution dropdown change."""
        if value == "Custom":
            self.use_custom_resolution.set(True)
            self.custom_res_frame.grid()
        else:
            self.use_custom_resolution.set(False)
            self.custom_res_frame.grid_remove()
        self.schedule_background_update()
    
    def on_custom_resolution_change(self, event=None):
        """Handle custom resolution input changes."""
        if hasattr(self, '_res_update_timer'):
            self.root.after_cancel(self._res_update_timer)
        
        self._res_update_timer = self.root.after(800, self.schedule_background_update)
    
    def get_current_resolution(self):
        """Get the current resolution as (width, height)."""
        if self.use_custom_resolution.get():
            try:
                width = max(100, self.custom_width_var.get())
                height = max(100, self.custom_height_var.get())
                return (width, height)
            except Exception:
                return (1920, 1080)  # fallback
        else:
            res_str = self.resolution_var.get()
            if "x" in res_str:
                try:
                    width, height = map(int, res_str.split('x'))
                    return (width, height)
                except Exception:
                    return (1920, 1080)
            return (1920, 1080)
    
    def rgb_to_hex(self, rgb_tuple: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color string."""
        return f"#{rgb_tuple[0]:02x}{rgb_tuple[1]:02x}{rgb_tuple[2]:02x}"
    
    def adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust brightness of a hex color."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, int(c * factor))) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
        # Also remove old functions that are no longer needed
        pass
    
    def update_pattern_buttons(self):
        """Update pattern button styling."""
        for pattern, widgets in self.pattern_buttons.items():
            button = widgets["button"]
            if pattern == self.selected_pattern:
                button.configure(fg_color=("gray70", "gray30"), border_width=2, border_color=("blue", "lightblue"))
            else:
                button.configure(fg_color=("gray85", "gray20"), border_width=0)
    
    def update_color_buttons(self):
        """Update color button styling."""
        for palette, button in self.color_buttons.items():
            if palette == self.selected_color:
                button.configure(border_width=4)
            else:
                button.configure(border_width=3)
    
    def select_pattern(self, pattern: Pattern):
        """Select a pattern."""
        self.selected_pattern = pattern
        self.update_pattern_buttons()
        self.schedule_background_update()
    
    def select_color(self, color_palette):
        """Select a color palette."""
        self.selected_color = color_palette
        self.update_color_buttons()
        self.schedule_background_update()
    
    def on_setting_change(self, value):
        """Handle setting changes."""
        self.count_value_label.configure(text=str(int(self.count_var.get())))
        self.scale_value_label.configure(text=f"{self.scale_var.get():.1f}")
        self.font_value_label.configure(text=str(int(self.font_size_var.get())))
        self.schedule_background_update()
    
    def randomize_selection(self):
        """Randomize all selections and update text input."""
        all_emojis = ["👀", "✨", "🦖", "🐈‍⬛", "🐧", "🦀", "🎨", "🚀", "💎", "🌟",
                      "🦄", "🌈", "🎯", "🔥", "⚡", "🌊", "🍕", "🎵", "📱", "💻",
                      "🎮", "📷", "🎧", "⌚", "🛒", "🔮", "🎪", "🎭", "❤️", "💛"]
        count = random.randint(4, 12)
        self.selected_emojis = random.sample(all_emojis, count)
        
        # Update the text input
        emoji_text = " ".join(self.selected_emojis)
        self.emoji_input.delete("1.0", "end")
        self.emoji_input.insert("1.0", emoji_text)
        
        self.selected_pattern = random.choice(list(Pattern))
        self.selected_color = random.choice(list(self.color_options.values()))
        
        self.count_var.set(random.randint(100, 400))
        self.scale_var.set(round(random.uniform(0.3, 1.5), 1))
        
        self.emoji_count_label.configure(text=f"{len(self.selected_emojis)} emojis selected")
        self.update_pattern_buttons()
        self.update_color_buttons()
        self.on_setting_change(None)
        self.schedule_background_update()
    
    def schedule_background_update(self):
        """Schedule background update with debouncing."""
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        
        self._update_timer = self.root.after(400, self.update_background)
    
    def update_background(self):
        """Update background preview with improved quality and error handling."""
        if self.generation_in_progress:
            return
        
        try:
            width, height = self.get_current_resolution()
            
            # Better preview scaling with minimum quality thresholds
            canvas_width = max(400, self.canvas.winfo_width())
            canvas_height = max(300, self.canvas.winfo_height())
            
            preview_scale = min(canvas_width/width, canvas_height/height) * 0.8
            preview_width = max(400, int(width * preview_scale))
            preview_height = max(300, int(height * preview_scale))
            
            # Ensure we have valid emojis
            if not self.selected_emojis:
                self.selected_emojis = ["😊", "🎨", "✨"]
            
            config = {
                "emojis": self.selected_emojis,
                "img_size": (preview_width, preview_height),
                "font_path": EMOJI_FONT_PATH,
                "font_size": max(32, int(self.font_size_var.get() * preview_scale)),
                "grid": (max(8, int(preview_width/80)), max(6, int(preview_height/80))),
                "pattern": self.selected_pattern,
                "scale_variation": self.scale_var.get(),
                "emoji_count": min(100, max(20, int(self.count_var.get() * 0.5))),
                "color": self.selected_color,
                "margin": 6,
                "output_filename": f"main_preview_{id(self)}.png"
            }
            
            self.current_config = config
            self.show_loading(True, "🎨 Generating preview...")
            
            def generate():
                try:
                    self.generation_in_progress = True
                    time.sleep(0.1)  # Small delay to show loading state
                    generate_wallpaper_with_config(config)
                    self.root.after(50, self.load_background_preview)
                except Exception as e:
                    print(f"Preview generation failed: {e}")
                    error_msg = str(e)
                    self.root.after(0, lambda: self.show_loading(False))
                    self.root.after(0, lambda: self.show_preview_error(error_msg))
                finally:
                    self.generation_in_progress = False
            
            threading.Thread(target=generate, daemon=True).start()
            
        except Exception as e:
            print(f"Failed to start preview generation: {e}")
            self.show_loading(False)
    
    def show_preview_error(self, error_msg: str):
        """Show preview error in canvas."""
        try:
            self.canvas.delete("all")
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # Draw error message
                self.canvas.create_text(
                    canvas_width//2, canvas_height//2,
                    text=f"❌ Preview Error\n{error_msg[:100]}...",
                    font=("Arial", 14),
                    fill="red",
                    justify="center"
                )
        except Exception as e:
            print(f"Failed to show preview error: {e}")
    
    def show_loading(self, show: bool, message: str = "Loading..."):
        """Show/hide loading overlay."""
        if show:
            self.loading_label.configure(text=message)
            self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.progress_bar.set(0.5)
            self.status_label.configure(text=message)
        else:
            self.loading_frame.place_forget()
            self.progress_bar.set(0)
            self.status_label.configure(text="Ready")
    
    def load_background_preview(self):
        """Load generated preview with better error handling."""
        try:
            filename = f"main_preview_{id(self)}.png"
            if os.path.exists(filename):
                image = Image.open(filename)
                self.tile_background(image)
                self.show_loading(False)
                self.status_label.configure(text="✅ Preview updated")
                
                # Cleanup
                try:
                    os.remove(filename)
                except Exception as cleanup_error:
                    print(f"Failed to cleanup preview file: {cleanup_error}")
            else:
                # Fallback to legacy filename
                if os.path.exists("temp_preview.png"):
                    image = Image.open("temp_preview.png")
                    self.tile_background(image)
                    self.show_loading(False)
                    self.status_label.configure(text="✅ Preview updated")
                    os.remove("temp_preview.png")
                else:
                    self.show_loading(False)
                    self.show_preview_error("Preview file not found")
                    
        except Exception as e:
            print(f"Failed to load preview: {e}")
            self.show_loading(False)
            self.show_preview_error(f"Loading failed: {str(e)}")
    
    def tile_background(self, image: Image.Image):
        """Tile background image with improved scaling."""
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                self.root.after(100, lambda: self.tile_background(image))
                return
            
            self.canvas.delete("all")
            
            # Calculate optimal scaling
            scale_factor = min(canvas_width / image.width, canvas_height / image.height) * 0.92
            new_width = max(100, int(image.width * scale_factor))
            new_height = max(100, int(image.height * scale_factor))
            
            if new_width > 0 and new_height > 0:
                # Use high-quality resampling
                resized_image = image.resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized_image)
                
                # Center the image
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                
                self.canvas.create_image(x, y, anchor="nw", image=photo)
                self.canvas.image = photo  # Keep reference
                
                # Add subtle border
                self.canvas.create_rectangle(
                    x-1, y-1, x+new_width+1, y+new_height+1,
                    outline=("gray" if ctk.get_appearance_mode() == "Light" else "gray40"),
                    width=1
                )
                
        except Exception as e:
            print(f"Failed to tile background: {e}")
            self.show_preview_error(f"Display failed: {str(e)}")
    
    def generate_wallpaper(self):
        """Generate full resolution wallpaper."""
        width, height = self.get_current_resolution()
        
        config = {
            "emojis": self.selected_emojis,
            "img_size": (width, height),
            "font_path": EMOJI_FONT_PATH,
            "font_size": int(self.font_size_var.get()),
            "grid": (10, 12),
            "pattern": self.selected_pattern,
            "scale_variation": self.scale_var.get(),
            "emoji_count": int(self.count_var.get()),
            "color": self.selected_color,
            "margin": 10,
            "output_filename": f"wallpaper_{width}x{height}_{int(time.time())}.png"
        }
        
        self.show_loading(True, "Generating wallpaper...")
        
        def generate():
            try:
                generate_wallpaper_with_config(config)
                self.root.after(0, lambda: self.on_generation_complete(config["output_filename"]))
            except Exception as error:
                error_msg = str(error)
                self.root.after(0, lambda: self.on_generation_error(error_msg))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def on_generation_complete(self, filename: str):
        """Handle successful generation."""
        self.show_loading(False)
        self.status_label.configure(text=f"✅ Saved: {filename}")
        self.progress_bar.set(1.0)
        self.root.after(2000, lambda: self.progress_bar.set(0))
        
        # Success dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Success")
        dialog.geometry("350x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        label = ctk.CTkLabel(dialog, text=f"✅ Wallpaper saved!\n{filename}", font=ctk.CTkFont(size=12))
        label.pack(pady=20)
        
        ok_btn = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=80)
        ok_btn.pack(pady=10)
    
    def on_generation_error(self, error: str):
        """Handle generation error."""
        self.show_loading(False)
        self.status_label.configure(text="❌ Generation failed")
        print(f"Error: {error}")
    
    def on_window_resize(self, event):
        """Handle window resize."""
        if event.widget == self.root:
            self.schedule_background_update()
    
    def on_closing(self):
        """Clean up on close."""
        try:
            if os.path.exists("temp_preview.png"):
                os.remove("temp_preview.png")
        except Exception:
            pass
        self.root.destroy()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = WorkshopGUI()
    app.run()