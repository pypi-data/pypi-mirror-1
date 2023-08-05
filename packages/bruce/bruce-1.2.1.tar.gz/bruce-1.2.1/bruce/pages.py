
# convenience - list all page types here
from bruce.text import TextPage
from bruce.interp import InterpreterPage
from bruce.scratch_interp import ScratchPadInterpreterPage
from bruce.codefile import CodeFilePage
from bruce.image import ImagePage
from bruce.spawnpage import SpawnPage
from bruce.shellinterp import ShellInterpreterPage
from bruce.mixins import AutoMixin


def reinitPageConfig():
    import bruce.shellinterp
    bruce.shellinterp.init(True)


class AutoImagePage(AutoMixin, ImagePage, object):
    pass
class AutoTextPage(AutoMixin, TextPage, object):
    pass
class AutoCodeFilePage(AutoMixin, CodeFilePage, object):
    pass


