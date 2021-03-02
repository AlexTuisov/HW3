import random
import math
from itertools import chain, combinations

ids = ['205542764', '312273063']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.order = order
        self.rows = len(initial_state)
        self.cols = len(initial_state[0])
        self.agent_zoc = self.get_agent_zoc()
        self.last_state = [[0 for i in range(self.cols)] for j in range(self.rows)]
        self.penultimate_state = [[0 for i in range(self.cols)] for j in range(self.rows)]

    def get_agent_zoc(self):
        agent_zoc = []
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) not in self.zoc:
                    agent_zoc.append((i, j))
        return agent_zoc

    def act(self, state):
        our_state = self.personal_state(self.last_state, self.penultimate_state, state)
        self.penultimate_state = self.last_state
        self.last_state = state
        if self.order == "first":
            node = Node(None, None, our_state, self.zoc, self.agent_zoc, 0, False)
            self.max_value(node, -math.inf, math.inf, True, False)
        else:
            node = Node(None, None, our_state, self.zoc, self.agent_zoc, 0, True)
            self.min_value(node, -math.inf, math.inf, True, True)
        if node.selected_action is None:
            return self.random_vaccinate(state, self.zoc)
        return node.selected_action

    def personal_state(self, last, penultimate, state):
        our_state = [[(0, 0) for i in range(self.cols)] for j in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j] == 'S':
                    if last[i][j] == 'S' and penultimate[i][j] == 'S':
                        our_state[i][j] = (state[i][j], 1)
                    elif last[i][j] == 'S' and penultimate[i][j] != 'S':
                        our_state[i][j] = (state[i][j], 2)
                    elif last[i][j] != 'S' and penultimate[i][j] != 'S':
                        our_state[i][j] = (state[i][j], 3)
                elif state[i][j] == 'Q':
                    if last[i][j] == 'Q':
                        our_state[i][j] = (state[i][j], 1)
                    else:
                        our_state[i][j] = (state[i][j], 2)
                else:
                    our_state[i][j] = (state[i][j], 0)
        our_state = tuple(tuple(row) for row in our_state)
        return our_state

    def min_value(self, node, alpha, beta, our_move, change_state):
        if node.depth >= 4 or self.goal_test(node.state):
            return node.total_score
        val = math.inf
        for successor in node.expand(self, our_move, change_state):
            our_move = not our_move
            change_state = not change_state
            max_val = self.max_value(successor, alpha, beta, our_move, change_state)
            if val <= alpha:
                return val
            beta = min(beta, val)
            if max_val <= val:
                val = max_val
                node.selected_action = successor.creator
        return val

    def max_value(self, node, alpha, beta, our_move, change_state):
        if node.depth >= 4 or self.goal_test(node.state):
            return node.total_score
        val = -math.inf
        for successor in node.expand(self, our_move, change_state):
            our_move = not our_move
            change_state = not change_state
            min_val = self.min_value(successor, alpha, beta, our_move, change_state)
            if val >= beta:
                return val
            alpha = max(alpha, val)
            if min_val >= val:
                val = min_val
                node.selected_action = successor.creator
        return val

    def goal_test(self, state):
        win = True
        for i in range(self.rows):
            for j in range(self.cols):
                if state[i][j][0] == "S":
                    return False
        return win

    def actions(self, state, zone):
        possible_actions = []
        v_actions = []
        q_actions = []
        for (i, j) in zone:
            if state[i][j][0] == 'H':
                if self.amount_of_neighbors(state, i, j, zone, 'S') >= 1:
                    v_actions.append(("vaccinate", (i, j)))
            if state[i][j][0] == 'S':
                if self.amount_of_neighbors(state, i, j, zone, 'H') >= 3:
                    q_actions.append(("quarantine", (i, j)))
        if v_actions is [] and zone == self.agent_zoc:
            v_actions = self.random_vaccinate(state, zone)
        v_combs = list(chain.from_iterable(combinations(v_actions, r) for r in range(2)))[1:]
        q_combs = list(chain.from_iterable(combinations(q_actions, r) for r in range(3)))
        for i in range(len(v_combs)):
            for j in range(len(q_combs)):
                possible_actions.append(v_combs[i] + q_combs[j])
        return possible_actions

    def result(self, state, action, our_move):
        new_state = [list(row) for row in state]
        for act in action:
            if act[0] == "vaccinate":
                new_state[act[1][0]][act[1][1]] = ("I", 0)
            if act[0] == "quarantine":
                new_state[act[1][0]][act[1][1]] = ("Q", 3)
        if not our_move:
            for i in range(self.rows):
                for j in range(self.cols):
                    if new_state[i][j][0] == "H":
                        if self.check_s_neighbors(new_state, i, j):
                            new_state[i][j] = ("H", 4)
                    elif new_state[i][j][0] == "S":
                        new_state[i][j] = ("S", (new_state[i][j][1]) - 1)
                    elif new_state[i][j][0] == "Q":
                        new_state[i][j] = ("Q", (new_state[i][j][1]) - 1)
            for i in range(self.rows):
                for j in range(self.cols):
                    if (new_state[i][j][0] == "S" or new_state[i][j][0] == "Q") and (new_state[i][j][1] == 0):
                        new_state[i][j] = ("H", 0)
                    if new_state[i][j] == ("H", 4):
                        new_state[i][j] = ("S", 3)
        new_state = tuple(tuple(row) for row in new_state)
        return new_state

    def random_vaccinate(self, state, zone):
        action = []
        healthy = set()
        for (i, j) in zone:
            if 'H' in state[i][j]:
                healthy.add((i, j))
                if self.amount_of_neighbors(state, i, j, self.agent_zoc, 'S') >= 1:
                    healthy = set()
                    healthy.add((i, j))
                    break
        try:
            to_vaccinate = random.sample(healthy, 1)
        except ValueError:
            to_vaccinate = []
        if len(to_vaccinate) != 0:
            action.append(('vaccinate', to_vaccinate[0]))
        return action

    def amount_of_neighbors(self, state, row, col, zone, target):
        locations = [False] * 4
        sum_target = 0
        if row == 0:
            locations[0] = True
        if row == 9:
            locations[1] = True
        if col == 0:
            locations[2] = True
        if col == 9:
            locations[3] = True
        if not locations[0]:
            if state[row - 1][col][0] == target and (row - 1, col) in zone:
                sum_target += 1
        if not locations[1]:
            if state[row + 1][col][0] == target and (row + 1, col) in zone:
                sum_target += 1
        if not locations[2]:
            if state[row][col - 1][0] == target and (row, col - 1) in zone:
                sum_target += 1
        if not locations[3]:
            if state[row][col + 1][0] == target and (row, col + 1) in zone:
                sum_target += 1
        return sum_target

    def check_s_neighbors(self, state, row, col):
        locations = [False] * 4
        sick_neighbor = False
        if row == 0:
            locations[0] = True
        if row == self.rows - 1:
            locations[1] = True
        if col == 0:
            locations[2] = True
        if col == self.cols - 1:
            locations[3] = True
        if not locations[0]:
            if state[row - 1][col][0] == 'S':
                sick_neighbor = True
        if not locations[1]:
            if state[row + 1][col][0] == 'S':
                sick_neighbor = True
        if not locations[2]:
            if state[row][col - 1][0] == 'S':
                sick_neighbor = True
        if not locations[3]:
            if state[row][col + 1][0] == 'S':
                sick_neighbor = True
        return sick_neighbor


