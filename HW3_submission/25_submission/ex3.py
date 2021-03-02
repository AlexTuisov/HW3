import time
import math
import random
import itertools
from copy import deepcopy
from collections import defaultdict

ids = ['206330342', '313329666']
DIMENSIONS = (10, 10)
MAX_DEPTH = 2
TIME_LIMIT = 4.85
DISCOUNT_FACTOR = 0.9


def binary_search(arr, low, high, x):
    if high > low:
        mid = (high + low) // 2

        if arr[mid] == x:
            return True

        elif arr[mid] > x:
            return binary_search(arr, low, mid - 1, x)

        else:
            return binary_search(arr, mid + 1, high, x)

    else:
        return False


class State:
    global_id = 0

    def __init__(self, state_dict: dict):
        self.state_dict = state_dict
        self.sick_set, self.healthy_set = self.sick_healthy_sets()
        self.DIMENSIONS = DIMENSIONS
        self.ID = State.global_id
        State.global_id += 1

    def is_terminal(self):
        return not ('S1' in self.state_dict.values() or
                    'S2' in self.state_dict.values() or
                    'S3' in self.state_dict.values() or
                    'S' in self.state_dict.values())

    def sick_healthy_sets(self):
        sick_set = set()
        healthy_set = set()
        for loc, status in self.state_dict.items():
            if 'S' in status:
                sick_set.add(loc)
            elif 'H' in status:
                healthy_set.add(loc)
        return sick_set, healthy_set


def is_valid(coordinate, max_row, max_col):
    if 0 <= coordinate[0] < max_row and 0 <= coordinate[1] < max_col:
        return True
    return False


def get_actions(state: State, zoc, improved=True):

    sick_set = state.sick_set.intersection(zoc)
    healthy_set = state.healthy_set.intersection(zoc)

    if improved:
        # compute sick/healthy coordinate which maximizes "worthness" scores:
        sick_dict = {}
        for loc in state.sick_set.intersection(zoc):
            score = worth_quarantine(state, loc, zoc)
            if score not in sick_dict.keys():
                sick_dict[score] = set()
            sick_dict[score].add(loc)
        if sick_dict.keys():
            sick_set = sick_dict[max(sick_dict.keys())]

        healthy_dict = defaultdict(set)
        for loc in state.healthy_set.intersection(zoc):
            score = worth_vaccinate(state, loc, zoc)
            healthy_dict[score].add(loc)
        if healthy_dict.keys():
            healthy_set = healthy_dict[max(healthy_dict.keys())]

    police = 1
    medics = 1
    atomic_q_actions = list(itertools.product(['quarantine'], sick_set))
    atomic_v_actions = list(itertools.product(['vaccinate'], healthy_set))

    non_atomic_q_actions = []
    non_atomic_v_actions = []
    for r in range(police + 1):
        non_atomic_q_actions += list(itertools.combinations(atomic_q_actions, r))
    for r in range(medics + 1):
        non_atomic_v_actions += list(itertools.combinations(atomic_v_actions, r))

    actions = list(itertools.product(non_atomic_q_actions, non_atomic_v_actions))
    return [tuple(itertools.chain.from_iterable(action)) for action in actions]


def worth_vaccinate(state, loc, zoc):
    good_h_neigh = defaultdict(int)
    bad_h_neigh = defaultdict(int)
    i, j = loc[0], loc[1]
    n = len(zoc)
    neighbors = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
    for neigh in neighbors:
        if is_valid(neigh, *DIMENSIONS):
            if binary_search(zoc, 0, n, neigh):  # neigh in zoc
                status = state.state_dict[neigh][0]
                good_h_neigh[status] += 1
            else:
                status = state.state_dict[neigh][0]
                bad_h_neigh[status] += 1

    return good_h_neigh['S'] + bad_h_neigh['S'] - good_h_neigh['I'] - good_h_neigh['U'] - 2 * bad_h_neigh['H']


def worth_quarantine(state, loc, zoc):
    good_h_neigh = defaultdict(int)
    bad_h_neigh = defaultdict(int)
    i, j = loc[0], loc[1]
    n = len(zoc)
    neighbors = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
    for neigh in neighbors:
        if is_valid(neigh, *DIMENSIONS):
            if binary_search(zoc, 0, n, neigh):  # neigh in zoc
                status = state.state_dict[neigh][0]
                good_h_neigh[status] += 1
            else:
                status = state.state_dict[neigh][0]
                bad_h_neigh[status] += 1

    return 2 * good_h_neigh['H'] - 5 * bad_h_neigh['H'] - good_h_neigh['I'] - good_h_neigh['U']


