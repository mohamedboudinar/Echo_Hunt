import pygame


class HeartDisplay:
    def __init__(self, x=1035, y=24):
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont("consolas", 18, bold=True)

    def render(self, screen, player):
        panel_width = 250
        panel_height = 72
        panel = pygame.Rect(self.x, self.y, panel_width, panel_height)
        pygame.draw.rect(screen, (8, 14, 28), panel, border_radius=6)
        pygame.draw.rect(screen, (255, 90, 120), panel, width=2, border_radius=6)

        label = self.font.render("LIVES", True, (255, 190, 205))
        screen.blit(label, (panel.x + 16, panel.y + 10))

        for i in range(player.max_hearts):
            center_x = panel.x + 86 + i * 48
            center_y = panel.y + 42
            filled = i < player.hearts
            self.draw_heart(screen, center_x, center_y, 15, filled)

    def draw_heart(self, screen, center_x, center_y, size, filled=True):
        outline = (255, 215, 225)
        fill = (255, 55, 105) if filled else (55, 28, 45)
        glow = (255, 120, 155) if filled else (105, 55, 75)

        points = [
            (center_x, center_y + size),
            (center_x - int(size * 1.45), center_y - int(size * 0.18)),
            (center_x - int(size * 0.72), center_y - size),
            (center_x, center_y - int(size * 0.52)),
            (center_x + int(size * 0.72), center_y - size),
            (center_x + int(size * 1.45), center_y - int(size * 0.18)),
        ]

        pygame.draw.polygon(screen, outline, points)
        pygame.draw.circle(screen, outline, (center_x - size // 2, center_y - size // 3), size // 2 + 3)
        pygame.draw.circle(screen, outline, (center_x + size // 2, center_y - size // 3), size // 2 + 3)
        pygame.draw.polygon(screen, fill, points)
        pygame.draw.circle(screen, fill, (center_x - size // 2, center_y - size // 3), size // 2)
        pygame.draw.circle(screen, fill, (center_x + size // 2, center_y - size // 3), size // 2)
        pygame.draw.polygon(screen, glow, points, width=2)
        pygame.draw.circle(screen, glow, (center_x - size // 2, center_y - size // 3), size // 2, width=2)
        pygame.draw.circle(screen, glow, (center_x + size // 2, center_y - size // 3), size // 2, width=2)

        if filled:
            pygame.draw.circle(screen, (255, 225, 235), (center_x - size // 2, center_y - size // 2), 3)
