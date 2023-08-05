import os
from weakref import WeakValueDictionary

import pygame
from gfx import gl


class GLSurface(object):
    def __init__(self, surface, type='RGBA', **kw):
        self.size = surface.get_size()
        self.texture_id = gl.load_texture(pygame.image.tostring(surface, type), self.size, type=type, **kw)

    def __del__(self):
        if hasattr(gl, 'delete'): gl.delete(self.texture_id)


class ImageLibrary(object):
    def __init__(self, dir, **kw):
        self.dir = dir
        self.kw = kw
        self.surfaces = WeakValueDictionary()

    def __getitem__(self, filename):
        if filename in self.surfaces:
            return self.surfaces[filename]
        surface = self.surfaces[filename] = GLSurface(pygame.image.load(os.path.join(self.dir, filename)), **self.kw)
        return surface
