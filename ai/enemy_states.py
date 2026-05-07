from enum import Enum, auto
class EnemyState(Enum):
    PATROL = auto()
    CHASE = auto()
    SEARCH = auto()
    AMBUSH = auto()
    RECOVER = auto()
