import math
import pygame
from config import BACKGROUND_COLOR, GRID_COLOR, TILE_WIDTH, TILE_HEIGHT
from rendering.iso import IsoProjector
from generation.tilemap import TileType

TILE_COLORS = {
    TileType.FLOOR: (58, 68, 104),
    TileType.WALL: (128, 74, 168),
    TileType.DOOR: (0, 220, 255),
    TileType.HAZARD: (255, 75, 95),
    TileType.EXIT: (80, 255, 175),
    TileType.REWARD: (255, 220, 80),
}

class Renderer:
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera
        self.font = pygame.font.SysFont('consolas', 20)
        self.alpha_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.button_rects = {}

    def clear(self):
        self.screen.fill(BACKGROUND_COLOR)

    def world_to_screen(self, x, y):
        iso_x, iso_y = IsoProjector.cart_to_iso(x, y)
        return self.camera.apply(iso_x, iso_y)

    def draw_iso_tile(self, grid_x, grid_y, tile=TileType.FLOOR):
        sx, sy = self.world_to_screen(grid_x, grid_y)
        points = [(sx, sy), (sx + TILE_WIDTH//2, sy + TILE_HEIGHT//2), (sx, sy + TILE_HEIGHT), (sx - TILE_WIDTH//2, sy + TILE_HEIGHT//2)]
        pygame.draw.polygon(self.screen, TILE_COLORS.get(tile, GRID_COLOR), points)
        pygame.draw.polygon(self.screen, GRID_COLOR, points, width=1)
        if tile == TileType.EXIT:
            pygame.draw.polygon(self.screen, (225, 255, 245), points, width=3)
        elif tile == TileType.HAZARD:
            pygame.draw.polygon(self.screen, (255, 210, 220), points, width=2)

    def draw_grid(self, grid):
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                if tile != TileType.EMPTY:
                    self.draw_iso_tile(x, y, tile)

    def draw_entity(self, entity, color, label=None, radius=15):
        sx, sy = self.world_to_screen(entity.grid_x, entity.grid_y)
        center = (int(sx), int(sy + 12))
        pygame.draw.circle(self.screen, (255, 255, 255), center, radius + 4)
        pygame.draw.circle(self.screen, (10, 16, 28), center, radius + 2)
        pygame.draw.circle(self.screen, color, center, radius)
        pygame.draw.circle(self.screen, (255, 255, 255), center, radius, width=2)
        if label:
            label_surface = self.font.render(label, True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=(center[0], center[1] - radius - 15))
            self.screen.blit(label_surface, label_rect)

    def draw_player(self, player):
        color = (0, 255, 255) if player.invulnerability_timer <= 0 else (255, 255, 255)
        self.draw_entity(player, color, "YOU", 18)

    def draw_enemies(self, enemies):
        for enemy in enemies:
            self.draw_entity(enemy, enemy.color, enemy.__class__.__name__[0], 15)

    def draw_path(self, path):
        for x, y in path:
            sx, sy = self.world_to_screen(x, y)
            pygame.draw.circle(self.screen, (255, 80, 80), (int(sx), int(sy + 12)), 4)

    def draw_enemy_paths(self, enemies):
        for enemy in enemies:
            self.draw_path(enemy.brain.path)

    def draw_exit_marker(self, exit_position):
        sx, sy = self.world_to_screen(*exit_position)
        tick = pygame.time.get_ticks() / 220.0
        pulse = int(8 + abs((tick % 2) - 1) * 8)
        center = (int(sx), int(sy - 18))
        pygame.draw.circle(self.screen, (225, 255, 245), center, 24 + pulse, width=3)
        pygame.draw.circle(self.screen, (80, 255, 175), center, 16 + pulse // 2)
        label = pygame.font.SysFont('consolas', 24, bold=True).render("EXIT", True, (225, 255, 245))
        self.screen.blit(label, label.get_rect(center=(center[0], center[1] - 42)))

    def draw_dash_trail(self, trail):
        self.alpha_surface.fill((0, 0, 0, 0))
        for x, y, alpha in trail.positions:
            sx, sy = self.world_to_screen(x, y)
            pygame.draw.circle(self.alpha_surface, (0, 255, 255, int(alpha * 180)), (int(sx), int(sy + 12)), 10)
        self.screen.blit(self.alpha_surface, (0, 0))

    def draw_threat_meter(self, director):
        width, height = 300, 20
        x = 20
        y = 145
        self.draw_text("THREAT", (x, y - 2), (255, 170, 180))
        bar_y = y + 25
        pygame.draw.rect(self.screen, (45, 45, 55), (x, bar_y, width, height))
        fill = int(width * min(1.0, max(0.0, director.threat_level / director.max_threat)))
        pygame.draw.rect(self.screen, (255, 60, 80), (x, bar_y, fill, height))
        pygame.draw.rect(self.screen, (245, 250, 255), (x, bar_y, width, height), width=1)

    def draw_text(self, text, pos, color=(0,255,180)):
        self.screen.blit(self.font.render(text, True, color), pos)

    def draw_center_text(self, text, y, color=(0, 255, 180), font_size=42):
        font = pygame.font.SysFont('consolas', font_size, bold=True)
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.screen.get_width() // 2, y))
        self.screen.blit(surface, rect)

    def draw_overlay(self, alpha=185):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((5, 8, 18, alpha))
        self.screen.blit(overlay, (0, 0))

    def draw_synth_noise(self, strength=38):
        width, height = self.screen.get_size()
        self.alpha_surface.fill((0, 0, 0, 0))
        tick = pygame.time.get_ticks()
        for y in range((tick // 45) % 6, height, 6):
            pygame.draw.line(self.alpha_surface, (0, 255, 255, 16), (0, y), (width, y))
        for i in range(70):
            x = (i * 149 + tick // 3) % width
            y = (i * 83 + tick // 5) % height
            color = (255, 80, 165, strength) if i % 2 else (0, 255, 255, strength)
            pygame.draw.rect(self.alpha_surface, color, (x, y, 2, 2))
        self.screen.blit(self.alpha_surface, (0, 0))

    def draw_menu_animation(self):
        width, _ = self.screen.get_size()
        tick = pygame.time.get_ticks() / 1000.0
        self.alpha_surface.fill((0, 0, 0, 0))
        for ring in range(4):
            angle = tick * (0.7 + ring * 0.14)
            radius = 140 + ring * 40
            color = (24, 200 + ring * 8, 255 - ring * 20, 48)
            points = []
            for step in range(60):
                theta = angle + step * (2 * math.pi / 60)
                x = int(width // 2 + math.cos(theta) * (radius + 6 * math.sin(tick * 1.6 + step * 0.2)))
                y = int(240 + math.sin(theta) * (radius * 0.35 + 4 * math.cos(tick * 1.2 + step * 0.3)))
                points.append((x, y))
            pygame.draw.aalines(self.alpha_surface, color, True, points)
        for i in range(10):
            x = int(width // 2 + math.sin(tick * 1.8 + i * 0.7) * 280)
            y = int(240 + math.cos(tick * 1.2 + i * 0.9) * 24)
            alpha = 128 if i % 2 == 0 else 72
            pygame.draw.circle(self.alpha_surface, (0, 255, 255, alpha), (x, y), 6)
        self.screen.blit(self.alpha_surface, (0, 0))

    def draw_button(self, action, text, center, width=360, height=54, accent=(0, 255, 220)):
        rect = pygame.Rect(0, 0, width, height)
        rect.center = center
        self.button_rects[action] = rect
        pygame.draw.rect(self.screen, (13, 22, 42), rect, border_radius=8)
        pygame.draw.rect(self.screen, accent, rect, width=2, border_radius=8)
        shine = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, 8)
        pygame.draw.rect(self.screen, (255, 255, 255, 24), shine, border_radius=4)
        label = pygame.font.SysFont('consolas', 24, bold=True).render(text, True, (245, 250, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def clicked_button(self, pos):
        if pos is None:
            return None
        for action, rect in self.button_rects.items():
            if rect.collidepoint(pos):
                return action
        return None

    def draw_menu(self, move_label="WASD", player_name="", high_scores=None, name_active=False):
        self.button_rects = {}
        self.draw_overlay(205)
        self.draw_synth_noise(52)
        self.draw_menu_animation()
        width, _ = self.screen.get_size()
        pygame.draw.line(self.screen, (255, 80, 165), (width // 2 - 300, 190), (width // 2 + 300, 190), 3)
        pygame.draw.line(self.screen, (0, 255, 255), (width // 2 - 220, 875), (width // 2 + 220, 875), 2)
        self.draw_center_text("ECHO HUNT", 245, (0, 255, 255), 80)
        self.draw_center_text("A* SMART PURSUIT SURVIVAL", 325, (255, 110, 175), 30)
        self.draw_center_text("Reach the green EXIT. Avoid hunters, red hazards, and moving walls.", 382, (235, 245, 255), 24)
        self.draw_center_text("You win a sector by escaping. You lose when your hearts reach zero.", 426, (255, 220, 80), 24)
        self.draw_name_entry(player_name, (width // 2, 535), name_active)
        self.draw_button("start", "START RUN  [Enter]", (width // 2, 620), accent=(0, 255, 220))
        self.draw_button("shortcuts", "SHORTCUTS", (width // 2, 685), accent=(0, 255, 255))
        self.draw_button("settings", "SETTINGS", (width // 2, 750), accent=(255, 220, 80))
        self.draw_button("quit", "QUIT GAME  [Q]", (width // 2, 815), accent=(255, 90, 120))
        self.draw_high_scores(high_scores or [], (70, 455))

    def draw_name_entry(self, player_name, center, active=False):
        rect = pygame.Rect(0, 0, 520, 72)
        rect.center = center
        self.button_rects["name"] = rect
        border = (0, 255, 220) if active else (255, 220, 80)
        pygame.draw.rect(self.screen, (8, 14, 28), rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, width=3, border_radius=8)
        title = "PLAYER NAME - typing..." if active else "CLICK HERE TO TYPE PLAYER NAME"
        title_surface = pygame.font.SysFont('consolas', 18, bold=True).render(title, True, border)
        self.screen.blit(title_surface, (rect.x + 18, rect.y + 8))
        shown_name = player_name or "PLAYER"
        if active and pygame.time.get_ticks() % 900 < 450:
            shown_name += "_"
        label = pygame.font.SysFont('consolas', 30, bold=True).render(shown_name, True, (245, 250, 255))
        self.screen.blit(label, (rect.x + 18, rect.y + 34))

    def draw_high_scores(self, scores, pos):
        x, y = pos
        rect = pygame.Rect(x, y, 410, 245)
        pygame.draw.rect(self.screen, (8, 14, 28), rect, border_radius=8)
        pygame.draw.rect(self.screen, (0, 255, 220), rect, width=2, border_radius=8)
        self.draw_text("HIGH SCORES", (x + 18, y + 16), (255, 220, 80))
        if not scores:
            self.draw_text("No runs yet.", (x + 18, y + 52), (235, 245, 255))
            return
        for index, score in enumerate(scores[:6], start=1):
            text = f"{index}. {score['name'][:10]:<10} L{score['max_level']}  {score['survival_time']:>5.1f}s"
            self.draw_text(text, (x + 18, y + 24 + index * 30), (235, 245, 255))

    def draw_pause(self):
        self.button_rects = {}
        self.draw_overlay(175)
        self.draw_synth_noise(34)
        width, _ = self.screen.get_size()
        self.draw_center_text("PAUSED", 300, (255, 220, 80), 58)
        self.draw_button("resume", "RESUME  [Esc]", (width // 2, 390), accent=(0, 255, 220))
        self.draw_button("shortcuts", "SHORTCUTS", (width // 2, 470), accent=(0, 255, 255))
        self.draw_button("settings", "SETTINGS", (width // 2, 550), accent=(255, 220, 80))
        self.draw_button("menu", "MAIN MENU  [M]", (width // 2, 630), accent=(255, 220, 80))
        self.draw_button("quit", "QUIT GAME  [Q]", (width // 2, 710), accent=(255, 90, 120))

    def draw_game_over(self, sector, survival_time, high_scores=None):
        self.button_rects = {}
        self.draw_overlay()
        self.draw_synth_noise(46)
        width, _ = self.screen.get_size()
        self.draw_center_text("GAME OVER", 280, (255, 80, 90), 66)
        self.draw_center_text(f"Reached sector {sector}", 365, (0, 255, 180), 30)
        self.draw_center_text(f"Survived {survival_time:0.1f} seconds", 415, (220, 235, 255), 28)
        self.draw_center_text("Lose condition: hearts reached zero.", 465, (255, 170, 180), 24)
        self.draw_button("restart", "RESTART  [Enter/R]", (width // 2, 550), accent=(0, 255, 220))
        self.draw_button("menu", "MAIN MENU  [M]", (width // 2, 625), accent=(255, 220, 80))
        self.draw_button("quit", "QUIT GAME  [Q]", (width // 2, 700), accent=(255, 90, 120))
        self.draw_high_scores(high_scores or [], (70, 455))

    def draw_settings(self, music_on, sfx_on, music_vol, sfx_vol):
        self.button_rects = {}
        self.draw_overlay(205)
        self.draw_synth_noise(46)
        width, _ = self.screen.get_size()
        self.draw_center_text("SETTINGS", 240, (0, 255, 255), 72)
        self.draw_center_text("Audio options for background music and sound effects.", 320, (255, 220, 80), 26)
        self.draw_button(
            "toggle_music",
            f"MUSIC: {'ON' if music_on else 'OFF'}",
            (width // 2, 470),
            width=560,
            accent=(0, 255, 220),
        )
        self.draw_text(f"MUSIC VOLUME: {int(music_vol * 100)}%", (width // 2, 540), (235, 245, 255))
        self.draw_button("music_decrease", "-", (width // 2 - 120, 600), width=120, accent=(255, 90, 120))
        self.draw_button("music_increase", "+", (width // 2 + 120, 600), width=120, accent=(0, 255, 220))
        self.draw_button(
            "toggle_sfx",
            f"SFX: {'ON' if sfx_on else 'OFF'}",
            (width // 2, 730),
            width=560,
            accent=(255, 220, 80),
        )
        self.draw_text(f"SFX VOLUME: {int(sfx_vol * 100)}%", (width // 2, 800), (235, 245, 255))
        self.draw_button("sfx_decrease", "-", (width // 2 - 120, 860), width=120, accent=(255, 90, 120))
        self.draw_button("sfx_increase", "+", (width // 2 + 120, 860), width=120, accent=(0, 255, 220))
        self.draw_button("back", "BACK TO MENU  [Esc]", (width // 2, 940), accent=(255, 90, 120))
        self.draw_text("Click the buttons to mute/unmute audio and change volume.", (width // 2 - 430, 1000), (235, 245, 255))

    def draw_shortcuts(self, keyboard_layout=None):
        self.button_rects = {}
        self.draw_overlay(205)
        self.draw_synth_noise(46)
        width, _ = self.screen.get_size()
        self.draw_center_text("SHORTCUTS", 225, (0, 255, 255), 72)

        panel = pygame.Rect(0, 0, 820, 540)
        panel.center = (width // 2, 560)
        pygame.draw.rect(self.screen, (8, 14, 28), panel, border_radius=8)
        pygame.draw.rect(self.screen, (0, 255, 220), panel, width=2, border_radius=8)

        header_font = pygame.font.SysFont("consolas", 24, bold=True)
        key_font = pygame.font.SysFont("consolas", 22, bold=True)
        text_font = pygame.font.SysFont("consolas", 22)
        key_header = header_font.render("KEY", True, (255, 220, 80))
        function_header = header_font.render("FUNCTION", True, (255, 220, 80))
        self.screen.blit(key_header, (panel.x + 54, panel.y + 32))
        self.screen.blit(function_header, (panel.x + 255, panel.y + 32))
        pygame.draw.line(self.screen, (255, 80, 165), (panel.x + 42, panel.y + 72), (panel.right - 42, panel.y + 72), 2)

        movement_labels = getattr(
            keyboard_layout,
            "movement_labels",
            {"up": "W", "left": "A", "down": "S", "right": "D"},
        )
        rows = [
            (f"{movement_labels['up']} / Up Arrow", "Move forward"),
            (f"{movement_labels['down']} / Down Arrow", "Move backward"),
            (f"{movement_labels['left']} / Left Arrow", "Move left"),
            (f"{movement_labels['right']} / Right Arrow", "Move right"),
            ("Left Shift", "Sprint while stamina is available"),
            ("Space", "Dash in the current movement direction"),
            ("Tab", "Maximize or minimize the minimap"),
            ("Esc", "Pause, resume, or go back"),
            ("T", "Hide or show the first-sector tutorial"),
            ("Enter", "Start a run or restart after game over"),
            ("M", "Return to main menu from pause or game over"),
            ("Q", "Quit the game"),
        ]
        for index, (key, function) in enumerate(rows):
            y = panel.y + 88 + index * 38
            if index % 2 == 0:
                pygame.draw.rect(self.screen, (13, 22, 42), (panel.x + 30, y - 9, panel.width - 60, 34), border_radius=5)
            key_surface = key_font.render(key, True, (0, 255, 220))
            function_surface = text_font.render(function, True, (235, 245, 255))
            self.screen.blit(key_surface, (panel.x + 54, y))
            self.screen.blit(function_surface, (panel.x + 255, y))

        self.draw_button("back", "BACK TO MENU  [Esc]", (width // 2, 900), accent=(255, 90, 120))

    def draw_objective_box(self, move_label="WASD", sector=1):
        rect = pygame.Rect(20, 15, 980, 118)
        pygame.draw.rect(self.screen, (8, 14, 28), rect, border_radius=6)
        pygame.draw.rect(self.screen, (0, 255, 220), rect, width=2, border_radius=6)
        self.draw_text(f"Level {sector}: reach the bright green EXIT tile.", (35, 28), (80, 255, 175))
        self.draw_text("Hunters block your route. Avoid red hazards and moving walls.", (35, 53), (255, 215, 220))
        self.draw_text(f"Controls: {move_label} move | Shift sprint | Space dash | Tab map | Esc pause.", (35, 78), (235, 245, 255))
        self.draw_text("Lose: hearts reach 0. Level 1 teaches damage without killing you.", (35, 103), (255, 220, 80))

    def draw_tutorial(self, sector, survival_time, objectives=None, keyboard_layout=None):
        if sector != 1:
            return
        move_label = keyboard_layout.move_label if keyboard_layout else "WASD"
        layout_name = keyboard_layout.name if keyboard_layout else "QWERTY"
        objectives = objectives or {}
        rect = pygame.Rect(self.screen.get_width() - 670, 260, 650, 265)
        pygame.draw.rect(self.screen, (8, 14, 28), rect, border_radius=6)
        pygame.draw.rect(self.screen, (255, 220, 80), rect, width=2, border_radius=6)
        self.draw_text(f"LEVEL 1 TUTORIAL - {layout_name}", (rect.x + 18, rect.y + 16), (255, 220, 80))
        self.draw_text("Complete the checklist. It disappears after Level 1.", (rect.x + 18, rect.y + 44), (210, 230, 255))
        items = [
            ("move", f"Move with {move_label}."),
            ("sprint", "Hold Left Shift to sprint."),
            ("dash", "Press Space while moving to dash."),
            ("survive", "Survive for 12 seconds while hunters chase you."),
            ("exit", "Reach the bright green EXIT tile to finish Level 1."),
        ]
        for index, (key, label) in enumerate(items):
            done = objectives.get(key, False)
            mark = "[x]" if done else "[ ]"
            color = (80, 255, 175) if done else (235, 245, 255)
            self.draw_text(f"{mark} {label}", (rect.x + 18, rect.y + 82 + index * 30), color)
        self.draw_text("Tip: red paths show enemy A* decisions. Press T to hide.", (rect.x + 18, rect.y + 238), (255, 220, 80))

    def draw_damage_tip(self, message, remaining_time):
        if remaining_time <= 0:
            return
        rect = pygame.Rect(self.screen.get_width() // 2 - 450, 145, 900, 100)
        pygame.draw.rect(self.screen, (28, 10, 18), rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 90, 120), rect, width=3, border_radius=8)
        self.draw_center_text("YOU GOT HIT", rect.y + 25, (255, 170, 180), 24)
        self.draw_center_text(message, rect.y + 58, (245, 250, 255), 20)

    def draw_ai_debug(self, enemies, director):
        x, y = 20, 275
        self.draw_text("AI DEBUG", (x, y), (255, 220, 80))
        y += 26
        self.draw_text(f"Threat: {director.threat_level:.0f}/{director.max_threat:.0f}", (x, y))
        y += 26
        for enemy in enemies:
            brain = enemy.brain
            state = brain.state_machine.current_state.name
            name = enemy.__class__.__name__
            self.draw_text(
                f"{name}: {state} | nodes {brain.astar.nodes_explored} | path {brain.astar.last_path_length} | recalc {brain.update_interval:.2f}s",
                (x, y),
                enemy.color,
            )
            y += 26
