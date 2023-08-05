import os

path = os.path.abspath(os.path.join(os.getcwd(), __file__))

class Config:
    page_bgcolour = (0, 0, 0)
    text_fgcolour = (255, 255, 255)
    title_fgcolour = (255, 55, 55)

    code_bgcolour = (50, 50, 50)
    code_fgcolour = (0, 255, 0)

    cursor_fgcolour = (200, 200, 255)

    data = os.path.join(os.path.split(os.path.split(path)[0])[0], 'data')
