from itertools import product
from copy import deepcopy
import numpy as np
import time

ids = ['314923301', '206693665']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.initial_state = self.change_map(initial_state)
        self.zoc = zone_of_control
        self.order = order
        self.enemy_zoc = [(i, j) for i in range(len(initial_state))
                          for j in range(len(initial_state)) if (i, j) not in zone_of_control]
        self.max_search_depth = 2
        self.start_time = 0
        self.max_search_time = 4.95
        self.ignore_action = "Non-relevant"

    def act(self, state):
        self.start_time = time.time()
        self.update_map(state)
        action_idx, actions = self.max(self.initial_state, 0, -np.inf, np.inf)
        possible_actions = []
        for pos, action in zip(action_idx, actions):
            if pos == (-1, -1):
                continue
            app_val = ('vaccinate', pos) if action == "I" else ('quarantine', pos)
            possible_actions.append(app_val)
        for (act, (i, j)) in possible_actions:
            val = "I" if act == "vaccinate" else "Q0"
            self.initial_state[i][j] = val
        self.initial_state = self.update_time_effects(self.initial_state)
        return possible_actions

    # def initial_to_act(self, move_step):
    #     for (act, (i, j)) in move_step:
    #         print (act,i,j)
    #         self.initial_state[i][j] = self.decide_act(act)
    #     self.initial_state = self.update_time_effects(self.initial_state)

    # @staticmethod
    # def decide_act(act):
    #     return "I" if act == "vaccinate" else "Q0"

    # @staticmethod
    # def check_ignore(pos):
    #     return pos != (-1, -1)

   # @staticmethod
    # def decide_app_val(place, o):
    #     return ('vaccinate', place) if o == "I" else ('quarantine', place)

    @staticmethod
    def change_map(initial_state):
        for i in range(len(initial_state)):
            for j in range(len(initial_state[0])):
                if initial_state[i][j] == 'S':
                    initial_state[i][j] = 'S1'
                elif initial_state[i][j] == 'Q':
                    initial_state[i][j] = 'Q1'
        return initial_state

    def create_dict_operations(self, indices, op='I'):
        return {((-1, -1), x): (self.ignore_action, op) for x in indices}

    def ss(self, state):
        q = []
        for (i, j) in self.zoc:
            if 'S' in state[i][j]:
                q.append((i, j))
        return q

    def sh(self, state):
        h = []
        for (i, j) in self.zoc:
            if state[i][j] == 'H':
                h.append((i, j))
        return h

    @staticmethod
    def med_and_also_cop(h_indices, q_indices):
        return {(h, q): ('I', 'Q0') for h, q in product(h_indices, q_indices)}

    def generate_player_actions(self, state):
        q_indices = self.ss(state)
        h_indices = self.sh(state)
        return q_indices, h_indices

    def options_to_play(self, q_indices, h_indices):
        cops_med = self.med_and_also_cop(h_indices, q_indices)
        cops = self.create_dict_operations(q_indices, op='Q0')
        no_op = {((-1, -1), (-1, -1)): (self.ignore_action, self.ignore_action)}
        med = self.create_dict_operations(h_indices, op='I')
        return no_op, cops, med, cops_med

    @staticmethod
    def legal_op(i):
        return i != (-1, -1)

    def check_if_first(self):
        return self.order == 'first'

    def do_operation(self, state, operat, place):
        move = deepcopy(state)
        for i, j in zip(place, operat):
            if self.legal_op(i):
                move[i[0]][i[1]] = j
        return move

    def create_the_move(self, state, o, place):
        move = self.do_operation(state, o, place)
        move = self.update_time_effects(move)
        if not self.check_if_first():
            move = self.update_time_effects(move)
        return move

    @staticmethod
    def beta_value_check(value, beta):
        return value >= beta

    def do_the_up(self, elem, state, i, j):
        if elem == 'H' and state[i][j] == 'Q':
            self.check_the_initial(i, j)
        if 'S' in elem and state[i][j] == 'Q':
            self.check_the_initial(i, j)
        if elem == 'S1' and state[i][j] == 'H':
            self.initial_state[i][j] = 'H'
        if elem == 'S1' and state[i][j] == 'I':
            self.initial_state[i][j] = 'I'
        if elem == 'H' and state[i][j] == 'I':
            self.initial_state[i][j] = 'I'

    def stop_the_search(self):
        return time.time() - self.start_time > self.max_search_time

    @staticmethod
    def return_val_max_min(cur_depth, maximizer, func):
        return func(maximizer, key=maximizer.get) if cur_depth == 0 else func(maximizer.values())

    def calc_val(self, state, o, place, cur_depth, alpha, beta, val):
        move = self.create_the_move(state, o, place)
        res = self.min(move, cur_depth + 1, alpha, beta)
        value = max(val, res)
        return res, value

    @staticmethod
    def medical_or_not(options, med):
        return not options or not med

    def moving(self, med, cops_med, no_op, cops):
        options = {}
        options.update(med)
        options.update(cops_med)
        if self.medical_or_not(options, med):
            options.update(no_op)
            options.update(cops)
        return options

    def check_the_initial(self, i, j):
        if self.check_if_first():
            self.initial_state[i][j] = 'Q1'
        else:
            self.initial_state[i][j] = 'Q0'

    def create_option_dict(self, state):
        q_indices, h_indices = self.generate_player_actions(state)
        no_op, cops, med, cops_med = self.options_to_play(q_indices, h_indices)
        options = self.moving(med, cops_med, no_op, cops)
        return options

    def create_the_move_min(self, state, o, place):
        move = self.do_operation(state, o, place)
        if self.check_if_first():
            move = self.update_time_effects(move)
        return move

    def calc_val_res(self, state, o, place, cur_depth, alpha, beta, val):
        move = self.create_the_move_min(state, o, place)
        res = self.max(move, cur_depth + 1, alpha, beta)
        value = min(val, res)
        return res, value

    @staticmethod
    def alpha_value_check(value, alpha):
        return value <= alpha

    def max(self, state, cur_depth, alpha, beta):
        maximizer = {}
        if cur_depth == self.max_search_depth:
            return self.heuristic(state)
        value = -np.inf
        options = self.create_option_dict(state)
        for place, o in options.items():
            res, value = self.calc_val(state, o, place, cur_depth, alpha, beta, value)
            if self.beta_value_check(value, beta):
                return value
            maximizer[(place, o)] = res
            alpha = max(alpha, value)
            if self.stop_the_search():
                break
        max_to_return = self.return_val_max_min(cur_depth, maximizer, max)
        return max_to_return

    def min(self, state, cur_depth, alpha, beta):
        minimizer = {}
        if cur_depth == self.max_search_depth:
            return self.heuristic(state)
        value = np.inf
        options = self.create_option_dict(state)
        for place, o in options.items():
            res, value = self.calc_val_res(state, o, place, cur_depth, alpha, beta, value)
            if self.alpha_value_check(value, alpha):
                return value
            minimizer[(place, o)] = res
            beta = min(beta, value)
            if self.stop_the_search():
                break
        min_to_return = self.return_val_max_min(cur_depth, minimizer, min)
        return min_to_return

    def heuristic(self, state):
        my_score, enemy_score = 0, 0
        for i, line in enumerate(state):
            for j, elem in enumerate(line):
                points = 0
                if elem == "H" or elem == "I":
                    points = 1
                elif elem == "S":
                    points = -1
                elif elem == "Q":
                    points = -5
                my_score += points if (i, j) in self.zoc else 0
                enemy_score += points if (i, j) not in self.zoc else 0
        return my_score - enemy_score

    @staticmethod
    def update_time_effects(state):
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
        for i, row in enumerate(self.initial_state):
            for j, elem in enumerate(row):
                self.do_the_up(elem, state, i, j)
