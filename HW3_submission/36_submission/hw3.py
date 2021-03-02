import random
# import math
from itertools import chain, combinations
from copy import deepcopy

ids = ['205737372', '308513704']


class Node:

    def __init__(self, state, zoc, rival_zoc, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.zoc = zoc
        self.action = action
        self.col = len(state[0])
        self.row = len(state[:])
        self.path_cost = path_cost + self.get_rate()
        self.best_action = None
        self.depth = 0
        self.rival_zoc = rival_zoc

        if parent:
            self.depth = parent.depth + 1

    def get_rate(self):
        my_score = 0
        rival_score = 0
        for i in range(self.row):
            for j in range(self.col):
                if 'H' in self.state[i][j] or 'I' in self.state[i][j]:
                    if (i, j) in self.zoc:
                        my_score += 1
                    else:
                        rival_score += 1
                    if 'S' in self.state[i][j]:
                        if (i, j) in self.zoc:
                            my_score -= 1
                        else:
                            rival_score -= 1
                    if 'Q' in self.state[i][j]:
                        if (i, j) in self.zoc:
                            my_score -= 5
                        else:
                            rival_score -= 5
        return my_score - rival_score

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, agent,
               max_turn):  # לבדוק איזה תור אנחנו ונמזמת ACTION ומעדכנת את הZOC שרוצים לעבור עליו (ואז לא SELF)
        # פה צריך לחשוב איך לתקן את התנאים של מי מהם זה התורה עכשיו, כי כל פעם מזמזנים עם מישה שזה התור שלו את ACTIONS כדי למצוא מה הפעולות האפשריות באיזור שלו

        if max_turn:
            actions_list = agent.actions(self.state, self.zoc)
        else:
            actions_list = agent.actions(self.state, self.rival_zoc)
        return [self.child_node(agent, action, max_turn) for action in actions_list]

    def child_node(self, Agent, action, max_turn):

        next = Agent.result(self.state, action, max_turn)
        return Node(next, self.zoc, self.rival_zoc, self, [action], self.path_cost)

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.col = len(initial_state[0])
        self.row = len(initial_state[:])
        self.order = order
        self.initial_state = initial_state
        rival_zoc = []
        for i in range(self.row):  # איך מאחדים לפי כמה משטרה ורםואה יש
            for j in range(self.col):
                if (i, j) not in zone_of_control:
                    rival_zoc.append((i, j))
        self.rival_zoc = rival_zoc
        state = list(list(sub) for sub in initial_state)
        self.prior_state = [[0 for i in range(10)] for j in range(10)]
        self.prior_prior_state = [[0 for i in range(10)] for j in range(10)]

        for i in range(self.row):  # making board with S1 Q1....
            for j in range(self.col):
                if initial_state[i][j] == "S":
                    state[i][j] = "S1"
                elif initial_state[i][j] == "Q":
                    state[i][j] = "Q1"
        state = tuple(tuple(sub) for sub in state)
        self.initial_state = state

    def fix_board(self, state, prior_state, prior_prior_state):
        for i in range(self.row):
            for j in range(self.col):
                if state[i][j] == 'Q':
                    if prior_state[i][j] == 'Q':
                        state[i][j] = 'Q2'
                    else:
                        state[i][j] = 'Q1'
                if state[i][j] == 'S':
                    if prior_state[i][j] == 'S':
                        if prior_prior_state[i][j] == 'S':
                            state[i][j] = 'S3'
                        else:
                            state[i][j] = 'S2'
                    else:
                        state[i][j] = 'S1'
        return state

    def act(self, state):
        # making board with S1 Q1....
        new_state = list(list(sub) for sub in state)
        state = self.fix_board(new_state, self.prior_state, self.prior_prior_state)
        self.prior_prior_state = self.prior_state
        self.prior_state = new_state

        node = Node(state, self.zoc, self.rival_zoc)
        # אם אני שחקן ראשון מתחיל במקס ואם לא מתחיל במינ!
        MaxTurn = True
        if self.order == 'first':
            self.max_value(node, MaxTurn, -10 ** (10), 10 ** (10))
        else:
            self.min_value(node, MaxTurn, -10 ** (10), 10 ** (10))
        best_act = []
        if node.best_action is None:
            for (i, j) in self.zoc:
                if node.state[i][j] == 'H' and i > 0 and j > 0 and i < self.row - 1 and j < self.col - 1:
                    best_act = [("vaccinate", (i, j))]
                    if best_act:
                        return best_act
            if best_act == []:
                for (i, j) in self.zoc:
                    if node.state[i][j] == 'H' and (i == 0 or j == 0 or i == self.row - 1 or j == self.col - 1):
                        best_act = [("vaccinate", (i, j))]
                        if best_act != []:
                            return best_act
            # if best_act == []:
            #     for (i, j) in self.zoc:
            #         if "S" in node.state[i][j] and (i == 0 or j == 0 or i == self.row - 1 or j == self.col - 1):
            #             best_act = [("quarantine", (i, j))]
            #         if best_act != [] :
            #             return best_act
            if best_act == [] :
                return []
        return node.best_action


    def goal_test(self, state):
        for i in state:
            for j in i:
                if 'S' in j:
                    return False
        return True

    def min_value(self, my_node, MaxTurn, alpha, beta):
        # base case : targetDepth reached
        if my_node.depth == 4 or self.goal_test(my_node.state):  # or #goal
            return my_node.path_cost
        val = 100000000000
        for child in my_node.expand(self, MaxTurn):
            MaxTurn = not MaxTurn
            max_val = self.max_value(child, MaxTurn, alpha, beta)
            if val < alpha:
                return val
            beta = min(val, beta)
            if max_val <= val:
                val = max_val
                my_node.best_action = child.action

        return val

    # אם אני שחקן ראשון מתחיל במקס ואם לא מתחיל במינ!

    def max_value(self, my_node, MaxTurn, alpha, beta):
        # base case : targetDepth reached
        if my_node.depth == 4 or self.goal_test(my_node.state):  # or #goal
            return my_node.path_cost
        val = -100000000000
        for child in my_node.expand(self, MaxTurn):
            MaxTurn = not MaxTurn
            min_val = self.min_value(child, MaxTurn, alpha, beta)
            # print("best max",my_node.best_action)
            if val > beta:
                return val
            alpha = max(val, alpha)
            if min_val >= val:
                val = min_val
                my_node.best_action = child.action

        return val

    def spread_right(self, state, i, j):
        if j == self.col - 1:
            return state
        if state[i][j + 1] == "H":
            state[i][j + 1] = "S"
        return state

    def spread_left(self, state, i, j):
        if j == 0:
            return state
        if state[i][j - 1] == "H":
            state[i][j - 1] = "S"
        return state

    def spread_up(self, state, i, j):
        if i == 0:
            return state
        if state[i - 1][j] == "H":
            state[i - 1][j] = "S"
        return state

    def spread_down(self, state, i, j):
        if i == self.row - 1:
            return state
        if state[i + 1][j] == "H":
            state[i + 1][j] = "S"

        return state

    def spreading(self, boardy):  # spreading S to all sides
        for i in range(self.row):
            for j in range(self.col):
                if 'S' in boardy[i][j]:
                    boardy = self.spread_right(boardy, i, j)
                    boardy = self.spread_left(boardy, i, j)
                    boardy = self.spread_up(boardy, i, j)
                    boardy = self.spread_down(boardy, i, j)

        return boardy

    def healed_or_free(self, boardy):  # updating the S and Q to H (days=0)
        # count the days up and release sick or quarantine, explain the tricl with S and S1
        for i in range(self.row):
            for j in range(self.col):
                if boardy[i][j] == 'S':
                    boardy[i][j] = 'S1'
                elif boardy[i][j] == 'S1':
                    boardy[i][j] = 'S2'
                elif boardy[i][j] == 'S2':
                    boardy[i][j] = 'S3'
                elif boardy[i][j] == 'S3':
                    boardy[i][j] = 'H'
                elif boardy[i][j] == 'Q':
                    boardy[i][j] = 'Q1'
                elif boardy[i][j] == 'Q1':
                    boardy[i][j] = 'Q2'
                elif boardy[i][j] == 'Q2':
                    boardy[i][j] = 'H'

        return boardy

    def result(self, state, action, MaxTurn):
        state = [list(i) for i in state]
        actions = []
        if type(action) == tuple:
            actions.append(action)
            action = actions
        for i in range(len(action)):  # updeting the incoming action

            row_to_change = action[i][1][0]
            col_to_change = action[i][1][1]
            if action[i][0] == "vaccinate":
                state[row_to_change][col_to_change] = 'I'
            if action[i][0] == "quarantine":
                state[row_to_change][col_to_change] = 'Q'

        if (MaxTurn and self.order == "first") or (not MaxTurn and self.order != "first"):
            state = tuple(tuple(sub) for sub in state)
            return state
        else:
            state = self.spreading(state)
            state = self.healed_or_free(state)
            state = tuple(tuple(sub) for sub in state)
            return state

    def neighbors(self, state, i, j, zoc, sign):
        amount = 0
        # to check how many h neigbors the s has, if 4 append to vac. else- no
        if sign == 'S':
            if i >= 1:
                if (i - 1, j) in zoc and state[i - 1][j] == 'H':
                    amount += 1
            if j >= 1:
                if (i, j - 1) in zoc and state[i][j - 1] == 'H':
                    amount += 1
            if i < self.row - 1:
                if (i + 1, j) in zoc and state[i + 1][j] == 'H':
                    amount += 1
            if j < self.col - 1:
                if (i, j + 1) in zoc and state[i][j + 1] == 'H':
                    amount += 1
            if amount == 4:
                return True
            else:
                return False
        if sign == 'H':
            if i >= 1:
                if 'S' in state[i - 1][j]:
                    return True
            if j >= 1:
                if 'S' in state[i][j - 1]:
                    return True
            if i < self.row - 1:
                if 'S' in state[i + 1][j]:
                    return True
            if j < self.col - 1:
                if 'S' in state[i][j + 1]:
                    return True

            return False

    def actions(self, states, zoc):
        # states = [list(i) for i in state]#
        action_vac = []
        action_qur = []
        s_amount, h_amount = 0, 0
        police = 2
        medical = 1
        best_act = []
        for i in range(self.row):
            for j in range(self.col):
                if 'S' in states[i][j] and (i, j) in zoc:
                    if self.neighbors(states, i, j, zoc,
                                      'S'):  # if there are 4 h negibors than we all to list of quarentine
                        action_qur.append(("quarantine", (i, j)))
                        s_amount += 1
                elif states[i][j] == "H" and (i, j) in zoc:
                    if self.neighbors(states, i, j, zoc,
                                      'H'):  # if there are 4 h negibors than we all to list of quarentine
                        action_vac.append(("vaccinate", (i, j)))
                        h_amount += 1

        if len(action_vac) == 0:
            for (i, j) in zoc:
                if states[i][j] == 'H':  # and i>0 and j>0 and i < self.row-1 and j<self.col-1 :
                    best_act = [("vaccinate", (i, j))]
                    if len(action_qur) == 0:
                        return best_act
                    else:
                        action_vac = best_act
        if s_amount <= police:
            all_comb_qur = list(
                chain.from_iterable(combinations(action_qur, s_amount)))
        else:
            all_comb_qur = list(chain.from_iterable(combinations(action_qur, police)))
        if h_amount <= medical:
            all_comb_vac = list(chain.from_iterable(combinations(action_vac, h_amount)))
        else:
            all_comb_vac = list(chain.from_iterable(combinations(action_vac, medical)))
        if len(all_comb_vac) == 0 and len(all_comb_qur) == 0: return []
        if len(all_comb_vac) == 0 and len(all_comb_qur) != 0: return all_comb_qur
        if len(all_comb_vac) != 0 and len(all_comb_qur) == 0: return all_comb_vac
        all_mixed_comb = []
        for i in all_comb_vac:
            for j in all_comb_qur:
                all_mixed_comb.append(i + j)
        return all_mixed_comb

# ------------------------- לא צריך את כל הפעולות ששלוחים. לעשות סינון לH
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
