import pygame
from pygame.locals import *
from gfx import gl
from gfx.mvc.engine import Engine
from gfx.mvc.view import root, Image, Group
from gfx.ext import GLSurface
from rect import quadtree, Rect
import random
import numpy


def note(s, color=(255,255,255)):
    fo = pygame.font.Font('Verdana.ttf', 32)
    return GLSurface(fo.render(s, True, color))
    

pygame.init()
flags =  OPENGL|DOUBLEBUF|HWSURFACE
pygame.display.set_mode((1280,800), flags)

pygame.font.init()


random.seed(1)
engine = Engine((1280,800), step_size=20)
index = quadtree.index(10000, depth=4)

for i in xrange(1000):
    x = random.randint(-100,100)
    y = random.randint(-100,100)
    x *= 100
    y *= 100
    img = Image(note("(%s, %s)" % (x,y)))
    img.rect.center = x,y
    root.add(img)
    index.insert(img, img.rect)

def interpolate(start, stop, time=1000.0):
    start = numpy.array(start)
    stop = numpy.array(stop)
    diff = stop - start
    current = numpy.array(start)
    dec = time
    while True:
        T = yield current
        d = T / time
        current += (diff * d)
        dec -= T 
        if dec <= 0:
            break

def draw(n, p):
    xy = n.rect.left, n.rect.bottom
    gl.draw_quad(xy, ((0,0),(0,n.rect.height), (n.rect.width, n.rect.height), (n.rect.width, 0)), texture_id=n.surface.texture_id)

camera = Rect((0,0,1280,800))
camera.last = Rect(camera)
camera.mover = None

def render(p):
    gl.clear()
    gl.reset_transform()
    x = camera.left - ((camera.last.left - camera.left) * p)
    y = camera.bottom - ((camera.last.bottom - camera.bottom) * p)
    gl.transform((-x,-y))
    images = index.query(camera)
    for i in images:
        draw(i, p)
    pygame.display.flip()

def click(event):
    xy = gl.world_coords(event.pos)
    camera.mover = interpolate(camera.center, xy)
    camera.center = camera.mover.next()
engine.connect('MouseButtonDown', click)

def tick(p):
    if camera.mover:
        try:
            camera.last = Rect(camera)
            camera.center = camera.mover.send(p)
        except StopIteration:
            camera.mover = None


engine.connect('Render', render)
engine.connect('Tick', tick)




engine.loop.start()

