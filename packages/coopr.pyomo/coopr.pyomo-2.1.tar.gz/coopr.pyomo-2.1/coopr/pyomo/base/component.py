
class Component(object):

    def __init__(self, ctype):
        self.active=True
        self._type=ctype
        self.model=None

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def type(self):
        return self._type

    def construct(self, data=None):
        pass

