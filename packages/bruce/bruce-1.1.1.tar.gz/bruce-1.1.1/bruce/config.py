import os

path = os.path.abspath(os.path.join(os.getcwd(), __file__))

class Config:
    # colour specifications
    page_bgcolour = (0, 0, 0)
    text_fgcolour = (255, 255, 255)
    title_fgcolour = (255, 55, 55)      # kinda red-pink-ish
    code_bgcolour = (50, 50, 50)
    code_fgcolour = (0, 255, 0)
    cursor_fgcolour = (200, 200, 255)

    # fonts may be a list of system font names or a font file name
    text_font = 'Vera,Helvetica,Arial'
    title_font = 'Vera,Helvetica,Arial'
    code_font = 'VeraMono,Monaco'       # (Monaco is an Apple font)
    # if not defined, we use the above text_font system font with bold=True
    bold_font = None

