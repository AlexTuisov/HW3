import random
from utils import vector_add
from itertools import combinations
from copy import deepcopy
import time

ids = ['201555760', '204729636']


class State:
    def __init__(self, initial_map):
        self.state = self.initiate_state(initial_map)

    def initiate_state(self, initial_state):
        new_state = deepcopy(initial_state)
        for i in range(len(new_state)):
            for j in range(len(new_state[0])):
                if initial_state[i][j] == 'S':
                    new_state[i][j] = 'S1'
        return new_state

    def update_state(self, state):
        new_state = deepcopy(state)
        for i in range(len(new_state)):
            for j in range(len(new_state[0])):
                if state[i][j] == 'S' and 'S' in self.state[i][j]:
                    turn = int(self.state[i][j][1])
                    new_state[i][j] = 'S' + str(turn + 1)
                elif state[i][j] == 'S':
                    new_state[i][j] = 'S1'
                elif state[i][j] == 'Q' and 'Q' in self.state[i][j]:
                    turn = int(self.state[i][j][1])
                    new_state[i][j] = 'Q' + str(turn + 1)
                elif state[i][j] == 'Q':
                    new_state[i][j] = 'Q1'
                else:
                    new_state[i][j] = state[i][j]
        self.state = new_state

    def get_state(self):
        return self.state


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.rival_zoc = [(i, j) for i in range(len(initial_state)) for j in range(len(initial_state[0]))
                          if (i, j) not in zone_of_control]
        self.order = order
        self.police = 2
        self.state = State(initial_state)

    def min_max_plan(self, state, max_depth=1):
        alpha = -float("inf")
        beta = float("inf")
        if self.order == "first":
            plan, best_score = self.max_score_first_player(0, max_depth, state, alpha, beta)
        else:
            plan, best_score = self.max_second_player_depth1(state)

        return plan

    def max_score_first_player(self, current_depth, max_depth, state, alpha, beta):
        if self.is_terminal(state) or current_depth == max_depth:
            return [], 0
        else:
            actions = self.get_heuristic_subset_of_actions(state, self.zoc)
            value = -float('inf')
            best_plan = []
            for action in actions:
                potential_state = self.apply_action(state, action)
                plan, action_score = self.min_score_second_player(current_depth, max_depth, potential_state, alpha, beta)
                if action_score > value:
                    value = action_score
                    best_plan = plan[:]
                    best_plan.append(action)
                if value >= beta:
                    return best_plan, value
                alpha = max(alpha, value)
            return best_plan, value

    def min_score_second_player(self, current_depth, max_depth, state, alpha, beta):
        # print("{} Started min, current_depth: {}".format("    "*current_depth, current_depth))
        actions = self.get_heuristic_subset_of_actions(state, self.rival_zoc)
        value = float('inf')
        best_plan = []
        for action in actions:
            potential_state = self.apply_dynamics(self.apply_action(state, action))
            current_score = self.sum_zero_scores(state)
            plan, action_score = self.max_score_first_player(current_depth + 1, max_depth, potential_state, alpha, beta)
            if action_score + current_score < value:
                value = action_score + current_score
                best_plan = plan[:]
            if value <= alpha:
                return best_plan, value
            beta = min(beta, value)

        return best_plan, value

    def max_second_player_depth1(self, state):
        actions = self.get_heuristic_subset_of_actions(state, self.zoc)
        value = -float('inf')
        best_plan = []
        for action in actions:
            current_score = self.sum_zero_scores(self.apply_dynamics(self.apply_action(state, action)))
            if current_score > value:
                value = current_score
                best_plan = [action]
        return best_plan, value

    def is_terminal(self, state):
        has_sick = [True for i in range(len(state)) for j in range(len(state[0])) if 'S' in state[i][j]]
        if any(has_sick):
            return False
        return True

    def act(self, state):
        self.state.update_state(state)
        plan = self.min_max_plan(self.state.get_state())
        if not plan:
            return []
        else:
            return plan[0]

    def neighbors(self, coordinate, tile_size):
        available = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        x = coordinate[0]
        y = coordinate[1]
        X = tile_size[0]
        Y = tile_size[1]
        if x == 0:
            available.remove((-1, 0))
        if x == X - 1:
            available.remove((1, 0))
        if y == 0:
            available.remove((0, -1))
        if y == Y - 1:
            available.remove((0, 1))

        return [vector_add(coordinate, elem) for elem in available]

    def has_sick_neighbor(self, location, state):
        neighbors_locs = self.neighbors(location, (10, 10))
        for neighbor_i, neighbor_j in neighbors_locs:
            if 'S' in state[neighbor_i][neighbor_j]:
                return True
        return False

    def quarantine_profitability(self, location, state, zoc):
        neighbors_locs = self.neighbors(location, (10, 10))
        healthy_neighbors_in_zoc = 0
        for neighbor_i, neighbor_j in neighbors_locs:
            if state[neighbor_i][neighbor_j] == 'H':
                if (neighbor_i, neighbor_j) in zoc:
                    healthy_neighbors_in_zoc += 1
                else:
                    healthy_neighbors_in_zoc -= 1
        return healthy_neighbors_in_zoc

    def all_actions(self, state, rival=False):
        if rival:
            zone = self.rival_zoc
        else:
            zone = self.zoc

        healthy = set()
        sick = set()
        for (i, j) in zone:
            if 'H' in state[i][j]:
                healthy.add((i, j))
            if 'S' in state[i][j]:
                sick.add((i, j))

        vaccinate_actions = [[('vaccinate', item)] for item in healthy]
        possible_quarantine = [("quarantine", item) for item in sick]
        quarantine_actions = []
        for i in range(self.police+1):
            quarantine_actions += list(combinations(possible_quarantine, i))
        return [quarantine + tuple(vaccinate) for quarantine in quarantine_actions for vaccinate in vaccinate_actions]

    def get_heuristic_subset_of_actions(self, state, zoc):
        potential_vaccinate = self.get_healthy_subset(state, zoc)
        potential_quarantine = self.get_best_quarantine_subset(state, zoc)

        vaccinate_actions = [[('vaccinate', item)] for item in potential_vaccinate]
        possible_quarantine = [("quarantine", item) for item in potential_quarantine]

        quarantine_actions = []
        for i in range(self.police + 1):
            quarantine_actions += list(combinations(possible_quarantine, i))
        return [quarantine + tuple(vaccinate) for quarantine in quarantine_actions for vaccinate in
                vaccinate_actions]

    def get_healthy_subset(self, state, zoc):

        potential_vaccinate = [(i, j) for (i, j) in zoc if state[i][j] == 'H' and
                               self.has_sick_neighbor((i, j), state)]
        if len(potential_vaccinate) > 0:
            return potential_vaccinate

        potential_vaccinate = [(i, j) for (i, j) in zoc if state[i][j] == 'H' and
                               self.has_k_healthy_neighbor((i, j), state, zoc)]

        if len(potential_vaccinate) > 0:
            return potential_vaccinate

        potential_vaccinate = [(i, j) for (i, j) in zoc if state[i][j] == 'H']
        return potential_vaccinate

    def get_best_quarantine_subset(self, state, zoc):
        subset = []
        i = 4
        while not subset and i > 0:
            subset = [(i, j) for (i, j) in zoc if 'S' in state[i][j] and
                      self.quarantine_profitability((i, j), state, zoc) == i]
            i -= 1
        return subset

    def apply_action(self, state, action):
        new_state = deepcopy(state)
        for atomic_action in action:
            if atomic_action[0] == "vaccinate":
                new_state[atomic_action[1][0]][atomic_action[1][1]] = 'I'
            else:
                new_state[atomic_action[1][0]][atomic_action[1][1]] = 'Q0'
        return new_state

    def has_k_healthy_neighbor(self, location, state, zoc, k=2):
        if k > 4:
            return False
        neighbors_locs = self.neighbors(location, (10, 10))
        healthy_neighbors = 0
        for neighbor_i, neighbor_j in neighbors_locs:
            if (neighbor_i, neighbor_j) in zoc and state[neighbor_i][neighbor_j] == 'H':
                healthy_neighbors += 1
            if healthy_neighbors == k:
                return True
        return False

    def apply_dynamics(self, state):
        """
        taken shamelessly from the GAME class
        """
        new_state = deepcopy(state)
        for i in range(len(new_state)):
            for j in range(len(new_state[0])):
                if state[i][j] == 'H' and self.has_sick_neighbor((i, j), state):
                    new_state[i][j] = 'S1'
                if 'S' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 3:
                        new_state[i][j] = 'S' + str(turn + 1)
                    else:
                        new_state[i][j] = 'H'
                if 'Q' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn < 2:
                        new_state[i][j] = 'Q' + str(turn + 1)
                    else:
                        new_state[i][j] = 'H'
        return new_state

    def sum_zero_scores(self, state):
        score = 0
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                score += 1
            if 'I' in state[i][j]:
                score += 1
            if 'S' in state[i][j]:
                score -= 1
            if 'Q' in state[i][j]:
                score -= 5

        for (i, j) in self.rival_zoc:
            if 'H' in state[i][j]:
                score -= 1
            if 'I' in state[i][j]:
                score -= 1
            if 'S' in state[i][j]:
                score += 1
            if 'Q' in state[i][j]:
                score += 5
        return score
