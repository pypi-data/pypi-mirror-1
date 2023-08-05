import rabbyt
import pygame

import os.path
# We do this so that you don't have to be in the same directory as the script
# to use it.
rabbyt.data_directory = os.path.dirname(__file__)

# Make sure that you allways have a valid OpenGL context before creating a
# sprite.  This init function will do that for you:
rabbyt.init_display((640, 480))

# Creating a sprite is easy.  Just give it an image filename.
car = rabbyt.Sprite("car.png")

while not pygame.event.peek(pygame.QUIT):
    rabbyt.clear((1,1,1))

    car.render()

    pygame.display.flip()
