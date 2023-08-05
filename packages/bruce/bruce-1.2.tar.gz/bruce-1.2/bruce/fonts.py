import os

import pygame

fonts = { }

def get_font(name, size, bold=False, italic=False):
    key = (name, bold, italic)
    f = fonts.get(key, {})
    if not size in f:
        if os.path.isfile(name):
            f[size] = pygame.font.Font(name, size)
        else:
            f[size] = pygame.font.SysFont(name, size, bold, italic)
        fonts[key] = f
    return f[size]

