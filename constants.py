from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    SETTINGS = auto()
    SHORTCUTS = auto()
    GAME_OVER = auto()
    VICTORY = auto()
