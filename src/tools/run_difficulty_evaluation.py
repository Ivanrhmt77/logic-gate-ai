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
from src.game_logic.random_agent import RandomAgent
from src.config import ID_TO_CARD

DIFFICULTY_LEVELS = {
    "Easy": {"agent_class": RandomAgent, "params": {}},
    "Medium": {"agent_class": MCTSAgent, "params": {"num_simulations": 5}},
    "Hard": {"agent_class": MCTSAgent, "params": {"num_simulations": 25}},
    "Very Hard": {"agent_class": MCTSAgent, "params": {"num_simulations": 500}},
}

BASELINE_AGENT_CONFIG = {
    "name": "Hard (25 Sims)",
    "class": MCTSAgent,
    "params": {"num_simulations": 25}
}

if __name__ == "__main__":
    print("Menjalankan Mode Evaluasi Tingkat Kesulitan AI...")

    NUM_EVAL_GAMES = 100
    summary_results = []

    print("\n" + "🏆"*35)
    print(f"TURNAMEN TINGKAT KESULITAN AI")
    print(f"Semua level akan diadu melawan baseline: {BASELINE_AGENT_CONFIG['name']}")
    print(f"Jumlah Game per Match: {NUM_EVAL_GAMES}")
    print("🏆"*35 + "\n")

    for diff_name, diff_config in DIFFICULTY_LEVELS.items():
        print("\n" + "#"*70)
        print(f"### MATCH UP: {diff_name} vs {BASELINE_AGENT_CONFIG['name']} ###")
        print("#"*70)

        print(f"\n--- Match 1: {diff_name} (Player 1) vs Baseline (Player 2) ---")
        agent_p1_params = {**diff_config["params"], "player_id": 1}
        agent_p1 = diff_config["agent_class"](**agent_p1_params)
        agent_p2_params = {**BASELINE_AGENT_CONFIG["params"], "player_id": 2}
        agent_p2 = BASELINE_AGENT_CONFIG["class"](**agent_p2_params)

        results1 = evaluate_two_agents(
            num_games=NUM_EVAL_GAMES,
            agent1=agent_p1,
            agent2=agent_p2,
            show_progress=True
        )
        display_evaluation_results(results1, agent1_name=f"{diff_name} (P1)", agent2_name="Baseline (P2)")

        print(f"\n--- Match 2: Baseline (Player 1) vs {diff_name} (Player 2) ---")
        agent_p1_params_match2 = {**BASELINE_AGENT_CONFIG["params"], "player_id": 1}
        agent_p1_match2 = BASELINE_AGENT_CONFIG["class"](**agent_p1_params_match2)
        agent_p2_params_match2 = {**diff_config["params"], "player_id": 2}
        agent_p2_match2 = diff_config["agent_class"](**agent_p2_params_match2)

        results2 = evaluate_two_agents(
            num_games=NUM_EVAL_GAMES,
            agent1=agent_p1_match2,
            agent2=agent_p2_match2,
            show_progress=True
        )
        display_evaluation_results(results2, agent1_name="Baseline (P1)", agent2_name=f"{diff_name} (P2)")

        total_wins = results1['p1_wins'] + results2['p2_wins']
        total_losses = results1['p2_wins'] + results2['p1_wins']
        total_draws = results1['draws'] + results2['draws']
        total_games = (NUM_EVAL_GAMES * 2)
        
        summary_results.append({
            "Difficulty": diff_name,
            "Wins": total_wins,
            "Losses": total_losses,
            "Draws": total_draws,
            "Win Rate": total_wins / total_games if total_games > 0 else 0
        })

    print("\n" + "="*70)
    print("📊 RINGKASAN KESELURUHAN TURNAMEN")
    print(f"(Melawan Baseline: {BASELINE_AGENT_CONFIG['name']})")
    print("="*70)
    print(f"{'Difficulty':<12} | {'Win Rate':<10} | {'Wins':<6} | {'Losses':<6} | {'Draws':<6} | (Total {NUM_EVAL_GAMES * 2} Games)")
    print("-" * 70)
    
    for res in summary_results:
        print(f"{res['Difficulty']:<12} | {res['Win Rate']:<10.1%} | {res['Wins']:<6} | {res['Losses']:<6} | {res['Draws']:<6} |")
        
    print("="*70)
    print("💡 INSIGHT: Win rate harusnya meningkat seiring dengan naiknya tingkat kesulitan.")
    print("   - 'Easy' harusnya sangat rendah (mendekati 0%).")
    print("   - 'Hard' harusnya sekitar 50% (karena melawan dirinya sendiri).")
    print("   - 'Very Hard' harusnya > 50%.")
