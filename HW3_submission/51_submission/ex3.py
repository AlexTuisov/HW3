import itertools
import math
import time


ids = ['312146897', '311418214']


class Agent:
    INITIAL_MAX_DEPTH = 2
    MAX_DURATION = 4.9  # Seconds

    def __init__(self, initial_state, zone_of_control, order):
        self.state = {}
        self.control = zone_of_control
        self.enemy_control = []
        self.order = order
        self.transform = {}
        # self.update(initial_state)
        for r, row in enumerate(initial_state):
            for c, item in enumerate(row):
                self.state[r, c] = 'H'
        for pos in self.state:
            if pos not in zone_of_control:
                self.enemy_control.append(pos)

    def act(self, state):
        start = time.time()
        self.update(state)
        depth = Agent.INITIAL_MAX_DEPTH
        best_action = None
        timeout = False
        # Attempt increased depth until timeout
        while not timeout:
            action, _, timeout = self.minimax(self.state, depth=depth, start_time=start)
            if best_action is not None and timeout:
                break
            best_action = action
            depth += 1
        return best_action

    def update(self, new_state):
        for r, row in enumerate(new_state):
            for c, item in enumerate(row):
                pos = r, c
                if pos in self.transform:
                    self.transform[pos] -= 1
                if pos in self.state:
                    if self.state[pos] != 'S' and item == 'S':
                        self.transform[pos] = 3
                    if self.state[pos] != 'Q' and item == 'Q':
                        self.transform[pos] = 2
                self.state[r, c] = item

    def minimax(self, state, depth, start_time, alpha=-math.inf, beta=math.inf, enemy=False):
        if depth == 0:
            return None, self.state_score(state, enemy), False
        control = self.enemy_control if enemy else self.control
        actions = []
        vaccinate_actions = []
        quarantine_actions = []
        num_vaccinate, num_quarantine = 0, 0
        for pos in control:
            if state[pos] == 'H':
                actions.append(('vaccinate', pos))
                vaccinate_actions.append(('vaccinate', pos))
                num_vaccinate += 1
            if state[pos] == 'S':
                actions.append(('quarantine', pos))
                quarantine_actions.append(('quarantine', pos))
                num_quarantine += 1
        if len(actions) == 0:
            return None, self.state_score(state, enemy), False
        best_action = []
        best_score = math.inf if enemy else -math.inf
        max_parallel = min(1, num_vaccinate) + min(2, num_quarantine)
        comb = [[]]
        # Avoid quarantine if possible
        if num_vaccinate >= 1:
            if num_quarantine >= 1:
                comb.extend(itertools.combinations(vaccinate_actions, 1))
            if num_quarantine >= 2:
                comb.extend(itertools.product(vaccinate_actions, quarantine_actions))
        else:
            if num_quarantine >= 2:
                comb.extend(itertools.combinations(quarantine_actions, 1))
        comb.extend(itertools.combinations(actions, min(max_parallel, 3)))
        timeout = False
        for action_set in comb:
            new_state = state.copy()
            medics, police = 0, 0
            for action, pos in action_set:
                if action == 'vaccinate':
                    new_state[pos] = 'I'
                    medics += 1
                if action == 'quarantine':
                    new_state[pos] = 'Q'
                    police += 1
            if medics > 1 or police > 2:
                continue
            if self.order == 'first' and enemy or self.order == 'second' and not enemy:
                self.tick(new_state)
            _, score, _ = self.minimax(new_state, depth - 1, start_time, alpha, beta, not enemy)
            if enemy:
                if score < best_score:
                    best_action = action_set
                    best_score = score
                beta = min(beta, score)
                if beta <= alpha:
                    break
            else:
                if score > best_score:
                    best_action = action_set
                    best_score = score
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            if time.time() - start_time >= Agent.MAX_DURATION:
                timeout = True
                break
        return best_action, best_score + self.state_score(state, enemy), timeout

    def state_score(self, state, enemy):
        control = self.enemy_control if enemy else self.control
        score = 0
        for pos in control:
            if state[pos] in {'H', 'I'}:
                score += 1
            if state[pos] == 'S':
                score -= 1
            if state[pos] == 'Q':
                score -= 5
        return score

    def tick(self, state):
        for pos in state:
            if pos in self.transform and self.transform[pos] == 1 and state[pos] in {'S', 'Q'}:
                state[pos] = 'H'
        for px, py in state:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (px + dx, py + dy) in state and state[px, py] == 'H' and state[px + dx, py + dy] == 'S':
                    state[px, py] = 'S'
                    break
