import random
from generation.room_templates import RoomTemplates
from generation.tilemap import TileType
from generation.validator import TraversabilityValidator

class DungeonGenerator:
    def __init__(self, seed=None):
        self.random = random.Random(seed)
        self.spawn = (2, 2)
        self.exit = (0, 0)

    def generate(self, width=38, height=24):
        grid = [[TileType.WALL for _ in range(width)] for _ in range(height)]
        templates = [RoomTemplates.arena_room, RoomTemplates.corridor_room, RoomTemplates.crossroads_room, RoomTemplates.hazard_room]
        cursor_x, cursor_y = 2, height // 2 - 4
        last_center = None
        for _ in range(4):
            room = self.random.choice(templates)()
            rh, rw = len(room), len(room[0])
            y = max(1, min(height-rh-1, cursor_y + self.random.randint(-3,3)))
            x = max(1, min(width-rw-1, cursor_x))
            for ry, row in enumerate(room):
                for rx, tile in enumerate(row):
                    if tile != TileType.EMPTY:
                        grid[y+ry][x+rx] = tile
            center = (x+rw//2, y+rh//2)
            if last_center:
                self._carve_corridor(grid, last_center, center)
            last_center = center
            cursor_x += rw + self.random.randint(3, 6)
        self.spawn = self._first_walkable(grid)
        self.exit = self._farthest_walkable(grid, self.spawn) or last_center or self.spawn
        ex, ey = self.exit
        grid[ey][ex] = TileType.EXIT
        if not TraversabilityValidator.validate(grid, self.spawn, self.exit):
            self._carve_corridor(grid, self.spawn, self.exit)
        return grid

    def _carve_corridor(self, grid, a, b):
        x, y = a
        bx, by = b
        while x != bx:
            grid[y][x] = TileType.FLOOR
            x += 1 if bx > x else -1
        while y != by:
            grid[y][x] = TileType.FLOOR
            y += 1 if by > y else -1
        grid[y][x] = TileType.FLOOR

    def _first_walkable(self, grid):
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile in (TileType.FLOOR, TileType.DOOR):
                    return (x, y)
        return (1, 1)

    def _farthest_walkable(self, grid, start):
        best_position = None
        best_distance = -1
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile not in (TileType.FLOOR, TileType.DOOR):
                    continue
                distance = abs(x - start[0]) + abs(y - start[1])
                if distance > best_distance:
                    best_distance = distance
                    best_position = (x, y)
        return best_position
