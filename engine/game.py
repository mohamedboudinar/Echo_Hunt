import pygame
from config import WIDTH, HEIGHT, FPS, TITLE
from constants import GameState
from engine.timer import Timer
from engine.camera import Camera
from engine.input_handler import InputHandler
from engine.game_state import StateManager
from rendering.renderer import Renderer
from rendering.iso import IsoProjector
from rendering.lighting import LightingEngine
from effects.screen_shake import ScreenShake
from effects.hit_flash import HitFlash
from effects.dash_trail import DashTrail
from ui.heart_display import HeartDisplay
from ui.stamina_bar import StaminaBar
from ui.minimap import Minimap
from engine.progression import ProgressionSystem
from engine.save_manager import SaveManager
from engine.high_scores import HighScoreManager
from engine.audio_manager import AudioManager
from generation.dungeon_generator import DungeonGenerator
from generation.dynamic_obstacles import DynamicObstacleManager
from generation.tilemap import TileType
from ai.astar import AStar
from ai.navigation_grid import NavigationGrid
from ai.pressure_director import PressureDirector
from entities.player import Player
from entities.hunter import Hunter
from entities.dasher import Dasher
from entities.sentinel import Sentinel

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.running = True
        self.timer = Timer(FPS)
        self.camera = Camera(WIDTH, HEIGHT)
        self.input_handler = InputHandler()
        self.state_manager = StateManager()
        self.renderer = Renderer(self.screen, self.camera)
        self.lighting = LightingEngine(WIDTH, HEIGHT)
        self.screen_shake = ScreenShake()
        self.hit_flash = HitFlash(WIDTH, HEIGHT)
        self.dash_trail = DashTrail()
        self.hearts_ui = HeartDisplay()
        self.stamina_ui = StaminaBar()
        self.director = PressureDirector()
        self.minimap = Minimap()
        self.progression = ProgressionSystem()
        self.save_manager = SaveManager()
        self.high_scores = HighScoreManager()
        self.high_score_entries = self.high_scores.load()
        self.audio = AudioManager()
        self.settings_return_state = GameState.MENU
        loaded = self.save_manager.load()
        self.progression.sector = loaded.get("sector", 1)
        self.player_name = ""
        self.name_entry_active = False
        self.score_submitted = False
        self.survival_time = 0.0
        self.tutorial_visible = True
        self.minimap_maximized = False
        self.damage_tip_timer = 0.0
        self.damage_tip_message = ""
        self.tutorial_objectives = self.create_tutorial_objectives()
        self.new_sector()

    def create_tutorial_objectives(self):
        return {
            "move": False,
            "sprint": False,
            "dash": False,
            "survive": False,
            "exit": False,
        }

    def new_sector(self):
        self.generator = DungeonGenerator(seed=self.progression.sector * 1337)
        self.grid = self.generator.generate()
        sx, sy = self.generator.spawn
        ex, ey = self.generator.exit
        self.player = Player(sx, sy)
        self.enemies = self.create_enemy_lineup()
        self.apply_sector_difficulty()
        obstacle_count = min(8, 4 + self.progression.sector)
        obstacle_interval = max(0.55, 1.15 - self.progression.sector * 0.08)
        self.dynamic_obstacles = DynamicObstacleManager(seed=self.progression.sector * 911, count=obstacle_count, move_interval=obstacle_interval)
        self.dynamic_obstacles.initialize(self.grid, self.generator.spawn, self.generator.exit, [enemy.get_position() for enemy in self.enemies])
        self.previous_player_x = self.player.grid_x
        self.previous_player_y = self.player.grid_y

    def create_enemy_lineup(self):
        route = AStar().find_path(self.grid, self.generator.spawn, self.generator.exit)
        if not route:
            ex, ey = self.generator.exit
            return [Hunter(max(1, ex - 8), ey), Dasher(max(1, ex - 5), max(1, ey - 3)), Sentinel(max(1, ex - 3), min(len(self.grid) - 2, ey + 3))]

        if self.progression.sector == 1:
            fractions = (0.34, 0.52, 0.70)
        else:
            fractions = (0.25, 0.48, 0.66)
        positions = [self.route_position(route, fraction) for fraction in fractions]
        return [Hunter(*positions[0]), Dasher(*positions[1]), Sentinel(*positions[2])]

    def route_position(self, route, fraction):
        index = max(1, min(len(route) - 2, int((len(route) - 1) * fraction)))
        for offset in range(0, len(route)):
            for candidate_index in (index + offset, index - offset):
                if 0 < candidate_index < len(route) - 1:
                    x, y = route[candidate_index]
                    if NavigationGrid.is_walkable(self.grid, x, y):
                        return x, y
        return route[index]

    def apply_sector_difficulty(self):
        multiplier = 1.08 + min(0.65, (self.progression.sector - 1) * 0.12)
        for enemy in self.enemies:
            enemy.speed *= multiplier
            enemy.brain.update_interval = max(0.10, enemy.brain.update_interval - (self.progression.sector - 1) * 0.025)
            enemy.brain.detection_radius += min(6, self.progression.sector)
            if self.progression.sector == 1:
                enemy.brain.detection_radius = 99
                enemy.brain.force_repath()
        if self.progression.sector >= 2:
            ex, ey = self.generator.exit
            extra = Hunter(max(1, ex - 10), max(1, ey - 5))
            extra.speed *= multiplier
            extra.brain.update_interval = max(0.14, extra.brain.update_interval - 0.05)
            self.enemies.append(extra)

    def start_new_run(self):
        self.progression = ProgressionSystem()
        self.survival_time = 0.0
        self.tutorial_visible = True
        self.minimap_maximized = False
        self.damage_tip_timer = 0.0
        self.damage_tip_message = ""
        self.tutorial_objectives = self.create_tutorial_objectives()
        self.score_submitted = False
        self.director = PressureDirector()
        self.reset_feedback_effects()
        self.new_sector()
        self.state_manager.set_state(GameState.PLAYING)

    def restart_run(self):
        self.start_new_run()

    def return_to_menu(self):
        self.progression = ProgressionSystem()
        self.survival_time = 0.0
        self.tutorial_visible = True
        self.minimap_maximized = False
        self.name_entry_active = False
        self.damage_tip_timer = 0.0
        self.damage_tip_message = ""
        self.tutorial_objectives = self.create_tutorial_objectives()
        self.score_submitted = False
        self.director = PressureDirector()
        self.reset_feedback_effects()
        self.new_sector()
        self.state_manager.set_state(GameState.MENU)

    def reset_feedback_effects(self):
        self.hit_flash.alpha = 0.0
        self.screen_shake.intensity = 0
        self.screen_shake.duration = 0.0
        self.dash_trail.positions = []

    def try_move_player(self, dx, dy, speed, dt):
        nx = self.player.grid_x + dx * speed * dt
        ny = self.player.grid_y + dy * speed * dt
        if NavigationGrid.is_walkable(self.grid, int(round(nx)), int(round(self.player.grid_y))):
            self.player.grid_x = nx
        if NavigationGrid.is_walkable(self.grid, int(round(self.player.grid_x)), int(round(ny))):
            self.player.grid_y = ny

    def update(self, dt):
        self.input_handler.process_events()
        if self.input_handler.quit_requested:
            self.running = False
            return
        self.handle_state_input()
        if not self.state_manager.is_playing():
            return
        self.survival_time += dt
        dx, dy = self.input_handler.movement_vector()
        if dx or dy:
            self.tutorial_objectives["move"] = True
        pdx = self.player.grid_x - self.previous_player_x
        pdy = self.player.grid_y - self.previous_player_y
        self.previous_player_x = self.player.grid_x
        self.previous_player_y = self.player.grid_y
        self.player.sprinting = self.input_handler.sprinting() and self.player.stamina > 0 and not self.player.exhausted
        if self.player.sprinting:
            self.tutorial_objectives["sprint"] = True
        sprint_multiplier = 1.75 if self.player.sprinting else 1.0
        self.try_move_player(dx, dy, self.player.speed * sprint_multiplier, dt)
        if self.input_handler.dash_pressed() and self.player.start_dash(dx, dy):
            self.tutorial_objectives["dash"] = True
            self.screen_shake.trigger(6, 0.15)
            self.audio.play_sfx("dash")
        if self.player.dash_timer > 0:
            self.try_move_player(self.player.dash_dir_x, self.player.dash_dir_y, self.player.dash_speed, dt)
            self.dash_trail.add(self.player.grid_x, self.player.grid_y)
        self.player.update_stamina(dt)
        self.player.update_timers(dt)
        obstacles_moved = self.dynamic_obstacles.update(dt, self.grid, self.generator.spawn, self.generator.exit, [enemy.get_position() for enemy in self.enemies])
        for enemy in self.enemies:
            if obstacles_moved:
                enemy.brain.force_repath()
            enemy.update(dt, self.grid, self.player, pdx, pdy)
        self.director.update(self.player, self.enemies)
        self.hide_damage_tip_when_safe()
        if self.survival_time >= 12.0:
            self.tutorial_objectives["survive"] = True
        self.check_hazard_collision()
        self.check_enemy_collisions()
        self.check_sector_exit()
        self.screen_shake.update(dt)
        self.hit_flash.update(dt)
        self.damage_tip_timer = max(0.0, self.damage_tip_timer - dt)
        self.dash_trail.update(dt)
        tx, ty = IsoProjector.cart_to_iso(self.player.grid_x, self.player.grid_y)
        self.camera.update(tx, ty)
        if self.player.hearts <= 0:
            self.submit_score()
            self.audio.play_game_over()
            self.state_manager.set_state(GameState.GAME_OVER)

    def submit_score(self):
        if self.score_submitted:
            return
        self.high_score_entries = self.high_scores.add_score(self.player_name, self.progression.sector, self.survival_time)
        self.score_submitted = True

    def handle_state_input(self):
        clicked_action = self.renderer.clicked_button(self.input_handler.mouse_click())
        if self.state_manager.current_state == GameState.MENU and self.input_handler.mouse_click() is not None:
            self.name_entry_active = clicked_action == "name"
        self.update_player_name()
        is_menu = self.state_manager.current_state == GameState.MENU
        typed_this_frame = bool(self.input_handler.typed_text())
        if (self.input_handler.quit_game_pressed() and (not is_menu or not typed_this_frame)) or clicked_action == "quit":
            self.running = False
            return
        if self.input_handler.tutorial_toggle_pressed():
            self.tutorial_visible = not self.tutorial_visible
        if self.input_handler.minimap_toggle_pressed() and self.state_manager.current_state == GameState.PLAYING:
            self.minimap_maximized = not self.minimap_maximized

        if self.input_handler.start_pressed():
            if self.state_manager.current_state == GameState.MENU:
                self.start_new_run()
            elif self.state_manager.current_state == GameState.GAME_OVER:
                self.restart_run()
        if clicked_action == "start" and self.state_manager.current_state == GameState.MENU:
            self.start_new_run()
        if clicked_action == "settings" and self.state_manager.current_state in (GameState.MENU, GameState.PAUSED):
            self.settings_return_state = self.state_manager.current_state
            self.state_manager.set_state(GameState.SETTINGS)
            self.audio.play_sfx("menu")
        if clicked_action == "shortcuts" and self.state_manager.current_state == GameState.MENU:
            self.state_manager.set_state(GameState.SHORTCUTS)
            self.audio.play_sfx("menu")
        if clicked_action == "toggle_music" and self.state_manager.current_state == GameState.SETTINGS:
            self.audio.play_sfx("menu")
            self.audio.set_music_enabled(not self.audio.music_enabled)
        if clicked_action == "music_decrease" and self.state_manager.current_state == GameState.SETTINGS:
            self.audio.set_music_volume(self.audio.music_volume - 0.10)
        if clicked_action == "music_increase" and self.state_manager.current_state == GameState.SETTINGS:
            self.audio.set_music_volume(self.audio.music_volume + 0.10)
        if clicked_action == "toggle_sfx" and self.state_manager.current_state == GameState.SETTINGS:
            self.audio.play_sfx("menu")
            self.audio.set_sfx_enabled(not self.audio.sfx_enabled)
        if clicked_action == "sfx_decrease" and self.state_manager.current_state == GameState.SETTINGS:
            self.audio.set_sfx_volume(self.audio.sfx_volume - 0.10)
        if clicked_action == "sfx_increase" and self.state_manager.current_state == GameState.SETTINGS:
            self.audio.set_sfx_volume(self.audio.sfx_volume + 0.10)
        if clicked_action == "back" and self.state_manager.current_state == GameState.SETTINGS:
            self.state_manager.set_state(self.settings_return_state)
            self.audio.play_sfx("menu")
        if clicked_action == "back" and self.state_manager.current_state == GameState.SHORTCUTS:
            self.state_manager.set_state(GameState.MENU)
            self.audio.play_sfx("menu")
        if clicked_action == "resume" and self.state_manager.current_state == GameState.PAUSED:
            self.state_manager.set_state(GameState.PLAYING)
        if (self.input_handler.menu_pressed() or clicked_action == "menu") and self.state_manager.current_state in (GameState.PAUSED, GameState.GAME_OVER):
            self.return_to_menu()
        if self.input_handler.restart_pressed() and self.state_manager.current_state == GameState.GAME_OVER:
            self.restart_run()
        if clicked_action == "restart" and self.state_manager.current_state == GameState.GAME_OVER:
            self.restart_run()
        if self.state_manager.current_state == GameState.SETTINGS and self.input_handler.pause_pressed():
            self.state_manager.set_state(self.settings_return_state)
        elif self.state_manager.current_state == GameState.SHORTCUTS and self.input_handler.pause_pressed():
            self.state_manager.set_state(GameState.MENU)
        elif self.input_handler.pause_pressed():
            self.state_manager.toggle_pause()

    def update_player_name(self):
        if self.state_manager.current_state != GameState.MENU:
            return
        if not self.name_entry_active:
            return
        if self.input_handler.backspace_pressed():
            self.player_name = self.player_name[:-1]
        for char in self.input_handler.typed_text():
            if len(self.player_name) >= 12:
                break
            if char.isalnum() or char in (" ", "_", "-"):
                self.player_name += char.upper()
        self.player_name = self.player_name[:12]

    def check_enemy_collisions(self):
        for enemy in self.enemies:
            if abs(enemy.grid_x - self.player.grid_x) < 0.55 and abs(enemy.grid_y - self.player.grid_y) < 0.55:
                if self.apply_player_damage("enemy"):
                    self.hit_flash.trigger()
                    self.screen_shake.trigger(10, 0.25)

    def check_hazard_collision(self):
        x, y = self.player.get_position()
        if self.grid[y][x] == TileType.HAZARD and self.apply_player_damage("hazard"):
            self.hit_flash.trigger()
            self.screen_shake.trigger(8, 0.20)

    def apply_player_damage(self, source):
        if self.progression.sector == 1 and self.player.hearts <= 1:
            if self.player.invulnerability_timer > 0:
                return False
            self.player.invulnerability_timer = 1.0
            self.show_damage_tip(source)
            Game.play_hit_sfx(self)
            return True
        damaged = self.player.damage()
        if damaged:
            Game.play_hit_sfx(self)
            if self.progression.sector == 1:
                self.show_damage_tip(source)
        return damaged

    def play_hit_sfx(self):
        audio = getattr(self, "audio", None)
        if audio:
            audio.play_sfx("hit")

    def show_damage_tip(self, source):
        self.damage_tip_timer = 5.5
        if source == "hazard":
            self.damage_tip_message = "Red tiles are hazards. Route around them or dash away quickly."
        else:
            self.damage_tip_message = "Hunters damage you on contact. Sprint, dash, and turn corners to escape."

    def hide_damage_tip_when_safe(self):
        if self.damage_tip_timer <= 0:
            return
        if self.director.threat_level <= 0:
            self.damage_tip_timer = 0.0

    def check_sector_exit(self):
        if self.player.get_position() == self.generator.exit:
            self.tutorial_objectives["exit"] = True
            self.audio.play_level_up()
            self.progression.next_sector()
            self.save_manager.save({"sector": self.progression.sector})
            self.new_sector()

    def render(self):
        shake_x, shake_y = self.screen_shake.get_offset()
        self.camera.set_render_offset(shake_x, shake_y)
        self.renderer.clear()
        self.renderer.draw_grid(self.grid)
        self.renderer.draw_exit_marker(self.generator.exit)
        self.renderer.draw_dash_trail(self.dash_trail)
        self.renderer.draw_enemy_paths(self.enemies)
        self.renderer.draw_player(self.player)
        self.renderer.draw_enemies(self.enemies)
        self.lighting.begin()
        px, py = self.renderer.world_to_screen(self.player.grid_x, self.player.grid_y)
        self.lighting.apply_light(px, py, 260)
        for enemy in self.enemies:
            ex, ey = self.renderer.world_to_screen(enemy.grid_x, enemy.grid_y)
            self.lighting.apply_light(ex, ey, 125)
        self.lighting.render(self.screen)
        self.renderer.draw_synth_noise(16)
        self.hearts_ui.render(self.screen, self.player)
        self.stamina_ui.render(self.screen, self.player)
        self.renderer.draw_objective_box(self.input_handler.keyboard_layout.move_label, self.progression.sector)
        self.renderer.draw_threat_meter(self.director)
        self.renderer.draw_text(f"Sector: {self.progression.sector}", (20, 195))
        self.renderer.draw_text(f"Time: {self.survival_time:05.1f}s", (20, 220))
        self.renderer.draw_text(f"FPS: {self.timer.get_fps():.0f}", (20, 245))
        self.renderer.draw_ai_debug(self.enemies, self.director)
        if self.state_manager.current_state == GameState.PLAYING and self.tutorial_visible:
            self.renderer.draw_tutorial(self.progression.sector, self.survival_time, self.tutorial_objectives, self.input_handler.keyboard_layout)
        if self.state_manager.current_state == GameState.PLAYING:
            self.renderer.draw_damage_tip(self.damage_tip_message, self.damage_tip_timer)
        self.minimap.render(
            self.screen,
            self.grid,
            self.player,
            self.enemies,
            maximized=self.minimap_maximized and self.state_manager.current_state == GameState.PLAYING,
        )
        if self.state_manager.current_state == GameState.MENU:
            self.renderer.draw_menu(self.input_handler.keyboard_layout.move_label, self.player_name, self.high_score_entries, self.name_entry_active)
        elif self.state_manager.current_state == GameState.SETTINGS:
            self.renderer.draw_settings(self.audio.music_enabled, self.audio.sfx_enabled, self.audio.music_volume, self.audio.sfx_volume)
        elif self.state_manager.current_state == GameState.SHORTCUTS:
            self.renderer.draw_shortcuts(self.input_handler.keyboard_layout.move_label)
        elif self.state_manager.current_state == GameState.PAUSED:
            self.renderer.draw_pause()
        if self.state_manager.current_state == GameState.GAME_OVER:
            self.renderer.draw_game_over(self.progression.sector, self.survival_time, self.high_score_entries)
        self.hit_flash.render(self.screen)
        pygame.display.flip()
        self.camera.set_render_offset(0, 0)

    def run(self):
        while self.running:
            dt = self.timer.tick()
            self.update(dt)
            self.render()
        pygame.quit()
