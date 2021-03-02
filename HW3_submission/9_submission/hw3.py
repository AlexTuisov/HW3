import time
import random


ids = ['205889892', '205907132']

class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.adversary_zoc = self.get_adversary_zoc()
        self.initial_state = initial_state
        self.cur_state = self.make_map(initial_state)
        self.order = order
        self.max_depth = 5
        self.turn = 0
        self.cur_act = ""



    def get_adversary_zoc(self):
        adversary_zoc = []
        for i in range (10):
            for j in range (10):
                if (i,j) not in self.zoc:
                    adversary_zoc.append((i,j))
        return adversary_zoc

    def make_map(self, game_map):
        for i in range(10):
            for j in range(10):
                cur_tile = game_map[i][j]
                if cur_tile == "S":
                    game_map[i][j] = "S1"
        return tuple(tuple(i) for i in game_map)

    def is_terminated(self, state):
        s_count = 0
        for i in range(10):
            for j in range(10):
                cur_tile = state[i][j]
                if cur_tile == "S1" or cur_tile == "S2" or cur_tile == "S3":
                    s_count += 1
        if not s_count:
            return True
        else:
            return False

    def actions(self, state, zoc):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        healthy = {}
        sick = {}
        for (i, j) in zoc:
            if "H" in state[i][j]:
                healthy[(i, j)] = [0, 0]
            elif state[i][j] in ['S1', 'S2' ,'S3'] :
                sick[(i, j)] = [0, 0]

        #======s======
        for key in list(sick.keys()):
            h_nighbors = self.look_for_h_nighbors(key, state)
            if h_nighbors:
                score_self_H = 0
                score_adversary_H = 0
                for i in range(len(h_nighbors)):
                    if h_nighbors[i] in zoc:
                        score_self_H += 1
                    else:
                        score_adversary_H += 1
                sick[key] = [score_self_H, score_adversary_H]

        sorted_sick_dict = {k: v for k, v in sorted(sick.items(), key=lambda item: item[1][1], reverse=False)}
        sorted_sick_dict = {k: v for k, v in sorted(sorted_sick_dict.items(), key=lambda item: item[1][0], reverse=True)}

        sick_partial = []
        for key in sorted_sick_dict:
            # remove s tiles to quarantine i not surrounded by our H or surrounded by 4 adversary H.
            if (not sorted_sick_dict[key][1] == 4) and (not sorted_sick_dict[key][0] == 0) :
                sick_partial.append(key)


        #======H======
        for key in list(healthy.keys()):
            s_neighbors = self.look_for_s_nighbors(key, state)
            if s_neighbors:
                score_self_s = 0
                score_adversary_s = 0
                for i in range(len(s_neighbors)):
                    if s_neighbors[i] in zoc:
                        score_self_s += 1
                    else:
                        score_adversary_s += 1
                healthy[key] = [score_adversary_s, score_self_s]

        sorted_healthy_dict = {k: v for k, v in sorted(healthy.items(),key=lambda item: item[1][1], reverse=True)}
        sorted_healthy_dict = {k: v for k, v in sorted(sorted_healthy_dict.items(), key=lambda item: item[1][0], reverse=True)}

        healthy_partial = []
        for key in sorted_healthy_dict:

            if (not sorted_healthy_dict[key][1] == 0): #46%, diff = -8.|||| 1. 434 ||| 1 435
                healthy_partial.append(key)


        if len(healthy_partial) == 0:
            healthy_all = list(sorted_healthy_dict.keys())

        # ===== words addition ====
        policeAct = []
        for ids in sick_partial:
            policeAct.append(("quarantine", tuple(ids)))
        policeAct.append(())

        medicalAct = []
        if len(healthy_partial) == 0:
            for idh in healthy_all:
                medicalAct.append(("vaccinate", tuple(idh)))
        else:
            for idh in healthy_partial:
                medicalAct.append(("vaccinate", tuple(idh)))

        # ====== mix actions =======
        actions = []
        if len(policeAct)-1:
            for i in range(len(policeAct)-1):
                for j in range(i+1, len(policeAct)):
                    if medicalAct:
                        for k in medicalAct:
                            if policeAct[i][1] != () and policeAct[j] != ():
                                actions.append(tuple([(policeAct[i])] + [(policeAct[j])] + [(k)]))
                            elif policeAct[i] == () and policeAct[j] != ():
                                actions.append(tuple([(policeAct[j])] + [(k)]))
                            elif policeAct[i] != () and policeAct[j] == ():
                                actions.append(tuple([(policeAct[i])] + [(k)]))

        else:
            for k in medicalAct:
                actions.append(tuple([(k)]))

        actions = tuple(actions)
        return actions

    def active_result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        action = [action[i] for i in range(len(action))]
        new_state = [list(i) for i in state]
        if len(action) > 0:
            for single_action in action:
                if single_action == ():
                    continue
                idx = single_action[1][0]
                idy = single_action[1][1]
                if single_action[0] == "vaccinate":
                    new_state[idx][idy] = "I"
                elif single_action[0] == "quarantine":
                    new_state[idx][idy] = 'Q1'
        return new_state

    def check_neighbors(self, loc, state):
        # North, South, East, West
        neighbors = [-1, -1, -1, -1]
        if loc[0] > 0:
            neighbors[0] = state[loc[0] - 1][loc[1]]
        if loc[0] < (9):
            neighbors[1] = state[loc[0] + 1][loc[1]]
        if loc[1] > 0:
            neighbors[2] = state[loc[0]][loc[1] - 1]
        if loc[1] < (9):
            neighbors[3] = state[loc[0]][loc[1] + 1]
        return neighbors

    def board_dynamics(self, state):

        """ Find all S to be recovered and turn them into H
        Find all Q to be healthy and turn them into H
        Update the true value of remaining turns for Q, S """

        new_state = [list(i) for i in state]
        for i in range(10):
            for j in range(10):
                if state[i][j] == "H":
                    orientations = [i, j]
                    h_neighbors = self.check_neighbors(orientations, new_state)
                    if h_neighbors.count("S3") + h_neighbors.count("S2") + h_neighbors.count("S1") > 0:
                        state[i][j] = "S0"

        for i in range(10):
            for j in range(10):
                cur_tile = new_state[i][j]
                if cur_tile == "S3" or cur_tile == "Q2":
                    new_state[i][j] = "H"
                elif cur_tile == "S1":
                    new_state[i][j] = "S2"
                elif cur_tile == "S2":
                    new_state[i][j] = "S3"
                elif cur_tile == "Q1":
                    new_state[i][j] = "Q2"

        new_state = tuple(tuple(i) for i in new_state)
        return new_state

    def evaluation_function(self, state):
        our_score = 0
        for (i, j) in self.zoc:
            if 'H'== state[i][j]:
                our_score += 1
            if 'I' == state[i][j]:
                our_score += 1
            if state[i][j] in ['S1', 'S2', 'S3']:
                our_score -= 1
            if state[i][j] in ['Q1', 'Q2']:
                our_score -= 5

        adversary_score = 0
        for (i, j) in self.adversary_zoc:
            if 'H' == state[i][j]:
                adversary_score += 1
            if 'I' == state[i][j]:
                adversary_score += 1
            if state[i][j] in ['S1', 'S2', 'S3']:
                adversary_score -= 1
            if state[i][j] in ['Q1', 'Q2']:
                adversary_score -= 5

        return our_score - adversary_score

    def look_for_h_nighbors(self, loc, state):
        # Fill sick dictionary with values of # H neighbors in my zoc and # H neighbors in adversary zoc
        # North, South, East, West
        neighbors = []
        if loc[0] > 0 and state[loc[0] - 1][loc[1]] == 'H':
            neighbors.append((loc[0] - 1, loc[1]))
        if loc[0] < (9) and state[loc[0] + 1][loc[1]] == 'H':
            neighbors.append((loc[0] + 1, loc[1]))
        if loc[1] > 0 and state[loc[0]][loc[1] - 1] == 'H':
            neighbors.append((loc[0], loc[1] - 1))
        if loc[1] < (9) and state[loc[0]][loc[1] + 1] == 'H':
            neighbors.append((loc[0], loc[1] + 1))
        return neighbors

    def look_for_s_nighbors(self, loc, state):
        # North, South, East, West
        neighbors = []
        if loc[0] > 0 and state[loc[0] - 1][loc[1]] in ['S1', 'S2','S3'] :
            neighbors.append((loc[0] - 1, loc[1]))
        if loc[0] < 9 and state[loc[0] + 1][loc[1]] in ['S1', 'S2','S3']:
            neighbors.append((loc[0] + 1, loc[1]))
        if loc[1] > 0 and state[loc[0]][loc[1] - 1] in ['S1', 'S2','S3']:
            neighbors.append((loc[0], loc[1] - 1))
        if loc[1] < 9 and state[loc[0]][loc[1] + 1] in ['S1', 'S2','S3']:
            neighbors.append((loc[0], loc[1] + 1))
        return neighbors

    def infer_map(self, state):
        for i in range(9):
            for j in range(9):
                state_tile = state[i][j]
                cur_tile = self.cur_state[i][j]
                if state_tile == "S":
                    if cur_tile == "S1":
                        state[i][j] = "S2"
                    elif cur_tile == "S2":
                        state[i][j] = "S3"
                    # cur_tile - "H"
                    else:
                        state[i][j] = "S1"
                elif state_tile == "Q":
                    if cur_tile == "S1" or cur_tile == "S2" or cur_tile == "S3":
                        state[i][j] = "Q1"
                    elif cur_tile == "Q1":
                        state[i][j] = "Q2"
        self.cur_state = state

    def min_max_first(self):

        def max_value_first(state, cur_depth, alpha, beta):
            cur_depth += 1
            if self.is_terminated(state) or cur_depth == self.max_depth:
                return self.evaluation_function(state)
            actions = self.actions(self.cur_state, self.zoc)
            val = float('-inf')
            for act in actions:
                child_state = self.active_result(self.cur_state, act)
                val = min_value_first(child_state, cur_depth, alpha, beta)
                if val >= beta:
                    return val
                alpha = max(alpha, val)
            return val

        def min_value_first(state, cur_depth, alpha, beta):
            if self.is_terminated(state) or cur_depth == self.max_depth:
                return self.evaluation_function(state)
            actions = self.actions(self.cur_state, self.adversary_zoc)
            val = float('inf')
            for act in actions:
                child_state = self.board_dynamics(self.active_result(self.cur_state, act))
                val = max_value_first(child_state,cur_depth, alpha, beta)
                if val <= alpha:
                    return val
                beta = min(beta, val)
            return val

        actions = self.actions(self.cur_state, self.zoc)
        max_val = float('-inf')
        best_act = ""
        for act in actions:
            child_state = self.active_result(self.cur_state, act)
            val = min_value_first(child_state, 0, float('inf'), float('-inf'))
            if val > max_val:
                max_val = val
                best_act = act
        return best_act

    def min_max_second(self):
        def max_value_second(state, cur_depth, alpha, beta):
            if self.is_terminated(state) or cur_depth == self.max_depth:
                return self.evaluation_function(state)
            actions = self.actions(self.cur_state, self.zoc)
            val = float('-inf')
            for act in actions:
                child_state = self.board_dynamics(self.active_result(self.cur_state, act))
                val = min_value_second(child_state,cur_depth, alpha, beta)
                if val >= beta:
                    return val
                alpha = max(alpha, val)
            return val

        def min_value_second(state, cur_depth, alpha, beta):
            cur_depth += 1
            if self.is_terminated(state) or cur_depth == self.max_depth:
                return self.evaluation_function(state)
            actions = self.actions(self.cur_state, self.adversary_zoc)
            val = float('inf')
            for act in actions:
                child_state = self.active_result(self.cur_state, act)
                val = max_value_second(child_state,cur_depth, alpha, beta)
                if val <= alpha:
                    return val
                beta = min(beta, val)
            return val

        actions = self.actions(self.cur_state, self.zoc)
        max_val = float('-inf')
        best_act = ""
        for act in actions:
            child_state = self.board_dynamics(self.active_result(self.cur_state, act))
            val = min_value_second(child_state, 0, float('inf'), float('-inf'))
            if val > max_val:
                max_val = val
                best_act = act

        return best_act


    def act(self, state):
        if self.order == 'first':
            if self.turn:
                self.infer_map(state)
            self.cur_act = self.min_max_first()
            self.turn += 1
            if len(self.cur_act) == 0:
                self.cur_act = []
            return self.cur_act
        else:
            if self.turn:
                self.infer_map(state)
            self.cur_act = self.min_max_second()
            self.turn += 1
            return self.cur_act
