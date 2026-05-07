from entities.entity import Entity
from ai.enemy_brain import EnemyBrain
class Enemy(Entity):
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y)
        self.brain = EnemyBrain(self)
        self.color = (255, 60, 60)
    def update(self, dt, grid, player, pdx, pdy):
        self.brain.update(dt, grid, player, pdx, pdy)
