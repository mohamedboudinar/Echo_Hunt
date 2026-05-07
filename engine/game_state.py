from constants import GameState

class StateManager:
    def __init__(self):
        self.current_state = GameState.MENU

    def set_state(self, state: GameState):
        self.current_state = state

    def is_playing(self):
        return self.current_state == GameState.PLAYING

    def toggle_pause(self):
        if self.current_state == GameState.PLAYING:
            self.current_state = GameState.PAUSED
        elif self.current_state == GameState.PAUSED:
            self.current_state = GameState.PLAYING
