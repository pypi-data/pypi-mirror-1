import random
import pygame
from pygame.locals import *
from gfx.mvc.engine import Engine
from gfx.mvc.view import root, Image
from gfx.ext import GLSurface, ImageLibrary
from gfx import gl

pygame.init()
pygame.font.init()
flags =  OPENGL|DOUBLEBUF|HWSURFACE
pygame.display.set_mode((1200,800), flags)
e = Engine((1280,800), step_size=50, max_frame_time=2000)

images = ImageLibrary(".")

ball = Image(images['ball.png'])
root.add(ball)
ball.rect.left = 0.0
ball.rect.bottom = 0.0
ball.ox = 0.0
ball.oy = 0.0
ball.xd = 0.1
ball.yd = 0.1



def tick(step_size):
    if ball.rect.left > 1200-64 or ball.rect.left < 0: ball.xd *= -1
    if ball.rect.bottom > 800-64 or ball.rect.bottom < 0: ball.yd *= -1
    ball.ox,ball.oy = ball.rect.left, ball.rect.bottom
    ball.rect.left += (ball.xd*step_size)
    ball.rect.bottom += (ball.yd*step_size)
    
    

e.connect('Tick', tick)

e.loop.start()
