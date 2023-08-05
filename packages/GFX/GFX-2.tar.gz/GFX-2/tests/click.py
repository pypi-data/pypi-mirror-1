import random
import pygame
from pygame.locals import *
from gfx.mvc.engine import Engine
from gfx.ext import GLSurface, ImageLibrary
from gfx import gl

pygame.init()
pygame.font.init()
flags =  OPENGL|DOUBLEBUF|HWSURFACE
pygame.display.set_mode((1200,800), flags)
e = Engine((1280,800), step_size=100, max_frame_time=2000)
gl.enable_blend(True)

images = ImageLibrary(".")
images['ball.png']

positions  = {}
for x in xrange(0,1200,128):
    for y in xrange(0,800,128):
        positions[x,y] = True

texture_id = images['ball.png'].texture_id
d = [0.0]
def render(P):
    gl.clear()
    gl.reset_transform()
    gl.transform((d[0], 10.0), 45)
    d[0] += 0.1
    for pos in positions:
        if positions[pos]:
            gl.draw_quad(pos,[(-32,-32),(-32,32),(32,32),(32,-32)], texture_id=texture_id)
    pygame.display.flip()

def tick(step_size):
    pass

def mouse(event):
    positions[gl.world_coords(event.pos)] = True
    
e.connect('MouseButtonDown', mouse)
e.connect('Render', render)
e.connect('Tick', tick)

e.loop.start()
