
import pygame
from pygame.locals import *
from gfx import gl

pygame.init()
flags =  OPENGL|DOUBLEBUF|HWSURFACE
pygame.display.set_mode((1200,800), flags)
img = pygame.image.load("land.jpg")
texture = gl.load_texture(pygame.image.tostring(img, 'RGBA', True), img.get_size())
gl.set_viewport(0,0,1200,800)

running = True
while running:
    for event in pygame.event.get():
        if event.type is QUIT:
            running = False 
    gl.clear()
    gl.draw_quad([(-100.0,-100.0),(-100.0,100.0),(100.0,100.0),(100.0,-100.0)], rgba=(0.0,1.0,1.0,0.2), texture_id=texture)
    pygame.display.flip()

gl.unload_texture(texture)

