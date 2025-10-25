import tensorflow as tf
import numpy as np
import os
import sys
from collections import defaultdict

try:
    from .evaluation_utils import setup_python_path, evaluate_two_agents, display_evaluation_results
except ImportError:
    from evaluation_utils import setup_python_path, evaluate_two_agents, display_evaluation_results

setup_python_path()

from src.game_logic.state import GameState
from src.game_logic.mcts_agent import MCTSAgent
from src.config import ID_TO_CARD, CARD_TO_ID, NUM_BINARY_SLOTS, NUM_CARD_SLOTS

print("TensorFlow version:", tf.__version__)

def state_to_vector(game_state):
    binary_vector = game_state.binary_slots.astype(np.float32)
    card_slots_vector = game_state.card_slots.astype(np.float32)

    p1_hand_vector = np.zeros(len(CARD_TO_ID), dtype=np.float32)
    for card_id in game_state.player1_hand:
        if 1 <= card_id <= 5:
            p1_hand_vector[card_id - 1] = 1.0

    p2_hand_vector = np.zeros(len(CARD_TO_ID), dtype=np.float32)
    for card_id in game_state.player2_hand:
        if 1 <= card_id <= 5:
            p2_hand_vector[card_id - 1] = 1.0

    player_vector = np.array([1.0 if game_state.current_player == 1 else -1.0], dtype=np.float32)

    state_vector = np.concatenate([
        binary_vector, card_slots_vector, p1_hand_vector, p2_hand_vector, player_vector
    ])

    if state_vector.shape[0] != 36:
        raise ValueError(f"State vector length is {state_vector.shape[0]}, expected 36")
    return state_vector


class KerasAgent:
    def __init__(self, model_path, player_id):
        self.model = tf.keras.models.load_model(model_path, compile=False)
        self.player_id = player_id
        print(f"Keras model loaded from {model_path} for Player {player_id}")
        self.model.summary()

    def select_move(self, game_state):
        valid_moves = game_state.get_valid_moves()
        if not valid_moves:
            return None

        state_vec = state_to_vector(game_state)
        input_tensor = np.expand_dims(state_vec, axis=0)
        predictions = self.model.predict(input_tensor, verbose=0)[0]

        if predictions.shape[0] != 50:
            raise ValueError(f"Model output size is {predictions.shape[0]}, expected 50")

        best_move = None
        max_score = -np.inf

        move_to_pred_idx = {}
        for move in valid_moves:
            slot = move['slot']
            card_id = move['card']
            pred_idx = slot * 5 + (card_id - 1)
            if 0 <= pred_idx < 50:
                move_to_pred_idx[tuple(sorted(move.items()))] = pred_idx

        for move in valid_moves:
            move_key = tuple(sorted(move.items()))
            if move_key in move_to_pred_idx:
                pred_idx = move_to_pred_idx[move_key]
                score = predictions[pred_idx]
                if score > max_score:
                    max_score = score
                    best_move = move

        if best_move is None and valid_moves:
            print("Warning: KerasAgent choosing randomly.")
            best_move = valid_moves[np.random.randint(len(valid_moves))]
        
        return best_move


if __name__ == "__main__":
    print("Menjalankan Mode Perbandingan AI (MCTS vs Keras)...")

    NUM_EVAL_GAMES = 100
    MCTS_SIMULATIONS = 500
    MODEL_H5_PATH = "models/logic_gate_ai_selfplay_episode_14000.h5"

    if not os.path.exists(MODEL_H5_PATH):
        print(f"\n❌ Error: File model '{MODEL_H5_PATH}' tidak ditemukan.")
        print("Pastikan file .h5 ada di direktori yang sama dengan script ini atau berikan path lengkap.")
        sys.exit(1)

    print("\n" + "#"*70)
    print("### MATCH 1: Keras AI (Player 1) vs MCTS AI (Player 2) ###")
    print("#"*70)

    try:
        agent_keras_p1 = KerasAgent(model_path=MODEL_H5_PATH, player_id=1)
    except Exception as e:
        print(f"\n❌ Gagal membuat KerasAgent: {e}")
        sys.exit(1)
        
    agent_mcts_p2 = MCTSAgent(num_simulations=MCTS_SIMULATIONS, player_id=2)

    results1 = evaluate_two_agents(
        num_games=NUM_EVAL_GAMES,
        agent1=agent_keras_p1,
        agent2=agent_mcts_p2,
        show_progress=True
    )
    display_evaluation_results(results1, agent1_name="Keras AI", agent2_name="MCTS AI")

    print("\n" + "#"*70)
    print("### MATCH 2: MCTS AI (Player 1) vs Keras AI (Player 2) ###")
    print("#"*70)

    agent_mcts_p1 = MCTSAgent(num_simulations=MCTS_SIMULATIONS, player_id=1)
    try:
        agent_keras_p2 = KerasAgent(model_path=MODEL_H5_PATH, player_id=2)
    except Exception as e:
        print(f"\n❌ Gagal membuat KerasAgent: {e}")
        sys.exit(1)

    results2 = evaluate_two_agents(
        num_games=NUM_EVAL_GAMES,
        agent1=agent_mcts_p1,
        agent2=agent_keras_p2,
        show_progress=True
    )
    display_evaluation_results(results2, agent1_name="MCTS AI", agent2_name="Keras AI")

    print("\n" + "="*70)
    print("📊 RINGKASAN KESELURUHAN")
    print("="*70)
    print(f"Total Games per Matchup: {NUM_EVAL_GAMES}")
    print(f"MCTS Simulations: {MCTS_SIMULATIONS}")
    print("-" * 70)
    print("Match 1: Keras AI (P1) vs MCTS AI (P2)")
    print(f"  Keras AI Wins: {results1['p1_wins']} ({results1.get('p1_win_rate', 0):.1%})")
    print(f"  MCTS AI Wins:  {results1['p2_wins']} ({results1.get('p2_win_rate', 0):.1%})")
    print(f"  Draws:         {results1['draws']} ({results1.get('draw_rate', 0):.1%})")
    print("-" * 70)
    print("Match 2: MCTS AI (P1) vs Keras AI (P2)")
    print(f"  MCTS AI Wins:  {results2['p1_wins']} ({results2.get('p1_win_rate', 0):.1%})")
    print(f"  Keras AI Wins: {results2['p2_wins']} ({results2.get('p2_win_rate', 0):.1%})")
    print(f"  Draws:         {results2['draws']} ({results2.get('draw_rate', 0):.1%})")
    print("="*70)
