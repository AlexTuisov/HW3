from copy import deepcopy
import random
from itertools import combinations, product

ids = ['208776559', '308558741']

# Constants
MAX_DEPTH = 2


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        self.initial_state = initial_state
        self.rows = len(initial_state)
        self.columns = len(initial_state[0])
        self.first = order == 'first'
        pass

    def _is_game_over(self, state):
        for (i, j) in self.zoc:
            if 'S' in state[i][j]:
                return False
        return True

    def _all_possible_actions(self, state):
        healthy = []
        sick = []
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.append(('vaccinate', (i, j)))
            if 'S' in state[i][j]:
                sick.append(('quarantine', (i, j)))
        healthy.append(())
        sick.append(())
        police_pairs = list(combinations(sick, 2))
        return product(healthy, police_pairs)

    def _apply_action(self, state, action):
        new_state = deepcopy(state)
        for a in action:
            if a == ():
                continue
            action_name, (i, j) = a
            if action_name == 'vaccinate':
                assert new_state[i][j] == 'H'
                new_state[i][j] = 'I'
            if action_name == 'quarantine':
                assert new_state[i][j] == 'S'
                new_state[i][j] = 'Q'
        return new_state

    def _minimax(self, state, depth, alpha, beta, max_player):
        if depth == 0 or self._is_game_over(state):
            return self._calculate_score(state), []
        selected_action = []
        if max_player:
            maxEval = float("-inf")
            for action in self._all_possible_actions(state):
                fixed_action = [action[0], action[1][0], action[1][1]]
                new_state = self._apply_action(state, fixed_action)
                eval, act = self._minimax(new_state, depth - 1, alpha, beta, False)
                if eval > maxEval:
                    maxEval = max(eval, maxEval)
                    selected_action = fixed_action
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval, selected_action
        else:
            minEval = float("inf")
            for action in self._all_possible_actions(state):
                fixed_action = [action[0], action[1][0], action[1][1]]
                new_state = self._apply_action(state, fixed_action)
                eval, act = self._minimax(new_state, depth - 1, alpha, beta, True)
                if eval < minEval:
                    minEval = eval
                    selected_action = fixed_action
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval, selected_action

    def _get_X_neighbors(self, state, i, j, X):
        sum = 0
        if i > 0:
            sum += state[i - 1][j] == X
        if j > 0:
            sum += state[i][j - 1] == X
        if i < self.rows - 1:
            sum += state[i + 1][j] == X
        if j < self.columns - 1:
            sum += state[i][j + 1] == X
        return sum

    def _calculate_score(self, state):
        score = 0
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                score += 1
            if 'I' in state[i][j]:
                score += 1
            if 'S' in state[i][j]:
                score -= (1 + self._get_X_neighbors(state, i, j, 'H'))
            if 'Q' in state[i][j]:
                score -= 5
        return score

    def act(self, state):
        score, selected_action = self._minimax(state, MAX_DEPTH, float("-inf"), float("inf"), True)
        return [a for a in selected_action if a != ()]


class RandomAgent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = zone_of_control
        # print(initial_state)

    def act(self, state):
        action = []
        healthy = set()
        sick = set()
        for (i, j) in self.zoc:
            if 'H' in state[i][j]:
                healthy.add((i, j))
            if 'S' in state[i][j]:
                sick.add((i, j))
        try:
            to_quarantine = random.sample(sick, 2)
        except ValueError:
            to_quarantine = []
        try:
            to_vaccinate = random.sample(healthy, 1)
        except ValueError:
            to_vaccinate = []
        for item in to_quarantine:
            action.append(('quarantine', item))
        for item in to_vaccinate:
            action.append(('vaccinate', item))
        return action