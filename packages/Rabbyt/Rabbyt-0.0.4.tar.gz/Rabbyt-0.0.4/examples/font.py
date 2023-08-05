import rabbyt
from rabbyt.fonts import Font, FontSprite
import pygame

rabbyt.init_display()

font = Font(pygame.font.Font(pygame.font.get_default_font(), 20))
sprite = FontSprite(font, "hello world")
sprite.rot = rabbyt.lerp(0, 360, dt=6000, extend="repeat")
sprite.x = 100
sprite.rgb = 0,1,1

while not pygame.event.peek(pygame.QUIT):
    rabbyt.clear()
    rabbyt.set_time(pygame.time.get_ticks())
    sprite.render()
    pygame.display.flip()