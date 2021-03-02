from itertools import chain, combinations
import random

ids = ['308387497', '311385041']
# define infinity
inf = float('inf')
n_inf = float("-inf")


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.order = order
        self.initial_state = initial_state
        self.zoc = zone_of_control
        self.m = len(initial_state)  # number of rows
        self.n = len(initial_state[0])  # number of columns
        self.rival_zoc = self.rivalZoc(self.zoc, initial_state, self.m,
                                       self.n)
        self.last_state = [[0 for i in range(self.n)] for j in range(self.m)]
        self.two_last_state = [[0 for i in range(self.n)] for j in range(self.m)]

    # convert the state to state of our form
    def convert_state(self, state, last, two_last):
        state = list(list(sub) for sub in state)
        for i in range(self.m):
            for j in range(self.n):
                x = state[i][j]
                y = last[i][j]
                z = two_last[i][j]
                if x == "S":
                    if y == "S" and z == "S":
                        state[i][j] = "S2"
                    elif y == "S" and z != "S":
                        state[i][j] = "S1"
                elif x == "Q":
                    if y != "Q":
                        state[i][j] = "Q1"
                    elif (y == "Q"):
                        state[i][j] = "Q2"
        # state = tuple(tuple(sub) for sub in state)
        return state

    def act(self, state):

        converted_state = self.convert_state(state, self.last_state,
                                             self.two_last_state)

        self.two_last_state = self.last_state
        self.last_state = state

        node = Node(converted_state, self.zoc, self.rival_zoc)

        # we are always the max player, when we  play first turn is 1 when we play second turn is 2
        if self.order == "first":
            self.max_value(node, 1, n_inf, inf,5)
        else:
            self.max_value(node, 2, n_inf, inf,5)

        if node.best_action == [()]: return ()
        return node.best_action

    # # minmax
    def min_value(self, node, turn, a, b, depth=4):
        if self.goal_test(node.state) or node.depth >= depth:
            return node.path_cost
        v = inf
        if turn == 1:
            turn = 2
        else:
            turn = 1
        for child in node.expand(self, turn):

            maxValue = self.max_value(child, turn, a, b, depth)
            if maxValue <= v:
                v = maxValue
                node.best_action = child.last_action
            if v <= a:  # alpha beta pruning
                return v
            b = min(b, v)

        return v

    def max_value(self, node, turn, a, b, depth=4):
        if self.goal_test(node.state) or node.depth >= depth:
            return node.path_cost
        v = n_inf
        if turn == 1:
            turn = 2
        else:
            turn = 1
        for child in node.expand(self, turn):

            minValue = self.min_value(child, turn, a, b, depth)
            if minValue >= v:
                v = minValue
                node.best_action = child.last_action
            if v >= b:
                return v
            a = max(a, v)

        return v

    # check if current state is goal
    def goal_test(self, state):

        for i in state:
            if "S" in i: return False
            if "S1" in i: return False
            if "S2" in i: return False
        return True

    # define the rival zone
    def rivalZoc(self, zoc, state, m, n):
        map_indices = [(i, j) for i in range(m) for j in range(n)]
        rival_zoc = []
        for x in map_indices:
            if x not in self.zoc:
                rival_zoc.append(x)
        return rival_zoc

    # find if the current H has S neighbors
    def s_neighbor(self, state, i, j):
        if i > 0 and "S" in state[i - 1][j]:
            return True
        if j > 0 and "S" in state[i][j - 1]:
            return True
        if i < self.m - 1 and "S" in state[i + 1][j]:
            return True
        if j < self.n - 1 and "S" in state[i][j + 1]:
            return True

    # find which H's are candidates to vaccinate
    def good_v(self, state, z):
        actions_v = []
        for (i, j) in z:
            if state[i][j] == "H":
                if self.s_neighbor(state, i, j):
                    actions_v.append(("vaccinate", (i, j)))
        return actions_v

    # find which S's are candidates to quarantine
    def good_q(self, state, z):
        actions_q = []
        for (i, j) in z:
            if "S" in state[i][j]:
                if self.h_neighbor(state, i, j, z):
                    actions_q.append(("quarantine", (i, j)))
        return actions_q

    # find if current S has 4 H neighbors
    def h_neighbor(self, state, i, j, z):
        counter = 0
        if i > 0 and (i - 1, j) in z and "H" in state[i - 1][j]:
            counter += 1
        if j > 0 and (i, j - 1) in z and "H" in state[i][j - 1]:
            counter += 1
        if i < self.m - 1 and (i + 1, j) in z and "H" in state[i + 1][j]:
            counter += 1
        if j < self.n - 1 and (i, j + 1) in z and "H" in state[i][j + 1]:
            counter += 1
        return counter >= 3

    # in case their are no good candidates to be vaccinate we will find a random H
    def find_random_h(self, state, z):
        for (i, j) in z:
            if state[i][j] == "H":
                return [("vaccinate", (i, j))]
        return []



    # return the possible actions according to the current state and heuristics
    def actions(self, state, z):
        actions = []
        actions_v = self.good_v(state, z)
        actions_q = self.good_q(state, z)
        if actions_v == []: actions_v = self.find_random_h(state, z)
        if actions_v == []: actions_v.append(())
        if actions_v == [] and actions_q == []:
            return [()]
        all_comb_v = list(chain.from_iterable(
            combinations(actions_v, r) for r in range(2)))[1:]
        all_comb_q = list(chain.from_iterable(
            combinations(actions_q, r) for r in range(3)))
        for i in range(len(all_comb_v)):
            for j in range(len(all_comb_q)):
                actions.append(all_comb_v[i] + all_comb_q[j])

        list_actions = [list(sub) for sub in actions]
        random.shuffle(list_actions)


        return list_actions

    # return a state according to the action and the current state, only in turn of second player
    # updating the dynamic actions
    def result(self, state, action, turn):
        s = [list(i) for i in state]

        self.update_by_actions(s, action)
        if turn == 2:
            self.update_by_former_state(state, s)
        return s#tuple(tuple(sub) for sub in s)

    # functions from previous HW
    def update_by_former_state(self, state, s):
        for i in range(self.m):
            for j in range(self.n):
                if state[i][j] == "Q1" or state[i][j] == "Q":
                    s[i][j] = "Q2"
                elif state[i][j] == "Q2":
                    s[i][j] = "H"
                elif ((state[i][j] == "S") or (state[i][j] == "S1") or (
                        state[i][j] == "S2")) and s[i][j] != "Q1":
                    self.H_neighbors(state, s, i, j)
                    if state[i][j] == "S":
                        s[i][j] = "S1"
                    elif state[i][j] == "S1":
                        s[i][j] = "S2"
                    elif state[i][j] == "S2":
                        s[i][j] = "H"

    def update_by_actions(self, s, action):

        # if action == (): return 0
        for a in action:
            if len(a) == 0: continue
            act = a[0]
            i = a[1][0]
            j = a[1][1]
            if act == "vaccinate":

                s[i][j] = "I"
            elif act == "quarantine":

                s[i][j] = "Q1"

    def H_neighbors(self, state, s, i, j):
        try:
            if state[i][j + 1] == "H" and s[i][j + 1] != "I":
                s[i][j + 1] = "S"
        except IndexError:
            pass
        try:
            if state[i][j - 1] == "H" and j > 0 and s[i][j - 1] != "I":
                s[i][j - 1] = "S"
        except IndexError:
            pass
        try:
            if state[i + 1][j] == "H" and s[i + 1][j] != "I":
                s[i + 1][j] = "S"
        except IndexError:
            pass
        try:
            if state[i - 1][j] == "H" and i > 0 and s[i - 1][j] != "I":
                s[i - 1][j] = "S"
        except IndexError:
            pass


