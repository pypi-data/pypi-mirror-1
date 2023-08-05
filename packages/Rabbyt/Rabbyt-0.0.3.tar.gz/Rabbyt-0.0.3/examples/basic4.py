import rabbyt
import pygame

import os.path
rabbyt.data_directory = os.path.dirname(__file__)


rabbyt.init_display((640, 480))

car = rabbyt.Sprite("car.png")

# You don't have to be limited to static values!  Using rabbyt.lerp you can
# assign a value that linearly interpolates over time.  The interpolation is
# done in Pyrex code, so it is practically free.

# Fade the car in after one second.
car.alpha = rabbyt.lerp(0.0, 1.0, startt=1000, endt=2000)

# Rotate the car from 0 to 360 over three seconds, then repeat.
car.rot = rabbyt.lerp(0, 360, dt=3000, extend="repeat")

while True:
    rabbyt.clear((1,1,1))

    # When using dynamic values (such as returned by lerp,) we need to tell
    # rabbyt what time it is every frame.  This might sound silly, but there
    # are two good reasons for it.  1) Rabbyt isn't limited to one
    # high-resolution clock implementaion and 2) you can have complete control
    # over time.  This could be very useful if you want to add a 'pause' feature
    # to you game :)
    rabbyt.set_time(pygame.time.get_ticks())

    car.render()

    pygame.display.flip()
