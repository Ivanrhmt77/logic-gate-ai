import random

class RandomAgent:
    """Agent AI yang memilih langkah secara acak dari langkah yang valid."""
    def __init__(self, player_id):
        self.player_id = player_id
        print(f"RandomAgent (Easy) dibuat untuk Player {player_id}")

    def select_move(self, game_state):
        valid_moves = game_state.get_valid_moves()
        if not valid_moves:
            return None
        
        return valid_moves[random.randint(0, len(valid_moves) - 1)]