class Node:

    def __init__(self, state, zoc, rival_zoc, parent=None, action=None, path_cost=0):
        self.m = len(state)
        self.n = len(state[0])
        self.zoc = zoc
        self.rival_zoc = rival_zoc
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost + self.score()
        self.depth = 0
        self.best_action = ()

        self.last_action = None
        if parent:
            self.depth = parent.depth + 1

    # find the score of a given state
    def score(self):
        return self.zoc_score(self.zoc) - self.zoc_score(self.rival_zoc)

    # find the score of given zone
    def zoc_score(self, zoc):
        s = 0
        for (i, j) in zoc:
            x = self.state[i][j]
            if "S" in x:
                s -= 1
            elif "Q" in x:
                s -= 5
            elif x == "H" or x == "I":
                s += 1

        return s

    def expand(self, agent, turn):

        if turn == 1 and agent.order == "second":
            z = self.zoc
        elif turn == 2 and agent.order == "first":
            z = self.zoc
        else:
            z = self.rival_zoc
        return [self.child_node(agent, action, turn)
                for action in agent.actions(self.state, z)]

    def child_node(self, agent, action, turn):

        next = agent.result(self.state, action, turn)
        node = Node(next, self.zoc, self.rival_zoc, self, action,
                    self.path_cost)
        node.last_action = action

        return node

    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))
