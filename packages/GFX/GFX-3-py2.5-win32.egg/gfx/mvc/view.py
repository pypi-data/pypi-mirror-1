from dag import Node, Composite, traverse

from gfx.ext import GLSurface
from rect import Rect



class Image(Node):
    def __init__(self, surface):
        assert isinstance(surface, GLSurface)
        self.surface = surface
        self.rect = Rect((0,0) + surface.size)

class Line(Node):
    pass

class Group(Composite):
    def get_rect(self):
        return Rect.union(i.rect for i in self.children)
    rect = property(get_rect)

class Root(Composite):
    pass


root = Root()


