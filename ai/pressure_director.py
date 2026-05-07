class PressureDirector:
    def __init__(self):
        self.threat_level = 0.0
        self.max_threat = 100.0
    def update(self, player, enemies):
        close = 0
        for e in enemies:
            if abs(player.grid_x - e.grid_x) + abs(player.grid_y - e.grid_y) < 6:
                close += 1
        self.threat_level = min(self.max_threat, close * 25)
