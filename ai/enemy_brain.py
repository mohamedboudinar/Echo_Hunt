from ai.astar import AStar
from ai.enemy_states import EnemyState
from ai.state_machine import StateMachine
from ai.interception import Interception
from ai.navigation_grid import NavigationGrid

class EnemyBrain:
    def __init__(self, owner):
        self.owner = owner
        self.astar = AStar()
        self.state_machine = StateMachine()
        self.path = []
        self.update_interval = 0.30
        self.update_timer = 0.0
        self.detection_radius = 8

    def distance_to_player(self, player):
        return abs(player.grid_x - self.owner.grid_x) + abs(player.grid_y - self.owner.grid_y)

    def update_state(self, player):
        self.state_machine.set_state(EnemyState.CHASE if self.distance_to_player(player) <= self.detection_radius else EnemyState.PATROL)

    def calculate_path(self, grid, player, player_dx, player_dy):
        goal = Interception.predict_target(player.grid_x, player.grid_y, player_dx, player_dy)
        if not NavigationGrid.is_walkable(grid, *goal):
            goal = player.get_position()
        self.path = self.astar.find_path(grid, self.owner.get_position(), goal)

    def force_repath(self):
        self.update_timer = self.update_interval

    def move_along_path(self, delta_time):
        if len(self.path) < 2:
            return
        tx, ty = self.path[1]
        dx, dy = tx - self.owner.grid_x, ty - self.owner.grid_y
        if abs(dx) + abs(dy) < 0.05:
            self.path.pop(0)
            return
        self.owner.grid_x += max(-1, min(1, dx)) * self.owner.speed * delta_time
        self.owner.grid_y += max(-1, min(1, dy)) * self.owner.speed * delta_time

    def update(self, delta_time, grid, player, player_dx, player_dy):
        self.update_state(player)
        self.update_timer += delta_time
        if self.update_timer >= self.update_interval:
            self.update_timer = 0.0
            if self.state_machine.is_state(EnemyState.CHASE):
                self.calculate_path(grid, player, player_dx, player_dy)
        self.move_along_path(delta_time)
