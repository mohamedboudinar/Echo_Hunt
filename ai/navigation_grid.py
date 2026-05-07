from generation.tilemap import TileType

class NavigationGrid:
    WALKABLE = {TileType.FLOOR, TileType.DOOR, TileType.HAZARD, TileType.EXIT, TileType.REWARD}
    @staticmethod
    def is_walkable(grid, x, y):
        if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            return False
        return grid[y][x] in NavigationGrid.WALKABLE
