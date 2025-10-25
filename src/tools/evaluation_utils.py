import numpy as np
import time
import sys
import os

def setup_python_path():
    try:
        from src.game_logic.state import GameState
    except ImportError:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

setup_python_path()
from src.game_logic.state import GameState

def evaluate_two_agents(num_games=100, agent1=None, agent2=None, show_progress=True):
    if agent1 is None or agent2 is None:
        raise ValueError("Both agent1 and agent2 must be provided")

    results = {
        'p1_wins': 0,
        'p2_wins': 0,
        'draws': 0,
        'game_lengths': []
    }

    agent1_name = agent1.__class__.__name__
    agent2_name = agent2.__class__.__name__

    print(f"\n{'='*70}")
    print(f"EVALUASI: {num_games} games")
    print(f"Player 1 (Target=1): {agent1_name}")
    print(f"Player 2 (Target=0): {agent2_name}")
    print(f"{'='*70}\n")

    start_time = time.time()
    for game_num in range(num_games):
        if show_progress and (game_num + 1) % 5 == 0:
            elapsed_time = time.time() - start_time
            print(f"Progress: {game_num + 1}/{num_games} games ({elapsed_time:.1f}s elapsed)", end="\r")

        game = GameState(player1_target=1, player2_target=0)
        move_count = 0

        while not game.is_terminal():
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break

            if game.current_player == 1:
                move = agent1.select_move(game)
            else:
                move = agent2.select_move(game)

            if move is None:
                print(f"\nError: Agent {game.current_player} failed to select a move. Game set as draw.")
                winner = 0
                break

            game.apply_move(move)
            move_count += 1
        else:
            winner = game.get_winner()

        if winner == 1:
            results['p1_wins'] += 1
        elif winner == 2:
            results['p2_wins'] += 1
        else:
            results['draws'] += 1

        results['game_lengths'].append(move_count)

    end_time = time.time()
    total_time = end_time - start_time
    if show_progress:
        print(f"Progress: {num_games}/{num_games} games - SELESAI! ({total_time:.1f}s total)      ")

    if num_games > 0:
        results['p1_win_rate'] = results['p1_wins'] / num_games
        results['p2_win_rate'] = results['p2_wins'] / num_games
        results['draw_rate'] = results['draws'] / num_games
        results['avg_game_length'] = np.mean(results['game_lengths'])
        results['std_game_length'] = np.std(results['game_lengths'])
        results['min_game_length'] = np.min(results['game_lengths'])
        results['max_game_length'] = np.max(results['game_lengths'])
    else:
        results.update({k: 0 for k in ['p1_win_rate', 'p2_win_rate', 'draw_rate', 'avg_game_length', 'std_game_length', 'min_game_length', 'max_game_length']})

    return results


def display_evaluation_results(results, agent1_name="Agent 1", agent2_name="Agent 2"):
    print(f"\n{'='*70}")
    print("📊 HASIL EVALUASI")
    print(f"{'='*70}\n")

    print("🏆 KEMENANGAN:")
    print(f"  {agent1_name} (P1, Target=1): {results['p1_wins']} wins ({results.get('p1_win_rate', 0):.1%})")
    print(f"  {agent2_name} (P2, Target=0): {results['p2_wins']} wins ({results.get('p2_win_rate', 0):.1%})")
    print(f"  Draw:                   {results['draws']} games ({results.get('draw_rate', 0):.1%})")

    print(f"\n📈 STATISTIK GAME:")
    print(f"  Rata-rata panjang game: {results.get('avg_game_length', 0):.2f} moves")
    print(f"  Standar deviasi:        {results.get('std_game_length', 0):.2f} moves")
    print(f"  Game terpendek:         {results.get('min_game_length', 0)} moves")
    print(f"  Game terpanjang:        {results.get('max_game_length', 0)} moves")

    print(f"\n📊 VISUALISASI WIN RATE:")
    p1_rate = results.get('p1_win_rate', 0)
    p2_rate = results.get('p2_win_rate', 0)
    draw_rate = results.get('draw_rate', 0)

    p1_bar = "█" * int(p1_rate * 50)
    p2_bar = "█" * int(p2_rate * 50)
    draw_bar = "█" * int(draw_rate * 50)

    print(f"  {agent1_name} (P1): {p1_bar} {p1_rate:.1%}")
    print(f"  {agent2_name} (P2): {p2_bar} {p2_rate:.1%}")
    print(f"  Draw:       {draw_bar} {draw_rate:.1%}")

    print(f"\n{'='*70}\n")
