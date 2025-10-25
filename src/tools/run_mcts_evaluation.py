import numpy as np
import time
from collections import defaultdict

try:
    from .evaluation_utils import setup_python_path, display_evaluation_results
except ImportError:
    from evaluation_utils import setup_python_path, display_evaluation_results

setup_python_path()

from src.game_logic.state import GameState
from src.game_logic.mcts_agent import MCTSAgent
from src.config import ID_TO_CARD

def evaluate_ai_performance(num_games=100, ai1_simulations=500, ai2_simulations=500, show_progress=True):
    ai1 = MCTSAgent(num_simulations=ai1_simulations, player_id=1)
    ai2 = MCTSAgent(num_simulations=ai2_simulations, player_id=2)

    results = {
        'ai1_wins': 0,
        'ai2_wins': 0,
        'draws': 0,
        'game_lengths': []
    }

    print(f"\n{'='*70}")
    print(f"EVALUASI AI: {num_games} games")
    print(f"AI1 (Target=1): {ai1_simulations} simulasi MCTS")
    print(f"AI2 (Target=0): {ai2_simulations} simulasi MCTS")
    print(f"{'='*70}\n")

    for game_num in range(num_games):
        if show_progress and (game_num + 1) % 10 == 0:
            print(f"Progress: {game_num + 1}/{num_games} games", end="\r")

        game = GameState(player1_target=1, player2_target=0)
        move_count = 0

        while not game.is_terminal():
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break

            if game.current_player == 1:
                move = ai1.select_move(game)
            else:
                move = ai2.select_move(game)

            game.apply_move(move)
            move_count += 1

        winner = game.get_winner()

        if winner == 1:
            results['ai1_wins'] += 1
        elif winner == 2:
            results['ai2_wins'] += 1
        else:
            results['draws'] += 1
        results['game_lengths'].append(move_count)

    if show_progress:
        print(f"Progress: {num_games}/{num_games} games - SELESAI!     ")

    results['ai1_win_rate'] = results['ai1_wins'] / num_games
    results['ai2_win_rate'] = results['ai2_wins'] / num_games
    results['draw_rate'] = results['draws'] / num_games
    results['avg_game_length'] = np.mean(results['game_lengths'])
    results['std_game_length'] = np.std(results['game_lengths'])
    results['min_game_length'] = np.min(results['game_lengths'])
    results['max_game_length'] = np.max(results['game_lengths'])

    display_args = {
        'p1_wins': results['ai1_wins'], 'p2_wins': results['ai2_wins'], 'draws': results['draws'],
        'p1_win_rate': results['ai1_win_rate'], 'p2_win_rate': results['ai2_win_rate'],
        'draw_rate': results['draw_rate'], 'avg_game_length': results['avg_game_length'],
        'std_game_length': results['std_game_length'], 'min_game_length': results['min_game_length'],
        'max_game_length': results['max_game_length']
    }
    display_evaluation_results(display_args, agent1_name=f"MCTS (P1, {ai1_simulations} sims)", agent2_name=f"MCTS (P2, {ai2_simulations} sims)")

    return results

def compare_different_simulations(num_games_per_config=50):
    print(f"\n{'='*70}")
    print("🔬 EVALUASI KOMPARATIF: Pengaruh Jumlah Simulasi MCTS")
    print(f"{'='*70}\n")

    simulation_configs = [
        (100, 500),
        (300, 500),
        (500, 500),
        (500, 1000),
        (1000, 1000),
    ]

    comparison_results = []

    for ai1_sims, ai2_sims in simulation_configs:
        print(f"\n🎯 Testing: AI1({ai1_sims} sims) vs AI2({ai2_sims} sims)")
        
        ai1 = MCTSAgent(num_simulations=ai1_sims, player_id=1)
        ai2 = MCTSAgent(num_simulations=ai2_sims, player_id=2)

        results = {
            'ai1_wins': 0,
            'ai2_wins': 0,
            'draws': 0,
            'game_lengths': []
        }

        for game_num in range(num_games_per_config):
            game = GameState(player1_target=1, player2_target=0)
            while not game.is_terminal():
                valid_moves = game.get_valid_moves()
                if not valid_moves:
                    break
                if game.current_player == 1:
                    move = ai1.select_move(game)
                else:
                    move = ai2.select_move(game)
                game.apply_move(move)
            
            winner = game.get_winner()
            if winner == 1:
                results['ai1_wins'] += 1
            elif winner == 2:
                results['ai2_wins'] += 1
            else:
                results['draws'] += 1
            results['game_lengths'].append(len(game.card_slots) - np.count_nonzero(game.card_slots==0))

        results['ai1_win_rate'] = results['ai1_wins'] / num_games_per_config
        results['ai2_win_rate'] = results['ai2_wins'] / num_games_per_config
        results['draw_rate'] = results['draws'] / num_games_per_config
        results['avg_game_length'] = np.mean(results['game_lengths'])
        
        comparison_results.append({
            'config': f"AI1({ai1_sims}) vs AI2({ai2_sims})",
            'ai1_sims': ai1_sims,
            'ai2_sims': ai2_sims,
            'ai1_win_rate': results['ai1_win_rate'],
            'ai2_win_rate': results['ai2_win_rate'],
            'draw_rate': results['draw_rate'],
            'avg_length': results['avg_game_length']
        })

    print(f"\n{'='*90}")
    print("📊 RINGKASAN KOMPARASI")
    print(f"{'='*90}")
    print(f"{'Config':<25} | {'AI1 Win':<10} | {'AI2 Win':<10} | {'Draw':<8} | {'Avg Moves':<10}")
    print(f"{'-'*90}")

    for res in comparison_results:
        print(f"{res['config']:<25} | {res['ai1_win_rate']:>8.1%} | {res['ai2_win_rate']:>8.1%} | "
              f"{res['draw_rate']:>6.1%} | {res['avg_length']:>10.2f}")

    print(f"{'='*90}\n")
    print("💡 INSIGHTS:")
    print("  • Semakin banyak simulasi MCTS → AI semakin kuat")
    print("  • Perbedaan simulasi yang besar → Win rate berbeda signifikan")
    print("  • Game lebih panjang → Kedua AI lebih hati-hati (banyak simulasi)")
    print()

    return comparison_results