class Node:
    def __init__(self, parent, action, state, zoc, agent_zoc, total_score, change_state):
        self.parent = parent
        self.creator = action
        self.state = state
        self.zoc = zoc
        self.agent_zoc = agent_zoc
        self.rows = len(state)
        self.cols = len(state[0])
        self.total_score = total_score
        self.selected_action = None
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1
            self.total_score += parent.total_score
        if change_state:
            self.total_score += self.score(self.zoc) - self.score(self.agent_zoc)

    def score(self, zoc):
        score = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) in zoc:
                    if self.state[i][j][0] == "S":
                        score -= 1
                    elif self.state[i][j][0] == "Q":
                        score -= 5
                    elif self.state[i][j][0] == "H" or self.state[i][j][0] == "I":
                        score += 1
        return score

    def expand(self, our_agent, our_move, change_state):
        if our_move:
            current_zone = self.zoc
        else:
            current_zone = self.agent_zoc
        return [self.successor_node(our_agent, action, our_move, change_state)
                for action in our_agent.actions(self.state, current_zone)]

    def successor_node(self, our_agent, action, our_move, change_state):
        next_state = our_agent.result(self.state, action, our_move)
        new_node = Node(self, action, next_state, self.zoc, self.agent_zoc, self.total_score, change_state)
        return new_node
