

class AutoMixin(object):
    def __init__(self, *args, **kwargs):
        if 'timer' in kwargs:
            self._auto_timer = float(kwargs.get('timer'))
            del kwargs['timer']
        super(AutoMixin, self).__init__(*args, **kwargs)

    def render(self, screen, deltat):
        ret = super(AutoMixin, self).render(screen, deltat)
        if ret: return True
        self._auto_timer -= (deltat/1000.0)
        if self._auto_timer <= 0:
            return True
        
