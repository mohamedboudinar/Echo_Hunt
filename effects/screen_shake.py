import random
class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0.0
    def trigger(self, intensity, duration):
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)
    def update(self, dt):
        self.duration = max(0.0, self.duration - dt)
        if self.duration <= 0:
            self.intensity = 0
    def get_offset(self):
        if self.intensity <= 0:
            return 0, 0
        return random.randint(-self.intensity, self.intensity), random.randint(-self.intensity, self.intensity)
