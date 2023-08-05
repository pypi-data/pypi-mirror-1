import pygame
import rabbyt
import rabbyt.physics

rabbyt.init_display((640,480))

class Cannon(rabbyt.Sprite):
    def __init__(self, xy):
        rabbyt.Sprite.__init__(self, shape=(-10,-10,10,30))
        self.xy = xy
        self.rot = 0

    def fire(self):
        CannonBall(self)
        self.scale = rabbyt.lerp((1,1), (1.4, .6), dt=100, extend="reverse")
        def reset():
            self.scale = 1
        rabbyt.scheduler.add(rabbyt.get_time()+200, reset)

cannon = Cannon((0,0))
sprites = [cannon]


class CannonBall(rabbyt.Sprite):
    def __init__(self, cannon):
        rabbyt.Sprite.__init__(self)

        self.xy = rabbyt.physics.Basic2(cannon.xy,
                cannon.convert_offset((0,200)), (0, -100))

        rabbyt.physics.default_update_manager.append(self)

        sprites.append(self)

        rabbyt.scheduler.add(rabbyt.get_time()+10000,
                lambda: sprites.remove(self))

    def update(self, dt):
        pass


clock = pygame.time.Clock()
running=True
while running:
    dt = clock.tick(40)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running=False
            elif event.key == pygame.K_SPACE:
                cannon.fire()

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_RIGHT]:
        cannon.rot -= 5
    if pressed[pygame.K_LEFT]:
        cannon.rot += 5

    rabbyt.set_time(pygame.time.get_ticks())
    rabbyt.scheduler.pump()

    rabbyt.clear()
    rabbyt.physics.update(dt/1000.)

    rabbyt.render_unsorted(sprites)

    pygame.display.flip()