def exists_S_neighbor(state_dict, i, j):
    neighbors = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
    for neigh in neighbors:
        if is_valid(neigh, *DIMENSIONS):
            if 'S' in state_dict[neigh]:
                return True
    return False


def exists_S_neighbor_actions(state_dict, i, j, zoc):
    neighbors = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
    n = len(zoc)
    for neigh in neighbors:
        if is_valid(neigh, *DIMENSIONS):
            if 'S' in state_dict[neigh] and not binary_search(zoc, 0, n, neigh):
                return True
    return False


def exists_H_neighbor(state_dict, i, j, zoc):
    neighbors = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
    n = len(zoc)
    for neigh in neighbors:
        if is_valid(neigh, *DIMENSIONS):
            if 'H' in state_dict[neigh] and binary_search(zoc, 0, n, neigh):
                return True
    return False


def take_action(state, actions, zoc, world_dynamics):
    sick_set, healthy_set = deepcopy(state.sick_set), deepcopy(state.healthy_set)
    new_state = deepcopy(state.state_dict)
    for atomic_action in actions:
        effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
        if 'v' in effect:
            new_state[location] = 'I'
            healthy_set.remove(location)
        else:
            new_state[location] = 'Q0'
            sick_set.remove(location)

    if world_dynamics:
        # virus spread
        n = len(zoc)
        new_state_2 = deepcopy(new_state)
        for i in range(0, DIMENSIONS[0]):
            for j in range(0, DIMENSIONS[1]):
                if new_state[(i, j)] == 'H' and exists_S_neighbor(new_state, i, j):
                    new_state_2[(i, j)] = 'S1'
                    if binary_search(zoc, 0, n, (i, j)) and (i, j) not in [a[1] for a in actions]:
                        sick_set.add((i, j))
                        healthy_set.remove((i, j))

        # advancing sick counters
        for i in range(0, DIMENSIONS[0]):
            for j in range(0, DIMENSIONS[1]):
                if 'S' in new_state[(i, j)]:
                    turn = int(new_state[(i, j)][1])
                    if turn < 3:
                        new_state_2[(i, j)] = 'S' + str(turn + 1)
                    else:
                        new_state_2[(i, j)] = 'H'
                        if binary_search(zoc, 0, n, (i, j)) and (i, j) not in [a[1] for a in actions]:
                            healthy_set.add((i, j))
                            sick_set.remove((i, j))

                # advancing quarantine counters
                if 'Q' in new_state[(i, j)]:
                    try:
                        turn = int(new_state[(i, j)][1])
                        if turn < 2:
                            new_state_2[(i, j)] = 'Q' + str(turn + 1)
                        else:
                            new_state_2[(i, j)] = 'H'
                            if binary_search(zoc, 0, n, (i, j)) and (i, j) not in [a[1] for a in actions]:
                                healthy_set.add((i, j))
                    except IndexError:
                        continue

        return State(new_state_2)

    return State(new_state)


