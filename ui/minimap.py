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

    def render(self, screen, grid, player, enemies, x=1640, y=30, scale=5):
        width = len(grid[0]) * scale
        height = len(grid) * scale
        pygame.draw.rect(screen, (10, 12, 25), (x-6, y-6, width+12, height+12))
        for gy, row in enumerate(grid):
            for gx, tile in enumerate(row):
                color = self.COLORS.get(tile)
                if color:
                    pygame.draw.rect(screen, color, (x + gx*scale, y + gy*scale, scale, scale))
        pygame.draw.rect(screen, (0, 255, 255), (x+int(player.grid_x)*scale, y+int(player.grid_y)*scale, scale, scale))
        for e in enemies:
            pygame.draw.rect(screen, e.color, (x+int(e.grid_x)*scale, y+int(e.grid_y)*scale, scale, scale))
