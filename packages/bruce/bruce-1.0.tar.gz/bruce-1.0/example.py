from bruce.text import TextPage
from bruce.interp import InterpreterPage
from bruce.scratch_interp import ScratchPadInterpreterPage
from bruce.codefile import CodeFilePage
from bruce.image import ImagePage

opening_pages = '''
=Presentations In Python

Using Bruce
the Presentation Tool
---
=How do you make
=a presentation?

Edit some Python code
-Add text, image & code pages
-Create your own page types
-World domination is yours!
'''

def pages():
    l = []
    # some intro
    for page in opening_pages.split('---'):
        l.append(TextPage(page))

    l.append(InterpreterPage('Zen of Python', 'import this'))

    l.append(ScratchPadInterpreterPage('Draw to the Screen', '''
car = pygame.image.load('car.png')
car
scratch.blit(car, (100, 100))
rotated = pygame.transform.rotate(car, 45)
scratch.blit(rotated, (150, 150))
'''))

    l.append(CodeFilePage("Sample Presentation", 'example.py'))

    # examples
    l.extend([
        ImagePage("Sample Image", 'data/sample.jpg'),
        ImagePage("Sample Image", 'data/sample.jpg'),
    ])
    l.append(TextPage('''=Questions?

www.pygame.org
pyopengl.sf.net
home.gna.org/oomadness
www.imitationpickles.org/pgu
'''))
    return l

