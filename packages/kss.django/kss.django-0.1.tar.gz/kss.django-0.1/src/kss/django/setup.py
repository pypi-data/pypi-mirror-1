from kss.base import load_plugins as base_load_plugins

class run_once(object):
    '''Run a function only once'''

    def __init__(self, func):
        self.ran = False
        self.func = func

    def __call__(self, *args, **kwargs):
        if self.ran:
            return

        self.func(*args, **kwargs)
        self.ran = True

@run_once
def load_plugins(*plugins):
    base_load_plugins(*plugins)
