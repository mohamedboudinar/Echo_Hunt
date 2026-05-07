import heapq
from itertools import count
from ai.node import Node
from ai.heuristic import Heuristic
from ai.navigation_grid import NavigationGrid

class AStar:
    def __init__(self):
        self.nodes_explored = 0
        self.last_path_length = 0
        self.closed_nodes = set()
        self.open_nodes = set()

    def reconstruct_path(self, current_node):
        path = []
        while current_node:
            path.append(current_node.position)
            current_node = current_node.parent
        path.reverse()
        self.last_path_length = len(path)
        return path

    def get_neighbors(self, grid, position):
        x, y = position
        result = []
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if NavigationGrid.is_walkable(grid, nx, ny):
                result.append((nx, ny))
        return result

    def find_path(self, grid, start, goal):
        self.nodes_explored = 0
        self.last_path_length = 0
        self.closed_nodes = set()
        self.open_nodes = set()
        if not grid or not NavigationGrid.is_walkable(grid, *start) or not NavigationGrid.is_walkable(grid, *goal):
            return []
        tie = count()
        open_heap = []
        g_score = {start: 0}
        start_node = Node(start)
        start_node.h = Heuristic.manhattan(start, goal)
        start_node.f = start_node.h
        heapq.heappush(open_heap, (start_node.f, next(tie), start_node))
        self.open_nodes.add(start)
        nodes = {start: start_node}
        while open_heap:
            _, _, current = heapq.heappop(open_heap)
            if current.position in self.closed_nodes:
                continue
            self.open_nodes.discard(current.position)
            if current.position == goal:
                return self.reconstruct_path(current)
            self.closed_nodes.add(current.position)
            self.nodes_explored += 1
            for neighbor in self.get_neighbors(grid, current.position):
                if neighbor in self.closed_nodes:
                    continue
                tentative = g_score[current.position] + 1
                if tentative >= g_score.get(neighbor, 10**9):
                    continue
                node = nodes.get(neighbor, Node(neighbor))
                nodes[neighbor] = node
                node.parent = current
                node.g = tentative
                node.h = Heuristic.manhattan(neighbor, goal)
                node.f = node.g + node.h
                g_score[neighbor] = tentative
                self.open_nodes.add(neighbor)
                heapq.heappush(open_heap, (node.f, next(tie), node))
        return []
