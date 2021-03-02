from itertools import chain, combinations, product
from copy import deepcopy
from utils import PriorityQueue
from time import time

ids = ['059238717']

points = {'H' : 1, 'I' : 1, 'Q' : -5, 'S' : -1, 'U': 0}
infinity = float('inf')
police = 2
medics = 1
SEARCH_TIMEOUT = 4.7
DIMENSIONS = (10, 10)

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.maxdepth = 2 #1  # depth = 1 count = 30, dept = 2 count = 15
        self.max_action_count = 15 #34  # Bug? 35=>4 34=>7
        self.prev_act_state = {}
        self.first_turn = 1
        #self.scratch_game = ScratchGame(initial_state, zone_of_control, self.first_turn, self.prev_act_state)
        self.order = order
        self.maxdepth = 2
        self.max_action_count = 5


    def act(self, state):
        start = time()
        self.scratch_game = ScratchGame(state, self.zoc, self.first_turn, self.prev_act_state)
        if 'Q' in self.scratch_game.state.values():
            xxx=1
        xxx = ScratchGame(state, self.zoc, self.first_turn, self.prev_act_state)
        if self.first_turn == 1:
            self.prev_act_state = self.scratch_game.initial_state
        self.first_turn = 0
        if 'Q' in self.scratch_game.state.values():
            xxx=1
        if self.order == 'first':
            best_action, value = self.max_value(self.scratch_game, self.maxdepth, -infinity, infinity, start)
        else:
            best_action, value = self.min_value(self.scratch_game, self.maxdepth, -infinity, infinity, start)

        action = ()
        for aa in best_action:
            action = action + ((aa[0], (aa[1][0]-1, aa[1][1]-1)),)
        return action

    def max_value(self, scratch_game, depth, alpha, beta, start):
        if depth == self.maxdepth:
            utility = 0
        else:
            utility = self.calc_value(scratch_game)
        if self.game_over(scratch_game.state) or depth == 0:
            return 0, utility
        value = -infinity
        actions = self.get_all_actions(scratch_game)
        save_state = deepcopy(scratch_game.state)
        max_action = ()
        actions_count = self.max_action_count
        while actions and actions_count:
            finish = time()
            if finish - start > SEARCH_TIMEOUT:
                break
            action = actions.pop()
            scratch_game.apply_action(action[0:-1])
            ma, mv = self.min_value(scratch_game, depth, alpha, beta, start)
            if mv > value:
                value = mv
                max_action = action[0:-1]
            if value >= beta:
                return max_action, value
            alpha = max(alpha, value)
            scratch_game.state = deepcopy(save_state)
            actions_count = actions_count - 1
        return max_action, value + utility

    def min_value(self, scratch_game, depth, alpha, beta, start):
        value = infinity
        actions = self.get_all_actions(scratch_game)
        save_state = deepcopy(scratch_game.state)
        min_action = ()
        actions_count = self.max_action_count
        while actions and actions_count:
            finish = time()
            if finish - start > SEARCH_TIMEOUT:
                break
            action = actions.pop()
            scratch_game.apply_action(action[0:-1])
            scratch_game.change_state()
            ma, mv = self.max_value(scratch_game, depth - 1, alpha, beta, start)
            if mv < value:
                value = mv
                min_action = action[0:-1]
            if value <= alpha:
                return min_action, value
            beta = min(beta, value)
            scratch_game.state = deepcopy(save_state)
            actions_count = actions_count - 1
        return min_action, value

    def calc_value(self, scratch_game):
        score = 0
        for z in scratch_game.control_zone_1:
            score = score + points[scratch_game.state[z][0]]
        for z in scratch_game.control_zone_2:
            score = score - points[scratch_game.state[z][0]]
        return score

    def game_over(self, state):
        for key in state:
            if state[key][0] == 'S':
                return False
        return True

    def next_state(self, state, action):
        new_state = deepcopy(state)
        for q in action[0]:  # quarantine comes first
            assert state[q[0]][q[1][0]] == 'S'
            new_state[q[0]][q[1]] = 'Q0'
        for v in action[1]:
            assert state[v[0]][v[1]] == 'H'
            new_state[v[0]][v[1]] = 'I'

    def get_all_actions(self, scratch_game):
        healthy = []
        sick = []
        for z in scratch_game.control_zone_1:
            if 'H' in scratch_game.state[z]:
                healthy.append(('vaccinate', z), )
            if 'S' in scratch_game.state[z]:
                sick.append(('quarantine', z), )
        to_quarantine = []
        for q in range(1, police+1):
            to_quarantine = to_quarantine + list(combinations(sick, min(q, len(sick))))
        to_vaccinate = list(combinations(healthy, min(medics, len(healthy))))
        a = list(product(to_quarantine, to_vaccinate))+to_vaccinate
        actions = PriorityQueue(max, lambda x: x[-1])
        for a1 in a:
            if len(a1) == 2: # account for cases where there are quarantines
                aa = a1[0] + a1[1]
            else:
                aa = a1 # only vaccinations
            fom = 0
            for atomic_action in aa:
                z1 = (atomic_action[1][0] - 1, atomic_action[1][1]) in scratch_game.control_zone_1
                z2 = (atomic_action[1][0] + 1, atomic_action[1][1]) in scratch_game.control_zone_1
                z3 = (atomic_action[1][0], atomic_action[1][1] - 1) in scratch_game.control_zone_1
                z4 = (atomic_action[1][0], atomic_action[1][1] + 1) in scratch_game.control_zone_1
                x1 = scratch_game.state[(atomic_action[1][0] - 1, atomic_action[1][1])]
                x2 = scratch_game.state[(atomic_action[1][0] + 1, atomic_action[1][1])]
                x3 = scratch_game.state[(atomic_action[1][0], atomic_action[1][1] - 1)]
                x4 = scratch_game.state[(atomic_action[1][0], atomic_action[1][1] + 1)]
                if atomic_action[0] == 'vaccinate':
                    fom = fom + (x1[0] == 'S' or x2[0] == 'S' or x3[0] == 'S' or x4[0] == 'S')
                else:
                    fom = fom + (x1[0] == 'H') * (z1 * 2 - 1) + (x2[0] == 'H') * (z2 * 2 - 1) + (x3[0] == 'H') * (
                                z3 * 2 - 1) + (x4[0] == 'H') * (z4 * 2 - 1)
                    fom = fom - 4  # penalty  for using police: 4
            aa = aa + (fom,)
            actions.append(aa)
        return actions

