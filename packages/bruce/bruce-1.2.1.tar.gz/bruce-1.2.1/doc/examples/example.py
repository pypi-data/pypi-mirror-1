from bruce.config import Config
Config.text_font = 'python_games/Vera.ttf'
Config.bold_font = 'python_games/VeraBd.ttf'
Config.code_font = 'python_games/VeraMono.ttf'
from bruce.main import main
from bruce.pages import *

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

pages = []
for page in opening_pages.split('---'):
    pages.append(TextPage(page))

pages.append(InterpreterPage('Zen of Python', 'import this'))

pages.append(ScratchPadInterpreterPage('Draw to the Screen', '''
car = pygame.image.load('python_games/car.png')
car
scratch.blit(car, (100, 100))
rotated = pygame.transform.rotate(car, 45)
scratch.blit(rotated, (150, 150))
'''))

pages.append(CodeFilePage("Sample Presentation", 'example.py'))

pages.extend([
    ImagePage("Sample Image", 'sample.jpg'),
    ImagePage("Sample Image", 'sample.jpg'),
])
pages.append(TextPage('''=Questions?

www.pygame.org
pyopengl.sf.net
home.gna.org/oomadness
www.imitationpickles.org/pgu
'''))

main(pages)
