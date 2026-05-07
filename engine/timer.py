import pygame

class Timer:
    def __init__(self, fps: int):
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.delta_time = 0.0

    def tick(self) -> float:
        self.delta_time = self.clock.tick(self.fps) / 1000.0
        return self.delta_time

    def get_fps(self) -> float:
        return self.clock.get_fps()
