import numpy as np
import random
import math
import copy
from .state import GameState

class MCTSNode:
    def __init__(self, state: GameState, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = state.get_valid_moves()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.41):
        choices_weights = [
            (child.wins / child.visits) + c_param * math.sqrt(2 * math.log(self.visits) / child.visits)
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def expand(self):
        move = self.untried_moves.pop(random.randint(0, len(self.untried_moves) - 1))
        next_state = self.state.copy()
        next_state.apply_move(move)
        child_node = MCTSNode(next_state, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def rollout(self):
        current_state = self.state.copy()

        while not current_state.is_terminal():
            valid_moves = current_state.get_valid_moves()
            if not valid_moves:
                break
            move = random.choice(valid_moves)
            current_state.apply_move(move)

        return current_state.get_winner()

    def backpropagate(self, result, player_perspective):
        self.visits += 1
        if result == player_perspective:
            self.wins += 1
        elif result == 0:
            self.wins += 0.5

        if self.parent:
            self.parent.backpropagate(result, player_perspective)