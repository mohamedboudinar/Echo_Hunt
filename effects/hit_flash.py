import pygame
class HitFlash:
    def __init__(self, width, height):
        self.alpha = 0.0
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
    def trigger(self):
        self.alpha = 150.0
    def update(self, dt):
        self.alpha = max(0.0, self.alpha - 300 * dt)
    def render(self, screen):
        if self.alpha <= 0:
            return
        self.surface.fill((255, 40, 70, int(self.alpha)))
        screen.blit(self.surface, (0, 0))
