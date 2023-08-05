import os
from weakref import WeakValueDictionary

import pygame
from gfx import gl, array


class GLSurface(object):
    """
    Create a texture from a pygame.Surface instance.
    """
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


class ImageBatch(object):
    """
    Draw lots of quads in one operation.
    """
    def __init__(self, count, surface):
        """
        count: number of quads.
        surface: GLSurface of texture to use.
        """
        self.surface = surface
        self.count = count
        self.vertices, self.colors, self.texture_coords = array.quads(count)

    def velocities(self):
        pass

    def set_quad(self, index, vertices, colors=None, texture_coords=None):
        """
        Set vertices, colors and texture coords for an index.
        """
        if colors is None: colors = ((1.0,1.0,1.0,1.0),) * 4
        if texture_coords is None: texture_coords = (0.0,0.0),(0.0,1.0),(1.0,1.0),(1.0,0.0)
        assert len(vertices) == 4
        assert len(colors) == 4
        assert len(texture_coords) == 4
        start_index = index * 4
        for v,c,t in zip(vertices, colors, texture_coords):
            self.vertices[start_index] = v
            self.colors[start_index] = c
            self.texture_coords[start_index] = t
            start_index += 1

    def draw(self):
        """
        Draw the image batch.
        """
        array.draw(self.vertices, self.colors, self.texture_coords, self.surface.texture_id)



