class DashTrail:
    def __init__(self):
        self.positions = []
    def add(self, x, y):
        self.positions.append((x, y, 1.0))
    def update(self, dt):
        self.positions = [(x, y, a - dt * 3.5) for x, y, a in self.positions if a - dt * 3.5 > 0]
