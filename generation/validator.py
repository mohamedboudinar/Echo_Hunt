from collections import deque
from ai.navigation_grid import NavigationGrid

class TraversabilityValidator:
    @staticmethod
    def validate(grid, start, goal):
        if not grid or not NavigationGrid.is_walkable(grid, *start) or not NavigationGrid.is_walkable(grid, *goal):
            return False
        width, height = len(grid[0]), len(grid)
        queue = deque([start])
        visited = {start}
        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                return True
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited and NavigationGrid.is_walkable(grid, nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return False
