import pygame
class HeartDisplay:
    def render(self, screen, player):
        for i in range(player.max_hearts):
            color = (255, 60, 100) if i < player.hearts else (70, 30, 45)
            pygame.draw.circle(screen, color, (40 + i * 40, 55), 14)
