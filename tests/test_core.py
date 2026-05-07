import pygame

from ai.heuristic import Heuristic
from ai.astar import AStar
from generation.tilemap import TileType
from generation.dungeon_generator import DungeonGenerator
from generation.dynamic_obstacles import DynamicObstacleManager
from generation.validator import TraversabilityValidator
from entities.player import Player
from engine.game import Game
from engine.game_state import StateManager
from engine.input_handler import InputHandler
from engine.keyboard_layout import KeyboardLayout
from engine.high_scores import HighScoreManager
from ui.minimap import Minimap
from constants import GameState


def test_manhattan():
    assert Heuristic.manhattan((0, 0), (5, 5)) == 10


def test_astar_path():
    grid = [[TileType.FLOOR, TileType.FLOOR], [TileType.WALL, TileType.FLOOR]]
    path = AStar().find_path(grid, (0, 0), (1, 1))
    assert path[0] == (0, 0)
    assert path[-1] == (1, 1)


def test_astar_no_path():
    grid = [[TileType.FLOOR, TileType.WALL], [TileType.WALL, TileType.FLOOR]]
    assert AStar().find_path(grid, (0, 0), (1, 1)) == []


def test_astar_invalid_grid():
    assert AStar().find_path([], (0, 0), (1, 1)) == []


def test_generator_traversable():
    gen = DungeonGenerator(seed=42)
    grid = gen.generate()
    assert TraversabilityValidator.validate(grid, gen.spawn, gen.exit)


def test_dash_uses_stamina_and_timer():
    p = Player(0, 0)
    assert p.start_dash(1, 0)
    assert p.stamina == 75
    assert p.dash_timer > 0


def test_damage_invulnerability():
    p = Player(0, 0)
    assert p.damage()
    hearts = p.hearts
    assert not p.damage()
    assert p.hearts == hearts


def test_keyboard_layout_labels_by_language():
    assert KeyboardLayout("fr").move_label == "ZQSD"
    assert KeyboardLayout("en").move_label == "WASD"
    assert KeyboardLayout("de").move_label == "WASD"
    assert KeyboardLayout("de").name == "QWERTZ"
    assert KeyboardLayout("en").movement_labels["up"] == "W"
    assert KeyboardLayout("fr").movement_labels["left"] == "Q"


def test_input_handler_accepts_arrow_keys_for_movement(monkeypatch):
    pressed = {
        pygame.K_UP: True,
        pygame.K_RIGHT: True,
    }

    class FakeKeys:
        def __getitem__(self, key):
            return pressed.get(key, False)

    monkeypatch.setattr(pygame.key, "get_pressed", lambda: FakeKeys())
    handler = InputHandler()
    assert handler.movement_vector() == (0.7071, -0.7071)


def test_minimap_draws_explicit_exit_marker():
    surface = pygame.Surface((120, 120))
    grid = [
        [TileType.FLOOR, TileType.FLOOR, TileType.FLOOR],
        [TileType.FLOOR, TileType.FLOOR, TileType.FLOOR],
        [TileType.FLOOR, TileType.FLOOR, TileType.FLOOR],
    ]
    player = type("Player", (), {"grid_x": 0, "grid_y": 0})()

    Minimap().render(surface, grid, player, [], exit_position=(2, 1), x=10, y=10, scale=10)

    assert surface.get_at((35, 25))[:3] == (80, 255, 175)


def test_hazard_damage_respects_invulnerability():
    p = Player(0, 0)
    assert p.damage()
    hearts = p.hearts
    assert not p.damage()
    assert p.hearts == hearts


def test_dynamic_obstacles_avoid_spawn_exit_and_keep_traversable():
    gen = DungeonGenerator(seed=99)
    grid = gen.generate()
    manager = DynamicObstacleManager(seed=7, count=4)
    manager.initialize(grid, gen.spawn, gen.exit)
    assert gen.spawn not in manager.positions
    assert gen.exit not in manager.positions
    assert TraversabilityValidator.validate(grid, gen.spawn, gen.exit)


def test_dynamic_obstacles_move_without_blocking_route():
    gen = DungeonGenerator(seed=101)
    grid = gen.generate()
    manager = DynamicObstacleManager(seed=12, count=4)
    manager.initialize(grid, gen.spawn, gen.exit)
    manager.move_obstacles(grid, gen.spawn, gen.exit)
    assert gen.spawn not in manager.positions
    assert gen.exit not in manager.positions
    assert TraversabilityValidator.validate(grid, gen.spawn, gen.exit)


class FakeInput:
    def __init__(self, start=False, pause=False, restart=False, quit_game=False, menu=False, tutorial=False, minimap=False, typed_text="", backspace=False, mouse_click=None):
        self.start = start
        self.pause = pause
        self.restart = restart
        self.quit_game = quit_game
        self.menu = menu
        self.tutorial = tutorial
        self.minimap = minimap
        self.typed = typed_text
        self.backspace = backspace
        self.click = mouse_click

    def start_pressed(self):
        return self.start

    def pause_pressed(self):
        return self.pause

    def restart_pressed(self):
        return self.restart

    def quit_game_pressed(self):
        return self.quit_game

    def menu_pressed(self):
        return self.menu

    def tutorial_toggle_pressed(self):
        return self.tutorial

    def minimap_toggle_pressed(self):
        return self.minimap

    def mouse_click(self):
        return self.click

    def typed_text(self):
        return self.typed

    def backspace_pressed(self):
        return self.backspace


