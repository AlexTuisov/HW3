import random
from itertools import combinations

ids = ['212197222', '315392639']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):

        self.rows = len(initial_state)
        self.cols = len(initial_state[0])

        self.initial_state = initial_state
        self.cur_state = []
        for i in range(self.rows):
            temp_row = []
            for j in range(self.cols):
                temp_row.append([initial_state[i][j], 0])
            self.cur_state.append(temp_row)


        self.order = order
        self.police = 2
        self.medics = 1

        self.zoc = zone_of_control
        #find other agent's zone of control:
        self.other_zoc = []
        for i in range(self.rows):
            for j in range(self.cols):
                if (i,j) not in self.zoc:
                    self.other_zoc.append((i,j))

        self.first_day = 1

    def actions(self, state, zoc): #from HW1
        S_locations = []
        H_locations = []

        for i in range(self.rows):
            for j in range(self.cols):
                if (i,j) in zoc:
                    if state[i][j] == 'S':
                        S_locations.append((i, j))
                    elif state[i][j] == 'H':
                        H_locations.append((i, j))

        actions = []

        police_options = list(combinations(S_locations, min(len(S_locations), self.police)))
        medics_options = list(combinations(H_locations, min(len(H_locations), self.medics)))

        if medics_options and police_options:
            for police_locs in police_options:
                for medics_locs in medics_options:
                    p_action = [("quarantine", loc) for loc in police_locs]
                    m_action = [("vaccinate", loc) for loc in medics_locs]
                    actions.append(tuple(p_action+m_action))

        elif medics_options: #will not happen, we will always need police or we win since there is no S
            for medics_locs in medics_options:
                m_action = [("vaccinate", loc) for loc in medics_locs]
                actions.append(tuple(m_action))

        elif police_options:
            for police_locs in police_options:
                p_action = [("quarantine", loc) for loc in police_locs]
                actions.append(tuple(p_action))

        return tuple(actions)

    def no_Q_actions(self, state, zoc, my_agent):  # from HW1
        S_locations = []
        H_locations = []

        good_S = []
        if my_agent:
            good_S = self.find_S_with_4_H(state)

        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) in zoc:
                    if state[i][j] == 'S':
                        S_locations.append((i, j))
                    elif state[i][j] == 'H':
                        H_locations.append((i, j))

        actions = []

        police_options = list(combinations(S_locations, min(len(S_locations), self.police)))
        good_police_options = list(combinations(good_S, min(len(good_S), self.police)))
        medics_options = list(combinations(H_locations, min(len(H_locations), self.medics)))

        if medics_options:
            for medics_locs in medics_options:
                m_action = [("vaccinate", loc) for loc in medics_locs]
                actions.append(tuple(m_action))
        if good_police_options:
            for police_locs in good_police_options:
                p_action = [("quarantine", loc) for loc in police_locs]
                actions.append(tuple(p_action))

        if not good_police_options and not medics_options and police_options:
            for police_locs in police_options:
                p_action = [("quarantine", loc) for loc in police_locs]
                actions.append(tuple(p_action))

        return tuple(actions)

    def result(self, state, action): #from HW1
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        #Do we need to check "the action must be one of self.actions(state)"?
        action_indexes = []
        for sub in action:
            action_indexes.append(sub[1])

        #see where S was located, to update infected areas (only sick areas that are not quarantined):
        S_locations = []
        for i, row in enumerate(state):
            for j, area in enumerate(row):
                if area[0] == 'S' and (i,j) not in action_indexes:
                    S_locations.append((i,j))

        new_map = []
        for i, row in enumerate(state):
            temp_row = []
            for j, area in enumerate(row):
                #change according to action:
                if (i,j) in action_indexes:
                    if area[0] == 'S': #area contains S
                        temp_row.append(('Q', 1))
                    else: #area contains H
                        temp_row.append(('I', 1))

                #change according to infection/time passing:
                elif area[0] == 'H': #infection
                    if (i+1,j) in S_locations or (i-1, j) in S_locations or (i, j+1) in S_locations or (i, j-1) in S_locations:
                        temp_row.append(('S', 1))
                    else:
                        temp_row.append(('H', area[1]+1))
                elif area[0] == 'S' and area[1] == 3: #time passing
                    temp_row.append(('H', 1))
                elif area[0] == 'Q' and area[1] == 1: # if one turn had passed since became Q, protected infection twice
                    temp_row.append(('H', 1))
                else:
                    temp_row.append((area[0], area[1]+1))
            new_map.append(tuple(temp_row))
        new_state = tuple(new_map)

        return new_state

    def get_actions_score(self, state, actions):
        '''
        2 - S infects me (1 for each H that will be infected)
        -0.5 - S will infect others H (-0.5 for every infection of other)

        not modeling S that does not infect anyone - will get score 0

        1 - H that will not be infected
        4 - H that could be infected
        '''

        check_my_infection = lambda index: 2 if index in self.zoc and state[index[0]][index[1]] == 'H' else 0
        check_other_infection = lambda index: -0.5 if index in self.other_zoc and state[index[0]][index[1]] == 'H' else 0
        '''check_my_H_infected = lambda index: 2 if index in self.other_zoc+self.other_zoc\
                                                 and state[index[0]][index[1]] == 'S' else 0'''
        check_my_H_infected = lambda index: True if index in self.other_zoc + self.other_zoc \
                                                 and state[index[0]][index[1]] == 'S' else False

        score = 0
        for action in actions:
            to_do, index = action
            i, j = index
            if to_do == 'quarantine':
               #check if I am infected:
               score += check_my_infection((i + 1, j))
               score += check_my_infection((i - 1, j))
               score += check_my_infection((i, j + 1))
               score += check_my_infection((i, j - 1))

               #check if other is infected:
               score += check_other_infection((i + 1, j))
               score += check_other_infection((i - 1, j))
               score += check_other_infection((i, j + 1))
               score += check_other_infection((i, j - 1))

            elif to_do == 'vaccinate':
                '''score += 1
                score += check_my_H_infected((i + 1, j))
                score += check_my_H_infected((i - 1, j))
                score += check_my_H_infected((i, j + 1))
                score += check_my_H_infected((i, j - 1))'''
                if check_my_H_infected((i + 1, j)) or check_my_H_infected((i - 1, j)) \
                    or check_my_H_infected((i, j + 1)) or check_my_H_infected((i, j - 1)):
                    score += 3
                else:
                    score -= 0.5

        return score

    def find_S_with_4_H(self, state):
        check_my_H = lambda index: 1 if index in self.other_zoc + self.other_zoc \
                                                 and state[index[0]][index[1]] == 'S' else 0
        good_S = []
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j] == 'S':
                    score = 0
                    score += check_my_H((i + 1, j))
                    score += check_my_H((i - 1, j))
                    score += check_my_H((i, j + 1))
                    score += check_my_H((i, j - 1))
                    if score == 4:
                        good_S.append((i,j))
        return good_S

    def priorities_actions(self, state, all_actions):
        scores = []
        for action in all_actions:
            score = self.get_actions_score(state, action)
            scores.append(score)
        actions_scores = list(zip(scores, all_actions))
        sorted_scores = sorted(actions_scores, reverse=True)
        scores, actions = zip(*sorted_scores)
        return actions[:20]

    def calc_scores(self, state):
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

        return score

    def update_cur_state(self, state):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cur_state[i][j][0] == state[i][j]:
                    self.cur_state[i][j][1] += 1
                else:
                    self.cur_state[i][j][0] = state[i][j]
                    self.cur_state[i][j][1] = 0

    def act(self, state):
        if self.first_day == 1:
            self.first_day = 0
        else:
            self.update_cur_state(state)

        if self.order == 'first':
            action = self.act_for_first(state)
        else:
            action = self.act_for_second(state)
        return action

    def act_for_first(self, state):
        action = []
        min_score = -500

        my_possible_actions = self.no_Q_actions(state, self.zoc, True)
        my_possible_actions = self.priorities_actions(state, my_possible_actions)
        for i, my_action in enumerate(my_possible_actions):  # LAYER 1 - we want to find the maximal option:
            other_possible_actions = self.no_Q_actions(state, self.other_zoc, False)

            #other_possible_actions = self.priorities_actions(other_possible_actions)
            other_scores = []

            for other_action in other_possible_actions:  # LAYER 2 - we want to find the minimal option:
                other_result = self.result(self.cur_state, other_action+my_action)
                temp_score = self.calc_scores(other_result)
                other_scores.append(temp_score)

            temp_min = min(other_scores)
            if min_score < temp_min:
                min_score = temp_min
                action = my_action

        return action

    def act_for_second(self, state):
        action = []
        min_score = -500

        my_possible_actions = self.no_Q_actions(state, self.zoc, True)
        my_possible_actions = self.priorities_actions(state, my_possible_actions)

        for i, my_action in enumerate(my_possible_actions):  # LAYER 1 - we want to find the maximal option:
            first_result = self.result(self.cur_state, my_action)
            other_possible_actions = self.no_Q_actions(first_result, self.other_zoc, False)
            # other_possible_actions = self.priorities_actions(other_possible_actions)
            other_scores = []
            for other_action in other_possible_actions:  # LAYER 2 - we want to find the minimal option:
                #ADDITION:
                my2_possible_actions = self.no_Q_actions(first_result, self.zoc, True)
                my2_possible_actions = self.priorities_actions(first_result, my2_possible_actions)
                for my2_action in my2_possible_actions:
                    second_result = self.result(first_result, other_action+my2_action)
                    temp_score = self.calc_scores(second_result)
                    other_scores.append(temp_score)
                #other_result = self.result(my_result, other_action)
                #temp_score = self.calc_scores(other_result)
                #other_scores.append(temp_score)

            temp_min = min(other_scores)
            if min_score < temp_min:
                min_score = temp_min
                action = my_action

        return action


# implementation of a random agent
# class Agent:
#     def __init__(self, initial_state, zone_of_control, order):
#         self.zoc = zone_of_control
#         print(initial_state)
#
#     def act(self, state):
#         action = []
#         healthy = set()
#         sick = set()
#         for (i, j) in self.zoc:
#             if 'H' in state[i][j]:
#                 healthy.add((i, j))
#             if 'S' in state[i][j]:
#                 sick.add((i, j))
#         try:
#             to_quarantine = random.sample(sick, 2)
#         except ValueError:
#             to_quarantine = []
#         try:
#             to_vaccinate = random.sample(healthy, 1)
#         except ValueError:
#             to_vaccinate = []
#         for item in to_quarantine:
#             action.append(('quarantine', item))
#         for item in to_vaccinate:
#             action.append(('vaccinate', item))
#
#         return action
