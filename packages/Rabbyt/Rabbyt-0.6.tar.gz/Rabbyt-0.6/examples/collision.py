from __future__ import division

import random

import rabbyt, rabbyt.collisions
from rabbyt import lerp, wrap

import pygame

rabbyt.init_display((800, 600))


sprites = []

r = lambda: random.random()-.5

for i in range(400):
    s = rabbyt.Sprite(shape=(-2,2,2,-2))

    s.x = wrap([-400,400], lerp(r()*800, r()*800, dt=4000, extend="extrapolate"))
    s.y = wrap([-300,300], lerp(r()*600, r()*600, dt=4000, extend="extrapolate"))

    sprites.append(s)

collision_times = []
c = pygame.time.Clock()
last_fps = 0
while not pygame.event.peek(pygame.QUIT):
    c.tick()
    if pygame.time.get_ticks() - last_fps > 1000:
        print "FPS: ", c.get_fps()
        last_fps = pygame.time.get_ticks()
        average = sum(collision_times)/len(collision_times)
        print "Average ms to find collisions:", average
        collision_times = []
    rabbyt.clear()
    rabbyt.set_time(pygame.time.get_ticks())

    start = pygame.time.get_ticks()
    # With so few sprites so close together, just using brute_force ends up
    # being faster.  If you have more sprites spread further apart, collide
    # should work better.
    collisions = rabbyt.collisions.brute_force(sprites)
    #collisions = rabbyt.collisions.collide(sprites)
    collision_times.append(pygame.time.get_ticks()-start)

    for s1, s2 in collisions:
        s1.rgb = lerp((1,0,0),(1,1,1), dt=400)
        s2.rgb = lerp((1,0,0),(1,1,1), dt=400)

    rabbyt.render_unsorted(sprites)
    pygame.display.flip()
