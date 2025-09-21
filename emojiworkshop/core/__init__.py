class RGB(tuple):
    def __new__(cls, r, g, b):
        return super(RGB, cls).__new__(cls, (r, g, b))

    def __repr__(self):
        return f"RGB({self[0]}, {self[1]}, {self[2]})"

    def to_hex(self):
        return '#{:02x}{:02x}{:02x}'.format(self[0], self[1], self[2])


class Color:
    DEFAULT_BACKGROUND = RGB(255, 255, 255)
    DEFAULT_FOREGROUND = RGB(0, 0, 0)

    def __init__(self, background=None, foreground=None):
        self.background = background or self.DEFAULT_BACKGROUND
        self.foreground = foreground or self.DEFAULT_FOREGROUND
