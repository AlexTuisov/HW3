import numpy as np
import itertools
import time


offsets = {
    "right": (0, 1),
    "left": (0, -1),
    "up": (-1, 0),
    "down": (1, 0)
}
ids = ['035904275', '315227686']
directions = {'right': (0, 1), 'left': (0, -1), 'up': (1, 0), 'down': (-1, 0)}


class State:
    def __init__(self, map_letters, map_count):
        self.map_letters = map_letters
        self.map_count = map_count

    def check_legal(self, i, j):
        n, m = self.map_count.shape
        if i >= n or i < 0 or j >= n or j < 0:
            return False
        return True

    def apply_actions(self, actions):
        map_letters, map_count = self.map_letters.copy(), self.map_count.copy()
        for change in actions:
            try:
                name, loc = change
                map_letters[loc] = 'I' if name == 'vaccinate' else 'Q'
                map_count[loc] = (map_letters[loc] == 'Q') * 3 + (map_letters[loc] == 'I') * -1
            except:
                pass
        return State(map_letters, map_count)

    def result(self, actions):
        # step 1 - choose which action to perform + some initialization
        new_map_s, new_map_c = self.map_letters.copy(), self.map_count.copy()
        for change in actions:
            name, loc = change
            new_map_s[loc] = 'I' if name == 'vaccinate' else 'Q'
            new_map_c[loc] = (new_map_s[loc] == 'Q') * 3 + (new_map_s[loc] == 'I') * -1

        # step 3 - The infection spreads. People that were close to sick people that are still sick will be infected
        State.step3(new_map_s, new_map_c)
        # step 4 - (-1) for 'Q' and 'S' and if they are equal to zero turn them to 'H'
        new_map_c -= 1
        new_map_s[new_map_c == 0] = 'H'
        return State(new_map_s, new_map_c)

    @staticmethod
    def step3(new_map_s, new_map_c):
        n, m = new_map_s.shape
        sick_loc = np.where(new_map_s == 'S')
        for k in range(sick_loc[0].shape[0]):
            i, j = sick_loc[0][k], sick_loc[1][k]
            if (i + 1) < n and new_map_s[i + 1, j] == 'H':
                new_map_s[i + 1, j] = 'S'
                new_map_c[i + 1, j] = 4
            if (i - 1 >= 0) and new_map_s[i - 1, j] == 'H':
                new_map_s[i - 1, j] = 'S'
                new_map_c[i - 1, j] = 4
            if (j + 1) < m and new_map_s[i, j + 1] == 'H':
                new_map_s[i, j + 1] = 'S'
                new_map_c[i, j + 1] = 4
            if (j - 1 >= 0) and new_map_s[i, j - 1] == 'H':
                new_map_s[i, j - 1] = 'S'
                new_map_c[i, j - 1] = 4

    def actions(self, opposite_zone_of_control):
        map_s, map_c = self.map_letters.copy(), self.map_count.copy()
        n, m = map_s.shape
        my_locs = np.ones(map_s.shape)
        my_locs[opposite_zone_of_control] = 0

        def all_actions_team(options, team_used):
            return [comb for comb in itertools.combinations(options, team_used) if comb != ()]

        def get_all_options(type_of_action, letter, teams_name):
            loc = np.where(map_s == letter)
            opt = list(zip([type_of_action, ] * loc[0].shape[0], zip(loc[0], loc[1])))
            if teams_name == 'police':
                for name, (i, j) in opt:
                    counter = 0
                    for direction in offsets:
                        x, y = i + offsets[direction][0], j + offsets[direction][1]
                        if not self.check_legal(x, y):
                            continue
                        #  check if there are friendly H tiles
                        if map_s[x, y] == 'H' and my_locs[x, y]:
                            counter += 1
                    if counter >= 3:
                        return [tuple([tuple((name, (i, j)))])]
                return []
            new_opt = [[], [], [], [], [], [], [], [], [], [], []]
            if teams_name == 'medic':
                for name, (i, j) in opt:
                    counter = 0
                    for direction in offsets:
                        x, y = i + offsets[direction][0], j + offsets[direction][1]
                        if not self.check_legal(x, y):
                            continue
                        #  check if there are friendly H tiles
                        if map_s[x, y] == 'H' and my_locs[x, y]:
                            counter += 1
                        # enemy H tiles nearby
                        if map_s[x, y] == 'H' and not my_locs[x, y]:
                            counter -= 1
                    if counter >= 0:
                        new_opt[4 - counter].append((name, (i, j)))
                opt = []
                for options in new_opt:
                    opt += options

                return [] + all_actions_team(opt, min([1, loc[0].shape[0]]))

        num_of_H = (map_s[np.where(my_locs == 1)] == 'H').sum()
        check = lambda i, j, letter: not (((i + 1) < n and map_s[i + 1, j] == letter) or ((i >= 1) and map_s[i - 1, j] == letter) or ((j + 1) < m and map_s[i, j + 1] == letter) or ((j >= 1) and map_s[i, j - 1] == letter))
        check2 = lambda i, j, letter: not (((i + 1) < n and map_s[i + 1, j] == letter and my_locs[i + 1, j]) or ((i >= 1) and map_s[i - 1, j] == letter and my_locs[i - 1, j]) or ((j + 1) < m and map_s[i, j + 1] == letter and my_locs[i, j + 1]) or ((j >= 1) and map_s[i, j - 1] == letter and my_locs[i, j - 1]))

        for i in range(n):
            for j in range(m):
                if not my_locs[i, j]:
                    map_s[i, j] = 'O'
                    continue
                if (map_s[i, j] == 'H' and num_of_H >= 2 and check(i, j, 'S')) or (map_s[i, j] == 'S' and check2(i, j, 'H')):
                    num_of_H = num_of_H - 1 if map_s[i, j] == 'H' else num_of_H
                    map_s[i, j] = 'X'

        q = get_all_options('quarantine', 'S', 'police')
        m = get_all_options('vaccinate', 'H', 'medic')

        if not q and m:
            return m
        if not m and q:
            return q[0]
        if not q and not m:
            return []
        all_actions = [element[0] + element[1] for element in itertools.product(m, q)]
        return all_actions


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zone = zone_of_control
        self.zone_of_control = ([zone_of_control[i][0] for i in range(len(zone_of_control))],
                                [zone_of_control[i][1] for i in range(len(zone_of_control))])
        map_s = np.array(initial_state)
        map_c = (map_s == 'S') * 3 + (map_s == 'Q') * 2 + (map_s == 'U') * -1 + (map_s == 'I') * -1
        self.state = State(map_s, map_c)
        self.locations = np.zeros(self.state.map_letters.shape)
        for location in zone_of_control:
            self.locations[location] = 1
        self.enemy_zone_of_control = np.where(self.locations == 0)
        self.order = order
        self.is_first_round = True

    def zones(self, is_max):
        if is_max:  # we will try to maximize our zone
            zone_of_control, opposite = self.zone_of_control, self.enemy_zone_of_control
        else:
            zone_of_control, opposite = self.enemy_zone_of_control, self.zone_of_control
        return zone_of_control, opposite

    def succ(self, state: State, is_max: bool):
        '''
        :param state: numpy array
        :param is_max: True if we are maximizing and false otherwise
        :param actions: if we are minimizing then will contain
        :return: list of possible states
        '''
        zone_of_control, opposite = self.zones(is_max)
        for set_of_actions in set(state.actions(opposite)):
            if is_max:
                yield set_of_actions, state.apply_actions(set_of_actions)
            else:
                yield set_of_actions, state.result(set_of_actions)

    def utility(self, state: State, is_max: bool):
        zone_of_control, opposite = self.zones(is_max)
        my_letters = state.map_letters[zone_of_control]
        enemy_letters = state.map_letters[opposite]
        score = (my_letters == 'H').sum() - (my_letters == 'S').sum() - 5 * (my_letters == 'Q').sum()
        enemy_score = (enemy_letters == 'H').sum() - (enemy_letters == 'S').sum() - 5 * (enemy_letters == 'Q').sum()
        # TODO Check again
        util = score - enemy_score
        return util if is_max else -util

    def terminal_test(self, state):
        all_sick = (state == 'S').sum()
        my_sick = (state[self.zone_of_control] == 'S').sum()
        return (my_sick == 0) or (all_sick == my_sick)

    def max_value(self, state: State, alpha, beta, height=1):
        # call apply action
        if self.terminal_test(state.map_letters) or not height:
            return self.utility(state, True)
        value = float('-inf')
        for operation, new_state in list(self.succ(state, True)):
            value = max([value, self.min_value(new_state, alpha, beta, height - 1)])
            if value >= beta:
                return value
            alpha = max([alpha, value])
        return value

    def min_value(self, state: State, alpha, beta, height=1):
        if self.terminal_test(state.map_letters) or not height:
            return self.utility(state, False)
        value = float('inf')
        for operation, state in list(self.succ(state, False)):
            value = min([value, self.max_value(state, alpha, beta, height - 1)])
            if value <= alpha:
                return value
            beta = min([beta, value])
        return value

    def minimax_decision(self, state: State):
        value = float('-inf')
        succ = set(self.succ(state, True))
        best_operation = None
        start = time.time()
        for operation, new_state in succ:
            now = time.time()
            time_passed = now - start
            if time_passed > 4.5:
                break
            value, best_operation = max([(value, best_operation), (self.min_value(new_state, float('-inf'), float('inf'), 4), operation)], key=lambda x: x[0])
        if not best_operation:
            best_operation = []
        return best_operation

    def update(self, state):
        if self.is_first_round:
            self.is_first_round = False
            return None
        self.state.map_count -= 1
        sick_quarantined = np.where((state == 'Q') & (self.state.map_letters == 'S'))
        self.state.map_letters[sick_quarantined] = 'Q'
        self.state.map_count[sick_quarantined] = 2

        if self.order == 'second':
            sick_quarantined = np.where((state == 'Q') & (self.state.map_letters == 'H'))
            self.state.map_letters[sick_quarantined] = 'Q'
            self.state.map_count[sick_quarantined] = 2

        si_now_healthy = np.where((state == 'H') & (self.state.map_letters == 'S'))
        self.state.map_letters[si_now_healthy] = 'H'
        self.state.map_count[si_now_healthy] = 0

        infected_healthy = np.where((state == 'I') & (self.state.map_letters == 'H'))
        self.state.map_letters[infected_healthy] = 'I'
        self.state.map_count[infected_healthy] = -1

        infected_healthy = np.where((state == 'S') & (self.state.map_letters == 'H'))
        self.state.map_letters[infected_healthy] = 'S'
        self.state.map_count[infected_healthy] = 3

        qu_now_healthy = np.where((state == 'H') & (self.state.map_letters == 'Q'))
        self.state.map_letters[qu_now_healthy] = 'H'
        self.state.map_count[qu_now_healthy] = 0

        self.state.map_letters[np.where(state == 'H')] = 'H'
        self.state.map_count[np.where(state == 'H')] = 0
        self.state.map_letters[np.where(state == 'I')] = 'I'

    def act(self, state):
        state = np.array(state)
        self.update(state)
        result = self.minimax_decision(self.state)
        self.state = self.state.apply_actions(result)

        return result
