class Entity:
    def __init__(self, grid_x, grid_y):
        self.grid_x = float(grid_x)
        self.grid_y = float(grid_y)
        self.speed = 3.0
        self.color = (255, 255, 255)

    def get_position(self):
        return int(round(self.grid_x)), int(round(self.grid_y))
