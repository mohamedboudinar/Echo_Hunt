import pygame
from engine.keyboard_layout import KeyboardLayout

class InputHandler:
    def __init__(self):
        self.keyboard_layout = KeyboardLayout()
        self.quit_requested = False
        self._dash_requested = False
        self._start_requested = False
        self._pause_requested = False
        self._restart_requested = False
        self._quit_game_requested = False
        self._menu_requested = False
        self._tutorial_toggle_requested = False
        self._mouse_click = None
        self._typed_text = ""
        self._backspace_requested = False

    def process_events(self):
        self._dash_requested = False
        self._start_requested = False
        self._pause_requested = False
        self._restart_requested = False
        self._quit_game_requested = False
        self._menu_requested = False
        self._tutorial_toggle_requested = False
        self._mouse_click = None
        self._typed_text = ""
        self._backspace_requested = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._mouse_click = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self._backspace_requested = True
                elif event.unicode and event.unicode.isprintable():
                    self._typed_text += event.unicode
                if event.key == pygame.K_SPACE:
                    self._dash_requested = True
                elif event.key == pygame.K_RETURN:
                    self._start_requested = True
                elif event.key == pygame.K_ESCAPE:
                    self._pause_requested = True
                elif event.key == pygame.K_r:
                    self._restart_requested = True
                elif event.key == pygame.K_q:
                    self._quit_game_requested = True
                elif event.key == pygame.K_m:
                    self._menu_requested = True
                elif event.key == pygame.K_t:
                    self._tutorial_toggle_requested = True

    def movement_vector(self):
        keys = pygame.key.get_pressed()
        bindings = self.keyboard_layout.bindings
        dx = int(keys[bindings["right"]]) - int(keys[bindings["left"]])
        dy = int(keys[bindings["down"]]) - int(keys[bindings["up"]])
        if dx and dy:
            return dx * 0.7071, dy * 0.7071
        return dx, dy

    def sprinting(self):
        return pygame.key.get_pressed()[pygame.K_LSHIFT]

    def dash_pressed(self):
        return self._dash_requested

    def start_pressed(self):
        return self._start_requested

    def pause_pressed(self):
        return self._pause_requested

    def restart_pressed(self):
        return self._restart_requested

    def quit_game_pressed(self):
        return self._quit_game_requested

    def menu_pressed(self):
        return self._menu_requested

    def tutorial_toggle_pressed(self):
        return self._tutorial_toggle_requested

    def mouse_click(self):
        return self._mouse_click

    def typed_text(self):
        return self._typed_text

    def backspace_pressed(self):
        return self._backspace_requested
