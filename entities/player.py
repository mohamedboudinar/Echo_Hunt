from entities.entity import Entity

class Player(Entity):
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y)
        self.speed = 5.0
        self.max_hearts = 3
        self.hearts = 3
        self.invulnerability_timer = 0.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.sprinting = False
        self.exhausted = False
        self.stamina_regeneration = 25.0
        self.stamina_drain = 40.0
        self.dash_speed = 24.0
        self.dash_duration = 0.12
        self.dash_timer = 0.0
        self.dash_cooldown = 0.22
        self.dash_cooldown_timer = 0.0
        self.dash_dir_x = 0.0
        self.dash_dir_y = 0.0

    def damage(self, amount=1):
        if self.invulnerability_timer > 0:
            return False
        self.hearts = max(0, self.hearts - amount)
        self.invulnerability_timer = 1.0
        return True

    def update_timers(self, delta_time):
        self.invulnerability_timer = max(0.0, self.invulnerability_timer - delta_time)
        self.dash_cooldown_timer = max(0.0, self.dash_cooldown_timer - delta_time)
        self.dash_timer = max(0.0, self.dash_timer - delta_time)

    def update_stamina(self, delta_time):
        if self.sprinting and self.stamina > 0 and not self.exhausted:
            self.stamina -= self.stamina_drain * delta_time
        else:
            self.stamina += self.stamina_regeneration * delta_time
        self.stamina = max(0.0, min(self.stamina, self.max_stamina))
        if self.stamina <= 0:
            self.exhausted = True
        elif self.stamina >= 20:
            self.exhausted = False

    def can_dash(self):
        return self.dash_cooldown_timer <= 0 and self.dash_timer <= 0 and self.stamina >= 25

    def start_dash(self, dx, dy):
        if not self.can_dash() or (dx == 0 and dy == 0):
            return False
        self.stamina -= 25
        self.dash_timer = self.dash_duration
        self.dash_cooldown_timer = self.dash_cooldown
        self.dash_dir_x = dx
        self.dash_dir_y = dy
        return True
