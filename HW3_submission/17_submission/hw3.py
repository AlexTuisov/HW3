import random
from itertools import chain, combinations
import pickle

ids = ['316406685', '205783244']
DIMENSIONS = (10, 10)
INF_PLUS = float('inf')
INF_MINUS = float('-inf')
MAX_DEPTH = 4


def pad_the_input(a_map):
    state = {}
    new_i_dim = DIMENSIONS[0] + 2
    new_j_dim = DIMENSIONS[1] + 2
    for i in range(0, new_i_dim):
        for j in range(0, new_j_dim):
            if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                state[(i, j)] = 'U'
            elif 'S' in a_map[i - 1][j - 1]:
                state[(i, j)] = 'S1'
            else:
                state[(i, j)] = a_map[i - 1][j - 1]
    return state


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.order = order
        self.pad_map = pickle.loads(pickle.dumps(pad_the_input(initial_state), -1))
        self.pad_ZOC = [(i + 1, j + 1) for (i, j) in zone_of_control]
        self.pad_other_ZOC = [(i, j) for (i, j) in self.pad_map.keys() if (i, j) not in self.pad_ZOC and self.pad_map[(i, j)] != 'U']
        self.take_first_action = False
        if self.order == 'first':
            self.take_first_action = True
            self.first_action = minimax_decision(self.pad_ZOC, self.pad_other_ZOC, self.pad_map, self.order, MAX_DEPTH, is_first_round=True)

    def act(self, state):
        self.update_counters(state)
        if self.take_first_action:
            self.take_first_action = False
            act_to_perform = self.first_action
        else:
            act_to_perform = minimax_decision(self.pad_ZOC, self.pad_other_ZOC, self.pad_map, self.order, MAX_DEPTH)
        if act_to_perform is None:
            act_to_perform = tuple()
        return act_to_perform

    def update_counters(self, state):
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                if state[i][j] == self.pad_map[(i + 1, j + 1)][0]:
                    if self.pad_map[(i + 1, j + 1)] in ['S0', 'S1', 'S2', 'Q0', 'Q1']:
                        self.pad_map[(i + 1, j + 1)] = str(self.pad_map[(i + 1, j + 1)][0]) + str(int(self.pad_map[(i + 1, j + 1)][1]) + 1)
                else:
                    self.pad_map[(i + 1, j + 1)] = state[i][j]
                    if state[i][j] in ['S', 'Q']:
                        self.pad_map[(i + 1, j + 1)] += '1'


def minimax_decision(ZOC, other_ZOC, init_state, order, max_depth, alpha=INF_MINUS, beta=INF_PLUS, is_first_round=False):
    root = Node(init_state)
    value = INF_MINUS
    turn = True
    best_act = None

    for child in root.expand(ZOC, other_ZOC, turn, order, is_first_game=is_first_round):
        minimum_value = min_value(ZOC, other_ZOC, child, not turn, max_depth, order, alpha, beta)
        if minimum_value > value:
            best_act = child.action
            value = minimum_value
            alpha = value
    return best_act


def min_value(ZOC, other_ZOC, node, turn, max_depth, order, alpha, beta):
    if goal_test(node.state) or node.depth >= max_depth:
        return node.utility

    value = INF_PLUS
    for child in node.expand(ZOC, other_ZOC, turn, order):
        value = min(value, max_value(ZOC, other_ZOC, child, not turn, max_depth, order, alpha, beta))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value


def max_value(ZOC, other_ZOC, node, turn, max_depth, order, alpha, beta):
    if goal_test(node.state) or node.depth >= max_depth:
        return node.utility

    value = INF_MINUS
    for child in node.expand(ZOC, other_ZOC, turn, order):
        value = max(value, min_value(ZOC, other_ZOC, child, not turn, max_depth, order, alpha, beta))
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value


