from enum import Enum

class TileType(Enum):
    EMPTY = 0
    FLOOR = 1
    WALL = 2
    DOOR = 3
    HAZARD = 4
    EXIT = 5
    REWARD = 6
