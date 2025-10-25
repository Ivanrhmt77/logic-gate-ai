from .mcts_node import MCTSNode
from .state import GameState

class MCTSAgent:
    def __init__(self, num_simulations=1000, player_id=2):
        self.num_simulations = num_simulations
        self.player_id = player_id

    def select_move(self, game_state: GameState):
        root = MCTSNode(game_state.copy())

        for _ in range(self.num_simulations):
            node = root

            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            if not node.state.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            winner = node.rollout()

            node.backpropagate(winner, self.player_id)

        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def get_move_statistics(self, game_state):
        root = MCTSNode(game_state.copy())

        for _ in range(self.num_simulations):
            node = root

            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            if not node.state.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            winner = node.rollout()
            node.backpropagate(winner, self.player_id)

        stats = []
        for child in root.children:
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            stats.append({
                'move': child.move,
                'visits': child.visits,
                'wins': child.wins,
                'win_rate': win_rate,
                'card': ID_TO_CARD.get(child.move['card'], 'Unknown'),
                'slot': child.move['slot']
            })

        return sorted(stats, key=lambda x: x['visits'], reverse=True)