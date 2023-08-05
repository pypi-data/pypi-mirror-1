import pygame
from gfx import gl
from gfx.mvc.controllers import Loop, GUIInput
from gfx.mvc.mediator import Mediator
from gfx.mvc.view import root


class Engine(object):
    def __init__(self, size, **kw):
        self.mediator = Mediator()
        self.loop = Loop(self.mediator, **kw)
        self.input = GUIInput(self.mediator)
        self.mediator.connect('HandleEvents', self.input.poll)
        self.mediator.connect('Quit', lambda e: self.loop.stop())
        self.connect = self.mediator.connect
        self.painter = Painter()
        gl.init(size)

