class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0
        self.smoothing = 0.1
        self.render_offset_x = 0
        self.render_offset_y = 0

    def update(self, target_x: float, target_y: float):
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing

    def set_render_offset(self, x: int, y: int):
        self.render_offset_x = x
        self.render_offset_y = y

    def apply(self, x: float, y: float):
        return (
            x - self.x + self.width // 2 + self.render_offset_x,
            y - self.y + self.height // 2 + self.render_offset_y,
        )
