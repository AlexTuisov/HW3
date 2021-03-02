import random
from itertools import combinations

ids = ['312320468', '316552710']

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zone = zone_of_control
        self.first_time_in = True
        self.state = initial_state
        temp = []
        for row in self.state:
            row_temp = []
            for col in row:
                row_temp.append([col, 0])
            temp.append(row_temp)
        self.cur_state = temp

        self.order = order
        self.other_zone = []
        for i in range(len(initial_state)):
            for j in range(len(initial_state[0])):
                if (i, j) not in zone_of_control:
                    self.other_zone.append((i, j))

    def add_day(self, state):
        for i in range(len(self.cur_state)):
            for j in range(len(self.cur_state[0])):
                if self.cur_state[i][j][0] == state[i][j]:
                    self.cur_state[i][j][1] += 1
                else:
                    self.cur_state[i][j][0] = state[i][j]
                    self.cur_state[i][j][1] = 0

    def act(self, state):
        #update cur_state if needed:
        if not self.first_time_in:
            self.add_day(state)
        else:
            self.first_time_in = False

        #find my relevant actions:
        i_healthy = set()
        i_sick = set()
        for (i, j) in self.zone:
            if 'H' in state[i][j]:
                #i_healthy.add((i, j))
                i_healthy.add(("vaccinate", (i, j)))
            if 'S' in state[i][j]:
                #i_sick.add((i, j)) quarantine
                i_sick.add(("quarantine", (i, j)))

        actions = self.find_actions(True, i_healthy, i_sick)
        w_actions = self.weight_actions(actions, state, self.zone)
        #find all min
        relevant_actions = w_actions[:10]

        #minmax
        max_val = -1000
        max_action = []

        if self.order == 'first':
            for i_action in relevant_actions: #has 10 actions
                # check other's actions
                o_healthy = set()
                o_sick = set()
                for (i, j) in self.other_zone:
                    if 'H' in self.cur_state[i][j]:
                        o_healthy.add(("vaccinate", (i, j)))
                    if 'S' in self.cur_state[i][j]:
                        o_sick.add(("quarantine", (i, j)))

                o_actions = self.find_actions(False, o_healthy, o_sick)
                temp_score_count = 0
                for o_action in o_actions:
                    # temp_score, _ = self.check_board(new_map, o_action)
                    temp_map = self.result(self.cur_state, o_action+i_action)
                    temp_score_o = self.update_scores(temp_map) #changed from other_zone
                    if temp_score_o < temp_score_count:
                        temp_score_count = temp_score_o
                if temp_score_count > max_val:
                    max_val = temp_score_count
                    max_action = i_action

        else: #I am second

            for i_action in relevant_actions:
                #temp_score, new_map = self.check_board(state, i_action) #לסדר את הפונ
                new_map = self.result(self.cur_state, i_action)
                #check other zone after my action
                o_healthy = set()
                o_sick = set()
                for (i, j) in self.other_zone:
                    if 'H' in new_map[i][j]:
                        o_healthy.add(("vaccinate", (i, j)))
                    if 'S' in new_map[i][j]:
                        o_sick.add(("quarantine", (i, j)))

                o_actions = self.find_actions(False, o_healthy, o_sick)
                temp_score_count = 0
                i_healthy_2 = set()
                i_sick_2 = set()
                for (i, j) in self.zone:
                    if 'H' in new_map[i][j]:
                        # i_healthy.add((i, j))
                        i_healthy_2.add(("vaccinate", (i, j)))
                    if 'S' in new_map[i][j]:
                        # i_sick.add((i, j)) quarantine
                        i_sick_2.add(("quarantine", (i, j)))
                i_actions_2 = self.find_actions(True, i_healthy_2, i_sick_2)
                i_actions_2 = self.weight_actions(i_actions_2, new_map, self.zone)[:10]
                for o_action in o_actions:
                    for i_action_2 in i_actions_2:
                        temp_map_2 = self.result(new_map, o_action+i_action_2)
                        temp_score_o = self.update_scores(temp_map_2)
                        if temp_score_o < temp_score_count:
                            temp_score_count = temp_score_o
                if temp_score_count > max_val:
                    max_val = temp_score_count
                    max_action = i_action
        return max_action

    def find_actions(self, me, list_of_h, list_of_s):
        power_h = list(combinations(list_of_h, 1))
        power_s = list(combinations(list_of_s, 2))
        power_best_s = []
        if me:
            best_s = []
            for s in list_of_s:
                if self.check_if_my_s_has_4_my_h(s, self.cur_state, self.zone):
                    best_s.append(s)
            power_best_s = list(combinations(best_s, 2))

        power_new = []

        #if power_h and power_s:
        #    for action_h in power_h:
        #        for action_s in power_s:
        #            power_new.append(action_h + action_s)
        if me and power_best_s:
            power_new += power_best_s
        if power_h:
            power_new += power_h
        if not power_best_s and not power_h and power_s:
            power_new += power_s
        if not power_new:
            power_new.append(())
        return power_new

    def check_s_neig(self, location, state, ri_zone):
        i, j = location[1]
        count_s_w =0
        if (i + 1 < len(state)) and ((i + 1, j) in ri_zone) and state[i + 1][j][0] == "H":
            count_s_w += 1
        if (i - 1 > 0) and ((i - 1, j) in ri_zone) and state[i - 1][j][0] == "H":
            count_s_w += 1
        if (j + 1 < len(state[0])) and ((i, j + 1) in ri_zone) and state[i][j + 1][0] == "H":
            count_s_w += 1
        if (j - 1 > 0) and ((i, j - 1) in ri_zone) and state[i][j - 1][0] == "H":
            count_s_w += 1
        return count_s_w

    def check_if_my_s_has_4_my_h(self, location, state, my_zone):
        i, j = location[1]
        count_s_h = 0
        if (i + 1 < len(state)) and ((i + 1, j) in my_zone) and state[i + 1][j][0] == "H":
            count_s_h += 1
        if (i - 1 > 0) and ((i - 1, j) in my_zone) and state[i - 1][j][0] == "H":
            count_s_h += 1
        if (j + 1 < len(state[0])) and ((i, j + 1) in my_zone) and state[i][j + 1][0] == "H":
            count_s_h += 1
        if (j - 1 > 0) and ((i, j - 1) in my_zone) and state[i][j - 1][0] == "H":
            count_s_h += 1
        if count_s_h == 4:
            return True
        return False

    def check_h_neig(self, location, state, ri_zone):
        i, j = location[1]
        count_h_w = 0
        if (i + 1 < len(state)) and ((i + 1, j) in ri_zone) and state[i + 1][j] == "S":
            count_h_w += 1
        elif (i - 1 > 0) and ((i - 1, j) in ri_zone) and state[i - 1][j] == "S":
            count_h_w += 1
        elif (j + 1 < len(state[0])) and ((i, j + 1) in ri_zone) and state[i][j + 1] == "S":
            count_h_w += 1
        elif (j - 1 > 0) and ((i, j - 1) in ri_zone) and state[i][j - 1] == "S":
            count_h_w += 1
        return count_h_w

    def weight_actions(self, actions, state, ri_zone):
        # if has H nei in rival zone
        # if my H is close to S rival
        weights = []
        #for i in range(len(state)):
         #   for j in range(len(state[i])):
        for act in actions:
            count = 0
            for a in act:
                i, j = a[1]
                if state[i][j] == "S":
                    count += self.check_s_neig(a, state, ri_zone)
                if state[i][j] == "H":
                    count += 1
                    count += self.check_h_neig(a, state, ri_zone)
            weights.append(count)
        weights_actions = list(zip(weights, actions))
        sorted_w_a = sorted(weights_actions, reverse=True)
        weights, w_actions = zip(*sorted_w_a)


        #w_actions = sorted(w_actions)
        #w_scores, w_actions = zip(*w_actions)
        return w_actions

    def update_scores(self, state):
        score = 0
        for (i, j) in self.zone:
            if 'H' in state[i][j]:
                score += 1
            if 'I' in state[i][j]:
                score += 1
            if 'S' in state[i][j]:
                score -= 1
            if 'Q' in state[i][j]:
                score -= 5
        return score

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        cur_action = action

        cur_state = []
        for line in state:
            cur_state.append(list(line))

        for i, row in enumerate(cur_state):
            for j, col in enumerate(row):

                if col[0] == "U" or col[0] == "I":
                    continue

                # actions
                if (i, j) in cur_action:
                    if col[0] == "S":
                        cur_state[i][j] = ["Q", 0]  ##########check days
                    elif col[0] == "H":
                        cur_state[i][j] = ["I", 0]

                else:
                    # check neighbors
                    if col[0] == "H":
                        if (i + 1 < len(cur_state)) and state[i + 1][j][0] == "S" and ((i + 1, j) not in cur_action):
                            cur_state[i][j] = ["S", 0]
                        elif (i - 1 > 0) and state[i - 1][j][0] == "S":
                            cur_state[i][j] = ["S", 0]
                        elif (j + 1 < len(state[0])) and state[i][j + 1][0] == "S" and ((i, j + 1) not in cur_action):
                            cur_state[i][j] = ["S", 0]
                        elif (j - 1 > 0) and state[i][j - 1][0] == "S":
                            cur_state[i][j] = ["S", 0]

                    ###check days
                    elif col[0] == "Q":
                        if col[1] >= 1:
                            cur_state[i][j] = ["H", 0]
                        # elif col[1] == 1:
                        # cur_state[i][j] = ("Q", 2)
                        elif col[1] == 0:
                            cur_state[i][j] = ["Q", 1]
                    elif col[0] == "S":
                        if col[1] >= 2:
                            cur_state[i][j] = ["H", 0]
                        elif col[1] == 0:
                            cur_state[i][j] = ["S", 1]
                        elif col[1] == 1:
                            cur_state[i][j] = ["S", 2]
                        # elif col[1] == 2:
                        #   cur_state[i][j] = ("S", 3)
        final_state = []
        for line in cur_state:
            final_state.append(line)

        return final_state

    def minimax(self, maximizing, minimizing, i_act, o_act, state):
        for action in i_act:
            i_result = self.che
        """
        function minimax(node, depth, maximizingPlayer) is
            if depth = 0 or node is a terminal node then
                return the heuristic value of node
            if maximizingPlayer then
                value := −∞
                for each child of node do
                    value := max(value, minimax(child, depth − 1, FALSE))
                return value
            else (* minimizing player *)
                value := +∞
                for each child of node do
                    value := min(value, minimax(child, depth − 1, TRUE))
                return value
        """
        pass


    def check_board(self, zone, action):
        score = 0
        new_map = self.state
        for (i, j) in zone:
            if (i, j) in action:
                if zone(i, j) == 'H':
                    new_map[i][j] = 'I'
                    continue
                elif self.state[(i, j)] == 'S':
                    score -= 5
                    new_map[i][j] = 'Q'
                    continue
            elif 'H' in self.state[(i, j)]:
                score += 1
            elif 'I' in self.state[(i, j)]:
                score += 1
            elif 'S' in self.state[(i, j)]:
                score -= 1
            elif 'Q' in self.state[(i, j)]:
                score -= 5
        return score, new_map

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