def actions(map_state, ZOC, use_h=True):
    V = "vaccinate"
    Q = "quarantine"

    Ncops = 2
    Nmedics = 1
    S_indexes = []
    H_indexes = []

    for (i, j) in ZOC:
        if map_state[(i, j)][0] == 'S':
            if use_h:
                # check if he has 4 H neighbors in his ZOC
                H_counter = 0
                if (i + 1, j) in ZOC and map_state[(i + 1, j)] == 'H':
                    H_counter += 1
                if (i - 1, j) in ZOC and map_state[(i - 1, j)] == 'H':
                    H_counter += 1
                if (i, j + 1) in ZOC and map_state[(i, j + 1)] == 'H':
                    H_counter += 1
                if (i, j - 1) in ZOC and map_state[(i, j - 1)] == 'H':
                    H_counter += 1
                if H_counter >= 4:
                    S_indexes.append((Q, (i - 1, j - 1)))
            else:
                S_indexes.append((Q, (i - 1, j - 1)))
        elif map_state[(i, j)][0] == 'H':
            if map_state[(i + 1, j)][0] == 'S' or map_state[(i, j + 1)][0] == 'S' or map_state[(i - 1, j)][0] == 'S' or map_state[(i, j - 1)][0] == 'S':
                H_indexes.append((V, (i - 1, j - 1)))

    final_sick = tuple(chain.from_iterable(combinations(S_indexes, r) for r in range(Ncops + 1)))[1:]
    final_health = tuple(combinations(H_indexes, min(Nmedics, len(H_indexes))))

    final_actions = []
    for health_comb in final_health:
        final_actions.append(health_comb)

    for sick_comb in final_sick:
        for health_comb in final_health:
            final_actions.append((sick_comb + health_comb))

    final_actions.append(tuple())
    random.shuffle(final_actions)
    return tuple(final_actions)


def goal_test(state):
    for val in state.values():
        if val[0] == 'S':
            return False
    return True


def update_scores(control_zone, state):
    score = 0
    for (i, j) in control_zone:
        if 'H' in state[(i, j)]:
            score += 1
        if 'I' in state[(i, j)]:
            score += 1
        if 'S' in state[(i, j)]:
            score -= 1
        if 'Q' in state[(i, j)]:
            score -= 5
    return score


def change_state(state):
    new_state = pickle.loads(pickle.dumps(state, -1))

    # virus spread
    for i in range(1, DIMENSIONS[0] + 1):
        for j in range(1, DIMENSIONS[1] + 1):
            if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
                                         'S' in state[(i + 1, j)] or
                                         'S' in state[(i, j - 1)] or
                                         'S' in state[(i, j + 1)]):
                new_state[(i, j)] = 'S1'

    # advancing sick counters
    for i in range(1, DIMENSIONS[0] + 1):
        for j in range(1, DIMENSIONS[1] + 1):
            if 'S' in state[(i, j)]:
                turn = int(state[(i, j)][1])
                if turn < 3:
                    new_state[(i, j)] = 'S' + str(turn + 1)
                else:
                    new_state[(i, j)] = 'H'

            # advancing quarantine counters
            if 'Q' in state[(i, j)]:
                turn = int(state[(i, j)][1])
                if turn < 2:
                    new_state[(i, j)] = 'Q' + str(turn + 1)
                else:
                    new_state[(i, j)] = 'H'

    return new_state


def apply_action(state, acts):
    new_state = pickle.loads(pickle.dumps(state, -1))
    for atomic_action in acts:
        effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
        if 'v' in effect:
            new_state[location] = 'I'
        else:
            new_state[location] = 'Q0'
    return new_state


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = pickle.loads(pickle.dumps(state, -1))
        self.parent = parent
        self.action = action
        self.depth = 0
        self.utility = 0
        if parent:
            self.depth = parent.depth + 1

    def expand(self, ZOC, other_ZOC, turn, order, is_first_game=False):
        child_nodes = []
        if turn:
            if order == 'first':
                for action in actions(self.state, ZOC, use_h=not is_first_game):
                    current_child = self.child_node(apply_action(self.state, action), action)
                    current_child.utility = current_child.parent.utility
                    child_nodes.append(current_child)
            else: #im second
                for action in actions(self.state, ZOC, use_h=not is_first_game):
                    current_child = self.child_node(change_state(apply_action(self.state, action)), action)
                    current_child.utility = current_child.parent.utility + (update_scores(ZOC, current_child.state) - update_scores(other_ZOC, current_child.state))
                    child_nodes.append(current_child)
        else: #not my turn
            if order == 'first': #he is playing and he is second
                for action in actions(self.state, other_ZOC, use_h=not is_first_game):
                    current_child = self.child_node(change_state(apply_action(self.state, action)), action)
                    current_child.utility = current_child.parent.utility + (update_scores(ZOC, current_child.state) - update_scores(other_ZOC, current_child.state))
                    child_nodes.append(current_child)
            else: #he is playing and he is first
                for action in actions(self.state, other_ZOC, use_h=not is_first_game):
                    current_child = self.child_node(apply_action(self.state, action), action)
                    current_child.utility = current_child.parent.utility
                    child_nodes.append(current_child)
        return tuple(child_nodes)

    def child_node(self, new_state, action):
        return Node(new_state, self, action)

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

    def __repr__(self):
        return "<Node {}>".format(self.state)
