from entities.enemy import Enemy
class Hunter(Enemy):
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y)
        self.speed = 3.5
        self.color = (255, 80, 80)
