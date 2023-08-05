
from bruce.page import Page

class SpawnPage(Page):
    def __init__(self, command, pause=True, repeat=False):
        self.run = False
        self.pause = pause
        self.command = command
        self.repeat = repeat

    def init(self, screen):
        pass

    def render(self, screen, deltat):
        from shell import spawner
        # We only allow a command
        if self.repeat or not self.run:
            spawner.spawn(self.command)
            self.run = True
        if not self.pause:
            return True
