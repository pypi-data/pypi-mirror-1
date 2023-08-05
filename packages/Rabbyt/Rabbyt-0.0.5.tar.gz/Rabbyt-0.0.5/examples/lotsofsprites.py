import random

import rabbyt
from rabbyt import lerp, wrap
import pygame
import os.path
rabbyt.data_directory = os.path.dirname(__file__)

rabbyt.init_display((640, 480))


sprites = []

r = lambda: random.random()-.5

for i in range(2400):
    s = rabbyt.Sprite("rounded_square.png")
    s.rgba = lerp((.5,.2,1,.2), (0,.8,0,.6), dt=3000*r()+2000, extend="reverse")

    s.x = wrap([-320,320], lerp(r()*640, r()*640, dt=2000, extend="extrapolate"))
    s.y = wrap([-240,240], lerp(r()*480, r()*480, dt=2000, extend="extrapolate"))

    s.scale = lerp(.1, 1, dt=1000*r()+750, extend="reverse")

    s.rot = lerp(0, 360, dt=2000, extend="extrapolate")

    sprites.append(s)

print "Drawing 2400 sprites..."

c = pygame.time.Clock()
last_fps = 0
while not pygame.event.peek(pygame.QUIT):
    c.tick()
    if pygame.time.get_ticks() - last_fps > 1000:
        print "FPS: ", c.get_fps()
        last_fps = pygame.time.get_ticks()
    rabbyt.clear()
    rabbyt.set_time(pygame.time.get_ticks())
    rabbyt.render_unsorted(sprites)
    pygame.display.flip()