def evaluate_opening_strategies(num_games=100):
    print(f"\n{'='*70}")
    print("🎲 EVALUASI STRATEGI PEMBUKAAN")
    print(f"{'='*70}\n")

    ai = MCTSAgent(num_simulations=500, player_id=2)

    opening_moves = defaultdict(int)
    opening_wins = defaultdict(int)

    for game_num in range(num_games):
        if (game_num + 1) % 20 == 0:
            print(f"Progress: {game_num + 1}/{num_games} games", end="\r")

        game = GameState(player1_target=1, player2_target=0)

        ai_temp = MCTSAgent(num_simulations=500, player_id=1)
        first_move = ai_temp.select_move(game)

        move_key = f"Slot {first_move['slot']} - {ID_TO_CARD[first_move['card']]}"
        opening_moves[move_key] += 1

        game.apply_move(first_move)

        while not game.is_terminal():
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break

            if game.current_player == 1:
                move = ai_temp.select_move(game)
            else:
                move = ai.select_move(game)

            game.apply_move(move)

        if game.get_winner() == 1:
            opening_wins[move_key] += 1

    print(f"Progress: {num_games}/{num_games} games - SELESAI!     \n")

    print(f"{'Opening Move':<20} | {'Frequency':<12} | {'Win Rate':<10}")
    print(f"{'-'*50}")

    sorted_openings = sorted(opening_moves.items(), key=lambda x: x[1], reverse=True)

    for move, freq in sorted_openings:
        wins = opening_wins[move]
        win_rate = wins / freq if freq > 0 else 0
        print(f"{move:<20} | {freq:>4} ({freq/num_games:>5.1%}) | {win_rate:>8.1%}")

    print(f"{'='*70}\n")

def run_full_evaluation():
    print("\n" + "🚀"*35)
    print("SISTEM EVALUASI LENGKAP - GERBANG LOGIKA AI")
    print("🚀"*35 + "\n")

    print("Pilih mode evaluasi:")
    print("1. Evaluasi Standar (100 games, AI vs AI balanced)")
    print("2. Evaluasi Komparatif (berbagai konfigurasi simulasi)")
    print("3. Evaluasi Strategi Pembukaan")
    print("4. Evaluasi Lengkap (semua di atas)")

    while True:
        choice = input("\nPilih (1-4): ").strip()

        if choice == '1':
            results = evaluate_ai_performance(num_games=100, ai1_simulations=500, ai2_simulations=500)
            break
        elif choice == '2':
            compare_different_simulations(num_games_per_config=50)
            break
        elif choice == '3':
            evaluate_opening_strategies(num_games=100)
            break
        elif choice == '4':
            print("\n🔥 Memulai evaluasi lengkap... Ini akan memakan waktu beberapa menit.\n")

            print("\n" + "="*70)
            print("BAGIAN 1: EVALUASI STANDAR")
            print("="*70)
            evaluate_ai_performance(num_games=100, ai1_simulations=500, ai2_simulations=500)

            print("\n" + "="*70)
            print("BAGIAN 2: EVALUASI KOMPARATIF")
            print("="*70)
            compare_different_simulations(num_games_per_config=50)

            print("\n" + "="*70)
            print("BAGIAN 3: EVALUASI STRATEGI PEMBUKAAN")
            print("="*70)
            evaluate_opening_strategies(num_games=100)

            print("\n✅ EVALUASI LENGKAP SELESAI!")
            break
        else:
            print("❌ Pilih 1-4!")

if __name__ == "__main__":
    print("Menjalankan Mode Evaluasi Internal MCTS...")
    run_full_evaluation()