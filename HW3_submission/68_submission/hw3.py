import math
import random
from copy import deepcopy
from main import Game
from itertools import combinations, product
ids = ['206851164', '312546609']

MAX_DEPTH = 1
RIVAL = "rival"
ME = "me"
INF = 99999999


#region first agent

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.observation = initial_state
        self.order = order
        self.rzoc = []
        self.rows , self.cols = len(initial_state), len(initial_state[0])

        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in self.zoc:
                    self.rzoc.append((row, col))


    def act(self, state):
        self.observation = state
        actions = []
        healthy = []
        sick = []

        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append(("vaccinate", (i, j), self.h_for_health((i, j))))
            if 'S' in state[i][j]:
                sick.append(("quarantine", (i, j), self.h_for_sick((i, j))))

        if len(healthy) > 0:
            healthy.sort(key=lambda tup: tup[2])
            actions.append(healthy[-1][:-1])
            return actions

        return []

        # if len(sick) > 0:
        #    sick.sort(key=lambda tup: tup[2])
        #    actions.append(sick[-1])
        #    return actions

        # return []




    def h_for_sick(self, indexes):
        row = indexes[0]
        col = indexes[1]
        grade = 0

        # check & fix above
        if row != 0 and self.observation[row - 1][col] == 'H':
            if (row - 1, col) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        # check & fix bellow
        if row != self.rows - 1 and self.observation[row + 1][col] == 'H':
            if (row + 1, col) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        # check & fix left
        if col != 0 and self.observation[row][col - 1] == 'H':
            if (row, col - 1) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        # check & fix right
        if col != self.cols - 1 and self.observation[row][col + 1] == 'H':
            if (row, col + 1) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        return grade


    def h_for_health(self, indexes):
        row = indexes[0]
        col = indexes[1]
        grade = 0

        # check & fix above
        if row != 0 and self.observation[row - 1][col] == 'S':
            if (row - 1, col) in self.rzoc:
                grade += 3
            else:
                grade += 1

        # check & fix bellow
        if row != self.rows - 1 and self.observation[row + 1][col] == 'S':
            if (row + 1, col) in self.rzoc:
                grade += 3
            else:
                grade += 1

        # check & fix left
        if col != 0 and self.observation[row][col - 1] == 'S':
            if (row, col - 1) in self.rzoc:
                grade += 3
            else:
                grade += 1

        # check & fix right
        if col != self.cols - 1 and self.observation[row][col + 1] == 'S':
            if (row, col + 1) in self.rzoc:
                grade += 3
            else:
                grade += 1

        return grade

#endregion

# region second agent
'''
class Agent:
    
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.observation = initial_state
        self.order = order
        self.rzoc = []
        self.rows , self.cols = len(initial_state), len(initial_state[0])

        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in self.zoc:
                    self.rzoc.append((row, col))


    def act(self, state):
        self.observation = deepcopy(state)
        actions = []
        healthy = []
        sick = []

        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append(("vaccinate", (i, j), self.h_for_health((i, j))))
            if 'S' in state[i][j]:
                sick.append(("quarantine", (i, j), self.h_for_sick((i, j))))

        if len(healthy) > 0:
            healthy.sort(key=lambda tup: tup[2])
            actions.append(healthy[-1])

        if len(sick) > 0:
            sick.sort(key=lambda tup: tup[2])
            if len(sick) > 1:
                actions.append(sick[-2])
                actions.append(sick[-1])
            else:
                actions.append(sick[-1])

        return actions


    def minmax(self, is_our_turn, curr_map, depth, possible_moves):
        if depth == MAX_DEPTH:
            if is_our_turn:
                return # h_for_max (h_for_max will choose the best action from all the possibale acts
            else:
                return # h for min


        copy_of_curr_map = deepcopy(curr_map)
        for move in possible_moves:



    def h_for_sick(self, indexes):
        row = indexes[0]
        col = indexes[1]
        my_state = self.observation[row][col]
        grade = 0

        # check & fix above
        if row != 0 and self.observation[row - 1][col] == 'H':
            if (row - 1, col) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        # check & fix bellow
        if row != self.rows - 1 and self.observation[row + 1][col] == 'H':
            if (row + 1, col) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        # check & fix left
        if col != 0 and self.observation[row][col - 1] == 'H':
            if (row, col - 1) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        # check & fix right
        if col != self.cols - 1 and self.observation[row][col + 1] == 'H':
            if (row, col + 1) in self.rzoc:
                grade -= 2
            else:
                grade += 1

        return grade


    def h_for_health(self, indexes):
        row = indexes[0]
        col = indexes[1]
        my_state = self.observation[row][col]
        grade = 0

        # check & fix above
        if row != 0 and self.observation[row - 1][col] == 'S':
            if (row - 1, col) in self.rzoc:
                grade += 3
            else:
                grade += 1

        # check & fix bellow
        if row != self.rows - 1 and self.observation[row + 1][col] == 'S':
            if (row + 1, col) in self.rzoc:
                grade += 3
            else:
                grade += 1

        # check & fix left
        if col != 0 and self.observation[row][col - 1] == 'S':
            if (row, col - 1) in self.rzoc:
                grade += 3
            else:
                grade += 1

        # check & fix right
        if col != self.cols - 1 and self.observation[row][col + 1] == 'S':
            if (row, col + 1) in self.rzoc:
                grade += 3
            else:
                grade += 1

        return grade
'''
#endregion

