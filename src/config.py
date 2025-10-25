import numpy as np
import random
import copy
import math
from collections import defaultdict

NUM_BINARY_SLOTS = 15
NUM_CARD_SLOTS = 10

CARD_TO_ID = {
    'AND': 1,
    'OR': 2,
    'NAND': 3,
    'NOR': 4,
    'XOR': 5
}

ID_TO_CARD = {v: k for k, v in CARD_TO_ID.items()}
INITIAL_BINARY_INPUTS = [0, 1, 0, 1, 0]