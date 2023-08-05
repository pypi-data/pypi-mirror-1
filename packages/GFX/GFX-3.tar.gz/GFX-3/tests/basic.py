import pygame
from pygame.locals import *
from gfx import gl

pygame.init()
flags =  OPENGL|DOUBLEBUF|HWSURFACE
pygame.display.set_mode((800,600), flags)
gl.init((800,600))
image = pygame.image.load('ball.png')
texture_id = gl.load_texture(pygame.image.tostring(image, 'RGBA'), image.get_size())
running = True
w,h = image.get_size()
while running:
    if QUIT in (i.type for i in pygame.event.get()):
        running = False 
    gl.draw_quad((0,0),((0,0),(0,h),(w,h),(w,0)), texture_id=texture_id)
    pygame.display.flip()

