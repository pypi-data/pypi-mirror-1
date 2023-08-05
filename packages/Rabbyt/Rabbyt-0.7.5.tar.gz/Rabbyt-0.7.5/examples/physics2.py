import rabbyt
import rabbyt.physics
import pygame

import os.path
rabbyt.data_directory = os.path.dirname(__file__)

rabbyt.init_display((640, 480))

car = rabbyt.Sprite("car.png")
car.xy = rabbyt.physics.Basic2(xy=(-100, 0), vxy=(100,200), axy=(0,-100))

c = pygame.time.Clock()
while not pygame.event.peek(pygame.QUIT):
    dt = c.tick(100)
    rabbyt.set_time(pygame.time.get_ticks())

    rabbyt.physics.update(dt/1000.0)

    rabbyt.clear((1,1,1))

    car.render()

    pygame.display.flip()
