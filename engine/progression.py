class ProgressionSystem:
    def __init__(self):
        self.sector = 1
        self.cores = 0
        self.cores_required = 3
        self.unlocked_dash_boost = False

    def collect_core(self):
        self.cores += 1
        if self.cores >= self.cores_required:
            self.unlocked_dash_boost = True

    def next_sector(self):
        self.sector += 1
        self.cores = 0
        self.cores_required = min(6, 2 + self.sector)
