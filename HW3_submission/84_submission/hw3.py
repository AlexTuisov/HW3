import random
import math
from copy import deepcopy
from itertools import chain, combinations, product

ids = ['322643677', '322210949']

dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
FIRST = 'first'
SECOND = 'second'


def powerset(iterable, limit):
    """powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    powerset_list = []
    for item in chain.from_iterable(combinations(iterable, r) for r in range(limit + 1)):
        if item != ():
            powerset_list.append(item)
    return powerset_list


def terminal_state(state):
    for row in state:
        for tile in row:
            if 'S' in tile:
                return False
    return True


def gets_infected(state, i, j):
    if state[i][j] == 'H':
        for dir in dirs:
            i_new = i + dir[0]
            j_new = j + dir[1]
            if 0 <= i_new < len(state) and 0 <= j_new < len(state[0]) and 'S' in state[i_new][j_new]:
                return True  # current tile is getting infected
    return False


def apply_action(state, actions):
    deepcopy_state = deepcopy(state)
    if not actions:
        return deepcopy_state
    for atomic_action in actions:
        effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
        if 'v' in effect:
            deepcopy_state[location[0]][location[1]] = 'I'
        else:
            deepcopy_state[location[0]][location[1]] = 'Q0'
    return deepcopy_state


def change_state(state):
    deepcopy_state = deepcopy(state)
    for i in range(len(state)):
        for j in range(len(state[0])):
            # virus spread
            if gets_infected(state, i, j):  # state[i][j] == 'H' and
                deepcopy_state[i][j] = 'S1'

    # advancing counters
    for i in range(len(state)):
        for j in range(len(state[0])):
            # advancing sick counters
            if 'S' in state[i][j]:
                turn = int(state[i][j][1])
                if turn < 3:
                    deepcopy_state[i][j] = 'S' + str(turn + 1)
                else:
                    deepcopy_state[i][j] = 'H'
            # advancing quarantine counters
            elif 'Q' in state[i][j]:
                turn = int(state[i][j][1])
                if turn < 2:
                    deepcopy_state[i][j] = 'Q' + str(turn + 1)
                else:
                    deepcopy_state[i][j] = 'H'
    return deepcopy_state


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.AI_zoc = [(i, j) for i, row in enumerate(initial_state) for j, tile in enumerate(row)
                       if (i, j) not in zone_of_control]
        self.order = order
        self.police = 2
        self.medics = 1
        self.init_state = initial_state
        self.set_initial_state()
        self.prev = self.init_state

    def set_initial_state(self):
        for i in range(len(self.init_state)):
            for j in range(len(self.init_state[0])):
                if self.init_state[i][j] == 'S':
                    if self.order != FIRST:
                        self.init_state[i][j] = 'S1'
                    else:
                        self.init_state[i][j] = 'S0'

    def infection_potential(self, state, coordinate):
        i, j = coordinate
        potential = 0
        for dir in dirs:
            i_new = i+dir[0]
            j_new = j+dir[1]
            if state[i][j] == 'S':
                if 0 <= i_new <= len(state)-1 and 0 <= j_new <= len(state[0])-1:
                    if state[i_new][j_new] == "H":
                        if (i_new, j_new) not in self.zoc:
                            potential += 1
                        else:
                            potential -= 1
        return potential

    def healthy_potential(self, state, coordinate):
        i, j = coordinate
        potential = 0
        flag = 0
        for dir in dirs:
            i_new = i+dir[0]
            j_new = j+dir[1]
            if state[i][j] == 'H':
                if 0 <= i_new <= len(state)-1 and 0 <= j_new <= len(state[0])-1:
                    if state[i_new][j_new] == "S" and not flag:
                        flag = 1
                        if state[i_new][j_new] == "H" and (i_new, j_new) not in self.zoc:
                            potential -= 1
                        if state[i_new][j_new] == "H" and (i_new, j_new) in self.zoc:
                            potential += 1
        return potential

    @staticmethod
    def get_all_actions(state, zoc):
        sick = []
        healthy = []
        for (i, j) in zoc:
            if "S" in state[i][j]:
                sick.append(('quarantine', (i, j)))
            if gets_infected(state, i, j):  # state[i][j] == "H" and # checking gets infected to reduce search space
                healthy.append(('vaccinate', (i, j)))
        return sick, healthy

    def successors_actions(self, state, our_agent):
        if our_agent:
            sick, healthy = self.get_all_actions(state, self.zoc)
        else:
            sick, healthy = self.get_all_actions(state, self.AI_zoc)

        sick.sort(key=lambda x: self.infection_potential(state, x[1]), reverse=False)
        healthy.sort(key=lambda x: self.healthy_potential(state, x[1]), reverse=False)
        try:
            to_quarantine = (sick[:2])
        except KeyError:
            to_quarantine = []
        try:
            to_vaccinate = (healthy[:1])
        except ValueError:
            to_vaccinate = []

        to_quarantine_power = powerset(to_quarantine, len(to_quarantine))
        new_to_quarantine_power = []
        for tile in to_quarantine_power:
            if len(tile) == 1:
                new_to_quarantine_power.append(tile[0])
            else:
                new_to_quarantine_power.append(tile)
        cartesian_product = list(product(new_to_quarantine_power, to_vaccinate))[:-1]
        new_cartesian_product = [list(item) for item in cartesian_product] + list((to_quarantine + to_vaccinate,))
        # new_cartesian_product = new_cartesian_product[:1] + new_cartesian_product[2:]  # without middle possibility

        if healthy:
            all_actions_healthy = [list((a,)) for a in healthy]
            all_actions_healthy = all_actions_healthy + [[]] + new_cartesian_product
            # + [to_quarantine[:1] + to_vaccinate]
            return all_actions_healthy
        else:
            # combinations_list = list(combinations(sick, min(self.police, len(sick))))
            # combinations_list = [list(action) for action in combinations_list] + [[]]
            return [[]] + [list((a, )) for a in sick]  # combinations_list
            # [[]] + [list(a) for a in to_quarantine_power]

    @staticmethod
    def update_scores(state, i, j):
        util = 0
        if 'H' in state[i][j]:
            util += 1
        if 'I' in state[i][j]:
            util += 1
        if 'S' in state[i][j]:
            util -= 1
        if 'Q' in state[i][j]:
            util -= 5
        return util

    def utility(self, state):
        util1 = 0
        util2 = 0
        for i in range(len(state)):
            for j in range(len(state[0])):
                if (i, j) in self.zoc:
                    util1 += self.update_scores(state, i, j)
                else:
                    util2 += self.update_scores(state, i, j)
        return util1 - util2  # the utilities function is the difference between the scores per round of the players

    def min_value(self, state, alpha, beta, max_depth, curr_depth):
        if self.order != FIRST:
            curr_depth += 1
            if curr_depth == max_depth:  # or terminal_state(state)
                return self.utility(state)
        v = math.inf
        for a in self.successors_actions(state, False):
            s = apply_action(state, a)
            if self.order == FIRST:
                s = change_state(s)
            v_tag = self.max_value(s, alpha, beta, max_depth, curr_depth)
            v = min(v, v_tag)
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def max_value(self, state, alpha, beta, max_depth, curr_depth):
        if self.order == FIRST:
            curr_depth += 1
            if curr_depth == max_depth:  # or terminal_state(state):
                return self.utility(state)
        v = -math.inf
        for a in self.successors_actions(state, True):
            s = apply_action(state, a)
            if self.order == SECOND:
                s = change_state(s)
            v_tag = self.min_value(s, alpha, beta, max_depth, curr_depth)
            v = max(v, v_tag)
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def change_first(self, state):
        deepcopy_state = deepcopy(state)
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] == 'Q':
                    if 'S' in self.prev[i][j]:
                        deepcopy_state[i][j] += '0'
                    if 'Q' in self.prev[i][j]:
                        new_count = int(self.prev[i][j][1]) + 1
                        deepcopy_state[i][j] += str(new_count)

                if state[i][j] == 'S':
                    if 'H' in self.prev[i][j]:
                        deepcopy_state[i][j] += '1'
                    if 'S' in self.prev[i][j]:
                        new_count = int(self.prev[i][j][1]) + 1
                        deepcopy_state[i][j] += str(new_count)

        return deepcopy_state

    def change_second(self, state):
        deepcopy_state = deepcopy(state)
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] == 'Q' and 'Q' not in self.prev[i][j]:
                    deepcopy_state[i][j] = 'Q0'
                if state[i][j] == 'Q' and 'Q' in self.prev[i][j]:
                    deepcopy_state[i][j] = self.prev[i][j]
                if state[i][j] == 'S' and 'S' in self.prev[i][j]:
                    deepcopy_state[i][j] = self.prev[i][j]

        return deepcopy_state

    def act(self, state):
        if self.order == FIRST:
            self.prev = self.change_first(state)
            updated_state = self.prev
        else:  # self.order == 'second':
            updated_state = self.change_second(state)

        # now we have updated_state with counters on its tiles - time to operate alpha beta pruning
        all_actions = self.successors_actions(updated_state, True)  # True stands for our agent (maximizer)
        best_action = []
        v = -math.inf
        for a in all_actions:
            successor_state = apply_action(updated_state, a)
            # TODO: check if better
            # if self.order == FIRST:
            #     successor_state = change_state(successor_state)
            v_tag = self.min_value(successor_state, -math.inf, math.inf, 2, 0)
            # v = max(v, v_tag)
            # if v == v_tag:
            #     best_action = a
            if v < v_tag:
                v = v_tag
                best_action = a

        if self.order == SECOND:
            updated_state = apply_action(updated_state, best_action)
            updated_state = change_state(updated_state)
            self.prev = updated_state
        return best_action
