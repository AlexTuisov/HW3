import random
from copy import deepcopy
from math import inf
import itertools
import time

ids = ['322212630', '322721283']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.police = 0
        self.medics = 1
        self.depth = 4
        self.zoc = zone_of_control
        self.order = order
        self.until_healthy = {}
        for i, line in enumerate(initial_state):
            for j, x in enumerate(line):
                if x == 'S':
                    self.until_healthy[(i, j)] = 3
                elif x == 'Q':
                    self.until_healthy[(i, j)] = 2
        self.known_state = deepcopy(initial_state)
        self.turn = 0
        self.last_action = -1
        self.limit = 4.9


        self.limit = 58
        self.start = time.time()
        if order == 'first':
            _, self.first_action = self.max1(deepcopy(initial_state), deepcopy(self.until_healthy), alpha=-inf, beta=inf, depth=6, score=0)
        self.limit = 4.9

    def act(self, state):
        self.start = time.time()
        self.turn += 1
        if self.turn == 1 and self.order == 'first':
            return self.first_action
        if self.order == 'first':
            return self.act1(state)
        elif self.order == 'second':
            return self.act2(state)

    def act1(self, state):
        # update 'until_healthy'
        if self.turn != 1:
            for i, line in enumerate(state):
                for j, x in enumerate(line):
                    if x == self.known_state[i][j]:
                        if x in ['Q', 'S']:
                            self.until_healthy[(i, j)] -= 1
                    elif x != self.known_state[i][j]:
                        if x == 'S':  # only H can become S
                            self.until_healthy[(i, j)] = 3
                        if x == 'Q':  # only S can become Q
                            self.until_healthy[(i, j)] = 2
                        if x == 'H':  # was Q or S
                            del self.until_healthy[(i, j)]
        self.known_state = state

        _, action = self.max1(deepcopy(state), deepcopy(self.until_healthy),
                              alpha=-inf, beta=inf, depth=self.depth, score=0)
        self.last_action = action
        return action

    # max of minmax when max player is first
    def max1(self, state, until_healthy, alpha, beta, depth, score):
        if depth <= 0:
            score_leaf = self.utility(state)
            return score_leaf + score, []
        value = -inf
        best_action = []
        all_actions = self.actions_max(state)
        if len(all_actions) == 1 and depth == self.depth:
            return 0, all_actions[0]
        for a in all_actions:
            old_states, old_uh = self.result_player1(state, until_healthy, a)
            if depth == self.depth:
                value2, _ = self.min1(state, until_healthy, alpha, beta, depth - 1, score)
            else:
                value2, _ = self.min1(state, until_healthy, alpha, beta, depth - 1, score + self.utility(state))
            self.revert(state, until_healthy, old_states, old_uh)
            if value2 > value:
                value = value2
                best_action = a
            if value >= beta:
                return value, []
            alpha = max(alpha, value)
            if time.time() - self.start > self.limit:
                return value, best_action
        return value, best_action

    # min of minmax when max player is first
    def min1(self, state, until_healthy, alpha, beta, depth, score):
        value = inf
        best_action = []
        for a in self.actions_min(state):
            old_states, old_uh = self.result_player2(state, until_healthy, a)
            value2, _ = self.max1(state, until_healthy, alpha, beta, depth - 1, score)
            self.revert(state, until_healthy, old_states, old_uh)
            if value2 < value:
                value = value2
                best_action = a
            if value <= alpha:
                return value, []
            beta = min(beta, value)
            if time.time() - self.start > self.limit:
                return value, best_action
        return value, best_action

    def revert(self, state, until_healthy, old_states, old_uh):
        for ((i, j), x) in old_states:
            state[i][j] = x
        for ((i, j), x) in old_uh:
            if x == "remove":
                del until_healthy[(i, j)]
            else:
                until_healthy[(i, j)] = x

    def game_over(self, state):
        for i, line in enumerate(state):
            if 'S' in line:
                return False
        return True

    def utility(self, state):
        score1 = 0
        score2 = 0
        for i, line in enumerate(state):
            for j, x in enumerate(line):
                if (i, j) in self.zoc:
                    if x == 'S':
                        score1 -= 1
                    elif x == 'H' or x == 'I':
                        score1 += 1
                    elif x == 'Q':
                        score1 -= 5
                else:
                    if x == 'S':
                        score2 -= 1
                    elif x == 'H' or x == 'I':
                        score2 += 1
                    elif x == 'Q':
                        score2 -= 5
        return score1 - score2

    def result_player1(self, state, until_healthy, action):

        old_states = []
        old_uh = []

        for a in action:
            i, j = a[1][0], a[1][1]
            if a[0] == 'vaccinate':
                old_states.append(((i, j), state[i][j]))
                state[i][j] = 'I'

        return old_states, old_uh

    def result_player2(self, state, until_healthy, action):

        old_states = []
        old_uh = []

        num_rows = len(state)
        num_columns = len(state[0])

        for a in action:
            i, j = a[1][0], a[1][1]
            if a[0] == 'vaccinate':
                old_states.append(((i, j), state[i][j]))
                state[i][j] = 'I'

        c_state = deepcopy(state)

        # spread infection
        for i in range(num_rows):
            for j in range(num_columns):
                if c_state[i][j] == 'H':
                    if ((i - 1 >= 0 and c_state[i - 1][j] == 'S') or
                            (i + 1 < num_rows and c_state[i + 1][j] == 'S') or
                            (j - 1 >= 0 and c_state[i][j - 1] == 'S') or
                            (j + 1 < num_columns and c_state[i][j + 1] == 'S')):
                        old_states.append(((i, j), state[i][j]))
                        state[i][j] = 'S'
                        old_uh.append(((i, j), "remove"))
                        until_healthy[(i, j)] = 4

        # sickness + quarantine expires
        expired = []
        for coordinates in until_healthy:
            old_uh.append((coordinates, until_healthy[coordinates]))
            until_healthy[coordinates] -= 1
            if until_healthy[coordinates] == 0:
                i, j = coordinates[0], coordinates[1]
                old_states.append(((i, j), state[i][j]))
                state[i][j] = 'H'
                expired.append((i, j))

        for coordinates in expired:
            del until_healthy[coordinates]

        return old_states, old_uh

    # actions of max player
    def actions_max(self, state):
        healthy_list = []  # coordinates of all healthy

        for i, line in enumerate(state):
            for j, x in enumerate(line):
                if (i, j) not in self.zoc:
                    continue
                elif x == 'H':
                    healthy_list.append((i, j))

        if len(healthy_list) == 0:
            healthy_iter = []
        else:
            healthy_iter = list(itertools.combinations(healthy_list, 1))

        actions_list = []

        for h in healthy_iter:
            action = []
            for c in h:
                action.append(('vaccinate', c))
            actions_list.append(action)
        return actions_list

    # actions of min player
    def actions_min(self, state):
        healthy_list = []  # coordinates of all healthy

        for i, line in enumerate(state):
            for j, x in enumerate(line):
                if (i, j) in self.zoc:
                    continue
                elif x == 'H':
                    healthy_list.append((i, j))

        if len(healthy_list) == 0:
            healthy_iter = []
        else:
            healthy_iter = list(itertools.combinations(healthy_list, 1))

        actions_list = []

        for h in healthy_iter:
            action = []
            for c in h:
                action.append(('vaccinate', c))
            actions_list.append(action)
        return actions_list

    def act2(self, state):
        # update 'until_healthy'
        if self.turn == 1:
            for i, line in enumerate(state):
                for j, x in enumerate(line):
                    if x != self.known_state[i][j] and x == 'Q':  # only S can become Q
                        self.until_healthy[(i, j)] = 2

        elif self.turn != 1:
            for i, line in enumerate(state):
                for j, x in enumerate(line):
                    if x in ['H', 'I'] and (i, j) in self.until_healthy:
                        del self.until_healthy[(i, j)]
                    if x == self.known_state[i][j]:
                        if x in ['Q', 'S']:
                            self.until_healthy[(i, j)] -= 1
                    elif x != self.known_state[i][j]:
                        if x == 'S':  # only H can become S
                            self.until_healthy[(i, j)] = 3
                        elif x == 'Q':  # was S or H
                            if ('quarantine', (i, j)) in self.last_action:
                                self.until_healthy[(i, j)] = 2
                            else:
                                self.until_healthy[(i, j)] = 3

        self.known_state = state

        _, action = self.max2(deepcopy(state), deepcopy(self.until_healthy),
                              alpha=-inf, beta=inf, depth=self.depth, score=0)
        self.last_action = action
        return action

    # max of minmax when max player is second
    def max2(self, state, until_healthy, alpha, beta, depth, score):
        value = -inf
        best_action = []
        for a in self.actions_max(state):
            old_states, old_uh = self.result_player2(state, until_healthy, a)
            value2, _ = self.min2(state, until_healthy, alpha, beta, depth - 1, score)
            self.revert(state, until_healthy, old_states, old_uh)
            if value2 > value:
                value = value2
                best_action = a
            if value >= beta:
                return value, []
            alpha = max(alpha, value)
            if time.time() - self.start > self.limit:
                return value, best_action
        return value, best_action

    # min of minmax when max player is second
    def min2(self, state, until_healthy, alpha, beta, depth, score):
        if depth <= 0:
            score_leaf = self.utility(state)
            return score_leaf + score, []
        value = inf
        best_action = []
        for a in self.actions_min(state):
            old_states, old_uh = self.result_player1(state, until_healthy, a)
            value2, _ = self.max2(state, until_healthy, alpha, beta, depth - 1, score + self.utility(state))
            self.revert(state, until_healthy, old_states, old_uh)
            if value2 < value:
                value = value2
                best_action = a
            if value <= alpha:
                return value, []
            beta = min(beta, value)
            if time.time() - self.start > self.limit:
                return value, best_action
        return value, best_action


def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))


if __name__ == '__main__':
    print(list(powerset([1, 2, 3, 4])))
