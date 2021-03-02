import itertools
from copy import deepcopy

ids = ['322723982', '322593377']

def illegal(state, decision):
    if decision:
        if decision[0][0] == 'vaccinate' and state[decision[0][1][0]][decision[0][1][1]][0] == 'S':
            return True
        if decision[0][0] == 'quarantine' and state[decision[0][1][0]][decision[0][1][1]][0] == 'H':
            return True
    return False


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.my_zoc = zone_of_control
        self.DIMENSIONS = (len(initial_state), len(initial_state[0]))
        self.op_zoc = [(i, j) for i, j in itertools.product(range(self.DIMENSIONS[0]),
                                                            range(self.DIMENSIONS[1])) if (i, j) not in self.my_zoc
                                                            and initial_state[i][j][0] != 'U']
        self.order = order
        self.prev_state = self.enrich_start_state(initial_state)
        self.num_actions = 0

    def enrich_start_state(self, state):
        prev_state = deepcopy(state)
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j] == 'S':
                    prev_state[i][j] = 'S1'
        return prev_state

    def enrich_state(self, state):
        if self.order == 'first':
            for i in range(len(state)):
                for j in range(len(state[0])):
                    if state[i][j][0] == 'Q' != self.prev_state[i][j][0]:
                        self.cur_state[i][j] = 'Q0'
                    elif state[i][j][0] == 'I' != self.prev_state[i][j][0]:
                        self.cur_state[i][j] = 'I'
            self.cur_state = self.natural_change(self.cur_state)
        else:
            for i in range(len(state)):
                for j in range(len(state[0])):
                    if state[i][j][0] == 'Q' != self.prev_state[i][j][0]:
                        self.cur_state[i][j] = 'Q0'
                    elif state[i][j][0] == 'I' != self.prev_state[i][j][0]:
                        self.cur_state[i][j] = 'I'

    def act(self, state):
        self.cur_state = deepcopy(self.prev_state)
        if self.num_actions > 0:
            self.enrich_state(state)
        self.num_actions += 1
        decision = self.minimax_decision(self.cur_state)
        decision2 = []
        if illegal(state, decision):
            for (i, j) in self.my_zoc:
                if 'H' == state[i][j][0]:
                    if check_neighbors(state, (i, j)):
                        decision = [(("vaccinate", (i, j)))]
                        self.prev_state = self.get_next_state(self.cur_state, decision, self.order)[1]
                        return decision
                    else:
                        decision2 = [(("vaccinate", (i, j)))]
            if decision2:
                self.prev_state = self.get_next_state(self.cur_state, decision2, self.order)[1]
                return decision2
            decision = []
            self.prev_state = self.get_next_state(self.cur_state, decision, self.order)[1]
            return decision
        self.prev_state = self.get_next_state(self.cur_state, decision, self.order)[1]
        return list(decision)

    def minimax_decision(self, state):
        max_value = float('-inf')
        max_action = []
        for a, s in self.get_successors(state, self.order, self.my_zoc):
            value = self.min_value(s, 1, float('-inf'), float('inf'))
            if value > max_value:
                max_value = value
                max_action = a
        return max_action

    def max_value(self, state, depth, alpha, beta):
        if self.terminal_state(state, depth):
            return self.heuristic(state)
        v = float('-inf')
        for a, s in self.get_successors(state, self.order, self.my_zoc):
            v = max(v, self.min_value(s, depth + 1, alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, state, depth, alpha, beta):
        if self.terminal_state(state, depth):
            return self.heuristic(state)
        v = float('inf')
        op_order = 'first'
        if self.order == 'first':
            op_order = 'second'
        for a, s in self.get_successors(state, op_order, self.op_zoc):
            v = min(v, self.max_value(s, depth + 1, alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def natural_change(self, state):
        new_state = deepcopy(state)
        n, m = len(state), len(state[0])
        # virus spread
        for i in range(n):
            for j in range(m):
                if state[i][j][0] == 'H':
                    if check_neighbors(state, (i, j)):
                        new_state[i][j] = 'S1'
                elif state[i][j][0] == 'S':
                    turn = int(state[i][j][1])
                    if turn < 3:
                        new_state[i][j] = 'S' + str(turn + 1)
                    else:
                        new_state[i][j] = 'H'
                elif state[i][j][0] == 'Q':
                    turn = int(state[i][j][1])
                    if turn < 2:
                        new_state[i][j] = 'Q' + str(turn + 1)
                    else:
                        new_state[i][j] = 'H'
        return new_state

    def get_next_state(self, state, actions, player):
        next_state = deepcopy(state)
        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
            if 'v' in effect:
                next_state[location[0]][location[1]] = 'I'
            else:
                next_state[location[0]][location[1]] = 'Q0'
        if player == 'second':
            return actions, self.natural_change(next_state)
        else:
            return actions, next_state

    def get_successors(self, state, player, zoc):
        sick_blocks = []
        med_action_list = []
        non_urgent_healthy = []
        for (i, j) in zoc:
            if 'H' == state[i][j][0]:
                if check_neighbors(state, (i, j)):
                    med_action_list.append(("vaccinate", (i, j)))
                else:
                    non_urgent_healthy.append(("vaccinate", (i, j)))
            if 'S' == state[i][j][0]:
                sick_blocks.append(("quarantine", (i, j)))
        successors_list = []
        police_actions = list(itertools.combinations(sick_blocks, 1))
        med_action_list = list(itertools.combinations(med_action_list, 1))
        actions = []
        if med_action_list:
            actions = med_action_list
        elif non_urgent_healthy:
            actions = list(itertools.combinations(non_urgent_healthy, 1))
        elif police_actions:
            actions = police_actions
        for act in actions:
            successors_list.append(self.get_next_state(state, act, player))
        return successors_list

    def terminal_state(self, state, depth):
        if depth >= 4:
            return True
        for i in range(len(state)):
            for j in range(len(state[0])):
                if state[i][j][0] == 'S':
                    return False
        return True

    def heuristic(self, state):
        my_score = 0
        op_score = 0
        for i in range(len(state)):
            for j in range(len(state[0])):
                if (i, j) in self.my_zoc:
                    if 'H' == state[i][j][0]:
                        my_score += 1
                    elif 'I' == state[i][j][0]:
                        my_score += 1
                    elif 'S' == state[i][j][0]:
                        my_score -= 1
                    elif 'Q' == state[i][j][0]:
                        my_score -= 5
                else:
                    if 'H' == state[i][j][0]:
                        op_score += 1
                    elif 'I' == state[i][j][0]:
                        op_score += 1
                    elif 'S' == state[i][j][0]:
                        op_score -= 1
                    elif 'Q' == state[i][j]:
                        op_score -= 5
        return my_score - op_score


def check_neighbors(new_map, loc):
    n = len(new_map)
    m = len(new_map[0])
    x, y = loc
    if x != 0:
        if new_map[x - 1][y][0] == 'S':
            return True
    if y != 0:
        if new_map[x][y - 1][0] == 'S':
            return True
    if x != n - 1:
        if new_map[x + 1][y][0] == 'S':
            return True
    if y != m - 1:
        if new_map[x][y + 1][0] == 'S':
            return True
    return False