class FakeRenderer:
    def __init__(self, clicked_action=None):
        self.clicked_action = clicked_action

    def clicked_button(self, pos):
        if pos is None:
            return None
        return self.clicked_action


class FakeAudio:
    def play_sfx(self, key):
        pass


class FakeGame:
    def __init__(self):
        self.state_manager = StateManager()
        self.restart_count = 0
        self.input_handler = FakeInput()
        self.renderer = FakeRenderer()
        self.audio = FakeAudio()
        self.shortcuts_return_state = GameState.MENU
        self.running = True
        self.tutorial_visible = True
        self.minimap_maximized = False
        self.player_name = ""
        self.name_entry_active = False

    def restart_run(self):
        self.restart_count += 1
        self.state_manager.set_state(GameState.PLAYING)

    def start_new_run(self):
        self.state_manager.set_state(GameState.PLAYING)

    def return_to_menu(self):
        self.state_manager.set_state(GameState.MENU)

    def update_player_name(self):
        Game.update_player_name(self)

    def show_damage_tip(self, source):
        Game.show_damage_tip(self, source)


def test_state_transitions_menu_pause_and_restart():
    fake = FakeGame()
    fake.input_handler = FakeInput(start=True)
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.PLAYING

    fake.input_handler = FakeInput(pause=True)
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.PAUSED

    fake.input_handler = FakeInput(pause=True)
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.PLAYING

    fake.state_manager.set_state(GameState.GAME_OVER)
    fake.input_handler = FakeInput(restart=True)
    Game.handle_state_input(fake)
    assert fake.restart_count == 1
    assert fake.state_manager.current_state == GameState.PLAYING


def test_high_scores_sort_by_level_then_time(tmp_path):
    manager = HighScoreManager(tmp_path / "scores.json", limit=3)
    manager.add_score("A", 1, 40)
    manager.add_score("B", 3, 5)
    scores = manager.add_score("C", 2, 90)
    assert [score["name"] for score in scores] == ["B", "C", "A"]


def test_menu_name_entry_updates_player_name():
    fake = FakeGame()
    fake.renderer = FakeRenderer("name")
    fake.input_handler = FakeInput(mouse_click=(10, 10))
    Game.handle_state_input(fake)
    fake.input_handler = FakeInput(typed_text="sam")
    Game.handle_state_input(fake)
    assert fake.player_name == "SAM"


def test_menu_name_entry_ignores_typing_until_clicked():
    fake = FakeGame()
    fake.input_handler = FakeInput(typed_text="sam")
    Game.handle_state_input(fake)
    assert fake.player_name == ""


def test_shortcuts_menu_opens_and_returns_to_menu():
    fake = FakeGame()
    fake.renderer = FakeRenderer("shortcuts")
    fake.input_handler = FakeInput(mouse_click=(10, 10))
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.SHORTCUTS

    fake.renderer = FakeRenderer("back")
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.MENU

    fake.renderer = FakeRenderer()
    fake.state_manager.set_state(GameState.SHORTCUTS)
    fake.shortcuts_return_state = GameState.MENU
    fake.input_handler = FakeInput(pause=True)
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.MENU


def test_shortcuts_menu_returns_to_pause_when_opened_from_pause():
    fake = FakeGame()
    fake.state_manager.set_state(GameState.PAUSED)
    fake.renderer = FakeRenderer("shortcuts")
    fake.input_handler = FakeInput(mouse_click=(10, 10))
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.SHORTCUTS
    assert fake.shortcuts_return_state == GameState.PAUSED

    fake.renderer = FakeRenderer("back")
    Game.handle_state_input(fake)
    assert fake.state_manager.current_state == GameState.PAUSED


def test_minimap_toggle_only_during_play():
    fake = FakeGame()
    fake.input_handler = FakeInput(minimap=True)
    Game.handle_state_input(fake)
    assert not fake.minimap_maximized

    fake.state_manager.set_state(GameState.PLAYING)
    Game.handle_state_input(fake)
    assert fake.minimap_maximized

    Game.handle_state_input(fake)
    assert not fake.minimap_maximized


def test_level_one_damage_cannot_kill_player():
    class FakePlayer:
        def __init__(self):
            self.hearts = 1
            self.invulnerability_timer = 0.0

        def damage(self):
            self.hearts = 0
            return True

    fake = FakeGame()
    fake.progression = type("Progression", (), {"sector": 1})()
    fake.player = FakePlayer()
    fake.damage_tip_timer = 0.0
    fake.damage_tip_message = ""
    assert Game.apply_player_damage(fake, "enemy")
    assert fake.player.hearts == 1
    assert fake.damage_tip_timer > 0


def test_level_one_enemies_spawn_between_spawn_and_exit():
    game = object.__new__(Game)
    game.progression = type("Progression", (), {"sector": 1})()
    game.generator = DungeonGenerator(seed=1337)
    game.grid = game.generator.generate()
    game.enemies = Game.create_enemy_lineup(game)
    Game.apply_sector_difficulty(game)
    sx, sy = game.generator.spawn
    ex, ey = game.generator.exit
    route_distance = abs(ex - sx) + abs(ey - sy)
    for enemy in game.enemies:
        enemy_distance = abs(enemy.grid_x - sx) + abs(enemy.grid_y - sy)
        assert 0 < enemy_distance < route_distance
        assert enemy.brain.detection_radius >= 99


def test_damage_tip_hides_when_safe():
    fake = FakeGame()
    fake.damage_tip_timer = 4.0
    fake.director = type("Director", (), {"threat_level": 0})()
    Game.hide_damage_tip_when_safe(fake)
    assert fake.damage_tip_timer == 0.0
