class Interception:
    @staticmethod
    def predict_target(player_x, player_y, dx, dy, distance=3):
        return int(round(player_x + dx * distance)), int(round(player_y + dy * distance))
