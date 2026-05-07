import random

from generation.tilemap import TileType
from generation.validator import TraversabilityValidator


class DynamicObstacleManager:
    def __init__(self, seed=None, count=4, move_interval=1.2):
        self.random = random.Random(seed)
        self.count = count
        self.move_interval = move_interval
        self.move_timer = 0.0
        self.positions = []
        self._underlying_tiles = {}

    def initialize(self, grid, spawn, exit_position, protected_positions=None):
        self.positions = []
        self._underlying_tiles = {}
        protected_positions = set(protected_positions or [])
        for _ in range(self.count):
            position = self._find_valid_position(grid, spawn, exit_position, protected_positions)
            if position is None:
                break
            self._place_obstacle(grid, position)

    def update(self, dt, grid, spawn, exit_position, protected_positions=None):
        self.move_timer += dt
        if self.move_timer < self.move_interval:
            return False
        self.move_timer = 0.0
        self.move_obstacles(grid, spawn, exit_position, protected_positions)
        return True

    def move_obstacles(self, grid, spawn, exit_position, protected_positions=None):
        old_positions = list(self.positions)
        self._clear_obstacles(grid)
        self.positions = []
        protected_positions = set(protected_positions or [])

        for old_position in old_positions:
            position = self._neighbor_or_random(grid, old_position, spawn, exit_position, protected_positions)
            if position is None:
                continue
            self._place_obstacle(grid, position)

    def _clear_obstacles(self, grid):
        for x, y in self.positions:
            grid[y][x] = self._underlying_tiles.get((x, y), TileType.FLOOR)
        self._underlying_tiles = {}

    def _place_obstacle(self, grid, position):
        x, y = position
        self._underlying_tiles[position] = grid[y][x]
        grid[y][x] = TileType.WALL
        self.positions.append(position)

    def _neighbor_or_random(self, grid, position, spawn, exit_position, protected_positions):
        x, y = position
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        self.random.shuffle(candidates)
        candidates.append(position)
        for candidate in candidates:
            if self._is_valid_candidate(grid, candidate, spawn, exit_position, protected_positions):
                return candidate
        return self._find_valid_position(grid, spawn, exit_position, protected_positions)

    def _find_valid_position(self, grid, spawn, exit_position, protected_positions):
        candidates = []
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile in (TileType.FLOOR, TileType.HAZARD, TileType.REWARD, TileType.DOOR):
                    candidates.append((x, y))
        self.random.shuffle(candidates)
        for candidate in candidates:
            if self._is_valid_candidate(grid, candidate, spawn, exit_position, protected_positions):
                return candidate
        return None

    def _is_valid_candidate(self, grid, position, spawn, exit_position, protected_positions):
        x, y = position
        if position in (spawn, exit_position) or position in self.positions or position in protected_positions:
            return False
        if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            return False
        if grid[y][x] not in (TileType.FLOOR, TileType.HAZARD, TileType.REWARD, TileType.DOOR):
            return False

        original = grid[y][x]
        grid[y][x] = TileType.WALL
        valid = TraversabilityValidator.validate(grid, spawn, exit_position)
        grid[y][x] = original
        return valid
