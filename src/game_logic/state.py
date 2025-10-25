import numpy as np
import copy
from src.config import *

class GameState:
    def __init__(self, player1_target=1, player2_target=0):
        self.binary_slots = np.full(NUM_BINARY_SLOTS, -1)
        self.binary_slots[:len(INITIAL_BINARY_INPUTS)] = INITIAL_BINARY_INPUTS
        self.card_slots = np.zeros(NUM_CARD_SLOTS)
        self.player1_hand = list(CARD_TO_ID.values())
        self.player2_hand = list(CARD_TO_ID.values())
        self.player1_target = player1_target
        self.player2_target = player2_target
        self.current_player = 1

    def _get_input_binary_indices(self, slot_idx):
        if 0 <= slot_idx <= 3:
            return slot_idx, slot_idx + 1
        elif 4 <= slot_idx <= 6:
            base = 5
            offset = slot_idx - 4
            return base + offset, base + offset + 1
        elif 7 <= slot_idx <= 8:
            base = 9
            offset = slot_idx - 7
            return base + offset, base + offset + 1
        elif slot_idx == 9:
            return 12, 13

    def _get_output_binary_index(self, slot_idx):
        if 0 <= slot_idx <= 3:
            return 5 + slot_idx
        elif 4 <= slot_idx <= 6:
            return 9 + (slot_idx - 4)
        elif 7 <= slot_idx <= 8:
            return 12 + (slot_idx - 7)
        elif slot_idx == 9:
            return 14

    def get_valid_moves(self):
        moves = []
        hand = self.player1_hand if self.current_player == 1 else self.player2_hand
        empty_slots = [i for i, slot in enumerate(self.card_slots) if slot == 0]

        for slot in empty_slots:
            idx1, idx2 = self._get_input_binary_indices(slot)
            if self.binary_slots[idx1] != -1 and self.binary_slots[idx2] != -1:
                for card in hand:
                    moves.append({'slot': slot, 'card': card})
        return moves

    def apply_move(self, move):
        slot = move['slot']
        card = move['card']
        hand = self.player1_hand if self.current_player == 1 else self.player2_hand
        hand.remove(card)
        self.card_slots[slot] = card

        idx1, idx2 = self._get_input_binary_indices(slot)
        output_idx = self._get_output_binary_index(slot)
        input_val1 = self.binary_slots[idx1]
        input_val2 = self.binary_slots[idx2]

        self.binary_slots[output_idx] = self._calculate_logic(card, input_val1, input_val2)
        self.current_player = 2 if self.current_player == 1 else 1

    def _calculate_logic(self, card_id, a, b):
        if card_id == CARD_TO_ID['AND']:
            return int(a and b)
        elif card_id == CARD_TO_ID['OR']:
            return int(a or b)
        elif card_id == CARD_TO_ID['NAND']:
            return int(not (a and b))
        elif card_id == CARD_TO_ID['NOR']:
            return int(not (a or b))
        elif card_id == CARD_TO_ID['XOR']:
            return int(a != b)

    def is_terminal(self):
        return self.binary_slots[NUM_BINARY_SLOTS - 1] != -1 and len(self.get_valid_moves()) == 0

    def get_winner(self):
        final_value = self.binary_slots[NUM_BINARY_SLOTS - 1]
        if final_value == -1:
            return 0
        if final_value == self.player1_target:
            return 1
        elif final_value == self.player2_target:
            return 2
        else:
            return 0

    def copy(self):
        return copy.deepcopy(self)