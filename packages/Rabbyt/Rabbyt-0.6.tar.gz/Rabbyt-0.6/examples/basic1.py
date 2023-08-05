import rabbyt
import pygame

# This is pretty much the bare minimum.

# This is a small shortcut function.  It'll call pygame.init() and
# pygame.display.set_mode() for us, and set up some default OpenGL attributes
# that rabbyt uses.
# If you want to use rabbyt with something other than pygame, you'll need to
# do these things yourself.  (Check the source, it's not hard.)
rabbyt.init_display((640, 480))

while not pygame.event.peek(pygame.QUIT):
    # Clear the screen to white.  (Colors in rabbyt are the same as in OpenGL,
    # from 0.0 to 1.0.)
    rabbyt.clear((1.0,1.0,1.0))

    pygame.display.flip()
