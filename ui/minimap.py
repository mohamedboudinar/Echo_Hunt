import pygame
from generation.tilemap import TileType

class Minimap:
    COLORS = {
        TileType.FLOOR: (50, 60, 90),
        TileType.DOOR: (0, 170, 220),
        TileType.HAZARD: (220, 60, 80),
        TileType.EXIT: (60, 255, 150),
        TileType.REWARD: (255, 220, 80),
    }

    def render(self, screen, grid, player, enemies, exit_position=None, maximized=False, x=None, y=30, scale=8):
        if maximized:
            self._render_maximized(screen, grid, player, enemies, exit_position)
            return

        width = len(grid[0]) * scale
        height = len(grid) * scale
        if x is None:
            x = screen.get_width() - width - 30
        self._render_grid(screen, grid, player, enemies, x, y, scale, exit_position=exit_position)

    def _render_maximized(self, screen, grid, player, enemies, exit_position=None):
        screen_width, screen_height = screen.get_size()
        map_columns = len(grid[0])
        map_rows = len(grid)
        scale = max(8, min((screen_width - 240) // map_columns, (screen_height - 220) // map_rows))
        width = map_columns * scale
        height = map_rows * scale
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2 + 20

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((4, 8, 18, 175))
        screen.blit(overlay, (0, 0))
        self._render_grid(screen, grid, player, enemies, x, y, scale, border=10, exit_position=exit_position)

        font = pygame.font.SysFont("consolas", 26, bold=True)
        title = font.render("SECTOR MAP", True, (235, 245, 255))
        screen.blit(title, title.get_rect(center=(screen_width // 2, y - 28)))

    def _render_grid(self, screen, grid, player, enemies, x, y, scale, border=6, exit_position=None):
        width = len(grid[0]) * scale
        height = len(grid) * scale
        pygame.draw.rect(screen, (10, 12, 25), (x-border, y-border, width+border*2, height+border*2))
        pygame.draw.rect(screen, (0, 255, 220), (x-border, y-border, width+border*2, height+border*2), width=2)
        for gy, row in enumerate(grid):
            for gx, tile in enumerate(row):
                color = self.COLORS.get(tile)
                if color:
                    pygame.draw.rect(screen, color, (x + gx*scale, y + gy*scale, scale, scale))
        if exit_position:
            self._draw_exit_marker(screen, x, y, scale, exit_position)
        pygame.draw.rect(screen, (0, 255, 255), (x+int(player.grid_x)*scale, y+int(player.grid_y)*scale, scale, scale))
        for e in enemies:
            pygame.draw.rect(screen, e.color, (x+int(e.grid_x)*scale, y+int(e.grid_y)*scale, scale, scale))

    def _draw_exit_marker(self, screen, x, y, scale, exit_position):
        exit_x, exit_y = exit_position
        rect = pygame.Rect(x + exit_x * scale, y + exit_y * scale, scale, scale)
        marker = rect.inflate(max(4, scale // 2), max(4, scale // 2))
        pygame.draw.rect(screen, (80, 255, 175), marker)
        pygame.draw.rect(screen, (225, 255, 245), marker, width=max(1, scale // 5))