class Node:
    global_id = 0

    def __init__(self, state: State, parent):
        self.state = state
        self.is_terminal = state.is_terminal()
        self.parent = parent
        self.children = {}
        self.ID = Node.global_id
        Node.global_id += 1


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = sorted(zone_of_control)
        self.curr_state = self.matrix_to_dict(initial_state)
        self.enemy_zoc = sorted(
            [(i, j) for i, j in itertools.product(range(0, 10), range(0, 10)) if (i, j) not in self.zoc])
        self.order = order
        self.zocs = {'max': self.zoc, 'min': self.enemy_zoc}
        self.state = State(self.curr_state)
        self.alpha = float("-inf")
        self.beta = float("inf")

    def update_map(self, state):
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                check_S = 'S' in state[i][j]
                check_Q = 'Q' in state[i][j]
                if check_S and 'S' not in self.curr_state[(i, j)]:
                    self.curr_state[(i, j)] = 'S1'
                elif check_S:
                    turn = int(self.curr_state[(i, j)][1])
                    # if turn < 3:
                    self.curr_state[(i, j)] = 'S' + str(turn + 1)
                    # else:
                    #     self.curr_state[(i, j)] = 'H'
                elif check_Q and 'Q' not in self.curr_state[(i, j)]:
                    self.curr_state[(i, j)] = 'Q0'
                elif check_Q:
                    turn = int(self.curr_state[(i, j)][1])
                    # if turn < 2:
                    self.curr_state[(i, j)] = 'Q' + str(turn + 1)
                    # else:
                    #     self.curr_state[(i, j)] = 'H'
                else:
                    self.curr_state[(i, j)] = state[i][j]
        return deepcopy(self.curr_state)

    @staticmethod
    def matrix_to_dict(matrix):
        res = {}
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                if matrix[i][j] == 'S':
                    res[(i, j)] = 'S1'
                elif matrix[i][j] == 'Q':
                    res[(i, j)] = 'Q0'
                else:
                    res[(i, j)] = matrix[i][j]
        return res

    def act(self, state):
        start_time = time.time()
        self.alpha = float("-inf")
        self.beta = float("inf")
        return self.minimax_decision(State(self.update_map(state)), start_time)

    def minimax_decision(self, state, start_time):
        depth = 0
        rewards = [0, 0]  # 0 -> me, 1 -> enemy
        value = float("-inf")
        optimal_action = None
        succ = [(action, take_action(state, action, self.zocs['max'], world_dynamics=False))
                for action in get_actions(state, self.zocs['max'])]
        for (next_action, next_state) in succ:
            returned_value = self.min_value(next_state, depth + 1, self.update_rewards(rewards, next_state, depth + 1), start_time)
            if returned_value > value:
                value = returned_value
                optimal_action = next_action

        return optimal_action

    def min_value(self, state, depth, rewards, start_time):
        if state.is_terminal() or depth == MAX_DEPTH or time.time() - start_time > TIME_LIMIT:
            return self.uristika(rewards, state)
        value = float("inf")
        succ = [(action, take_action(state, action, self.zocs['min'], world_dynamics=True))
                for action in get_actions(state, self.zocs['min'])]
        for (next_action, next_state) in succ:
            returned_value = self.max_value(next_state, depth + 1, self.update_rewards(rewards, next_state, depth + 1), start_time)
            if returned_value < value:
                value = returned_value
            if value <= self.alpha:
                return value
            self.beta = min(self.beta, value)
        return value

    def max_value(self, state, depth, rewards, start_time):
        if state.is_terminal() or depth == MAX_DEPTH or time.time() - start_time > TIME_LIMIT:
            return self.uristika(rewards, state)
        value = float("-inf")
        succ = [(action, take_action(state, action, self.zocs['max'], world_dynamics=False))
                for action in get_actions(state, self.zocs['max'])]
        for (next_action, next_state) in succ:
            returned_value = self.min_value(next_state, depth + 1, self.update_rewards(rewards, next_state, depth + 1), start_time)
            if returned_value > value:
                value = returned_value
            if value >= self.beta:
                return value
            self.alpha = max(self.alpha, value)
        return value

    def update_rewards(self, rewards, next_state: State, depth):
        updated_rewards = deepcopy(rewards)

        # our player reward:
        for (i, j) in self.zoc:
            if 'H' in next_state.state_dict[(i, j)]:
                updated_rewards[0] += 1*(DISCOUNT_FACTOR**depth)
            if 'I' in next_state.state_dict[(i, j)]:
                updated_rewards[0] += 1*(DISCOUNT_FACTOR**depth)
            if 'S' in next_state.state_dict[(i, j)]:
                updated_rewards[0] -= 1*(DISCOUNT_FACTOR**depth)
            if 'Q' in next_state.state_dict[(i, j)]:
                updated_rewards[0] -= 5*(DISCOUNT_FACTOR**depth)

        # enemy reward:
        for (i, j) in self.enemy_zoc:
            if 'H' in next_state.state_dict[(i, j)]:
                updated_rewards[1] += 1*(DISCOUNT_FACTOR**depth)
            if 'I' in next_state.state_dict[(i, j)]:
                updated_rewards[1] += 1*(DISCOUNT_FACTOR**depth)
            if 'S' in next_state.state_dict[(i, j)]:
                updated_rewards[1] -= 1*(DISCOUNT_FACTOR**depth)
            if 'Q' in next_state.state_dict[(i, j)]:
                updated_rewards[1] -= 5*(DISCOUNT_FACTOR**depth)

        return updated_rewards

    def uristika(self, rewards, state: State):
        num_sick = len(state.sick_set.intersection(self.zoc))
        num_healthy = len(state.healthy_set.intersection(self.zoc))

        enemy_num_sick = len(state.sick_set.intersection(self.enemy_zoc))
        enemy_num_healthy = len(state.healthy_set.intersection(self.enemy_zoc))

        sign = 0
        if rewards[0] - rewards[1] != 0:
            sign = (rewards[0] - rewards[1]) / abs(rewards[0] - rewards[1])

        s_ratio = ((enemy_num_sick + 1) / (num_sick + 1))**sign
        h_ratio = ((num_healthy + 1) / (enemy_num_healthy + 1))**sign

        s_abs_diff = abs(num_sick - enemy_num_sick)
        s_abs_healthy = abs(num_healthy - enemy_num_healthy)

        return (rewards[0] - rewards[1]) * s_ratio * h_ratio
