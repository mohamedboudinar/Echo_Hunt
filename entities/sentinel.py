from entities.enemy import Enemy
class Sentinel(Enemy):
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y)
        self.speed = 2.0
        self.color = (185, 40, 255)
        self.brain.detection_radius = 12
