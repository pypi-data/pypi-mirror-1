import random

import rabbyt
from rabbyt.fonts import Font, FontSprite
import pygame
import os.path
rabbyt.data_directory = os.path.dirname(__file__)

rabbyt.init_display((640, 160))

font = Font(pygame.font.Font(pygame.font.get_default_font(), 20))

sprites = []

kwargs = dict(start=-100, end=300, dt=5000, extend="repeat")
sprites.append(FontSprite(font, "linear", x=-300, y=70))
sprites.append(rabbyt.Sprite(x = rabbyt.lerp(**kwargs), y=60))

sprites.append(FontSprite(font, "sine", x=-300, y=40))
sprites.append(rabbyt.Sprite(x = rabbyt.sine(**kwargs), y=30))

sprites.append(FontSprite(font, "cosine", x=-300, y=10))
sprites.append(rabbyt.Sprite(x = rabbyt.cosine(**kwargs), y=0))

sprites.append(FontSprite(font, "exponential", x=-300, y=-20))
sprites.append(rabbyt.Sprite(x = rabbyt.exponential(**kwargs), y=-30))

c = pygame.time.Clock()
while not pygame.event.get(pygame.QUIT):
    rabbyt.add_time(c.tick(40))
    rabbyt.clear()
    rabbyt.render_unsorted(sprites)
    pygame.display.flip()
