import random
from copy import deepcopy
import operator


ids = ['318483906', '316051903']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.state = initial_state
        self.order = order
        self.out_of_zone = self.outer_zone(self.zoc)

    def outer_zone(self, zoc):
        out_of_zone = []
        for i in range(0, 10):
            for j in range(0, 10):
                if (i, j) not in zoc:
                    out_of_zone.append((i, j))
        return out_of_zone

    def neighbor_h_in_zone(self, zoc, state, i, j):
        counter = 0
        if i + 1 <= 9:
            if (i + 1, j) in zoc:
                if state[i + 1][j] == 'H':
                    counter = counter + 1
        if i - 1 >= 0:
            if (i - 1, j) in zoc:
                if state[i - 1][j] == 'H':
                    counter = counter + 1
        if j + 1 <= 9:
            if (i, j + 1) in zoc:
                if state[i][j + 1] == 'H':
                    counter = counter + 1
        if j - 1 >= 0:
            if (i, j - 1) in zoc:
                if state[i][j - 1] == 'H':
                    counter = counter + 1
        return counter

    def neighbor_I_in_zone(self, zoc, state, i, j):
        counter = 0
        if i + 1 <= 9:
            if (i + 1, j) in zoc:
                if state[i + 1][j] == 'I':
                    counter = counter + 1
        if i - 1 >= 0:
            if (i - 1, j) in zoc:
                if state[i - 1][j] == 'I':
                    counter = counter + 1
        if j + 1 <= 9:
            if (i, j + 1) in zoc:
                if state[i][j + 1] == 'I':
                    counter = counter + 1
        if j - 1 >= 0:
            if (i, j - 1) in zoc:
                if state[i][j - 1] == 'I':
                    counter = counter + 1
        return counter

    def neighbor_S_in_zone(self, zoc, state, i, j):
        counter = 0
        if i + 1 <= 9:
            if (i + 1, j) in zoc:
                if state[i + 1][j] == 'S':
                    counter = counter + 1
        if i - 1 >= 0:
            if (i - 1, j) in zoc:
                if state[i - 1][j] == 'S':
                    counter = counter + 1
        if j + 1 <= 9:
            if (i, j + 1) in zoc:
                if state[i][j + 1] == 'S':
                    counter = counter + 1
        if j - 1 >= 0:
            if (i, j - 1) in zoc:
                if state[i][j - 1] == 'S':
                    counter = counter + 1
        return counter

    def neighbor_U_in_zone(self, zoc, state, i, j):
        counter = 0
        if i + 1 <= 9:
            if (i + 1, j) in zoc:
                if state[i + 1][j] == 'U':
                    counter = counter + 1
        if i - 1 >= 0:
            if (i - 1, j) in zoc:
                if state[i - 1][j] == 'U':
                    counter = counter + 1
        if j + 1 <= 9:
            if (i, j + 1) in zoc:
                if state[i][j + 1] == 'U':
                    counter = counter + 1
        if j - 1 >= 0:
            if (i, j - 1) in zoc:
                if state[i][j - 1] == 'U':
                    counter = counter + 1
        return counter

    def neighbor_h_out_of_zone(self, zoc, state, i, j):
        counter = 0
        if i + 1 <= 9:
            if (i + 1, j) not in zoc:
                if state[i + 1][j] == 'H':
                    counter = counter + 1
        if i - 1 >= 0:
            if (i - 1, j) not in zoc:
                if state[i - 1][j] == 'H':
                    counter = counter + 1
        if j + 1 <= 9:
            if (i, j + 1) not in zoc:
                if state[i][j + 1] == 'H':
                    counter = counter + 1
        if j - 1 >= 0:
            if (i, j - 1) not in zoc:
                if state[i][j - 1] == 'H':
                    counter = counter + 1
        return counter

    def S_weight(self, S):
        s_weight = {}
        zoc = self.zoc
        state =self.state
        for s in S:
            i = s[0]
            j = s[1]
            s_weight[s] = self.neighbor_h_in_zone(zoc, state, i, j) \
                          - self.neighbor_h_out_of_zone(zoc, state, i, j) \
                          - self.neighbor_I_in_zone(zoc, state, i, j) \
                          - self.neighbor_S_in_zone(zoc, state, i, j) \
                          - self.neighbor_U_in_zone(zoc, state, i, j)
        sorted_s = dict(sorted(s_weight.items(), key=operator.itemgetter(1), reverse=True))
        return sorted_s

    def H_weight(self, H):
        h_weight = {}
        zoc = self.zoc
        state = self.state
        for h in H:
            i = h[0]
            j = h[1]
            h_weight[h] = self.H_in_danger(i, j) + self.neighbor_h_in_zone(zoc, state, i, j) \
                          - self.neighbor_h_out_of_zone(zoc, state, i, j) \
                          - self.neighbor_I_in_zone(zoc, state, i, j) \
                          - self.neighbor_U_in_zone(zoc, state, i, j)
        sorted_h = dict(sorted(h_weight.items(), key=operator.itemgetter(1), reverse=True))
        return sorted_h

    def H_in_danger(self, i, j):
        flag = False
        if i + 1 <= 9:
            if self.state[i + 1][j] == 'S':
                flag = True
        if i - 1 >= 0:
            if self.state[i - 1][j] == 'S':
                flag = True
        if j + 1 <= 9:
            if self.state[i][j + 1] == 'S':
                flag = True
        if j - 1 >= 0:
            if self.state[i][j - 1] == 'S':
                flag = True
        return flag

    def act(self, state):
        zoc = self.zoc
        out_of_zone = self.out_of_zone
        action = self.minimax(state, 4, True, zoc, out_of_zone)[1]
        return action

    def moves(self, state):
        healthy = set()
        sick = set()
        h_IN_dang = set()
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.add((i, j))
            if 'S' in state[i][j]:
                sick.add((i, j))
        weighted_s = self.S_weight(sick)
        for h in healthy:
            if self.H_in_danger(h[0], h[1]):
                h_IN_dang.add(h)
        if len(h_IN_dang) == 0:
            weighted_h = self.H_weight(healthy)
        else:
            weighted_h = self.H_weight(h_IN_dang)
        i = 1
        flag1 = False
        flag2 = False
        for Q_act in weighted_s:
            if len(weighted_s) > 0:
                    if i == 1:
                        max_weight = weighted_s[Q_act]
                        x1, y1 = Q_act[0], Q_act[1]
                        i = i + 1
                        flag1 = True

            if len(weighted_s) > 1:
                    if i == 2:
                        if weighted_s[Q_act] > max_weight:
                            max2_weight = max_weight
                            x2, y2 = x1, y1
                            max_weight = weighted_s[Q_act]
                            x1, y1 = Q_act[0], Q_act[1]
                        else:
                            max2_weight = weighted_s[Q_act]
                            x2, y2 = Q_act[0], Q_act[1]
                        flag2 = True
                        i = i + 1

                    elif i > 2:
                        if weighted_s[Q_act] > max_weight:
                            max2_weight = max_weight
                            x2, y2 = x1, y1
                            max_weight = weighted_s[Q_act]
                            x1, y1 = Q_act[0], Q_act[1]
                        elif weighted_s[Q_act] > max2_weight:
                            max2_weight = weighted_s[Q_act]
                            x2, y2 = Q_act[0], Q_act[1]

        list_Q = []
        if flag2 == True:
            list_Q = list(( (x1,y1),(x2,y2)))
        elif flag1 == True:
            list_Q = list((x1, y1))

        i = 1
        flag3 = False
        for I_act in weighted_h:
                if len(weighted_h) > 0:
                        flag3 = True
                        if i == 1:
                            max_weight = weighted_h[I_act]
                            x, y = I_act[0], I_act[1]
                        else:
                            if weighted_h[I_act] > max_weight:
                                max_weight = weighted_h[I_act]
                                x, y = I_act[0], I_act[1]

        list_I = []
        if flag3 == True:
            list_I.append((x, y))
        all_moves1 = []
        all_moves2 = []
        all_1 = []
        all_4 = []
        all_5 = []
        all_7 = []

        if flag2 == True :
            if flag3 == True:
                all_1 = [(('quarantine', (x1, y1)), ('quarantine', (x2, y2)), ('vaccinate', (x, y)))]
                all_7 = [(('quarantine', (x2, y2)), ('vaccinate', (x, y)))]

            all_2 = [(('quarantine', (x1, y1)), ('quarantine', (x2, y2)))]
            all_3 = [(('quarantine', (x2, y2)),)]
            all_moves1 = all_1 + all_2 + all_3 + all_7

        if flag1 == True:
            if flag3 ==True:
                all_4 = [(('quarantine', (x1, y1)), ('vaccinate', (x, y)))]
                all_5 = [(('vaccinate', (x, y)),)]
            all_6 = [(('quarantine', (x1, y1)),)]
            all_moves2 = all_4 + all_5 + all_6

        no_combinations = tuple()
        all_moves = all_moves1 + all_moves2
        all_moves.append(no_combinations)
        return all_moves

    def game_over(self, state):
        flag = True
        for (i, j) in self.zoc:
            if state[i][j] == 'S':
                flag = False
        for (i, j) in self.out_of_zone:
            if state[i][j] == 'S':
                flag = False
        return flag

    def update_heristic_scores(self, state, player, control_zone):
        score = [0, 0]
        for (i, j) in control_zone:
            if 'H' in state[i][j]:
                score[player] += 2
            if 'I' in state[i][j]:
                score[player] += 5
            if 'S' in state[i][j]:
                score[player] -= -1
            if 'Q' in state[i][j]:
                score[player] += 3
        return score[player]

    def evaluate(self, state,max_player, zoc, out_of_zone):
        if max_player:
            eval = self.update_heristic_scores(state, 0, zoc) - self.update_heristic_scores(state, 1, out_of_zone)
        else:
            eval = self.update_heristic_scores(state, 1, zoc) - self.update_heristic_scores(state, 0, out_of_zone)
        return eval

    def apply_action(self, action, state):
        new_state = deepcopy(state)
        for act in action:
            if act == ():
                return new_state
            x = act[1][0]
            y = act[1][1]
            if act[0] == 'vaccinate':
                new_state[x][y] = "I"
            elif act[0] == 'quarantine':
                new_state[x][y] = "Q"
        return new_state

    def minimax(self, state, depth, max_player, zoc, out_of_zone):
        if depth == 0 or self.game_over(state):
            return self.evaluate(state, max_player, zoc, out_of_zone), None
        actions = self.moves(state)
        if max_player:
            maxEval = float('-inf')
            best_action = None
            for act in actions:
                new_state = self.apply_action(act, state)
                evaluation = self.minimax(new_state, depth - 1, False, out_of_zone, zoc)[0]
                maxEval = max(maxEval, evaluation)
                if maxEval == evaluation:
                    best_action = act
            return maxEval, best_action
        else:
            minEval = float('inf')
            best_action = None
            for act in actions:
                new_state = self.apply_action(act, state)
                evaluation = self.minimax(new_state, depth - 1, True, zoc, out_of_zone)[0]
                minEval = min(minEval, evaluation)
                if minEval == evaluation:
                    best_action = act
            return minEval, best_action