class ScratchGame:
    def __init__(self, a_map, zone_of_control, first_turn, prev_state):
        self.initial_state = self.pad_the_input(a_map)
        self.state = deepcopy(self.initial_state)
        self.dimentions = (len(a_map), len(a_map[0]))
        self.control_zone_1 = None
        self.control_zone_2 = None
        self.divide_map(zone_of_control)
        if first_turn:
            for key in self.initial_state:
                if self.initial_state[key] == 'S':
                    self.initial_state[key] = 'S1'
        else:
            S_advance_list = {'1': '2', '2': '3', '3': '3'}
            Q_advance_list = {'0': '1', '1': '2', '2': '2'}
            for key in self.initial_state:
                advanced_state = prev_state[key]
                if 'S' in self.initial_state[key] and 'S' in advanced_state:
                    self.initial_state[key] = 'S'+S_advance_list[advanced_state[1]]
                elif 'Q' in self.initial_state[key] and 'Q' in advanced_state:
                    try:
                        self.initial_state[key] = 'Q'+Q_advance_list[advanced_state[1]]
                    except:
                        xxx=1
                elif 'S' in self.initial_state[key] and 'S' not in advanced_state:
                    self.initial_state[key] = 'S0'
                elif 'Q' in self.initial_state[key] and 'Q' not in advanced_state:
                    self.initial_state[key] = 'Q1'

    def divide_map(self, zoc):
        all_tiles = set(product(range(0,self.dimentions[0]-1), range(0,self.dimentions[1]-1)))
        self.control_zone_1 = []
        self.control_zone_2 = []
        for z in zoc:
            self.control_zone_1.append((z[0]+1, z[1]+1),)
        zoc2 = list(all_tiles - set(zoc))
        for z in zoc2:
            self.control_zone_2.append((z[0]+1, z[1]+1),)

    def pad_the_input(self, a_map):
        state = {}
        new_i_dim = DIMENSIONS[0] + 2
        new_j_dim = DIMENSIONS[1] + 2
        for i in range(0, new_i_dim):
            for j in range(0, new_j_dim):
                if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                    state[(i, j)] = 'U'
                elif 'S' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'S1'
                elif 'Q' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'Q0'
                else:
                    state[(i, j)] = a_map[i - 1][j - 1]
        return state

    def apply_action(self, actions):
        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
            if 'v' in effect:
                self.state[location] = 'I'
            else:
                self.state[location] = 'Q0'

    def change_state(self):
        new_state = deepcopy(self.state)

        # virus spread
        for i in range(1, DIMENSIONS[0] + 1):
            for j in range(1, DIMENSIONS[1] + 1):
                if self.state[(i, j)] == 'H' and ('S' in self.state[(i - 1, j)] or
                                                  'S' in self.state[(i + 1, j)] or
                                                  'S' in self.state[(i, j - 1)] or
                                                  'S' in self.state[(i, j + 1)]):
                    new_state[(i, j)] = 'S1'