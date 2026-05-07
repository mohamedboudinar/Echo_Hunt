from entities.enemy import Enemy
class Dasher(Enemy):
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y)
        self.speed = 5.3
        self.color = (255, 180, 60)
        self.brain.update_interval = 0.16
