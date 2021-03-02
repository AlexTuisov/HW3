import itertools
from itertools import chain, combinations
from copy import deepcopy
ids = ['208451997', '307871376']


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.zoc = self.pad_zoc(zone_of_control)
        self.init_state = self.pad_the_input(initial_state)
        self.state = deepcopy(self.init_state)
        self.ROW_DIM = len(initial_state) + 2
        self.COL_DIM = len(initial_state[0]) + 2
        self.adversary_zoc = self.calc_adv_zoc()
        self.waiting = bool(order == 'first')
        self.points = 0
        self.depth = 3

    def pad_zoc(self, zone):
        new_zone = [(i + 1, j + 1) for (i, j) in zone]
        return set(new_zone)

    def pad_the_input(self, a_map):
        state = {}
        new_i_dim = len(a_map) + 2
        new_j_dim = len(a_map[0]) + 2
        for i in range(0, new_i_dim):
            for j in range(0, new_j_dim):
                if i == 0 or j == 0 or i == new_i_dim - 1 or j == new_j_dim - 1:
                    state[(i, j)] = 'U'
                elif 'S' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'S0'
                else:
                    state[(i, j)] = a_map[i - 1][j - 1]
        return state

    def get_zoc(self):
        return self.zoc, self.adversary_zoc

    def calc_adv_zoc(self):
        adversary_tiles = [(i, j) for i, j in itertools.product(range(1, self.ROW_DIM - 1), range(1, self.COL_DIM - 1)) if 'U' not in self.state[(i, j)] and (i, j) not in self.zoc]
        return set(adversary_tiles)

    def check_game(self, state):
        values = state.values()
        if 'S1' in values or 'S2' in values or 'S3' in values:
            return False
        return True

    def is_danger(self, state, i, j, zone):
        total = 0
        neighbours = ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))
        for coord in neighbours:
            if coord in zone and 'H' in state[coord]:
                total += 1
        return bool(total == 4)

    def get_actions(self, state, adversary=False):
        """Returns all actions available from this current state to my agent and adversary agent."""
        actions = []
        v_actions = tuple()
        q_actions = tuple()
        healthy = set()
        sick = set()
        if not adversary:
            for (i, j) in self.zoc:
                if 'H' in state[(i, j)]:
                    healthy.add((i, j))
                if 'S' in state[(i, j)] and self.is_danger(state, i, j, self.zoc):
                    sick.add((i, j))
        else:
            for (i, j) in self.adversary_zoc:
                if 'H' in state[(i, j)]:
                    healthy.add((i, j))
                if 'S' in state[(i, j)] and self.is_danger(state, i, j, self.adversary_zoc):
                    sick.add((i, j))
        try:
            to_quarantine = list(chain.from_iterable(combinations(sick, r) for r in range(3)))[1:]
        except ValueError:
            to_quarantine = []
        try:
            to_vaccinate = list(chain.from_iterable(combinations(healthy, r) for r in range(2)))[1:]
        except ValueError:
            to_vaccinate = []
        for item in to_quarantine:
            temp_q_actions = ()
            for mini_item in item:
                temp_q_actions += (('quarantine', mini_item), )
            q_actions += (temp_q_actions, )
        for item in to_vaccinate:
            temp_v_actions = ()
            for mini_item in item:
                temp_v_actions += (('vaccinate', mini_item), )
            v_actions += (temp_v_actions, )
        for v_item in v_actions:
            actions.append(v_item)
        for q_item in q_actions:
            actions.append(q_item)
            for v_item in v_actions:
                actions.append(q_item + v_item)
        actions.append(tuple())
        return actions

    def act(self, state):
        self.absorb_map(state)
        action = self.build_minimax_decision(self.state, self.depth)
        # make suitable for the given map
        return_act = []
        for mini_act in action:
            return_act.append((mini_act[0], (mini_act[1][0] - 1, mini_act[1][1] - 1)))
        return return_act

    def absorb_map(self, state):
        for i in range(self.ROW_DIM - 2):
            for j in range(self.COL_DIM - 2):
                if state[i][j] == self.state[(i + 1, j + 1)][0]:
                    if self.state[(i + 1, j + 1)] in ['S0', 'S1', 'S2']:
                        turn = int(self.state[(i + 1, j + 1)][1])
                        self.state[(i + 1, j + 1)] = 'S' + str(turn + 1)
                    elif self.state[(i + 1, j + 1)] in ['Q0', 'Q1']:
                        turn = int(self.state[(i + 1, j + 1)][1])
                        self.state[(i + 1, j + 1)] = 'Q' + str(turn + 1)
                else:
                    tile = state[i][j]
                    self.state[(i + 1, j + 1)] = tile
                    if tile in ['S', 'Q']:
                        self.state[(i + 1, j + 1)] = tile + str(1)

    def build_minimax_decision(self, state, depth):
        root = Node(state, self.waiting)
        value = -999999
        actions = []
        alpha = -999999
        beta = 999999
        successors = root.expand(self, not self.waiting)
        for suc_node in successors:
            min_val = self.min_value(suc_node, depth - 1, alpha, beta)
            if min_val > value:
                value = min_val
                actions = suc_node.action
                alpha = value
        return actions

    def max_value(self, parent, depth, alpha, beta):
        if self.check_game(parent.state) or depth == 0:
            return parent.d_points
        value = -999999
        successors = parent.expand(self, not self.waiting, False)
        for suc_node in successors:
            min_val = self.min_value(suc_node, depth - 1, alpha, beta)
            value = max(min_val, value)
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def min_value(self, parent, depth, alpha, beta):
        if self.check_game(parent.state) or depth == 0:
            return parent.d_points
        value = 999999
        successors = parent.expand(self, self.waiting, True)
        for suc_node in successors:
            max_val = self.max_value(suc_node, depth - 1, alpha, beta)
            value = min(max_val, value)
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value


