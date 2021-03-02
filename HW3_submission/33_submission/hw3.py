from copy import deepcopy
from itertools import combinations, product
from random import random


ids = ['211622352', '211451364']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zone = zone_of_control
        self.cur_state = initial_state
        self.order = order
        self.turn = 0
        for row in range(len(self.cur_state)):
            for index in range(len(self.cur_state[0])):
                if "S" in self.cur_state[row][index]:
                    self.cur_state[row][index] = "S2"
                if "Q" in self.cur_state[row][index]:
                    self.cur_state[row][index] = "Q1"

    def act(self, state):
        self.turn += 1
        if self.turn > 1:
            for row in range(len(state)):
                for index in range(len(state[0])):
                    if "Q" in state[row][index]:
                        if "Q" in self.cur_state[row][index]:
                            state[row][index] = "Q0"
                        else:
                            state[row][index] = "Q1"
                    if "S" in state[row][index]:
                        if "S" not in self.cur_state[row][index]:
                            state[row][index] = "S2"
                        else:
                            state[row][index] = "S" + str(int(self.cur_state[row][index][1])-1)
            self.cur_state = state

        dimensions = (len(self.cur_state), len(self.cur_state[0]))
        # healthy = []
        # sick = []
        # for (i, j) in self.zone:
        #     if 'H' in self.cur_state[i][j]:
        #         healthy.append([("vaccinate", (i, j))])
        #     if 'S' in self.cur_state[i][j]:
        #         sick.append(('quarantine', (i, j)))
        # must_vac = healthy

        # max_to_q = min(len(sick), 0)
        # must_q = sum([list(combinations(sick, num_q)) for num_q in range(max_to_q + 1)], [])
        # x = list(product(must_vac, must_q))
        x = self.get_all_possible_actions(self.cur_state)
        # for action in x:
        #     cur_action = []
        #     for act in action:
        #         act = list(act)
        #         cur_action.append(act)
        #     cur_action = sum(cur_action, [])
        #     act_state = self.apply_action(cur_action, deepcopy(self.cur_state))
        #     act_result = self.change_state(act_state, dimensions)
        #     cur_score = self.update_scores(act_result)
        #     if cur_score > best_score:
        #         best_score = cur_score
        #         best_action = cur_action
        # if self.turn < 3:
        #     _, best_action = self.minmax(x, dimensions, deepcopy(self.cur_state), depth=1)
        _, best_action = self.minmax(x, dimensions, deepcopy(self.cur_state), depth=2, max_depth=2)
        # _, best_action = self.minmax(x, dimensions, deepcopy(self.cur_state), depth=3)
        return best_action

    def get_all_possible_actions(self, state):
        healthy = []
        for (i, j) in self.zone:
            if 'H' in state[i][j]:
                neighbors = Agent.get_neighbors(state, i, j)
                flag = False
                for k, l in neighbors:
                    if "S" in state[k][l]:
                        healthy.append([("vaccinate", (i, j))])
                        flag = True
                        break
                if not flag:
                    x = random()
                    if x < 0.15:
                        healthy.append([("vaccinate", (i, j))])
            # if 'S' in state[i][j]:
            #     sick.append(('quarantine', (i, j)))
        must_vac = healthy

        # max_to_q = min(len(sick), 0)
        # must_q = sum([list(combinations(sick, num_q)) for num_q in range(max_to_q + 1)], [])
        # x = list(product(must_vac, must_q))
        x = [(i,) for i in must_vac]
        return x

    def minmax(self, x, dimensions, state, depth, max_depth):
        best_action = []
        best_score = float("-inf")
        for action in x:
            cur_action = []
            for act in action:
                act = list(act)
                cur_action.append(act)
            cur_action = sum(cur_action, [])
            act_state = self.apply_action(cur_action, deepcopy(state))
            act_result = self.change_state(act_state, dimensions)
            all_possible_actions = self.get_all_possible_actions(act_result)
            cur_score = self.update_scores(act_result)
            if depth != 0:
                s, _ = self.minmax(all_possible_actions, dimensions, act_state, depth-1, max_depth)
                cur_score += s
            # if depth != 0:
            #     s, _ = self.minmax(all_possible_actions, dimensions, act_state, depth - 1, max_depth=max_depth)
            #     cur_score += s
            if cur_score > best_score:
                best_score = cur_score
                best_action = cur_action
        return best_score, best_action
        pass

    @staticmethod
    def get_neighbors(state, i, j):
        bottom = len(state) - 1
        right = len(state[0]) - 1
        neighbors = []
        if i != 0:
            neighbors.append((i - 1, j))
        if i != bottom:
            neighbors.append((i + 1, j))
        if j != 0:
            neighbors.append((i, j - 1))
        if j != right:
            neighbors.append((i, j + 1))
        return neighbors

    @staticmethod
    def change_state(state, dimensions):
        new_state = deepcopy(state)

        # virus spread
        for i in range(0, dimensions[0]):
            for j in range(0, dimensions[1]):
                neighbors = Agent.get_neighbors(state, i, j)
                sick_neighbors = [1 for loc in neighbors if state[loc[0]][loc[1]] == "S"]
                if state[i][j] == 'H' and len(sick_neighbors) > 0:
                    new_state[i][j] = 'S2'

        # advancing sick counters
        for i in range(0, dimensions[0]):
            for j in range(0, dimensions[1]):
                if 'S' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn > 0:
                        new_state[i][j] = 'S' + str(turn - 1)
                    else:
                        new_state[i][j] = 'H'

                # advancing quarantine counters
                if 'Q' in state[i][j]:
                    turn = int(state[i][j][1])
                    if turn > 0:
                        new_state[i][j] = 'Q' + str(turn - 1)
                    else:
                        new_state[i][j] = 'H'

        return new_state

    @staticmethod
    def apply_action(actions, state):
        for atomic_action in actions:
            effect, i, j = atomic_action[0], atomic_action[1][0], atomic_action[1][1]
            if 'v' in effect:
                state[i][j] = 'I'
            else:
                state[i][j] = 'Q1'
        return state

    def update_scores(self, state):
        score = 0
        for (i, j) in self.zone:
            if 'H' in state[i][j]:
                shahid = 0
                ours = 0
                neighbors = Agent.get_neighbors(state, i, j)
                for k, l in neighbors:
                    if "H" in state[k][l]:
                        if (k, l) not in self.zone:
                            shahid += 1
                        else:
                            ours += 1
                if shahid - ours == 1:
                    score += 0.6
                elif shahid - ours >= 2:
                    score += 1
                score += 0.5
            if 'I' in state[i][j]:
                score += 1
            if 'S' in state[i][j]:
                maniak = 0
                ours = 0
                neighbors = Agent.get_neighbors(state, i, j)
                for k, l in neighbors:
                    if "H" in state[k][l]:
                        if (k, l) not in self.zone:
                            maniak += 1
                        else:
                            ours += 1
                if maniak - ours == 1:
                    score += 0.6
                elif maniak - ours >= 2:
                    score += 1
                else:
                    score -= 1
            if 'Q' in state[i][j]:
                score -= 5
        # for row in state:
        #     for item in row:
        #         if "S" in item:
        #             score -= 5
        return score