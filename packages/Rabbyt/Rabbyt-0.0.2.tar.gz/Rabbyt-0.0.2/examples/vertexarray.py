import random

import rabbyt
import pygame

from rabbyt.vertexarrays import VertexArray

rabbyt.init_display((640, 480))

va = VertexArray()

r = random.random

print "Generating 20,000 quads..."
start = pygame.time.get_ticks()
for i in range(20000):
    x = r()*640 - 320
    y = r()*480 - 240
    va.append((x-5, y+5, 0, 0, r(), r(), r(), r()))
    va.append((x+5, y+5, 0, 0, r(), r(), r(), r()))
    va.append((x+5, y-5, 0, 0, r(), r(), r(), r()))
    va.append((x-5, y-5, 0, 0, r(), r(), r(), r()))
print pygame.time.get_ticks() - start

c = pygame.time.Clock()
last_fps = 0
while True:
    c.tick()
    if pygame.time.get_ticks() - last_fps > 1000:
        print "FPS: ", c.get_fps()
        last_fps = pygame.time.get_ticks()
    rabbyt.clear()
    va.render()
    pygame.display.flip()


