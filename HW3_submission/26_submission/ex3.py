from utils import *
import itertools
import math


ids = ["314687815", "337579254"]



Unpopulated = 'U'
Healthy = 'H'
Sick = 'S'
Immune = 'I'
Quarantined = 'Q'
quarantine_action = 'quarantine'
vaccinate_action = 'vaccinate'

score_dict_max = {'H': 1, 'I': 1, 'S': -1, 'Q': -5, 'U': 0}
score_dict_min = {'H': -1, 'I': -1, 'S': 1, 'Q': 5, 'U': 0}


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.medics = 1
        self.police = 0

        self.round = 1
        self.order = order

        self.zoc = zone_of_control
        self.zoc_rival = []

        self.initial = initial_state
        self.prev_state = None

        boards_tuples = initial_state
        self.number_of_rows = len(boards_tuples)
        self.number_of_cols = len(boards_tuples[0])


        self.max_actions_alpha_beta = -1
        self.max_depth = 3
        self.state_dict = hashabledict()


        for row in range(self.number_of_rows):
            for col in range(self.number_of_cols):
                self.state_dict[(row, col)] = (boards_tuples[row][col], 1)
                if (row, col) not in self.zoc:
                    self.zoc_rival.append((row, col))

    def get_all_possible_actions(self, state: hashabledict, is_rival=False):
        individual_police_actions = []
        individual_medical_actions = []

        if is_rival:
            current_squares = self.zoc_rival
        else:
            current_squares = self.zoc

        for (row, col) in current_squares:
            square_state, time_passed = state[(row, col)]
            if square_state == Sick:
                individual_police_actions.append((quarantine_action, (row, col)))
            elif square_state == Healthy:
                individual_medical_actions.append((vaccinate_action, (row, col)))

        actions = []
        for medical_subset in itertools.combinations(individual_medical_actions,
                                                     min(self.medics, len(individual_medical_actions))):
            for police_subset in itertools.combinations(individual_police_actions,
                                                        min(self.police, len(individual_police_actions))):
                actions.append(medical_subset + police_subset)
        return actions + [()]

    def get_state_after_action(self, action, state_dict, return_s_num=False, spreading_disease=False):
        new_state = state_dict.copy()
        for (action, coordinates) in action:
            if action == quarantine_action:
                new_state[coordinates] = (Quarantined, 0)   # to after spreading add 1
            else:
                new_state[coordinates] = (Immune, 0)

        if spreading_disease:
            new_state = self.get_state_after_spreading_disease(new_state)
        if return_s_num:
            counter = sum(tup[0] == Sick for tup in new_state)
            return new_state, counter
        return new_state

    def get_state_after_spreading_disease(self, state_dict):
        new_state_dict = hashabledict()

        for (row, col), (square_state, time_passed) in state_dict.items():
            if square_state == Sick and (row, col) not in new_state_dict:
                healthy_neighbors = self.return_neighbors(state_dict, row, col, square_state=Healthy)
                for healthy_neighbor in healthy_neighbors:
                    if healthy_neighbor not in new_state_dict:
                        new_state_dict[healthy_neighbor] = (Sick, 1)

        for (row, col), (square_state, time_passed) in state_dict.items():
            if square_state == Sick and (row, col) not in new_state_dict:
                if time_passed == 3:
                    new_state_dict[(row, col)] = (Healthy, 1)
                else:
                    new_state_dict[(row, col)] = (Sick, time_passed + 1)

        for (row, col), (square_state, time_passed) in state_dict.items():
            if square_state == Quarantined and (row, col) not in new_state_dict:
                if time_passed == 2:
                    new_state_dict[(row, col)] = (Healthy, 1)
                else:
                    new_state_dict[(row, col)] = (Quarantined, time_passed + 1)

        for (row, col), (square_state, time_passed) in state_dict.items():
            if (row, col) not in new_state_dict:
                new_state_dict[(row, col)] = (square_state, time_passed + 1)
        return new_state_dict

    def return_neighbors(self, state, row, col, square_state=Healthy):
        neighbors = []
        if row > 0:
            if state[(row - 1, col)][0] == square_state:
                neighbors.append((row - 1, col))

        if row < self.number_of_rows - 1:
            if state[(row + 1, col)][0] == square_state:
                neighbors.append((row + 1, col))

        if col > 0:
            if state[(row, col - 1)][0] == square_state:
                neighbors.append((row, col - 1))

        if col < self.number_of_cols - 1:
            if state[(row, col + 1)][0] == square_state:
                neighbors.append((row, col + 1))
        return neighbors

    def number_of_neighbours_in_zoc(self, state, row, col, square_state=Healthy, is_rival=False):
        counter = 0
        area = self.zoc if not is_rival else self.zoc_rival
        if row > 0:
            if (row, col) in area and state[(row - 1, col)][0] == square_state:
                counter += 1

        if row < self.number_of_rows - 1:
            if (row, col) in area and state[(row + 1, col)][0] == square_state:
                counter += 1

        if col > 0:
            if (row, col) in area and state[(row, col - 1)][0] == square_state:
                counter += 1

        if col < self.number_of_cols - 1:
            if (row, col) in area and state[(row, col + 1)][0] == square_state:
                counter += 1
        return counter


    def is_leaf(self, state):
        for val in state.values():
            if val[0] == Sick:
                return False
        return True

    def max_value(self, state, alpha, beta, max_depth, cur_depth):
        # Without this performs better
        all_max_actions = self.get_all_possible_actions(state, is_rival=self.order == 'second')

        if self.is_leaf(state):
            # return alpha + self.calculate_cur_score(state)
            return self.calculate_cur_score(state), all_max_actions[0]
        elif max_depth == cur_depth:
            return self.heuristic(state), all_max_actions[0]
        v = -math.inf

        next_state_by_action = {action: self.get_state_after_action(action, state) for action in all_max_actions}

        all_max_actions = sorted(all_max_actions, key=lambda action: self.heuristic(next_state_by_action[action]),
                                 reverse=True)

        all_max_actions = all_max_actions[:self.max_actions_alpha_beta]

        best_max_action = all_max_actions[0]
        for max_action in all_max_actions:
            state_after_action = next_state_by_action[max_action]
            v_min, _ = self.min_value(state_after_action, alpha, beta, max_depth, cur_depth+1)
            v = max(v, v_min)  # change state
            if v >= beta:
                return v, best_max_action
            if v > alpha:
                alpha = v
                best_max_action = max_action
        return v, best_max_action

    def min_value(self, state, alpha, beta, max_depth, cur_depth):
        all_min_actions = self.get_all_possible_actions(state, is_rival=self.order == 'first')

        if self.is_leaf(state):
            return 0, all_min_actions[0]
        elif max_depth == cur_depth:
            return self.heuristic(state), all_min_actions[0]
        v = math.inf

        next_state_by_action = {
            action: self.get_state_after_spreading_disease(self.get_state_after_action(action, state))
            for action in all_min_actions}

        all_min_actions = sorted(all_min_actions, key=lambda action: self.heuristic(next_state_by_action[action]),
                                 reverse=False)

        all_min_actions = all_min_actions[:self.max_actions_alpha_beta]

        best_min_action = all_min_actions[0]
        for min_action in all_min_actions:
            state_after_spreading = next_state_by_action[min_action]
            cur_score = self.calculate_cur_score(state_after_spreading)
            v_max, _ = self.max_value(state_after_spreading, alpha, beta, max_depth, cur_depth+1)
            v = min(v, v_max+cur_score)  # change state
            if v <= alpha:
                return v, best_min_action
            if v < beta:
                beta = v
                best_min_action = min_action
        return v, best_min_action



    def act(self, state):
        state_dict = hashabledict()
        if self.round == 1:
            for row in range(self.number_of_rows):
                for col in range(self.number_of_cols):
                    state_dict[(row, col)] = (state[row][col], 1)
            self.prev_state = state_dict.copy()
            self.round += 1
        else:
            for row in range(self.number_of_rows):
                for col in range(self.number_of_cols):
                    cur_val = state[row][col]
                    prev_state_val = self.prev_state[(row, col)]
                    if cur_val == Sick and (prev_state_val[0] == Sick):
                        state_dict[(row, col)] = (cur_val, prev_state_val[1]+1)
                    elif cur_val == Quarantined and (prev_state_val[0] == Quarantined):
                        state_dict[(row, col)] = (cur_val, prev_state_val[1]+1)
                    else:
                        state_dict[(row, col)] = (state[row][col], 1)
            self.prev_state = state_dict.copy()
            self.round += 1

        if self.order == 'first':
            _, action = self.max_value(state_dict, alpha=-math.inf, beta=math.inf,
                                       max_depth=self.max_depth, cur_depth=0)
        else:
            _, action = self.min_value(state_dict, alpha=-math.inf, beta=math.inf,
                                       max_depth=self.max_depth, cur_depth=0)

        return action

    def print_state(self, state):
        for row in state:
            print(row)

    def heuristic(self, state_dict):
        cur_score = self.calculate_cur_score(state_dict)
        sick_score = 0
        for val in state_dict.values():
            if val[0] == Sick:
                sick_score += 1
        return cur_score * sick_score



    def calculate_cur_score(self, state_dict):
        score = 0
        for (row, col) in (self.zoc if self.order == 'first' else self.zoc_rival):
            score += score_dict_max[state_dict[(row, col)][0]]

        for (row, col) in (self.zoc_rival if self.order == 'first' else self.zoc):
            score += score_dict_min[state_dict[(row, col)][0]]
        return score
