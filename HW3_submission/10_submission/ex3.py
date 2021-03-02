import itertools
from utils import is_in
from copy import deepcopy


ids = ['311127245', '315816157']
DIMENSIONS = (10, 10)
infinity = float('inf')


class Agent:
    def __init__(self, initial_state, zone_of_control, order):
        self.order = order
        self.zoc = zone_of_control
        self.zoc_rival = [(i, j) for i, j in itertools.product(range(0, 10), range(0, 10))
                          if 'U' not in initial_state[i][j] and (i, j) not in self.zoc]
        self.prev_state = None
        self.score = 0  # should be updated in each act
        self.limit = 4

    def state_as_dict(self, a_map):
        state = {}
        if not self.prev_state:
            for i in range(0, 10):
                for j in range(0, 10):
                    if 'S' in a_map[i][j]:
                        state[(i, j)] = 'S1'
                    elif 'Q' in a_map[i][j]:
                        state[(i, j)] = 'Q0'
                    else:
                        state[(i, j)] = a_map[i][j]
        else:
            for i in range(0, 10):
                for j in range(0, 10):
                    if 'S' in a_map[i][j]:
                        if 'S' in self.prev_state[(i, j)]:
                            turn = int(self.prev_state[(i, j)][1])
                            if turn < 3:
                                state[(i, j)] = 'S' + str(turn + 1)
                            else:
                                state[(i, j)] = 'H'
                        else:
                            state[(i, j)] = 'S1'
                    elif 'Q' in a_map[i][j]:
                        if 'Q' in self.prev_state[(i, j)]:
                            turn = int(self.prev_state[(i, j)][1])
                            if turn < 2:
                                state[(i, j)] = 'Q' + str(turn + 1)
                            else:
                                state[(i, j)] = 'H'
                        else:
                            state[(i, j)] = 'Q1'
                    else:
                        state[(i, j)] = a_map[i][j]
        return state

    def act(self, state):
        alpha, beta, max_val, max_action = -infinity, infinity, -infinity, None
        state_dict = self.state_as_dict(state)
        self.prev_state = deepcopy(state_dict)
        if self.order == 'first':
            agent_score = self.game_utility(self.zoc, state_dict)
            rival_score = self.game_utility(self.zoc_rival, state_dict)
            self.score += (agent_score - rival_score)
        parent_node = Node(state_dict, 0, self.score, self.order)
        actions_from_parent = self.actions(parent_node.state, self.zoc, self.zoc_rival)
        children = [(self.child_node(deepcopy(state_dict), self.zoc, self.zoc_rival, 0, parent_node.score, parent_node.order, action), action) for action in actions_from_parent]
        for child, action in children:
            temp_v = self.min_value(child, alpha, beta)
            if temp_v > max_val:
                max_val = temp_v
                max_action = action
        return max_action

    def min_value(self, node, alpha, beta):
        if self.terminate(node):
            return node.score
        v = infinity
        actions_from_node = self.actions(node.state, self.zoc_rival, self.zoc)
        children = [self.child_node(node.state, self.zoc, self.zoc_rival, node.depth, node.score, node.order, action) for action in actions_from_node]
        for child in children:
            temp_v = self.max_value(child, alpha, beta)
            v = min(v, temp_v)
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def max_value(self, node, alpha, beta):
        if self.terminate(node):
            return node.score
        v = -infinity
        actions_from_node = self.actions(node.state, self.zoc, self.zoc_rival)
        children = [self.child_node(node.state, self.zoc, self.zoc_rival, node.depth, node.score, node.order, action) for action in actions_from_node]
        for child in children:
            temp_v = self.min_value(child, alpha, beta)
            v = max(v, temp_v)
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def terminate(self, node):
        if ('S1' in node.state.values() or 'S2' in node.state.values() or 'S3' in node.state.values() or 'S' in node.state.values()) and self.limit > node.depth:
            return False
        return True

    @staticmethod
    def game_utility(zoc, state_dict):
        score = 0
        for (i, j) in zoc:
            if 'I' in state_dict[(i, j)]:
                score += 1
            elif 'H' in state_dict[(i, j)]:
                score += 1
            elif 'S' in state_dict[(i, j)]:
                score -= 1
            elif 'Q' in state_dict[(i, j)]:
                score -= 5
        return score

    # zoc - area he can change
    def actions(self, state, zoc, zoc_rival):
        s_action = self.quar_options(state, zoc, zoc_rival)
        h_action = self.vac_options(state, zoc, zoc_rival)
        actions = []
        # create a list of all possible actions combining medics + police
        if h_action:
            for vac in h_action:
                actions.append([vac])
                for quar in s_action:
                    action = [quar, vac]
                    actions.append(action)
        else:
            actions.append(tuple())
            for quar in s_action:
                actions.append([quar])
        return actions

    def child_node(self, state, zoc, zoc_rival, depth, score, parent_order, action):
        new_state = self.apply_action(deepcopy(state), action)
        new_score = score
        new_order = 'second'
        if parent_order == 'second':
            new_order = 'first'
            score_agent = self.game_utility(zoc, new_state)
            score_rival = self.game_utility(zoc_rival, new_state)
            new_score += (score_agent - score_rival)
        new_node = Node(new_state, depth+1, new_score, new_order, action)
        return new_node

    @staticmethod
    def apply_action(state, actions):
        if actions:
            for atomic_action in actions:
                effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
                if 'v' in effect:
                    state[location] = 'I'
                else:
                    state[location] = 'Q0'
        return state


    @staticmethod
    def vac_options(state, zoc, zoc_rival):
        to_vac = []
        scores =[]
        row_num, col_num = 10, 10
        for (i, j) in zoc:
            counter = 0
            if state[(i,j)] == 'H':
                if i > 0:
                    if 'S' in state[(i-1,j)]:
                        counter += 1
                    elif state[(i - 1, j)] in ['U', 'I']:
                        counter -= 1
                    elif (i - 1, j) in zoc_rival and state[(i - 1, j)] in ['H']:
                        counter -= 2
                if i < row_num - 1:
                    if 'S' in state[(i+1, j)]:
                        counter += 1
                    elif state[(i + 1, j)] in ['U', 'I']:
                        counter -= 1
                    elif (i + 1, j) in zoc_rival and state[(i + 1, j)] in ['H']:
                        counter -= 2
                if j > 0:
                    if 'S' in state[(i, j-1)]:
                        counter += 1
                    elif state[(i, j - 1)] in ['U', 'I']:
                        counter -= 1
                    elif (i, j - 1) in zoc_rival and state[(i, j - 1)] in ['H']:
                        counter -= 2
                if j < col_num - 1:
                    if 'S' in state[(i, j+1)]:
                        counter += 1
                    elif state[(i, j + 1)] in ['U', 'I']:
                        counter -= 1
                    elif (i, j + 1) in zoc_rival and state[(i, j + 1)] in ['H']:
                        counter -= 2
                scores.append(counter)
                to_vac.append((i, j, counter))
        if not to_vac:
            return tuple()
        else:
            max_score = max(scores)
            vac_options = []
            for x, y, z in to_vac:
                if z == max_score:
                    vac_options.append(("vaccinate", (x, y)))
            return vac_options

    @staticmethod
    def quar_options(state, zoc, zoc_rival):
        to_quar = []
        scores =[]
        row_num, col_num = 10, 10
        for (i, j) in zoc:
            counter = 0
            if state[(i,j)] == 'S':
                if i > 0:
                    if (i - 1, j) in zoc_rival and state[(i - 1, j)] in ['H']:
                        counter -= 4
                    elif (i - 1, j) in zoc and state[(i - 1, j)] in ['H']:
                        counter += 2
                    elif state[(i - 1, j)] in ['U', 'I']:
                        counter -= 1
                if i < row_num - 1:
                    if (i + 1, j) in zoc_rival and state[(i + 1, j)] in ['H']:
                        counter -= 4
                    elif (i + 1, j) in zoc and state[(i + 1, j)] in ['H']:
                        counter += 2
                    elif state[(i + 1, j)] in ['U', 'I']:
                        counter -= 1
                if j > 0:
                    if (i, j-1) in zoc_rival and state[(i, j-1)] in ['H']:
                        counter -= 4
                    elif (i, j-1) in zoc and state[(i, j-1)] in ['H']:
                        counter += 2
                    elif state[(i, j - 1)] in ['U', 'I']:
                        counter -= 1
                if j < col_num - 1:
                    if (i, j + 1) in zoc_rival and state[(i, j + 1)] in ['H']:
                        counter -= 4
                    elif (i, j + 1) in zoc and state[(i, j + 1)] in ['H']:
                        counter += 2
                    elif state[(i, j + 1)] in ['U', 'I']:
                        counter -= 1
                scores.append(counter)
                to_quar.append((i, j, counter))
        if not to_quar:
            return tuple()
        else:
            max_score = max(scores)
            quar_options = []
            for x, y, z in to_quar:
                if z == max_score:
                    quar_options.append(("quarantine", (x, y)))
            return quar_options

class Node:
    def __init__(self, state, depth, score, order, action=None):
        self.state = state  # state is dict
        self.depth = depth
        self.score = score
        self.order = order
        self.action = action
