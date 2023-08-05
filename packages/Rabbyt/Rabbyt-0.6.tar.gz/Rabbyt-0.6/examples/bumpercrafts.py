from __future__ import division

import random

import rabbyt, rabbyt.collisions, rabbyt.physics
from rabbyt import lerp, wrap

import pygame

rabbyt.init_display((800, 600))


sprites = []

r = lambda: random.random()-.5

class BumperCraft(rabbyt.Sprite):
    def __init__(self, x, y):
        rabbyt.Sprite.__init__(self)

        self._phy_x = rabbyt.physics.Basic1()
        self._phy_y = rabbyt.physics.Basic1()

        self._phy_x.p = x
        self._phy_y.p = y

        self.x = wrap([-400,400], lambda: self._phy_x.p)
        self.y = wrap([-300,300], lambda: self._phy_y.p)

        self._phy_x.a = lambda: 100 #self.convert_offset((10,0))[0]
        self._phy_y.a = lambda: 100 #self.convert_offset((10,0))[1]

    def update(self, dt):
        self._phy_x.update(dt)
        self._phy_y.update(dt)


for i in range(400):
    b = BumperCraft(r()*800, r()*600)

    sprites.append(b)

c = pygame.time.Clock()
while not pygame.event.peek(pygame.QUIT):
    dt = c.tick(60)

    rabbyt.set_time(pygame.time.get_ticks())

    time = dt/1000 # Update will expect time in seconds, not ms.
    for b in sprites:
        b.update(time)

    rabbyt.clear()

    collisions = rabbyt.collisions.brute_force(sprites)

    for s1, s2 in collisions:
        s1.rgb = lerp((1,0,0),(1,1,1), dt=400)
        s2.rgb = lerp((1,0,0),(1,1,1), dt=400)

    rabbyt.render_unsorted(sprites)
    pygame.display.flip()
