

import rabbyt
from rabbyt.fonts import Font, FontSprite
import pygame

rabbyt.init_display()

hello_earthling = (u'\u043f\u0440\u0438\u0432\u0435\u0442 '
            u'\u0437\u0430\u0437\u0435\u043c\u043b\u044f\u0442\u044c')

alphabet = set(hello_earthling)

font = Font(pygame.font.Font(pygame.font.get_default_font(), 20),
                alphabet=alphabet)
sprite = FontSprite(font, hello_earthling)
sprite.rot = rabbyt.lerp(0, 360, dt=6000, extend="repeat")
sprite.x = 100
sprite.rgb = 0,1,1

while not pygame.event.peek(pygame.QUIT):
    rabbyt.clear((0,.5,.5,1))
    rabbyt.set_time(pygame.time.get_ticks())
    sprite.render()
    pygame.display.flip()