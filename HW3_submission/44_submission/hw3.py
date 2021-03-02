import random
import itertools
ids = ['206354672', '318885001']


class Agent:
    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for row in state:
            for val in row:
                if val[0] == "S":
                    return False
        return True

    def get_rival_zoc(self, initial_state, my_zoc):
        rival_zoc = []
        for i, row in enumerate(initial_state):
            for j, col in enumerate(row):
                if (i, j) not in my_zoc and (i, j) not in rival_zoc:
                    rival_zoc.append((i, j))
        return list(set(rival_zoc))


    def init_num_turns(self, turn):
        if turn == "S":
            return ("S", 3)
        elif turn == "Q":
            return ("Q", 2)
        else:
            return (turn, 0)

    def tuple_row(self, row):
        return tuple(map(self.init_num_turns, row))

    def __init__(self, initial_state, zone_of_control, order):
        self.order = order
        if self.order == "first":
            self.max_player = True
        else:
            self.max_player = False
        self.medics = 1
        self.police = 2
        self.expand = 0
        self.healthy = set()
        self.sick = set()
        self.healthy_rival = set()
        self.sick_rival = set()
        self.max_depth = 3
        self.best_move = None
        init_tuple = []
        for row in initial_state:
            row = tuple(row)
            init_tuple.append(row)
        initial_state = init_tuple
       # print("1", initial_state)
        initial_state = tuple(map(self.tuple_row, initial_state))
        self.initial = initial_state
        #print("2", initial_state)
        self.zoc = zone_of_control
        self.rival_zoc = self.get_rival_zoc(initial_state, self.zoc)

    def quarantine_vaccinate(self):
        result = []
        if len(self.sick) != 0 and len(self.healthy) != 0:
            meds = set(itertools.combinations(self.healthy, self.medics))
           # police = set(itertools.combinations(sick_list, 0))
           # meds_and_police = set(itertools.product(meds, police))
            for val in meds:
                result.append((tuple(map(lambda me: ('vaccinate', me), val))))
        else:
            if (len(self.sick) == 0) and len(self.healthy) != 0:
                #police = set(itertools.combinations(' ', 0))
                meds = set(itertools.combinations(self.healthy, self.medics))
                #meds_and_police = set(itertools.product(meds, police))
                for val in meds:
                    result.append((tuple(map(lambda me: ('vaccinate', me), val))))
            elif (len(self.sick) != 0) and len(self.healthy) == 0:
               # meds = set(itertools.combinations(' ', 0))
                police = set(itertools.combinations(self.sick, self.police))
                #meds_and_police = set(itertools.product(meds, police))
                for val in police:
                    result.append((tuple(map(lambda po: ('quarantine', po), val))))
       # print("action", result)
        return result


    def actions(self, state):
        try:
            actions = self.quarantine_vaccinate()  # all_options
        except ValueError:
            actions = []
        return actions

    def rival_actions(self, state):
        self.healthy_rival = set()
        self.sick_rival = set()
        for (i, j) in self.rival_zoc:
            if 'H' in state[i][j]:
                self.healthy_rival.add((i, j))
            if 'S' in state[i][j]:
                self.sick_rival.add((i, j))
        try:
            actions = self.quarantine_vaccinate()  # all_options
        except ValueError:
            actions = []
        return actions



    def update_sick_to_quarantine(self, initial, index_row, index_col):
        len_row = len(initial) - 1
        len_col = len(initial[0]) - 1
        curr_row = initial[index_row]
        if (index_col == len_col) and (index_row == len_row):
            updated_val = curr_row[:index_col] + (("Q", 3),)
            updated_map = initial[:index_row] + (updated_val,)
        elif index_col == len_col:
            updated_val = curr_row[:index_col] + (("Q", 3),)
            updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
        elif index_row == len_row:
            updated_val = curr_row[:index_col] + (("Q", 3),) + curr_row[index_col + 1:]
            updated_map = initial[:index_row] + (updated_val,)
        else:
            updated_val = curr_row[:index_col] + (("Q", 3),) + curr_row[index_col + 1:]
            updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
        return updated_map

    def update_healthy_to_immune(self, initial, index_row, index_col):
        len_row = len(initial) - 1
        len_col = len(initial[0]) - 1
        curr_row = initial[index_row]
        if (index_col == len_col) and (index_row == len_row):
            updated_val = curr_row[:index_col] + (("I", 0),)
            updated_map = initial[:index_row] + (updated_val,)
        elif index_col == len_col:
            updated_val = curr_row[:index_col] + (("I", 0),)
            updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
        elif index_row == len_row:
            updated_val = curr_row[:index_col] + (("I", 0),) + curr_row[index_col + 1:]
            updated_map = initial[:index_row] + (updated_val,)
        else:
            updated_val = curr_row[:index_col] + (("I", 0),) + curr_row[index_col + 1:]
            updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
        return updated_map

    def update_healthy_to_sick(self, initial, index_row, index_col):
        len_row = len(initial) - 1
        len_col = len(initial[0]) - 1
        curr_row = initial[index_row]
        if (index_col == len_col) and (index_row == len_row):
            updated_val = curr_row[:index_col] + (("S", 4),)
            updated_map = initial[:index_row] + (updated_val,)
        elif index_col == len_col:
            updated_val = curr_row[:index_col] + (("S", 4),)
            updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
        elif index_row == len_row:
            updated_val = curr_row[:index_col] + (("S", 4),) + curr_row[index_col + 1:]
            updated_map = initial[:index_row] + (updated_val,)
        else:
            updated_val = curr_row[:index_col] + (("S", 4),) + curr_row[index_col + 1:]
            updated_map = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
        return updated_map

    def infection_spreads(self, curr_map):
        # print(curr_map)
        n = len(curr_map)  # cols
        m = len(curr_map[0])  # rows
        need_to_be_sick = []
        for ni in range(n):
            for nj in range(m):
                if curr_map[ni][nj][0] == "H":
                    # right
                    if nj + 1 < m:
                        if curr_map[ni][nj + 1][0] == "S":
                            # update the map - > to S
                            need_to_be_sick.append((ni, nj))
                    # left
                    if nj - 1 >= 0:
                        if curr_map[ni][nj - 1][0] == "S":
                            need_to_be_sick.append((ni, nj))

                    # down
                    if ni + 1 < n:
                        if curr_map[ni + 1][nj][0] == "S":
                            need_to_be_sick.append((ni, nj))

                    # up
                    if ni - 1 >= 0:
                        if curr_map[ni - 1][nj][0] == "S":
                            need_to_be_sick.append((ni, nj))

        for val in list(set(need_to_be_sick)):
            curr_map = self.update_healthy_to_sick(curr_map, val[0], val[1])
        return curr_map

    def quarantine_expires(self, initial):
        index_row = -1
        index_col = -1
        for row in initial:
            index_row += 1
            for val in row:
                index_col += 1
                if val[0] == "Q":
                    # print("in",initial[index_row])
                    if (val[1] > 1):
                        curr_row = initial[index_row]
                        # print("row",curr_row[:index_col])
                        updated_val = curr_row[:index_col] + ((val[0], (val[1] - 1)),) + curr_row[index_col + 1:]
                        # print("val",updated_val)
                        initial = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
                    else:
                        curr_row = initial[index_row]
                        # print("row",curr_row[:index_col])
                        updated_val = curr_row[:index_col] + (("H", (0)),) + curr_row[index_col + 1:]
                        # print("val",updated_val)
                        initial = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
            index_col = -1
        return initial

    def sickness_expires(self, initial):
        index_row = -1
        index_col = -1
        for row in initial:
            index_row += 1
            for val in row:
                index_col += 1
                if val[0] == "S":
                    # print("in",initial[index_row])
                    if (val[1] > 1):
                        curr_row = initial[index_row]
                        # print("row",curr_row[:index_col])
                        updated_val = curr_row[:index_col] + ((val[0], (val[1] - 1)),) + curr_row[index_col + 1:]
                        # print("val",updated_val)
                        initial = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
                    else:
                        curr_row = initial[index_row]
                        # print("row",curr_row[:index_col])
                        updated_val = curr_row[:index_col] + (("H", (0)),) + curr_row[index_col + 1:]
                        # print("val",updated_val)
                        initial = initial[:index_row] + (updated_val,) + initial[index_row + 1:]
            index_col = -1
        return initial

    def result(self, state, action, max_player):
        if max_player:
            for i in range(len(action)):
                action_i = action[i]
                if action_i[0] == 'quarantine':
                    # print("in", action_i)
                    state = self.update_sick_to_quarantine(state, action_i[1][0], action_i[1][1])
                    # print(state)
                elif action_i[0] == 'vaccinate':
                    state = self.update_healthy_to_immune(state, action_i[1][0], action_i[1][1])
        else:
            for i in range(len(action)):
                action_i = action[i]
                if action_i[0] == 'quarantine':
                    # print("in", action_i)
                    state = self.update_sick_to_quarantine(state, action_i[1][0], action_i[1][1])
                    # print(state)
                elif action_i[0] == 'vaccinate':
                    state = self.update_healthy_to_immune(state, action_i[1][0], action_i[1][1])
                state = self.infection_spreads(state)
                state = self.quarantine_expires(state)
                state = self.sickness_expires(state)
        return state

    def free_of_sick(self, state):
        for row in state:
            for col in row:
                if col[0] == "S":
                    return False, list(self.healthy)[0]
        return True, list(self.healthy)[0]

    def free_of_sick_rival(self, state):
        for row in state:
            for col in row:
                if col[0] == "S":
                    return False, list(self.healthy_rival)[0]
        return True, list(self.healthy_rival)[0]

    def evaluate(self, state, max_player):
        counter = 0
        if max_player:
            for row in state:
                for col in row:
                    if col[0] == "S":
                        counter -= 1
                    elif col[0] == "H" or col[0] == "I":
                        counter += 1
                    elif col[0] == "Q":
                        counter -= 5
        else:
            for row in state:
                for col in row:
                    if col[0] == "S":
                        counter += 1
                    elif col[0] == "H" or col[0] == "I":
                        counter -= 1
                    elif col[0] == "Q":
                        counter += 5
        return counter

    def count_sick_neighbors(self, curr_map, ni, nj):
        n = len(curr_map)  # cols
        m = len(curr_map[0])  # rows
        need_to_be_sick = []
        sick_counter = 0
        if nj + 1 < m:
            if curr_map[ni][nj + 1][0] == "S":
                # update the map - > to S
                sick_counter += 1
        # left
        if nj - 1 >= 0:
            if curr_map[ni][nj - 1][0] == "S":
                sick_counter += 1

        # down
        if ni + 1 < n:
            if curr_map[ni + 1][nj][0] == "S":
                sick_counter += 1

        # up
        if ni - 1 >= 0:
            if curr_map[ni - 1][nj][0] == "S":
                sick_counter += 1
        if sick_counter > 0:
            return 1
        else:
            return 0

    def count_healthy_neighbors(self, curr_map, ni, nj):
        n = len(curr_map)  # cols
        m = len(curr_map[0])  # rows
        need_to_be_sick = []
        sick_counter = 0
        if nj + 1 < m:
            if curr_map[ni][nj + 1][0] == "H":
                # update the map - > to S
                sick_counter += 1
        # left
        if nj - 1 >= 0:
            if curr_map[ni][nj - 1][0] == "H":
                sick_counter += 1

        # down
        if ni + 1 < n:
            if curr_map[ni + 1][nj][0] == "H":
                sick_counter += 1

        # up
        if ni - 1 >= 0:
            if curr_map[ni - 1][nj][0] == "H":
                sick_counter += 1
        return sick_counter

    def grade_action(self, state, actions):
        action_counter = 0
        for action in actions:
            action_loc = action[1]
            if action[0] == "vaccinate": #means location is healthy
                action_counter += self.count_sick_neighbors(state, action_loc[0], action_loc[1])
            if action[0] == "quarantine": #means location is sick
                action_counter += self.count_healthy_neighbors(state, action_loc[0], action_loc[1])
        return action_counter

    def sort_actions(self, state, all_actions):
        best_grade = float("-inf")
        best_action = []
        for action in all_actions:
            action_grade = self.grade_action(state, action)
            if action_grade > best_grade:
                best_grade = action_grade
                best_action.append(list((action, action_grade)))
        max_list = []
        max_grade = float("-inf")
        for best in best_action:
            if best[1] > max_grade:
                max_grade = best[1]
        for best in best_action:
            if best[1] == max_grade:
                max_list.append(best[0])
      # print("sorted actions", max_list)
        return list(set(max_list))

    def minimax_fixed(self, state, is_max=True, depth=0, alpha=float('-inf'), beta=float('inf')):
        score = self.evaluate(state, is_max)
        if depth == self.max_depth or abs(score) == float('inf') or self.goal_test(state):
            if len(self.healthy) > 0:
                self.best_move = (('vaccinate', list(self.healthy)[0]),)
            else:
                self.best_move = ((),)
            return score
        all_actions = self.actions(state)
        all_actions = self.sort_actions(state, all_actions)
        if not is_max:
            value = float('inf')
            for action in all_actions:
                prev_state = state
                self.initial = self.result(state, action, is_max)
                current_value = self.minimax_fixed(self.initial, True, depth + 1, alpha, beta)
                beta = min(beta, current_value)
                if current_value == value and depth == 0:
                    self.best_move = action
                if current_value < value:
                    value = current_value
                    beta = min(beta, value)
                    if depth == 0:
                        self.best_move = action
                self.initial = prev_state
                if alpha >= beta:
                    break
            return value

        else:
            value = float('-inf')
            for action in all_actions:
                #print(action)
                prev_state = state
                self.initial = self.result(state, action, is_max)
               # print("initial1max", action, self.initial)
                #curr_state = self.result(state, action, is_max)
                current_value = self.minimax_fixed(self.initial, False, depth + 1, alpha, beta)
                alpha = max(alpha, value)
                if current_value == value and depth == 0:
                    self.best_move = action
                if current_value > value:
                    value = current_value
                    alpha = max(alpha, value)
                    if depth == 0:
                        self.best_move = action
                self.initial = prev_state
                #print("initial2max", self.initial)
                if alpha >= beta:
                    break
            #print("&&", self.best_move)
            return value

    def best_my_move_max(self, state):
        self.minimax_fixed(state)
        #print("1", self.best_move)
        return self.best_move

    def best_my_move_min(self, state):
        self.minimax_fixed(state, False)
       # print("2", self.best_move)
        return self.best_move


    def get_best_move(self, state):
        if self.order == "second":
            move = self.best_my_move_min(state)
        else:
            move = self.best_my_move_max(state)
        return move

    def act(self, state):
        # actions = self.actions(state)
        # #print("ACTIONS", actions)
        # grade_all_possible_actions = []
        # max_grade = -10000000
        # max_option = []
        # for option in actions:
        #     grade_all_possible_actions.append((option, self.h(option)))
        # for grade in grade_all_possible_actions:
        #     if grade[1] > max_grade:
        #         max_grade = grade[1]
        #         max_option = grade[0]
        # max_option = list(max_option)
        self.healthy = set()
        self.sick = set()
        actions = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j][0]:
                self.healthy.add((i, j))
            if 'S' in state[i][j][0]:
                self.sick.add((i, j))
        init_tuple = []
        for row in state:
            row = tuple(row)
            init_tuple.append(row)
        state = init_tuple
        #print("1", state)
        initial_state = tuple(map(self.tuple_row, state))
       # print("healthy", self.healthy)
       # print("sick", self.sick)
        action = self.get_best_move(initial_state)
       # print("best move", self.best_move)
        return list(action)

