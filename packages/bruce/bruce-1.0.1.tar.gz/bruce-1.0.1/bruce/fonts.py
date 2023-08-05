import pygame

fonts = { }

def get_font(path, size):
    f = fonts.get(path, {})
    if not f.has_key(size):
        f[size] = pygame.font.Font(path, size)
    return f[size]
