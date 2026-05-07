import pygame
class StaminaBar:
    def render(self, screen, player):
        width, height = 250, 18
        pygame.draw.rect(screen, (35, 35, 45), (20, 85, width, height))
        fill_width = int(width * (player.stamina / player.max_stamina))
        color = (0, 220, 255) if not player.exhausted else (255, 80, 80)
        pygame.draw.rect(screen, color, (20, 85, fill_width, height))