def apply_action(actions, state):
    new_state = deepcopy(state)
    if actions:
        for atomic_action in actions:
            effect, location = atomic_action[0], (atomic_action[1][0], atomic_action[1][1])
            if 'v' in effect:
                new_state[location] = 'I'
            else:
                new_state[location] = 'Q0'
    return new_state


def change_state(state, agent):
    new_state = deepcopy(state)
    # virus spread
    for i in range(1, agent.ROW_DIM - 1):
        for j in range(1, agent.COL_DIM - 1):
            if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
                                              'S' in state[(i + 1, j)] or
                                              'S' in state[(i, j - 1)] or
                                              'S' in state[(i, j + 1)]):
                new_state[(i, j)] = 'S1'
    # advancing sick counters
    for i in range(1, agent.ROW_DIM - 1):
        for j in range(1, agent.COL_DIM - 1):
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


def get_score(control_zone, state):
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


def get_total_score(agent, next_state):
    self_zoc, adv_zoc = agent.get_zoc()
    pos = get_score(self_zoc, next_state)
    neg = get_score(adv_zoc, next_state)
    return pos-neg


# ______________________________________________________________________________


class Node:
    def __init__(self, state, waiting, parent=None, action=None, points=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = deepcopy(state)
        self.waiting = waiting
        self.parent = parent
        self.action = action
        self.d_points = points
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def child_node(self, agent, action, calc_dynamics=False):
        next_state = apply_action(action, self.state)
        if calc_dynamics:
            new_next_state = change_state(next_state, agent)
            score = self.d_points + get_total_score(agent, new_next_state)
            return Node(new_next_state, self.waiting, self, action, score)
        return Node(next_state, self.waiting, self, action, self.d_points)

    def expand(self, agent, calc_dynamics=False, adversary=False):
        """List the nodes reachable in one step from this node."""
        actions = agent.get_actions(self.state, adversary)
        return (self.child_node(agent, action, calc_dynamics) for action in actions)

