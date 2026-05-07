from config import TILE_WIDTH, TILE_HEIGHT

class IsoProjector:
    @staticmethod
    def cart_to_iso(grid_x: float, grid_y: float):
        screen_x = (grid_x - grid_y) * (TILE_WIDTH // 2)
        screen_y = (grid_x + grid_y) * (TILE_HEIGHT // 2)
        return screen_x, screen_y
