import rabbyt
import pygame

rabbyt.init_display((640, 480))

sprites = [rabbyt.Sprite(x=x) for x in range(-100, 100, 50)]

extend = lambda mode: rabbyt.lerp(-100, 100, 1000, 3000, extend=mode)

# Constant is the default extend mode.  It will not go beyond start or end.
sprites[0].y = extend("constant")

# With extrapolate, it just keeps going.
sprites[1].y = extend("extrapolate")

# With repeat, it starts at start again after reaching end.
sprites[2].y = extend("repeat")

# Reverse is like repeat, only every other time it moves from end to start.
sprites[3].y = extend("reverse")

while not pygame.event.peek(pygame.QUIT):
    rabbyt.clear()
    rabbyt.set_time(pygame.time.get_ticks())

    rabbyt.render_unsorted(sprites)

    pygame.display.flip()