#region minmax agent

'''
class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.order = order
        self.rzoc = []
        self.rows, self.cols = len(initial_state), len(initial_state[0])
        self.detailed_state = []

        for row in initial_state:
            detailed_row = []
            for tup in row:
                if tup == 'S':
                    detailed_row.append(tup + '0')
                else:
                    detailed_row.append(tup)

            self.detailed_state.append(detailed_row)

        for row in range(self.rows):#####
            for col in range(self.cols):####
                if (row, col) not in self.zoc:
                    self.rzoc.append((row, col))


    def act(self, state):
        self.update_detailed_state(state)
        detailed_state_copy = deepcopy(self.detailed_state)
        alpha =  -INF
        beta = INF
        action = self.minmax(0, ME, detailed_state_copy, alpha, beta)[1]
        # print("myyyyyy: ", action)
        return action


    def update_detailed_state(self, state):
        for row in range(self.rows):
            for col in range(self.cols):
                if state[row][col] == 'S':
                    if self.detailed_state[row][col] == 'S1':
                        self.detailed_state[row][col] = 'S2'
                    elif self.detailed_state[row][col] == 'S2':
                        self.detailed_state[row][col] = 'S3'
                    else:
                        self.detailed_state[row][col] = 'S1'

                elif state[row][col] == 'Q':
                    if self.detailed_state[row][col] == 'Q1':
                        self.detailed_state[row][col] = 'Q2'
                    else:
                        self.detailed_state[row][col] = 'Q1'
                else:
                    self.detailed_state[row][col] = state[row][col]


    def update_minmax_state(self, before_spread_state, actions):

        after_only_actions_state = deepcopy(before_spread_state)
        after_spread_and_actions_state = deepcopy(before_spread_state)
        # print(actions)

        # preform the actions
        for act in actions:
            row_idx = act[1][0]
            col_idx = act[1][1]
            if 'v' in act[0]:
                after_spread_and_actions_state[row_idx][col_idx] = 'I'
                after_only_actions_state[row_idx][col_idx] = 'I'
            else:
                after_spread_and_actions_state[row_idx][col_idx] = 'Q0'
                after_only_actions_state[row_idx][col_idx] = 'Q1'

        # infection spread
        for row_idx in range(self.rows):
            for col_idx in range(self.cols):
                if 'S' in after_only_actions_state[row_idx][col_idx]:
                    self.adjust_neighbors(row_idx, col_idx, after_spread_and_actions_state)

        # advancing turns + fix expires
        for row_idx in range(self.rows):
            for col_idx in range(self.cols):
                tup = after_spread_and_actions_state[row_idx][col_idx]
                if 'S' in tup:
                    if tup == 'S3':
                        after_spread_and_actions_state[row_idx][col_idx] = 'H'
                    else:
                        turn = int(tup[1])
                        after_spread_and_actions_state[row_idx][col_idx] = 'S' + str(turn + 1)
                elif 'Q' in tup:
                    if tup == 'Q2':
                        after_spread_and_actions_state[row_idx][col_idx] = 'H'
                    else:
                        turn = int(tup[1])
                        after_spread_and_actions_state[row_idx][col_idx] = 'Q' + str(turn + 1)



        return after_spread_and_actions_state


    def adjust_neighbors(self, row_idx, col_idx, after_actions_state):

        # check & fix above
        if row_idx != 0 and after_actions_state[row_idx - 1][col_idx] == 'H':
            after_actions_state[row_idx - 1][col_idx] = 'S0'

        # check & fix bellow
        if row_idx != self.rows - 1 and after_actions_state[row_idx + 1][col_idx] == 'H':
            after_actions_state[row_idx + 1][col_idx] = 'S0'

        # check & fix left
        if col_idx != 0 and after_actions_state[row_idx][col_idx - 1] == 'H':
            after_actions_state[row_idx][col_idx - 1] = 'S0'

        # check & fix right
        if col_idx != self.cols - 1 and after_actions_state[row_idx][col_idx + 1] == 'H':
            after_actions_state[row_idx][col_idx + 1] = 'S0'


    def minmax(self, curr_depth, player_name, curr_state, alpha, beta):
        if curr_depth == MAX_DEPTH or Agent.is_end_game(curr_state):
            if curr_depth == 0:
                all_possible_actions = self.get_all_possible_actions_updated(player_name, curr_state)
                return self.score(curr_state), all_possible_actions[0]
            else:
                return self.score(curr_state), ('dummy_act', (0, 0))

        if player_name == ME:
            curr_max = -INF
            all_possible_actions = self.get_all_possible_actions_updated(player_name, curr_state)
            max_value_action = all_possible_actions[0]
            for action in all_possible_actions:
                after_action_state = self.update_minmax_state(curr_state, action)
                curr_value = self.minmax(curr_depth + 1, RIVAL, after_action_state, alpha, beta)[0]
                if curr_value > curr_max:
                    curr_max = curr_value
                    max_value_action = action
                if curr_max >= beta:
                    return curr_max, max_value_action
                alpha = max(alpha, curr_max)

            return curr_max, max_value_action

        else:  # player_name == rival
            curr_min = INF
            all_possible_actions = self.get_all_possible_actions_updated(player_name, curr_state)
            min_value_action = all_possible_actions[0]
            for action in all_possible_actions:
                after_action_state = self.update_minmax_state(curr_state, action)
                curr_value = self.minmax(curr_depth + 1, ME, after_action_state, alpha, beta)[0]
                if curr_value < curr_min:
                    curr_min = curr_value
                    min_value_action = action
                if curr_min <= alpha:
                    return curr_min, min_value_action
                beta = min(beta, curr_min)

            return curr_min, min_value_action

    def score(self, curr_state):
        me_score = 0
        rival_score = 0

        for (i, j) in self.zoc:
            char_state = curr_state[i][j][0]
            me_score = me_score + 1 if char_state == 'H' else me_score
            me_score = me_score + 1 if char_state == 'I' else me_score
            me_score = me_score - 1 if char_state == 'S' else me_score
            me_score = me_score - 5 if char_state == 'Q' else me_score

        for (i, j) in self.rzoc:
            char_state = curr_state[i][j][0]
            rival_score = rival_score + 1 if char_state == 'H' else rival_score
            rival_score = rival_score + 1 if char_state == 'I' else rival_score
            rival_score = rival_score - 1 if char_state == 'S' else rival_score
            rival_score = rival_score - 5 if char_state == 'Q' else rival_score

        diff = me_score - rival_score
        return diff

    # return list of possible actions
    def get_possible_actions(self, curr_state, player_name):
        healthy_actions = []
        sick_actions = []
        player_zoc = self.zoc if player_name == ME else self.rzoc

        for (i, j) in player_zoc:
            if 'H' in curr_state[i][j]:
                healthy_actions.append(("vaccinate", (i, j)))
            if 'S' in curr_state[i][j]:
                sick_actions.append(("quarantine", (i, j)))


        s_combinations = []
        if len(sick_actions) > 1:
            s_combinations = combinations(sick_actions, 2)
            if len(healthy_actions) > 0:
                all_actions = list(product(healthy_actions, s_combinations))
                fixed_all_actions = []
                for act in all_actions:
                    flatten = [act[0], act[1][0], act[1][1]]
                    fixed_all_actions.append(flatten)

                all_actions = fixed_all_actions

            else:
                all_actions = s_combinations

        elif len(sick_actions) == 1:
            s_combinations = sick_actions
            if len(healthy_actions) > 0:
                all_actions = list(product(healthy_actions, s_combinations))

            else:
                all_actions = s_combinations

        else:
            all_actions = healthy_actions


        return all_actions


    @staticmethod
    def is_end_game(state):
        # print("our end_game: ", state)
        for row in state:
            for tup in row:
                if 'S' in tup:
                    return False

        return True



    def find_quarantine_and_vaccinate_possible_actions(self, player_name, curr_state):
        healthy_actions = []
        sick_actions = []
        player_zoc = self.zoc if player_name == ME else self.rzoc

        for (i, j) in player_zoc:
            if 'H' in curr_state[i][j]:
                healthy_actions.append(("vaccinate", (i, j)))
            if 'S' in curr_state[i][j]:
                sick_actions.append(("quarantine", (i, j)))

        return sick_actions, healthy_actions

    def merge_quarantine_vaccinate_actions(self, possible_quarantine_actions, possible_vaccinate_actions):
        # merge the lists
        possible_action_set = []
        len_quarantine = len(possible_quarantine_actions)
        len_vaccinate = len(possible_vaccinate_actions)
        if len_quarantine != 0 and len_vaccinate != 0:
            if len_quarantine == 1:
                combi_police = set(combinations(possible_quarantine_actions, 1))
                combi_medics = set(combinations(possible_vaccinate_actions, 1))
                raw_possible_action_set = set(product(combi_police, combi_medics))
            else:
                combi_police = set(combinations(possible_quarantine_actions, 2))
                combi_medics = set(combinations(possible_vaccinate_actions, 1))
                raw_possible_action_set = set(product(combi_police, combi_medics))
            for act in raw_possible_action_set:
                possible_action_set.append((tuple(map(lambda police_act: police_act, act[0])) + tuple(
                    map(lambda medic_act: medic_act, act[1]))))

        elif len_quarantine == 0 and len_vaccinate == 0:
            possible_action_set = []

        elif len_quarantine == 0:
            combi_medics = set(combinations(possible_vaccinate_actions, 1))
            possible_action_set = combi_medics

        else:
            combi_police = set(combinations(possible_quarantine_actions, 2))
            possible_action_set = combi_police


        return possible_action_set

    @staticmethod
    def fix_possible_orientation_error(possible_action_set):
        len_possible_action_set = len(possible_action_set)
        for idx in range(len_possible_action_set):
            if type(possible_action_set[idx][0]) is str:
                wrap_list = []
                wrap_list.append(possible_action_set[idx])
                possible_action_set[idx] = tuple(wrap_list)

        return possible_action_set

    def get_all_possible_actions_updated(self, player_name, curr_state):

        # find quarantine and vaccinate possible actions
        possible_quarantine_actions, possible_vaccinate_actions = self.find_quarantine_and_vaccinate_possible_actions(player_name, curr_state)

        # merge the lists
        possible_action_set = self.merge_quarantine_vaccinate_actions(possible_quarantine_actions, possible_vaccinate_actions)

        # fixing possible orientation error
        # possible_action_set = Agent.fix_possible_orientation_error(possible_action_set)

        return list(possible_action_set)

'''
#endregion

