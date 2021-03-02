import random
from itertools import product, combinations
from copy import deepcopy
import numpy as np
import time

ids = ['206014185', '316361641']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = self.change_map(initial_state)
        self.zone_of_control = zone_of_control
        self.order = order
        self.enemy_zone = [(row_idx, col_idx) for row_idx in range(len(initial_state))
                           for col_idx in range(len(initial_state)) if (row_idx, col_idx) not in zone_of_control]
        self.depth = 2
        self.start = time.time()
        self.timeout = 4.7

    def act(self, state):
        self.start = time.time()
        self.update_map(state)
        positions, actions = self.play_max(self.initial_state, 0, -np.inf, np.inf)
        action_list = []
        for pos, action in zip(positions, actions):
            if pos != (-1, -1):
                if action == 'I':
                    action_list.append(('vaccinate', pos))
                else:
                    action_list.append(('quarantine', pos))
        for atomic_action in action_list:
            effect, location = atomic_action[0], atomic_action[1]
            if 'v' in effect:
                self.initial_state[location[0]][location[1]] = 'I'
            else:
                self.initial_state[location[0]][location[1]] = 'Q0'
        self.initial_state = self.change_state(self.initial_state)
        return action_list

    def change_map(self, initial_state):
        for i in range(len(initial_state)):
            for j in range(len(initial_state[0])):
                if initial_state[i][j] == 'S':
                    initial_state[i][j] = 'S1'
                elif initial_state[i][j] == 'Q':
                    initial_state[i][j] = 'Q1'
        return initial_state

    def play_max(self, state, cur_depth, alpha, beta):
        value = -np.inf
        possible_quarantine = [(row_idx, col_idx) for (row_idx, col_idx) in self.zone_of_control if
                               'S' in state[row_idx][col_idx]]
        if cur_depth == self.depth:
            return self.heuristic(state, self.zone_of_control) - self.heuristic(state, self.enemy_zone)
        possible_immune = [(row_idx, col_idx) for (row_idx, col_idx) in self.zone_of_control if
                           state[row_idx][col_idx] == 'H']
        possible_combination_0_0 = {((-1, -1), (-1, -1)): ('FAKE', 'FAKE')}
        possible_combination_0_1 = {((-1, -1), pos): ('FAKE', 'Q0') for pos in possible_quarantine}
        possible_combination_1_0 = {((-1, -1), pos): ('FAKE', 'I') for pos in possible_immune}
        possible_combination_1_1 = {(pos1, pos2): ('I', 'Q0') for pos1, pos2 in
                                    product(possible_immune, possible_quarantine)}
        possible_actions = {}
        possible_actions.update(possible_combination_1_0)
        possible_actions.update(possible_combination_1_1)
        if not possible_actions or not possible_combination_1_0:
            possible_actions.update(possible_combination_0_0)
            possible_actions.update(possible_combination_0_1)
        max_dict = {}
        for positions, actions in possible_actions.items():
            new_state = deepcopy(state)
            for pos, action in zip(positions, actions):
                if pos != (-1, -1):
                    new_state[pos[0]][pos[1]] = action
            new_state = self.change_state(new_state)
            if self.order != 'first':
                new_state = self.change_state(new_state)
            result = self.play_min(new_state, cur_depth + 1, alpha, beta)
            value = max(value, result)
            if value >= beta:
                return value
            alpha = max(alpha, value)
            max_dict[(positions, actions)] = result
            if time.time() - self.start > self.timeout:
                break
        if cur_depth == 0:
            return max(max_dict, key=max_dict.get)
        return max(max_dict.values())

    def play_min(self, state, cur_depth, alpha, beta):
        value = np.inf
        possible_quarantine = [(row_idx, col_idx) for (row_idx, col_idx) in self.zone_of_control if
                               'S' in state[row_idx][col_idx]]
        if cur_depth == self.depth:
            return self.heuristic(state, self.zone_of_control) - self.heuristic(state, self.enemy_zone)
        possible_immune = [(row_idx, col_idx) for (row_idx, col_idx) in self.zone_of_control if
                           state[row_idx][col_idx] == 'H']
        possible_combination_0_0 = {((-1, -1), (-1, -1)): ('FAKE', 'FAKE')}
        possible_combination_0_1 = {((-1, -1), pos): ('FAKE', 'Q0') for pos in possible_quarantine}
        possible_combination_1_0 = {((-1, -1), pos): ('FAKE', 'I') for pos in possible_immune}
        possible_combination_1_1 = {(pos1, pos2): ('I', 'Q0') for pos1, pos2 in
                                    product(possible_immune, possible_quarantine)}
        possible_actions = {}
        possible_actions.update(possible_combination_1_0)
        possible_actions.update(possible_combination_1_1)
        if not possible_actions or not possible_combination_1_0:
            possible_actions.update(possible_combination_0_0)
            possible_actions.update(possible_combination_0_1)

        min_dict = {}
        for positions, actions in possible_actions.items():
            new_state = deepcopy(state)
            for pos, action in zip(positions, actions):
                if pos != (-1, -1):
                    new_state[pos[0]][pos[1]] = action
            if self.order == 'first':
                new_state = self.change_state(new_state)
            result = self.play_max(new_state, cur_depth + 1, alpha, beta)
            value = min(value, result)
            if value <= alpha:
                return value
            beta = min(beta, value)
            min_dict[(positions, actions)] = result
            if time.time() - self.start > self.timeout:
                break
        if cur_depth == 0:
            return min(min_dict, key=min_dict.get)
        return min(min_dict.values())

    def heuristic(self, state, zone):

        def count_surroundings(given_state, row_idx, col_idx, s, changed_zone):
            counter = 0
            if row_idx - 1 >= 0 and s in given_state[row_idx - 1][col_idx][0] and (row_idx - 1, col_idx) in \
                    changed_zone:
                counter += 1
                changed_zone.remove((row_idx - 1, col_idx))
            if row_idx + 1 < len(given_state) and s in given_state[row_idx + 1][col_idx][0] and (
                    row_idx + 1, col_idx) in changed_zone:
                counter += 1
                changed_zone.remove((row_idx + 1, col_idx))
            if col_idx - 1 >= 0 and s in given_state[row_idx][col_idx - 1][0] and (row_idx, col_idx - 1) in \
                    changed_zone:
                counter += 1
                changed_zone.remove((row_idx, col_idx - 1))
            if col_idx + 1 < len(given_state[row_idx]) and s in given_state[row_idx][col_idx + 1][0] and (
                    row_idx, col_idx + 1) in changed_zone:
                counter += 1
                changed_zone.remove((row_idx, col_idx + 1))
            return counter

        changed_zone = zone.copy()
        counterS = 0
        counterQ = 0
        counterI = 0
        counterH = 0
        count_Q1_surrounded_by_S = 0
        count_S_surrounded_by_H = 0
        count_S1_surrounded_by_Q = 0
        count_S2_surrounded_by_Q2 = 0
        count_I_surrounded_by_S_H = 0
        for row_idx in range(len(state)):
            for col_idx in range(len(state[row_idx])):
                if 'S' in state[row_idx][col_idx]:
                    if (row_idx, col_idx) in zone:
                        counterS += 1
                    count_S_surrounded_by_H += count_surroundings(state, row_idx, col_idx, 'H', changed_zone)
                if 'Q' in state[row_idx][col_idx] and (row_idx, col_idx) in zone:
                    counterQ += 1
                if state[row_idx][col_idx] == 'I' and (row_idx, col_idx) in zone:
                    counterI += 1
                if state[row_idx][col_idx] == 'H' and (row_idx, col_idx) in zone:
                    counterH += 1
        return -counterS - 5 * counterQ + counterI + counterH - count_S_surrounded_by_H - count_S1_surrounded_by_Q / 2 \
               - count_S2_surrounded_by_Q2 / 2 - count_Q1_surrounded_by_S + count_I_surrounded_by_S_H

    def change_state(self, state):
        new_state = deepcopy(state)
        # virus spread
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] == 'H' and ((i - 1 >= 0 and 'S' in state[i - 1][j]) or
                                           (i + 1 < len(state) and 'S' in state[i + 1][j]) or
                                           (j - 1 >= 0 and 'S' in state[i][j - 1]) or
                                           (j + 1 < len(state[0]) and 'S' in state[i][j + 1])):
                    new_state[i][j] = 'S0'

        state = new_state
        # advancing sick counters
        for i in range(len(state)):
            for j in range(len(state[0])):
                if 'S' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 3:
                        state[i][j] = 'S' + str(turn + 1)
                    else:
                        state[i][j] = 'H'

                # advancing quarantine counters
                if 'Q' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 2:
                        state[i][j] = 'Q' + str(turn + 1)
                    else:
                        state[i][j] = 'H'

        return state

    def update_map(self, state):
        for i in range(len(self.initial_state)):
            for j in range(len(self.initial_state[0])):
                if self.initial_state[i][j] == 'H' and state[i][j] == 'Q':  # enemy did S3 to Q
                    if self.order == 'first':
                        self.initial_state[i][j] = 'Q1'
                    else:
                        self.initial_state[i][j] = 'Q0'
                if 'S' in self.initial_state[i][j] and state[i][j] == 'Q':  # enemy did S1/2 to Q
                    if self.order == 'first':
                        self.initial_state[i][j] = 'Q1'
                    else:
                        self.initial_state[i][j] = 'Q0'
                if self.initial_state[i][j] == 'S1' and state[i][j] == 'H':  # we did misinfection when enemy did S to Q
                    self.initial_state[i][j] = 'H'
                if self.initial_state[i][j] == 'S1' and state[i][j] == 'I':  # we did misinfection when enemy did H to I
                    self.initial_state[i][j] = 'I'
                if self.initial_state[i][j] == 'H' and state[i][j] == 'I':  # enemy did H to I
                    self.initial_state[i][j] = 'I'
        return
