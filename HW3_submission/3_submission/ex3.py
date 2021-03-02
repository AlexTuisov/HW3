import random
import math
from copy import deepcopy
from itertools import chain, combinations, product

ids = ['207668286', '316327238']


# adjusted function from utilis.py
def powerset(iterable, t):
    """powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    power_list = []
    for item in chain.from_iterable(combinations(iterable, r) for r in range(t + 1)):
        if item != ():
            power_list.append(item)
    return power_list


# checks if a coord' is in the map limits
def check_limits(state, x, y):
    if 0 <= x < len(state):
        if 0 <= y < len(state[0]):
            return True
    return False


def act_to_use(state, action_list):
    s_copy = deepcopy(state)
    if action_list:
        for act in action_list:
            x = act[1][0]
            y = act[1][1]
            if 'vaccinate' == act[0]:
                s_copy[x][y] = 'I'
            else:
                s_copy[x][y] = 'Q' + str('0')
        return s_copy
    else:
        return s_copy


def update_turns(state):
    s_copy = deepcopy(state)
    num_rows = len(state)
    num_cols = len(state[0])
    # infect
    for x in range(num_rows):
        for y in range(num_cols):
            if state[x][y] == 'H' and tile_is_infected(state, x, y):
                s_copy[x][y] = 'S' + str('1')
    # update number of turns that the tile is at S/Q
    for x in range(num_rows):
        for y in range(num_cols):
            if state[x][y][0] == 'Q' or state[x][y][0] == 'S':
                turn = int(state[x][y][1])
                if state[x][y][0] == 'Q':
                    if turn >= 2:
                        s_copy[x][y] = 'H'
                    else:
                        s_copy[x][y] = 'Q' + str(turn + 1)
                else:
                    if turn >= 3:
                        s_copy[x][y] = 'H'
                    else:
                        s_copy[x][y] = 'S' + str(turn + 1)

    return s_copy


# Given a state, checks if a tile gets infected from any directions. Returns True if it is, False otherwise.
def tile_is_infected(state, x, y):
    # possible directions for infection (right, left, down, up)
    dircs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for direction in dircs:
        x1 = x + direction[0]
        y1 = y + direction[1]
        if check_limits(state, x1, y1):
            if state[x1][y1][0] == 'S':
                return True
    return False


def possible_actions(state, zone_of_control):
    police_actions = []
    medics_actions = []
    for tile in zone_of_control:
        x = tile[0]
        y = tile[1]
        if state[x][y][0] == 'S':
            police_actions.append(('quarantine', (x, y)))
        if state[x][y] == 'H' and tile_is_infected(state, x, y):
            medics_actions.append(('vaccinate', (x, y)))
    return police_actions, medics_actions


# change the value of the agent according to the rules given in the hw.
def change_val(state, x, y):
    val = 0
    if state[x][y] == 'H' or state[x][y] == 'I':
        val += 1
    elif state[x][y][0] == 'Q':
        val -= 5
    elif state[x][y][0] == 'S':
        val -= 1
    return val


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = initial_state
        self.zone_of_control = zone_of_control
        self.order = order
        self.zone_of_control_AI = [(x, y) for x, lst in enumerate(self.initial_state)
                                   for y, val in enumerate(lst) if (x, y) not in self.zone_of_control]
        self.num_rows = len(self.initial_state)
        self.num_cols = len(self.initial_state[0])
        for x in range(self.num_rows):
            for y in range(self.num_cols):
                if self.initial_state[x][y] == 'S':
                    if self.order == 'first':
                        self.initial_state[x][y] = 'S' + str('0')
                    else:
                        self.initial_state[x][y] = 'S' + str('1')

        self.pre_map = self.initial_state

    def h_value_infect(self, state, x, y):
        val = 0
        # possible directions for infection (right, left, down, up)
        dircs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if state[x][y][0] == 'S':
            for direction in dircs:
                x1 = x + direction[0]
                y1 = y + direction[1]
                if check_limits(state, x1, y1) and state[x1][y1] == 'H':
                    if (x1, y1) in self.zone_of_control:
                        val -= 1
                    elif (x1, y1) not in self.zone_of_control:
                        val += 1
        return val

    def h_value_healthy(self, state, x, y):
        val = 0
        flag = False
        # possible directions for infection (right, left, down, up)
        dircs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if state[x][y] == 'H':
            for direction in dircs:
                x1 = x + direction[0]
                y1 = y + direction[1]
                if check_limits(state, x1, y1) and state[x1][y1][0] == 'S' and not flag:
                    flag = True
                    if (x1, y1) not in self.zone_of_control:
                        val += 1
        return val

    # calculate our utility
    def util_value(self, state):
        util = 0
        for x in range(self.num_rows):
            for y in range(self.num_cols):
                if (x, y) in self.zone_of_control:
                    util += change_val(state, x, y)
        return util

    def possible_next_actions(self, state, our_turn):
        if our_turn:
            police_actions, medics_actions = possible_actions(state, self.zone_of_control)
        else:
            police_actions, medics_actions = possible_actions(state, self.zone_of_control_AI)

        police_actions.sort(key=lambda coord: self.h_value_infect(state, coord[1][0], coord[1][1]))
        medics_actions.sort(key=lambda coord: self.h_value_healthy(state, coord[1][0], coord[1][1]))

        # check if actions are possible with given teams
        try:
            quarantine = (police_actions[:2])
        except KeyError:
            quarantine = []
        try:
            vaccinate = (medics_actions[:1])
        except ValueError:
            vaccinate = []

        if not medics_actions:
            return [[]] + [list((action,)) for action in police_actions]

        else:
            quarantine_tmp = []
            for action in powerset(quarantine, len(quarantine)):
                if len(action) == 1:
                    quarantine_tmp.append(action[0])
                else:
                    quarantine_tmp.append(action)

            prod_of_actions = list(product(quarantine_tmp, vaccinate))[:-1]
            tmp_prod_of_actions = [list(actions) for actions in prod_of_actions] + list((quarantine + vaccinate,))

            return [list((action,)) for action in medics_actions] + [[]] + tmp_prod_of_actions

    def minimax_min_value(self, state, alpha, beta, current_d, maximum_d):
        if self.order != 'first':
            current_d += 1
            if current_d == maximum_d:
                return self.util_value(state)
        actions = self.possible_next_actions(state, False)
        min_val = math.inf
        for action in actions:
            tmp_state = act_to_use(state, action)
            if self.order == 'first':
                tmp_state = update_turns(tmp_state)
            tmp_min_val = self.minimax_max_value(tmp_state, alpha, beta, current_d, maximum_d)
            min_val = min(min_val, tmp_min_val)
            if min_val <= alpha:
                return min_val
            beta = min(beta, min_val)
        return min_val

    def minimax_max_value(self, state, alpha, beta, current_d, maximum_d):
        if self.order == 'first':
            current_d += 1
            if current_d == maximum_d:
                return self.util_value(state)
        actions = self.possible_next_actions(state, True)
        max_val = -math.inf
        for action in actions:
            tmp_state = act_to_use(state, action)
            if self.order == 'second':
                tmp_state = update_turns(tmp_state)
            tmp_max_val = self.minimax_min_value(tmp_state, alpha, beta, current_d, maximum_d)
            max_val = max(max_val, tmp_max_val)
            if max_val >= beta:
                return max_val
            alpha = max(alpha, max_val)
        return max_val

    # adjusts the map according to who starts the game and the previous map
    def who_starts(self, state):
        s_copy = deepcopy(state)
        if self.order == 'first':
            for x in range(self.num_rows):
                for y in range(self.num_cols):
                    if state[x][y][0] == 'S' and 'S' in self.pre_map[x][y]:
                        s_copy[x][y] += str(int(self.pre_map[x][y][1]) + 1)
                    if state[x][y][0] == 'S' and 'H' in self.pre_map[x][y]:
                        s_copy[x][y] += str('1')
                    if state[x][y][0] == 'Q' and 'Q' in self.pre_map[x][y]:
                        s_copy[x][y] += str(int(self.pre_map[x][y][1]) + 1)
                    if state[x][y][0] == 'Q' and 'S' in self.pre_map[x][y]:
                        s_copy[x][y] += str('0')
            self.pre_map = s_copy
        else:
            for x in range(self.num_rows):
                for y in range(self.num_cols):
                    if state[x][y][0] == 'S' and 'S' in self.pre_map[x][y]:
                        s_copy[x][y] = self.pre_map[x][y]
                    if state[x][y][0] == 'Q' and 'Q' not in self.pre_map[x][y]:
                        s_copy[x][y] = 'Q' + str('0')
                    if state[x][y][0] == 'Q' and 'Q' in self.pre_map[x][y]:
                        s_copy[x][y] = self.pre_map[x][y]
        return s_copy

    def act(self, state):
        current_map = self.who_starts(state)
        chosen_act = []
        value = -math.inf
        # define True to get the maximum
        for action in self.possible_next_actions(current_map, True):
            tmp_state = act_to_use(current_map, action)
            tmp_value = self.minimax_min_value(tmp_state, -math.inf, math.inf, 0, 2)
            if value < tmp_value:
                value = tmp_value
                chosen_act = action
        if self.order != 'first':
            current_map = act_to_use(current_map, chosen_act)
            current_map = update_turns(current_map)
            self.pre_map = current_map
        return chosen_act