# region agent with large init
'''
class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.order = order
        self.rzoc = []
        self.rows, self.cols = len(initial_state), len(initial_state[0])
        self.detailed_state = []

        for row in initial_state:
            detailed_row = []
            for tup in row:
                if tup == 'S':
                    detailed_row.append(tup + '0')
                else:
                    detailed_row.append(tup)

            self.detailed_state.append(detailed_row)

        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in self.zoc:
                    self.rzoc.append((row, col))


    def act(self, state):
        self.update_detailed_state(state)
        detailed_state_copy = deepcopy(self.detailed_state)
        alpha = -INF
        beta = INF
        action = self.minmax(0, ME, detailed_state_copy, alpha, beta)[1]
        # print("myyyyyy: ", action)
        return action


    def update_detailed_state(self, state):
        for row in range(self.rows):
            for col in range(self.cols):
                if state[row][col] == 'S':
                    if self.detailed_state[row][col] == 'S1':
                        self.detailed_state[row][col] = 'S2'
                    elif self.detailed_state[row][col] == 'S2':
                        self.detailed_state[row][col] = 'S3'
                    else:
                        self.detailed_state[row][col] = 'S1'

                elif state[row][col] == 'Q':
                    if self.detailed_state[row][col] == 'Q1':
                        self.detailed_state[row][col] = 'Q2'
                    else:
                        self.detailed_state[row][col] = 'Q1'
                else:
                    self.detailed_state[row][col] = state[row][col]


    def update_minmax_state(self, before_spread_state, actions):
        after_only_actions_state = deepcopy(before_spread_state)
        after_spread_and_actions_state = deepcopy(before_spread_state)
        # print(actions)

        # preform the actions
        for act in actions:
            row_idx = act[1][0]
            col_idx = act[1][1]
            if 'v' in act[0]:
                after_spread_and_actions_state[row_idx][col_idx] = 'I'
                after_only_actions_state[row_idx][col_idx] = 'I'
            else:
                after_spread_and_actions_state[row_idx][col_idx] = 'Q0'
                after_only_actions_state[row_idx][col_idx] = 'Q1'

        # infection spread
        for row_idx in range(self.rows):
            for col_idx in range(self.cols):
                if 'S' in after_only_actions_state[row_idx][col_idx]:
                    self.adjust_neighbors(row_idx, col_idx, after_spread_and_actions_state)

        # advancing turns + fix expires
        for row_idx in range(self.rows):
            for col_idx in range(self.cols):
                tup = after_spread_and_actions_state[row_idx][col_idx]
                if 'S' in tup:
                    if tup == 'S3':
                        after_spread_and_actions_state[row_idx][col_idx] = 'H'
                    else:
                        turn = int(tup[1])
                        after_spread_and_actions_state[row_idx][col_idx] = 'S' + str(turn + 1)
                elif 'Q' in tup:
                    if tup == 'Q2':
                        after_spread_and_actions_state[row_idx][col_idx] = 'H'
                    else:
                        turn = int(tup[1])
                        after_spread_and_actions_state[row_idx][col_idx] = 'Q' + str(turn + 1)

        return after_spread_and_actions_state


    def adjust_neighbors(self, row_idx, col_idx, after_actions_state):
        # check & fix above
        if row_idx != 0 and after_actions_state[row_idx - 1][col_idx] == 'H':
            after_actions_state[row_idx - 1][col_idx] = 'S0'

        # check & fix bellow
        if row_idx != self.rows - 1 and after_actions_state[row_idx + 1][col_idx] == 'H':
            after_actions_state[row_idx + 1][col_idx] = 'S0'

        # check & fix left
        if col_idx != 0 and after_actions_state[row_idx][col_idx - 1] == 'H':
            after_actions_state[row_idx][col_idx - 1] = 'S0'

        # check & fix right
        if col_idx != self.cols - 1 and after_actions_state[row_idx][col_idx + 1] == 'H':
            after_actions_state[row_idx][col_idx + 1] = 'S0'


    def minmax(self, curr_depth, player_name, curr_state, alpha, beta):
        if curr_depth == MAX_DEPTH or Agent.is_end_game(curr_state):
            if curr_depth == 0:
                all_possible_actions = self.get_all_possible_actions_updated(player_name, curr_state)
                return self.score(curr_state), all_possible_actions[0]
            else:
                return self.score(curr_state), ('dummy_act', (0, 0))

        if player_name == ME:
            curr_max = -INF
            all_possible_actions = self.get_all_possible_actions_updated(player_name, curr_state)
            max_value_action = all_possible_actions[0]
            for action in all_possible_actions:
                after_action_state = self.update_minmax_state(curr_state, action)
                curr_value = self.minmax(curr_depth + 1, RIVAL, after_action_state, alpha, beta)[0]
                if curr_value > curr_max:
                    curr_max = curr_value
                    max_value_action = action
                if curr_max >= beta:
                    return curr_max, max_value_action
                alpha = max(alpha, curr_max)

            return curr_max, max_value_action

        else:  # player_name == rival
            curr_min = INF
            all_possible_actions = self.get_all_possible_actions_updated(player_name, curr_state)
            min_value_action = all_possible_actions[0]
            for action in all_possible_actions:
                after_action_state = self.update_minmax_state(curr_state, action)
                curr_value = self.minmax(curr_depth + 1, ME, after_action_state, alpha, beta)[0]
                if curr_value < curr_min:
                    curr_min = curr_value
                    min_value_action = action
                if curr_min <= alpha:
                    return curr_min, min_value_action
                beta = min(beta, curr_min)

            return curr_min, min_value_action


    def score(self, curr_state):
        me_score = 0
        rival_score = 0

        for (i, j) in self.zoc:
            char_state = curr_state[i][j][0]
            me_score = me_score + 1 if char_state == 'H' else me_score
            me_score = me_score + 1 if char_state == 'I' else me_score
            me_score = me_score - 1 if char_state == 'S' else me_score
            me_score = me_score - 5 if char_state == 'Q' else me_score

        for (i, j) in self.rzoc:
            char_state = curr_state[i][j][0]
            rival_score = rival_score + 1 if char_state == 'H' else rival_score
            rival_score = rival_score + 1 if char_state == 'I' else rival_score
            rival_score = rival_score - 1 if char_state == 'S' else rival_score
            rival_score = rival_score - 5 if char_state == 'Q' else rival_score

        diff = me_score - rival_score
        return diff


    # return list of possible actions
    def get_possible_actions(self, curr_state, player_name):
        healthy_actions = []
        sick_actions = []
        player_zoc = self.zoc if player_name == ME else self.rzoc

        for (i, j) in player_zoc:
            if 'H' in curr_state[i][j]:
                healthy_actions.append(("vaccinate", (i, j)))
            if 'S' in curr_state[i][j]:
                sick_actions.append(("quarantine", (i, j)))

        s_combinations = []
        if len(sick_actions) > 1:
            s_combinations = combinations(sick_actions, 2)
            if len(healthy_actions) > 0:
                all_actions = list(product(healthy_actions, s_combinations))
                fixed_all_actions = []
                for act in all_actions:
                    flatten = [act[0], act[1][0], act[1][1]]
                    fixed_all_actions.append(flatten)

                all_actions = fixed_all_actions

            else:
                all_actions = s_combinations

        elif len(sick_actions) == 1:
            s_combinations = sick_actions
            if len(healthy_actions) > 0:
                all_actions = list(product(healthy_actions, s_combinations))

            else:
                all_actions = s_combinations

        else:
            all_actions = healthy_actions

        return all_actions


    @staticmethod
    def is_end_game(state):
        # print("our end_game: ", state)
        for row in state:
            for tup in row:
                if 'S' in tup:
                    return False

        return True


    def find_quarantine_and_vaccinate_possible_actions(self, player_name, curr_state):
        healthy_actions = []
        sick_actions = []
        player_zoc = self.zoc if player_name == ME else self.rzoc

        for (i, j) in player_zoc:
            if 'H' in curr_state[i][j]:
                healthy_actions.append(("vaccinate", (i, j)))
            if 'S' in curr_state[i][j]:
                sick_actions.append(("quarantine", (i, j)))

        return sick_actions, healthy_actions


    def merge_quarantine_vaccinate_actions(self, possible_quarantine_actions, possible_vaccinate_actions):
        # merge the lists
        possible_action_set = []
        len_quarantine = len(possible_quarantine_actions)
        len_vaccinate = len(possible_vaccinate_actions)
        if len_quarantine != 0 and len_vaccinate != 0:
            if len_quarantine == 1:
                combi_police = set(combinations(possible_quarantine_actions, 1))
                combi_medics = set(combinations(possible_vaccinate_actions, 1))
                raw_possible_action_set = set(product(combi_police, combi_medics))
            else:
                combi_police = set(combinations(possible_quarantine_actions, 2))
                combi_medics = set(combinations(possible_vaccinate_actions, 1))
                raw_possible_action_set = set(product(combi_police, combi_medics))
            for act in raw_possible_action_set:
                possible_action_set.append((tuple(map(lambda police_act: police_act, act[0])) + tuple(
                    map(lambda medic_act: medic_act, act[1]))))

        elif len_quarantine == 0 and len_vaccinate == 0:
            possible_action_set = []

        elif len_quarantine == 0:
            combi_medics = set(combinations(possible_vaccinate_actions, 1))
            possible_action_set = combi_medics

        else:
            combi_police = set(combinations(possible_quarantine_actions, 2))
            possible_action_set = combi_police

        return possible_action_set


    @staticmethod
    def fix_possible_orientation_error(possible_action_set):
        len_possible_action_set = len(possible_action_set)
        for idx in range(len_possible_action_set):
            if type(possible_action_set[idx][0]) is str:
                wrap_list = []
                wrap_list.append(possible_action_set[idx])
                possible_action_set[idx] = tuple(wrap_list)

        return possible_action_set


    def get_all_possible_actions_updated(self, player_name, curr_state):
        # find quarantine and vaccinate possible actions
        possible_quarantine_actions, possible_vaccinate_actions = self.find_quarantine_and_vaccinate_possible_actions(
            player_name, curr_state)

        # merge the lists
        possible_action_set = self.merge_quarantine_vaccinate_actions(possible_quarantine_actions,
                                                                      possible_vaccinate_actions)

        # fixing possible orientation error
        # possible_action_set = Agent.fix_possible_orientation_error(possible_action_set)

        return list(possible_action_set)
'''
#endregion
