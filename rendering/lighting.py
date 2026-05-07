import pygame

class LightingEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.darkness_alpha = 105
        self.darkness_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.light_texture_cache = {}

    def create_light_texture(self, radius):
        if radius in self.light_texture_cache:
            return self.light_texture_cache[radius]
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        center = radius
        # cached once; runtime frames only blit cached textures
        for r in range(radius, 0, -3):
            alpha = int(180 * (r / radius) ** 2)
            pygame.draw.circle(surface, (255, 255, 255, alpha), (center, center), r)
        self.light_texture_cache[radius] = surface
        return surface

    def begin(self):
        self.darkness_surface.fill((0, 0, 0, self.darkness_alpha))

    def apply_light(self, x, y, radius):
        light = self.create_light_texture(radius)
        self.darkness_surface.blit(light, (int(x - radius), int(y - radius)), special_flags=pygame.BLEND_RGBA_SUB)

    def render(self, screen):
        screen.blit(self.darkness_surface, (0, 0))
