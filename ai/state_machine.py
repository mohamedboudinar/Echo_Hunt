from ai.enemy_states import EnemyState
class StateMachine:
    def __init__(self):
        self.current_state = EnemyState.PATROL
    def set_state(self, state):
        self.current_state = state
    def is_state(self, state):
        return self.current_state == state
